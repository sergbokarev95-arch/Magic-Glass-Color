import io, zipfile, pathlib, hashlib, cairosvg
from PIL import Image
root = pathlib.Path(__file__).resolve().parents[1]
base = root / "base.hnt"
out = root / "dist" / "Magic_Glass_Color_0.4.32_Spotify_TEST.hnt"
out.parent.mkdir(exist_ok=True)
assert hashlib.sha256(base.read_bytes()).hexdigest() == "c80b58aea65cbb8c7212948ae785b77650d84e12ddd2e3d4e0290b613a90b1d2"
png = cairosvg.svg2png(url=str(root / "assets" / "Spotify_Green_Waves.svg"), output_width=512, output_height=512)
im = Image.open(io.BytesIO(png)).convert("RGBA")
assert im.size == (512, 512)
alpha = im.getchannel("A")
assert alpha.getextrema() == (0, 255)
assert all(im.getpixel(p)[3] == 0 for p in [(0,0),(511,0),(0,511),(511,511)])
assert all(p[:3] == (30,215,96) for p in im.getdata() if p[3] == 255)
target = "com.spotify.music.png"
with zipfile.ZipFile(base) as original:
    assert original.testzip() is None
    with zipfile.ZipFile(io.BytesIO(original.read("icons"))) as old_icons:
        assert old_icons.testzip() is None
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as new_icons:
            for item in old_icons.infolist():
                if item.filename != target:
                    new_icons.writestr(item, old_icons.read(item.filename))
            new_icons.writestr(target, png, compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(out, "w") as result:
        for item in original.infolist():
            result.writestr(item, buf.getvalue() if item.filename == "icons" else original.read(item.filename))
with zipfile.ZipFile(base) as a, zipfile.ZipFile(out) as b:
    assert b.testzip() is None
    assert set(a.namelist()) == set(b.namelist())
    for name in a.namelist():
        if name != "icons":
            assert a.read(name) == b.read(name), name
    with zipfile.ZipFile(io.BytesIO(a.read("icons"))) as ai, zipfile.ZipFile(io.BytesIO(b.read("icons"))) as bi:
        assert bi.testzip() is None
        assert set(bi.namelist()) == set(ai.namelist()) | {target}
        for name in ai.namelist():
            if name != target:
                assert ai.read(name) == bi.read(name), name
        assert bi.read(target) == png
print("Verified Spotify only:", out, out.stat().st_size, "alpha bounds:", alpha.getbbox())
