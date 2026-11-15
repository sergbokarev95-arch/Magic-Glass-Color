import io
import zipfile
from pathlib import Path
import cairosvg

root = Path(__file__).resolve().parents[1]
base = root / "Magic_Glass_Color_0.4.13_Pandora_2GIS_TEST.hnt"
svg = root / "assets" / "Magic_Glass_File_Manager_Plus.svg"
out = root / "dist" / "Magic_Glass_Color_0.4.14_File_Manager_Plus_TEST.hnt"
out.parent.mkdir(exist_ok=True)
png = cairosvg.svg2png(url=str(svg), output_width=512, output_height=512)
target = "com.alphainventor.filemanager.png"
with zipfile.ZipFile(base) as original:
    assert original.testzip() is None
    with zipfile.ZipFile(io.BytesIO(original.read("icons"))) as old_icons:
        assert old_icons.testzip() is None
        assert target not in old_icons.namelist(), "Target icon unexpectedly exists in baseline"
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as new_icons:
            for item in old_icons.infolist():
                new_icons.writestr(item, old_icons.read(item.filename))
            new_icons.writestr(target, png, compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(out, "w") as result:
        for item in original.infolist():
            result.writestr(item, buffer.getvalue() if item.filename == "icons" else original.read(item.filename))
with zipfile.ZipFile(base) as old_outer, zipfile.ZipFile(out) as new_outer:
    assert new_outer.testzip() is None
    for name in old_outer.namelist():
        if name != "icons":
            assert old_outer.read(name) == new_outer.read(name), f"Changed outer entry: {name}"
    with zipfile.ZipFile(io.BytesIO(old_outer.read("icons"))) as old_icons, zipfile.ZipFile(io.BytesIO(new_outer.read("icons"))) as new_icons:
        assert new_icons.testzip() is None
        assert set(new_icons.namelist()) - set(old_icons.namelist()) == {target}
        for name in old_icons.namelist():
            assert old_icons.read(name) == new_icons.read(name), f"Changed icon: {name}"
        assert new_icons.read(target) == png
print(f"Verified: {out} ({out.stat().st_size} bytes)")
