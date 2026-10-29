"""Fetch publisher character art candidates for replacing grayscale Astérix drawings."""
import json, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/image-qsj-sampler/candidates/asterix-color'
OUT.mkdir(parents=True,exist_ok=True)
page='https://www.salvat.com/asterix-86'
items={
 'asterix':'https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes2.png',
 'panoramix':'https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes3.png',
 'obelix':'https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes.png',
 'falbala':'https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes6.png',
 'candidate-4':'https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes4.png',
 'candidate-5':'https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes5.png',
 'candidate-7':'https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes7.png',
 'character-1':'https://ar.salvat.com/colecciones/asterix-libros/res/img/personaje-1.png',
 'character-2':'https://ar.salvat.com/colecciones/asterix-libros/res/img/personaje-2.png',
 'character-3':'https://ar.salvat.com/colecciones/asterix-libros/res/img/personaje-3.png',
 'character-4':'https://ar.salvat.com/colecciones/asterix-libros/res/img/personaje-4.png',
 'character-5':'https://ar.salvat.com/colecciones/asterix-libros/res/img/personaje-5.png',
 'character-6':'https://ar.salvat.com/colecciones/asterix-libros/res/img/personaje-6.png',
}
metadata={}
for key,url in items.items():
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'TriviaPartyPrivateLocalQuiz/1.0','Referer':page})
  with urllib.request.urlopen(req,timeout=25) as resp: data=resp.read(); typ=resp.headers.get('Content-Type','')
  if not typ.startswith('image/') or len(data)<1500: raise ValueError(f'{typ} {len(data)} bytes')
  path=OUT/(key+'.png'); path.write_bytes(data)
  metadata[key]={'candidate':path.relative_to(ROOT).as_posix(),'downloadedFrom':url,'sourcePage':page,'contentType':typ,'bytes':len(data),'license':'Copyrighted publisher character artwork; rights reserved; private local review only','review':'Pending visual inspection'}
  print('OK',key,len(data))
 except Exception as e: metadata[key]={'downloadedFrom':url,'sourcePage':page,'candidateStatus':str(e)}; print('SKIP',key,e)
 time.sleep(.15)
(OUT/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
