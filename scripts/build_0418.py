import io,zipfile,pathlib,cairosvg
root=pathlib.Path(__file__).resolve().parents[1]
base=root/"Magic_Glass_Color_0.4.17_VPSUS_TEST.hnt"
out=root/"dist"/"Magic_Glass_Color_0.4.18_Netcraze_TEST.hnt"
out.parent.mkdir(exist_ok=True)
png=cairosvg.svg2png(url=str(root/"assets"/"Netcraze.svg"),output_width=512,output_height=512)
target="ru.netcraze.app.png"
with zipfile.ZipFile(base) as original:
 assert original.testzip() is None
 with zipfile.ZipFile(io.BytesIO(original.read("icons"))) as old_icons:
  assert old_icons.testzip() is None
  buf=io.BytesIO()
  with zipfile.ZipFile(buf,"w") as new_icons:
   for item in old_icons.infolist():
    if item.filename!=target:new_icons.writestr(item,old_icons.read(item.filename))
   new_icons.writestr(target,png,compress_type=zipfile.ZIP_DEFLATED)
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
