"""Build the reviewed five-question expansion with offline visuals and source mirrors."""
from pathlib import Path
from collections import Counter
import csv,json,random,runpy,zipfile
from quiz_choice_order import randomize_choices
OUT=Path('package-examples/library-2026-10-12');OUT.mkdir(parents=True,exist_ok=True)
TOPICS=[t for file in sorted(Path('build').glob('library-*-data.py')) for t in runpy.run_path(str(file))['TOPICS']]
VISUALS={p['slug']:p for file in (OUT/'assets').glob('*.json') for p in [json.loads(file.read_text(encoding='utf-8'))]}
catalog=[];rows=[];ids=set();missing=[];pictures=0
for topic_index,t in enumerate(TOPICS):
 for mode in ['qcm','buzzer','qsj','chronologie']:
  entries=t[mode]
  if not entries:continue
  assert len(entries)==5
  pid=f'lib-{mode}-{t["slug"]}-20261012'
  prefix=f'{t["subject"]} — ' if t['slug'] in {'ghibli','ghibli-sorties','odyssee','odyssee-episodes','explorateurs','explorateurs-reperes','pop-rock','recits-autochtones'} else ''
  name=prefix+t['title']+' — '+{'qcm':'QCM','buzzer':'Buzzer','qsj':'Qui suis-je ?','chronologie':'Chronologie'}[mode]
  assert len(pid)<=64
  qs=[];references=[];images={};credits=[]
  for n,e in enumerate(entries,1):
   q=dict(id=f'{pid}-{n:02}',category=name,basePoints=20 if mode=='qsj' else 15,penaltyPoints=5 if mode=='qsj' else 0)
   assert q['id'] not in ids;ids.add(q['id']);note=''
   if mode=='qsj':q.update(kind='guessWho',prompt='Qui suis-je ?',clues=e['clues'],acceptableAnswers=e['answers'])
   elif mode=='qcm':q.update(kind='multipleChoice',prompt=e['prompt'],options=[f'{letter} — {value}' for letter,value in zip('ABCD',e['options'])],correctOptionIndex=e['index'])
   elif mode=='buzzer':q.update(kind='textAnswer',prompt=e['prompt'],acceptableAnswers=e['answers'],allowFuzzyMatch=True)
   else:
    events=e['events'];correct=[text for text,_ in sorted(events,key=lambda item:item[1])]
    assert len(correct)==len(set(correct))==3 and len({key for _,key in events})==3
    display=correct.copy();random.Random(q['id']).shuffle(display)
    if display==correct:display=display[1:]+display[:1]
    items=[dict(id=f'item-{index}',text=text) for index,text in enumerate(display)]
    q.update(kind='ordering',prompt=e['prompt'],items=items,correctOrderIds=[next(i['id'] for i in items if i['text']==text) for text in correct])
    note=' → '.join(f'{text} ({key})' if key>3 else text for text,key in sorted(events,key=lambda item:item[1]))
   if e.get('image'):
    if e['image'] not in VISUALS:missing.append(e['image']);continue
    p=VISUALS[e['image']];rel='images/'+p['file'];blob=(OUT/'assets'/p['file']).read_bytes();assert len(blob)<8*1024*1024
    q['imageUrl']=rel;images[rel]=blob;credits.append(p);pictures+=1
   qs.append(q)
   refs=e.get('sources') or t['sources']
   references.append(dict(question=n,sources=refs,note=note,visual=e.get('image')))
  if missing:continue
  if mode=='qcm':
   before=[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   randomize_choices(qs,pid,extra_positions=(topic_index%4,))
   assert before==[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   assert sorted(Counter(q['correctOptionIndex'] for q in qs).values())==[1,1,1,2]
  if mode in ('qcm','buzzer'):assert sum('imageUrl' in q for q in qs)==2,(pid,'Expected two pictures')
  segment=20 if mode=='qsj' else 15 if mode=='chronologie' else 10 if t['subject']=='Logique et énigmes' else 5
  description='5 questions accessibles en français. '+('4 indices de 20 s ; 20 → 15 → 10 → 5 pts ; erreur : −5 pts.' if mode=='qsj' else 'Lecture libre puis 45 s ; trois cartes à glisser ; 15 → 10 → 5 pts.' if mode=='chronologie' else f'2 visuelles et 3 textuelles ; {segment*3} s ; 15 → 10 → 5 pts.')
  game=dict(id=pid,name=name,description=description,categoryPackages=[pid],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=segment,decayPercentagePerFlip=0,maxFlips=3 if mode=='qsj' else 2,pointsDecayPerFlip=5))
  bank=dict(category=name,subject=t['subject'],answerMode='BUZZER' if mode in ('buzzer','qsj') else 'SIMULTANEOUS',questionTypes=['Qui suis-je ?' if mode=='qsj' else 'Réponse orale' if mode=='buzzer' else 'Chronologie' if mode=='chronologie' else 'Choix multiples'],questions=qs)
  with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
   for rel,value in [('game.json',game),(f'question-bank/{pid}.json',bank)]:
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n';target=OUT/'sources'/pid/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8');z.writestr(rel,text)
   for rel,blob in images.items():
    target=OUT/'sources'/pid/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);z.writestr(rel,blob)
   if credits:z.writestr('images/credits.json',json.dumps(credits,ensure_ascii=False,indent=2)+'\n')
  with zipfile.ZipFile(OUT/(pid+'.zip')) as z:
   assert z.testzip() is None
   assert all(q.get('imageUrl') is None or q['imageUrl'] in z.namelist() for q in qs)
  (OUT/'sources'/pid/'VERIFICATION.json').write_text(json.dumps(references,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  for n,(q,r) in enumerate(zip(qs,references),1):
   answer=q['options'][q['correctOptionIndex']] if mode=='qcm' else ' → '.join(next(i['text'] for i in q['items'] if i['id']==id) for id in q['correctOrderIds']) if mode=='chronologie' else q['acceptableAnswers'][0]
   rows.append([name,n,q['prompt'],q.get('imageUrl',''),*q.get('clues',[]),*(['']*(4-len(q.get('clues',[])))),*q.get('options',['','','','']),answer,' | '.join(q.get('acceptableAnswers',[])),' | '.join(r['sources']),r['note']])
  catalog.append(dict(id=pid,name=name,topic=t['title'],subject=t['subject'],mode=mode,count=5,images=len(images)))
assert not missing,sorted(set(missing))
assert len(ids)==len(rows) and len(catalog)*5==len(rows)
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','Question','Texte','Image',*['Indice '+str(i) for i in range(1,5)],'A','B','C','D','Réponse','Variantes acceptées','Sources','Note']);w.writerows(rows)
(OUT/'CATALOGUE.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
visuals=list(VISUALS.values())
(OUT/'PHOTOS.json').write_text(json.dumps(visuals,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'PHOTOS.md').write_text('# Photos, diagrammes et indices visuels\n\nLes images sont intégrées aux ZIP pour jouer hors ligne. Les indices de fiction sont des illustrations représentatives, pas des captures de films ou des planches de BD. Les diagrammes de logique sont créés pour les questions.\n\n'+'\n\n'.join(f"### {p['slug']}\n\n{p['artist']} — {p['license']}. [Source]({p.get('commons') or p['licenseUrl']}). {p.get('credit','')}\n\n{p['changes']}" for p in visuals)+'\n',encoding='utf-8')
(OUT/'README.md').write_text(f'# Bibliothèque équilibrée — {len(catalog)} forfaits\n\n{len(rows)} questions françaises accessibles, en forfaits de cinq questions. Mélange international et francophone.\n\n## Réglages\n\n- QCM et buzzer : 15 s ; 15 → 10 → 5 pts. Deux questions visuelles et trois textuelles par forfait. Réponse après buzzer : 10 s.\n- Logique et devinettes : 30 s pour réfléchir ; 15 → 10 → 5 pts. Pas de calcul long ou d’énigme nécessitant un piège non expliqué.\n- Qui suis-je ? : quatre indices courts, 20 s chacun ; 20 → 15 → 10 → 5 pts. Erreur : −5 pts ; retour au prochain indice.\n- Chronologies : lecture libre puis 45 s, cartes à glisser et bouton d’envoi. Révélation manuelle possible même si tout le monde n’a pas répondu.\n- A–D répartis en 1/1/1/2 par forfait de cinq questions ; la position supplémentaire varie entre forfaits.\n- Sujets et formats déclarés pour l’ordre équilibré de la partie.\n\n## Forfaits\n\n| Sujet | Thème | Format | Questions | Images | Archive |\n|---|---|---|---:|---:|---|\n'+'\n'.join(f"| {c['subject']} | {c['topic']} | {c['mode']} | 5 | {c['images']} | [{c['id']}.zip]({c['id']}.zip) |" for c in catalog)+'\n\n[Contenu et corrigé](QUESTIONS-ET-REPONSES.csv) · [Audit de la bibliothèque](AUDIT.md) · [Vérification](VERIFICATION.md) · [Crédits visuels](PHOTOS.md).\n\nLes JSON et images modifiables sont dans `sources/<identifiant>/`. Les données sont dans `build/library-*-data.py`. Régénération : `python build/build-library-packages.py`.\n\nCertains personnages ou repères reviennent entre formats, avec une formulation différente. Les sets de reconnaissance peuvent faciliter un Qui suis-je ? ultérieur ; sélectionner les formats selon le public. Les nouvelles séries complètent les anciennes sans les supprimer. Les forfaits de test et de démonstration restent volontairement courts.\n',encoding='utf-8')
print(f'Validated {len(catalog)} packages, {len(rows)} questions, {pictures} visual-question slots and {len(visuals)} offline assets.')
