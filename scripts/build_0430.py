import io,zipfile,pathlib,cairosvg
from PIL import Image
root=pathlib.Path(__file__).resolve().parents[1]
base=root/"base.hnt"
out=root/"dist"/"Magic_Glass_Color_0.4.30_AliExpress_Orange_Bag_TEST.hnt"
out.parent.mkdir(exist_ok=True)
png=cairosvg.svg2png(url=str(root/"assets"/"AliExpress_Orange_Bag.svg"),output_width=512,output_height=512)
im=Image.open(io.BytesIO(png)).convert("RGBA")
assert im.getpixel((0,0))[3]==0
target="com.alibaba.aliexpresshd.png"
with zipfile.ZipFile(base) as original:
 assert original.testzip() is None
 with zipfile.ZipFile(io.BytesIO(original.read("icons"))) as old_icons:
  assert old_icons.testzip() is None
  names=old_icons.namelist()
  assert target in names, "AliExpress package not found; refusing to write incorrect icon"
  buf=io.BytesIO()
  with zipfile.ZipFile(buf,"w") as new_icons:
   for item in old_icons.infolist():
    new_icons.writestr(item,png if item.filename==target else old_icons.read(item.filename))
 with zipfile.ZipFile(out,"w") as result:
  for item in original.infolist():result.writestr(item,buf.getvalue() if item.filename=="icons" else original.read(item.filename))
with zipfile.ZipFile(base) as a,zipfile.ZipFile(out) as b:
 assert b.testzip() is None
 for name in a.namelist():
  if name!="icons":assert a.read(name)==b.read(name),name
 with zipfile.ZipFile(io.BytesIO(a.read("icons"))) as ai,zipfile.ZipFile(io.BytesIO(b.read("icons"))) as bi:
  assert bi.testzip() is None
  for name in ai.namelist():
   if name!=target:assert ai.read(name)==bi.read(name),name
  assert bi.read(target)==png
print("Verified",out,out.stat().st_size)
