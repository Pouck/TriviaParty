from pathlib import Path
import hashlib,json,shutil,wave,html,base64
from datetime import datetime
R=Path.cwd(); src=Path(r'C:\Users\pierr\Downloads'); out=R/'build/downloaded-clips-20261016'; media=out/'originals';media.mkdir(parents=True,exist_ok=True)
files=sorted([p for p in src.iterdir() if p.is_file() and p.suffix.lower() in ('.wav','.mp3') and datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()>='2026-10-14'],key=lambda p:p.name.casefold())
seen={};rows=[];duplicates=[]
for p in files:
 b=p.read_bytes(); digest=hashlib.sha256(b).hexdigest()
 if digest in seen:
  duplicates.append(dict(file=p.name,duplicateOf=seen[digest]));continue
 n=len(rows)+1; name=f'{n:03d}'+p.suffix.lower(); shutil.copyfile(p,media/name);seen[digest]=p.name
 duration=None
 if p.suffix.lower()=='.wav':
  try:
   with wave.open(str(media/name),'rb') as w:duration=round(w.getnframes()/w.getframerate(),3)
  except wave.Error:pass
 rows.append(dict(number=n,originalName=p.name,file='originals/'+name,sha256=digest,bytes=len(b),durationSeconds=duration,textFromFilename=p.stem.replace('-',' '),reviewStatus='pending',source='User-provided local download; film and speaker unverified'))
manifest=dict(importedAt=datetime.now().isoformat(),sourceDirectory=str(src),downloadCount=len(files),uniqueCount=len(rows),duplicates=duplicates,clips=rows)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nouveaux extraits</title><style>body{background:#101a2b;color:#eef3ff;font:18px system-ui;max-width:1000px;margin:auto;padding:24px}article{background:#203049;padding:20px;border-radius:12px;margin:16px 0}audio{width:100%}button,input{font:inherit;padding:10px}h2{font-size:21px;overflow-wrap:anywhere}a{color:#abd9ff}</style><h1>Nouveaux extraits téléchargés</h1>'''
page+=f'<p>{len(rows)} fichiers uniques. Les titres proviennent des noms de fichiers ; films et interprètes restent à vérifier.</p><button id="all">Tout écouter</button> <button id="stop">Arrêter</button> <button id="export">Exporter mes choix</button>'
for r in rows:
 p=out/r['file']; mime='audio/wav' if p.suffix=='.wav' else 'audio/mpeg'
 page+=f'<article data-number="{r["number"]}"><h2>{r["number"]:03d} · {html.escape(r["textFromFilename"])}</h2><p>{r["durationSeconds"] if r["durationSeconds"] is not None else "?"} s</p><audio controls preload="none" src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"></audio><p><label><input type="checkbox" checked> À garder</label></p></article>'
page+='<script>const tracks='+json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')+';'
page+='''const cards=[...document.querySelectorAll('article')],audios=cards.map(c=>c.querySelector('audio'));let queue=[],next=null;const key='downloaded-clips-20261016';let saved={};try{saved=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}cards.forEach(c=>{let b=c.querySelector('input');if(typeof saved[c.dataset.number]==='boolean')b.checked=saved[c.dataset.number];b.onchange=()=>{saved[c.dataset.number]=b.checked;try{localStorage.setItem(key,JSON.stringify(saved))}catch(e){}}});function stop(){queue=[];next=null;audios.forEach(a=>{a.pause();a.currentTime=0})}async function play(a){next=a;a.currentTime=0;try{await a.play()}catch(e){queue=[]}}audios.forEach(a=>{a.onplay=()=>{if(next!==a)queue=[];next=a;audios.forEach(b=>{if(a!==b)b.pause()})};a.onended=()=>{if(queue.length)play(queue.shift())}});document.querySelector('#all').onclick=()=>{stop();queue=[...audios];play(queue.shift())};document.querySelector('#stop').onclick=stop;document.querySelector('#export').onclick=()=>{let choices=tracks.map((t,i)=>({...t,keep:cards[i].querySelector('input').checked}));let url=URL.createObjectURL(new Blob([JSON.stringify({sampler:key,choices},null,2)],{type:'application/json'}));let a=document.createElement('a');a.href=url;a.download='mes-choix-nouveaux-extraits.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};</script></html>'''
(out/'sampler.html').write_text(page,encoding='utf8')
assert all(hashlib.sha256((out/r['file']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
print(json.dumps(dict(downloads=len(files),unique=len(rows),duplicates=duplicates,totalSeconds=round(sum(r['durationSeconds'] or 0 for r in rows),1),sampler=str(out/'sampler.html')),ensure_ascii=False))
