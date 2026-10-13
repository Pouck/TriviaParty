from pathlib import Path
from collections import Counter
import csv,json,runpy,zipfile
from quiz_choice_order import randomize_choices
DATA=runpy.run_path('build/canada-history-20261011-data.py')
OUT=Path('package-examples/canada-2026-10-11');OUT.mkdir(parents=True,exist_ok=True)
rows=[];catalog=[]
for mode,key in [('qsj','GUESS'),('qcm','CHOICE'),('buzzer','BUZZER')]:
 for slug,title,entries in DATA[key]:
  pid=f'canada-{mode}-{slug}-20261011'
  name=('Qui suis-je ? — Canada — ' if mode=='qsj' else 'Canada — ')+title+(' — Buzzer' if mode=='buzzer' else ' — QCM' if mode=='qcm' else '')
  questions=[]
  for number,entry in enumerate(entries,1):
   common=dict(id=f'{pid}-{number:02}',category=name,basePoints=25 if mode=='qsj' else 15,penaltyPoints=5 if mode=='qsj' else 0)
   if mode=='qsj':
    answer,clues=entry;assert len(clues)==5
    q=dict(kind='guessWho',**common,prompt='Qui suis-je ?',clues=clues,acceptableAnswers=[answer])
   elif mode=='qcm':
    prompt,options,index=entry;q=dict(kind='multipleChoice',**common,prompt=prompt,options=[f'{letter} — {text}' for letter,text in zip('ABCD',options)],correctOptionIndex=index)
   else:
    prompt,answer=entry;q=dict(kind='textAnswer',**common,prompt=prompt,acceptableAnswers=[answer])
   questions.append(q)
  if mode=='qcm':
   before=[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in questions]
   randomize_choices(questions,pid,extra_positions=(0,2))
   assert before==[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in questions]
   assert sorted(Counter(q['correctOptionIndex'] for q in questions).values())==[2,2,3,3]
  timing=dict(secondsPerFlip=20 if mode=='qsj' else 5,decayPercentagePerFlip=0,maxFlips=4 if mode=='qsj' else 2,pointsDecayPerFlip=5)
  game=dict(id=pid,name=name,description=f'{len(questions)} questions en français. '+('5 indices de 20 secondes ; 25 → 20 → 15 → 10 → 5 points ; erreur : −5 points.' if mode=='qsj' else '15 secondes ; 15 → 10 → 5 points.'),categoryPackages=[pid],answerTimeSeconds=10,timingConfig=timing)
  bank=dict(category=name,answerMode='SIMULTANEOUS' if mode=='qcm' else 'BUZZER',questionTypes=['Choix multiples' if mode=='qcm' else 'Qui suis-je ?' if mode=='qsj' else 'Réponse orale'],questions=questions)
  source=OUT/'sources'/pid
  with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
   for rel,data in [('game.json',game),(f'question-bank/{pid}.json',bank)]:
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n';target=source/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8');z.writestr(rel,text)
  with zipfile.ZipFile(OUT/(pid+'.zip')) as z:assert z.testzip() is None
  for n,q in enumerate(questions,1):
   choices=q.get('options',['']*4);answer=q['options'][q['correctOptionIndex']] if mode=='qcm' else q['acceptableAnswers'][0]
   rows.append([name,n,q['prompt'],*q.get('clues',[]),*(['']*(5-len(q.get('clues',[])))),*choices,answer])
  catalog.append((name,pid,len(questions)))
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Catégorie','Question','Texte',*['Indice '+str(i) for i in range(1,6)],'A','B','C','D','Réponse']);w.writerows(rows)
assert len(catalog)==8 and len(rows)==70
(OUT/'README.md').write_text('# Canada — huit forfaits\n\n70 questions : 10 personnages avec cinq indices chacun, 30 QCM et 30 questions au buzzer.\n\n- Qui suis-je ? : 100 secondes de recherche, cinq indices de 20 secondes ; 25 → 20 → 15 → 10 → 5 points ; erreur : −5 points, nouvelle tentative au prochain indice.\n- QCM et buzzer : 15 secondes, 15 → 10 → 5 points. Réponse après buzzer : 10 secondes.\n- Les QCM ont deux ou trois bonnes réponses à chaque position A–D.\n- Les mises actuelles peuvent être proposées au début de chaque catégorie.\n\n| Forfait | Questions | Archive |\n|---|---:|---|\n'+'\n'.join(f'| {name} | {count} | [{pid}.zip]({pid}.zip) |' for name,pid,count in catalog)+'\n\nSources JSON dans `sources/`, corrigé dans [QUESTIONS-ET-REPONSES.csv](QUESTIONS-ET-REPONSES.csv), corrections dans [VERIFICATION.md](VERIFICATION.md).\n\nRégénération : `python build/build-canada-20261011-packages.py`. Données : `build/canada-history-20261011-data.py`.\n',encoding='utf-8')
print('Validated 8 ZIP packages, 70 unique questions; QCM answer positions balanced and keys preserved.')
