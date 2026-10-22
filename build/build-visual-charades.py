"""Build and register the user-provided visual charades without changing other packages."""
from pathlib import Path
import json,hashlib,zipfile,csv,re,html
R=Path.cwd();A=R/'package-examples/visual-charades-2026-10-18';O=R/'game-library/current';data=json.loads((A/'authoring.json').read_text(encoding='utf8'));prefix='charades-visuelles-';catalog=[];table=[]
for p in data['packages']:
 pid=p['id'];name=p['name'];mode=p['answerMode'];qs=[];blobs={};refs=[]
 for i,r in enumerate(p['questions'],1):
  b=(A/r['asset']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'];rel=f'images/charade-{i:02d}.png';blobs[rel]=b
  qs.append(dict(kind='textAnswer',id=r['id'],category=name,prompt=r['prompt'],imageUrl=rel,basePoints=15,penaltyPoints=0,acceptableAnswers=r['acceptableAnswers'],allowFuzzyMatch=False))
  refs.append(dict(questionId=r['id'],sourceFilename=r['originalFilename'],sourcePath=r['originalPath'],sha256=r['sha256'],canonicalAnswer=r['answer'],acceptedVariants=r['acceptableAnswers'],note='Réponse fournie par le nom du fichier ; orthographe et typographie françaises corrigées. Image originale conservée.'))
  table.append([pid,name,r['id'],'textAnswer',r['prompt'],rel,'','',r['answer'],'Images utilisateur — 2026-10-18'])
 assert 5<=len(qs)<=7
 bank=dict(category=name,subject=p['subject'],answerMode=mode,questionTypes=['Buzzer' if mode=='BUZZER' else 'Réponses écrites'],questions=qs)
 game=dict(id=pid,name=name,description=f'{len(qs)} charades visuelles. 45 secondes ; 15 → 10 → 5 points. '+('Réponse au buzzer : 10 secondes.' if mode=='BUZZER' else 'Réponses écrites, validées individuellement par l’hôte.'),categoryPackages=[pid],timingConfig=dict(secondsPerFlip=15,decayPercentagePerFlip=0,maxFlips=2,pointsDecayPerFlip=5),answerTimeSeconds=10)
 content={'game.json':game,f'question-bank/{pid}.json':bank,'VERIFICATION.json':refs,'images/credits.json':dict(source='Images générées et fournies par l’utilisateur ; fichiers conservés sans modification.',spellingSources=data['spellingSources'])}
 sd=O/'sources'/pid;sd.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(O/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for rel,obj in content.items():
   b=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf8');dest=sd/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
   if rel!="VERIFICATION.json":z.writestr(rel,b)
  for rel,b in blobs.items():
   dest=sd/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);z.writestr(rel,b)
 catalog.append(dict(id=pid,name=name,count=len(qs),subject=p['subject'],types=bank['questionTypes'],test=False,images=len(qs),sources=['visual-charades-20261018'],seconds=45))
old=json.loads((O/'CATALOGUE.json').read_text(encoding='utf8'));old=[c for c in old if not c['id'].startswith(prefix)];all_catalog=old+catalog
(O/'CATALOGUE.json').write_text(json.dumps(all_catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with (O/'QUESTIONS-ET-REPONSES.csv').open(encoding='utf-8-sig',newline='') as f:csvrows=list(csv.reader(f,delimiter=';'))
csvrows=[csvrows[0]]+[r for r in csvrows[1:] if not r[0].startswith(prefix)]+table
with (O/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f,delimiter=';').writerows(csvrows)
readme=(O/'README.md').read_text(encoding='utf8');readme=re.sub(r'^\d+ forfaits ; \d+ questions',f'{len(all_catalog)} forfaits ; {sum(c["count"] for c in all_catalog)} questions',readme,flags=re.M)
written_count=sum(json.loads((O/'sources'/c['id']/'question-bank'/(c['id']+'.json')).read_text(encoding='utf8')).get('answerMode')=='WRITTEN' for c in all_catalog)
readme=re.sub(r'^\d+ forfaits à réponses écrites',f'{written_count} forfaits à réponses écrites',readme,flags=re.M)
readme=re.sub(r'\n## Charades visuelles — 18 octobre 2026\n[\s\S]*$', '',readme)
readme+='\n## Charades visuelles — 18 octobre 2026\n\n17 nouveaux forfaits de 5 à 7 questions : 9 au buzzer et 8 à réponses écrites. 105 images inédites ; 25 images déjà présentes écartées. Sources durables : `package-examples/visual-charades-2026-10-18/authoring.json` et `assets/`. Reconstruction : `python build/build-visual-charades.py` (aussi appelée par le constructeur principal).\n\n| Sujet | Forfait | Questions | Archive |\n|---|---|---:|---|\n'+'\n'.join(f'| {c["subject"]} | {c["name"]} | {c["count"]} | [{c["id"]}.zip]({c["id"]}.zip) |' for c in catalog)+'\n'
(O/'README.md').write_text(readme,encoding='utf8')
review=A/'REVIEW.html';page='<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Charades visuelles</title><style>body{font:18px system-ui;background:#101827;color:#eef4ff;max-width:1100px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}article{background:#21324a;border-radius:12px;padding:15px;margin:15px 0}img{width:100%;max-height:300px;object-fit:contain}summary{cursor:pointer}a{color:#acd8ff}</style><h1>105 charades visuelles · 17 forfaits</h1><p>5 à 7 questions par forfait · 9 buzzer / 8 réponses écrites · 45 secondes par question.</p>'
for p in data['packages']:
 page+='<h2>'+html.escape(p['name'])+'</h2><p><a href="../../game-library/current/'+p['id']+'.zip">Télécharger le forfait</a></p><div class="grid">'
 for i,r in enumerate(p['questions'],1):page+='<article><p>'+str(i)+'. '+html.escape(r['prompt'])+'</p><img loading="lazy" src="'+r['asset']+'" alt="Charade visuelle"><details><summary>Réponse</summary><p>'+html.escape(' / '.join(r['acceptableAnswers']))+'</p></details></article>'
 page+='</div>'
review.write_text(page+'</html>',encoding='utf8')
with zipfile.ZipFile(A/'TOUS-LES-FORFAITS.zip','w',zipfile.ZIP_STORED) as z:
 for p in data['packages']:z.write(O/(p['id']+'.zip'),p['id']+'.zip')
(A/'SPELLING-REVIEW.json').write_text(json.dumps([dict(original=r['originalFilename'],answer=r['answer'],variants=r['acceptableAnswers']) for p in data['packages'] for r in p['questions']],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'Built {len(catalog)} packages; {len(table)} questions; {sum(p["answerMode"]=="BUZZER" for p in data["packages"])} buzzer / {sum(p["answerMode"]=="WRITTEN" for p in data["packages"])} written.')
