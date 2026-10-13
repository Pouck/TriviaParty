from pathlib import Path
from collections import Counter
from itertools import permutations
import csv,json,random,runpy,zipfile
from quiz_choice_order import randomize_choices

DATA=runpy.run_path('build/art-quiz-data.py')
OUT=Path('package-examples/arts-2026-10-11');OUT.mkdir(parents=True,exist_ok=True)
photos={p['slug']:p for p in json.loads((OUT/'PHOTOS.json').read_text(encoding='utf-8'))}
catalog=[];rows=[];ids=set();illustrations=0
for mode,key in [('qcm','CHOICE'),('buzzer','BUZZER'),('qsj','GUESS'),('chronologie','CHRONOLOGY')]:
 for number,(slug,title,entries) in enumerate(DATA[key]):
  pid=f'arts-{mode}-{slug}-20261011';name=f'Arts — {title} — '+{'qcm':'QCM','buzzer':'Buzzer','qsj':'Qui suis-je ?','chronologie':'Chronologie'}[mode]
  assert len(entries)==(5 if mode=='qsj' else 6 if mode=='chronologie' else 8)
  qs=[];references=[];images={};credits=[]
  for n,e in enumerate(entries,1):
   q=dict(id=f'{pid}-{n:02}',category=name,basePoints=20 if mode=='qsj' else 15,penaltyPoints=5 if mode=='qsj' else 0)
   assert q['id'] not in ids;ids.add(q['id']);note=e.get('note','')
   if mode=='qsj':
    assert len(e['clues'])==4 and len(set(e['clues']))==4
    q.update(kind='guessWho',prompt='Qui suis-je ?',clues=e['clues'],acceptableAnswers=e['answers'])
   elif mode=='buzzer':q.update(kind='textAnswer',prompt=e['prompt'],acceptableAnswers=e['answers'],allowFuzzyMatch=True)
   elif mode=='qcm':q.update(kind='multipleChoice',prompt=e['prompt'],options=[f'{letter} — {v}' for letter,v in zip('ABCD',e['options'])],correctOptionIndex=e['index'])
   else:
    works=e['works'];assert len(works)==3 and len({year for _,year in works})==3
    correct=[work for work,_ in sorted(works,key=lambda item:item[1])]
    options=[' → '.join(order) for order in list(permutations(correct))[:4]]
    display=correct.copy();random.Random(q['id']).shuffle(display)
    if display==correct:display=display[1:]+display[:1]
    q.update(kind='multipleChoice',prompt=e['theme']+' :\n'+'\n'.join('• '+work for work in display),options=[f'{letter} — {value}' for letter,value in zip('ABCD',options)],correctOptionIndex=0)
    note+=' Corrigé : '+' → '.join(f'{work} ({abs(year)}'+(' av. J.-C.)' if year<0 else ')') for work,year in sorted(works,key=lambda item:item[1]))
   if e.get('image'):
    p=photos[e['image']];rel='images/'+p['file'];blob=(OUT/'assets'/p['file']).read_bytes()
    assert len(blob)<8*1024*1024
    q['imageUrl']=rel;images[rel]=blob;credits.append(p);illustrations+=1
   qs.append(q)
   references.append(dict(question=n,sources=[DATA['SOURCES'][s] for s in e['sources']],note=note,photo=photos[e['image']]['commons'] if e.get('image') else None))
  if mode in ('qcm','buzzer'):assert sum('imageUrl' in q for q in qs)==4
  if mode in ('qcm','chronologie'):
   expected=[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   randomize_choices(qs,pid,extra_positions=() if len(qs)%4==0 else [(0,2),(1,3)][number])
   assert expected==[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   distribution=Counter(q['correctOptionIndex'] for q in qs)
   assert len(distribution)==4 and max(distribution.values())-min(distribution.values())<=1
  segment=20 if mode=='qsj' else 10 if mode=='chronologie' else 5
  description=f'{len(qs)} questions en français. '+('4 indices de 20 secondes ; 20 → 15 → 10 → 5 points ; erreur : −5 points.' if mode=='qsj' else 'Lecture libre puis 30 secondes ; 15 → 10 → 5 points.' if mode=='chronologie' else '4 images et 4 questions textuelles ; 15 secondes ; 15 → 10 → 5 points.')
  game=dict(id=pid,name=name,description=description,categoryPackages=[pid],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=segment,decayPercentagePerFlip=0,maxFlips=3 if mode=='qsj' else 2,pointsDecayPerFlip=5))
  bank=dict(category=name,subject='Arts',answerMode='BUZZER' if mode in ('buzzer','qsj') else 'SIMULTANEOUS',questionTypes=['Qui suis-je ?' if mode=='qsj' else 'Réponse orale' if mode=='buzzer' else 'Choix multiples'],questions=qs)
  with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
   for rel,value in [('game.json',game),(f'question-bank/{pid}.json',bank)]:
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n';target=OUT/'sources'/pid/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8');z.writestr(rel,text)
   for rel,blob in images.items():
    target=OUT/'sources'/pid/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);z.writestr(rel,blob)
   # Keep attribution with the redistributed images, including inside the ZIP.
   if credits:z.writestr('images/credits.json',json.dumps(credits,ensure_ascii=False,indent=2)+'\n')
  with zipfile.ZipFile(OUT/(pid+'.zip')) as z:
   assert z.testzip() is None
   assert all(q.get('imageUrl') is None or q['imageUrl'] in z.namelist() for q in qs)
  (OUT/'sources'/pid/'VERIFICATION.json').write_text(json.dumps(references,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  (OUT/'sources'/pid/'IMAGE-CREDITS.json').write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  for n,(q,r) in enumerate(zip(qs,references),1):
   answer=q['options'][q['correctOptionIndex']] if q['kind']=='multipleChoice' else q['acceptableAnswers'][0]
   rows.append([name,n,q['prompt'],q.get('imageUrl',''),*q.get('clues',[]),*(['']*(4-len(q.get('clues',[])))),*q.get('options',['','','','']),answer,' | '.join(q.get('acceptableAnswers',[])),' | '.join(r['sources']),r['note']])
  catalog.append(dict(id=pid,name=name,mode=mode,count=len(qs),images=len(images)))
assert len(catalog)==10 and len(rows)==70 and len(ids)==70 and illustrations==24
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','Question','Texte','Image',*['Indice '+str(i) for i in range(1,5)],'A','B','C','D','Réponse','Variantes acceptées','Sources','Note et dates']);w.writerows(rows)
(OUT/'CATALOGUE.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'README.md').write_text('# Peintures et sculptures célèbres — dix forfaits\n\n70 questions en français : trois QCM de huit questions, trois séries buzzer de huit questions, deux Qui suis-je ? de cinq questions et deux chronologies de six questions. Les six séries QCM/buzzer alternent quatre questions illustrées et quatre questions textuelles. Les 24 images sont intégrées aux archives pour jouer hors ligne. Niveau accessible à intermédiaire.\n\n## Réglages\n\n- QCM et buzzer : 15 secondes ; 15 → 10 → 5 points. Réponse après buzzer : 10 secondes.\n- Qui suis-je ? : quatre indices de 20 secondes (80 secondes au total) ; 20 → 15 → 10 → 5 points ; erreur : −5 points, nouvelle tentative au prochain indice. Pas d’image immédiatement révélatrice.\n- Chronologies : trois cartes à glisser, puis « Envoyer l’ordre ». Les ZIP restent compatibles avec la conversion automatique de l’application. Lecture libre avant le départ du chronomètre par l’hôte, puis 30 secondes ; 15 → 10 → 5 points, par tranches de 10 secondes. Le téléviseur réordonne les trois éléments à la révélation.\n- Bonnes réponses réparties également entre A–D pour les QCM de huit questions ; une ou deux par position dans les chronologies.\n- Sujet déclaré « Arts » pour le regroupement et l’ordre équilibré des catégories.\n\n| Forfait | Questions | Images | Archive |\n|---|---:|---:|---|\n'+'\n'.join(f"| {c['name']} | {c['count']} | {c['images']} | [{c['id']}.zip]({c['id']}.zip) |" for c in catalog)+'\n\n[Questions, indices et corrigé](QUESTIONS-ET-REPONSES.csv) · [Sources et vérification](VERIFICATION.md) · [Crédits des images](PHOTOS.md).\n\nLes sources modifiables sont dans `sources/<identifiant>/game.json`, `question-bank/<identifiant>.json` et `images/`. Données : `build/art-quiz-data.py`. Régénération : `python build/build-art-packages.py`. Images manquantes : `python build/download-art-images.py`.\n\nCertaines œuvres reviennent dans plusieurs formats avec une question différente. Jouer d’abord les Qui suis-je ? peut préserver la difficulté de leurs indices. La Grande Vague est explicitement présentée comme une estampe ; les moaï et la statue de la Liberté élargissent le thème à la sculpture monumentale.\n',encoding='utf-8')
print('Validated 10 art packages, 70 questions, 24 embedded images, balanced A-D and complete source references.')
