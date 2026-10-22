from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'build/image-tools')
from PIL import Image,ImageDraw,ImageFont
roots=[Path(r'C:\Users\pierr\.codex\generated_images\01a14fb5-2e3e-7b51-8eda-4d8cd4840333'),Path(r'C:\Users\pierr\Documents\Codex\2026-10-05\i\outputs')]
existing={hashlib.sha256(p.read_bytes()).hexdigest():str(p) for p in Path('game-library/current/sources').rglob('*') if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp')}
rows=[]
for p in [p for r in roots for p in r.rglob('*') if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp')]:
 h=hashlib.sha256(p.read_bytes()).hexdigest();rows.append(dict(number=len(rows)+1,path=str(p),name=p.stem,group=p.parent.name,sha256=h,existing=existing.get(h)))
out=Path('build/visual-charades-20261018');out.mkdir(exist_ok=True);(out/'inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
for start in range(0,len(rows),30):
 subset=rows[start:start+30];sheet=Image.new('RGB',(1200,220*((len(subset)+4)//5)),'white');d=ImageDraw.Draw(sheet)
 for j,r in enumerate(subset):
  im=Image.open(r['path']).convert('RGB');im.thumbnail((230,175));x=j%5*240;y=j//5*220;sheet.paste(im,(x+(230-im.width)//2,y));d.text((x+4,y+177),str(r['number'])+' '+r['name'][:28],fill='black',font=font)
 sheet.save(out/f'contact-{start//30+1}.jpg')
print('Images',len(rows),'already used',[(r['number'],r['name']) for r in rows if r['existing']])
