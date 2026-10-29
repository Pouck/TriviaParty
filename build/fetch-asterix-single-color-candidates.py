"""Fetch two visually promising color character replacements for review."""
import json, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/image-qsj-sampler/candidates/asterix-color'
ITEMS={
 'obelix-solo.png':('https://www.pngegg.com/es/png-idjao','https://e7.pngegg.com/pngimages/61/90/png-clipart-obelix-assurancetourix-asterix-the-gaul-getafix-lyre-comics-obelix.png'),
 'idefix-official.webp':('https://www.parcasterix.fr/en/to-do-in-park','https://www.parcasterix.fr/sites/default/files/styles/aventure_full_desktop/public/images/aventures/Idefix_Desk_1_0.png.webp?itok=Jr3EmBJj'),
 'panoramix-color.png':('https://www.pngwing.com/en/free-png-pmcwe','https://w7.pngwing.com/pngs/243/1000/png-transparent-getafix-obelix-jules-cesar-asterix-dogmatix-getafix-comics-food-vertebrate.png'),
 'idefix-color.png':('https://imgbin.com/png/FAPehcsR/obelix-getafix-dogmatix-falbala-png','https://cdn.imgbin.com/14/6/12/imgbin-obelix-getafix-dogmatix-falbala-asterix-XuN9nY1zJwq3sYWWmJq7MJM62.jpg'),
 'obelix-comic.jpg':('https://imgbin.com/png/MVnURjXd/obelix-asterix-cartoon-comic-book-comics-png','https://cdn.imgbin.com/25/25/5/imgbin-obelix-asterix-cartoon-comic-book-comics-asterix-and-obelix-CN81BUgtyeE0nin5Gv2zMMU8M.jpg'),
}
meta={}
for name,(page,url) in ITEMS.items():
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'TriviaPartyPrivateLocalQuiz/1.0','Referer':page})
  with urllib.request.urlopen(req,timeout=25) as r: data=r.read(); ctype=r.headers.get('Content-Type','')
  if not ctype.startswith('image/') or len(data)<1500: raise ValueError(f'{ctype} {len(data)} bytes')
  (OUT/name).write_bytes(data); meta[name]={'candidate':(OUT/name).relative_to(ROOT).as_posix(),'downloadedFrom':url,'sourcePage':page,'contentType':ctype,'bytes':len(data),'license':'Copyrighted character artwork; rights reserved; private local review only','review':'Pending visual inspection'}
  print('OK',name,len(data),ctype)
 except Exception as e: meta[name]={'downloadedFrom':url,'sourcePage':page,'candidateStatus':str(e)}; print('SKIP',name,e)
(OUT/'single-color-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
