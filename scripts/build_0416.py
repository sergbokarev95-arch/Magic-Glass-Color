import io,zipfile,pathlib,cairosvg
root=pathlib.Path(__file__).resolve().parents[1]
base=root/"Magic_Glass_Color_0.4.15_Happ_TEST.hnt"
out=root/"dist"/"Magic_Glass_Color_0.4.16_Happ_Size_TEST.hnt"
out.parent.mkdir(exist_ok=True)
source=(root/"assets"/"Happ.svg").read_text()
source=source.replace('<g fill="#fff" stroke="#50565e" stroke-width="3.5" stroke-linejoin="round">','<g transform="translate(56.32 56.32) scale(0.78)" fill="#fff" stroke="#50565e" stroke-width="3.5" stroke-linejoin="round">')
assert 'scale(0.78)' in source
png=cairosvg.svg2png(bytestring=source.encode(),output_width=512,output_height=512)
target="com.happproxy.png"
with zipfile.ZipFile(base) as original:
 assert original.testzip() is None
 with zipfile.ZipFile(io.BytesIO(original.read("icons"))) as old_icons:
  assert old_icons.testzip() is None
  assert target in old_icons.namelist()
  buff=io.BytesIO()
  with zipfile.ZipFile(buff,"w") as new_icons:
   for item in old_icons.infolist():
    new_icons.writestr(item,png if item.filename==target else old_icons.read(item.filename))
 with zipfile.ZipFile(out,"w") as result:
  for item in original.infolist():result.writestr(item,buff.getvalue() if item.filename=="icons" else original.read(item.filename))
with zipfile.ZipFile(base) as a,zipfile.ZipFile(out) as b:
 assert b.testzip() is None
 for name in a.namelist():
  if name!="icons":assert a.read(name)==b.read(name),name
 with zipfile.ZipFile(io.BytesIO(a.read("icons"))) as ai,zipfile.ZipFile(io.BytesIO(b.read("icons"))) as bi:
  assert bi.testzip() is None
  assert ai.namelist()==bi.namelist()
  for name in ai.namelist():
   if name!=target:assert ai.read(name)==bi.read(name),name
  assert bi.read(target)==png
print("Verified",out,out.stat().st_size)
