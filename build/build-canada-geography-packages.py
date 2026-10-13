from pathlib import Path
from collections import Counter
import csv, json, runpy, zipfile
from quiz_choice_order import randomize_choices

OUT=Path('package-examples/geographie-canada-2026-10-11')
OUT.mkdir(parents=True,exist_ok=True)
data=runpy.run_path('build/canada-geography-data.py')
catalog=[];rows=[];ids=set()
for mode,sets in [('qcm',data['MC_SETS']),('buzzer',data['BUZZER_SETS'])]:
 for number,(slug,title,entries) in enumerate(sets):
  pid=f'canada-geo-{mode}-{slug}-20261011';name=f'Géographie du Canada — {title}'
  assert pid not in ids;ids.add(pid)
  qs=[]
  for n,e in enumerate(entries,1):
   q=dict(kind='multipleChoice' if mode=='qcm' else 'textAnswer',id=f'{pid}-{n:02}',category=name,prompt=e[0],basePoints=15,penaltyPoints=0)
   if mode=='qcm':q.update(options=[f'{letter} — {value}' for letter,value in zip('ABCD',e[1])],correctOptionIndex=e[2])
   else:q.update(acceptableAnswers=e[1],allowFuzzyMatch=True)
   qs.append(q)
  if mode=='qcm':
   expected=[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   randomize_choices(qs,pid,extra_positions=[(0,2),(1,3),(0,1)][number])
   assert expected==[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   assert sorted(Counter(q['correctOptionIndex'] for q in qs).values())==[1,1,2,2]
   assert all(len(set(q['options']))==4 for q in qs)
  game=dict(id=pid,name=name,description=f'{len(qs)} questions en français ; 15 secondes ; 15 → 10 → 5 points.',categoryPackages=[pid],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=5,decayPercentagePerFlip=0,maxFlips=2,pointsDecayPerFlip=5))
  bank=dict(category=name,answerMode='SIMULTANEOUS' if mode=='qcm' else 'BUZZER',questionTypes=['Choix multiples' if mode=='qcm' else 'Réponse orale'],questions=qs)
  with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
   for rel,value in [('game.json',game),(f'question-bank/{pid}.json',bank)]:
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n';f=OUT/'sources'/pid/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text,encoding='utf-8');z.writestr(rel,text)
  with zipfile.ZipFile(OUT/(pid+'.zip')) as z:assert z.testzip() is None
  for n,q in enumerate(qs,1):
   opts=q.get('options',['','','','']);answer=opts[q['correctOptionIndex']] if mode=='qcm' else q['acceptableAnswers'][0]
   rows.append([name,n,q['prompt'],*opts,answer])
  catalog.append((name,pid))
assert len(rows)==28 and len(ids)==5
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','Question','Texte','A','B','C','D','Réponse']);w.writerows(rows)
(OUT/'README.md').write_text('# Géographie du Canada\n\nCinq forfaits : trois QCM de six questions et deux séries buzzer de cinq questions (28 questions). Tout est en français.\n\n15 secondes par question ; récompense 15 → 10 → 5 points par tranches de cinq secondes ; aucune pénalité ordinaire ; 10 secondes pour répondre après un buzzer.\n\nLes positions des bonnes réponses sont variées et équilibrées (une ou deux par lettre dans chaque QCM). Ce mélange est conservé dans le forfait, sans nouveau tirage à chaque partie.\n\n'+ '\n'.join(f'- [{name}]({pid}.zip)' for name,pid in catalog)+'\n\n[Questions et corrigé](QUESTIONS-ET-REPONSES.csv) · [Vérification et corrections](VERIFICATION.md).\n\nSources modifiables : `sources/<identifiant>/game.json` et `question-bank/<identifiant>.json`. Données : `build/canada-geography-data.py`. Régénération : `python build/build-canada-geography-packages.py`.\n',encoding='utf-8')
print('Validated 5 packages, 28 questions; ZIP integrity, unique IDs, varied A-D positions and preserved answer keys.')
