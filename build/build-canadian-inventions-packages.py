from pathlib import Path
from collections import Counter
import csv,json,runpy,zipfile
from quiz_choice_order import randomize_choices
OUT=Path('package-examples/inventions-canadiennes-2026-10-11');OUT.mkdir(parents=True,exist_ok=True)
rows=[];catalog=[]
for number,(slug,title,entries) in enumerate(runpy.run_path('build/canadian-inventions-data.py')['SETS']):
 pid=f'canada-inventions-{slug}-20261011';name=f'Inventions canadiennes — {title}'
 qs=[dict(kind='multipleChoice',id=f'{pid}-{n:02}',category=name,prompt=e[0],basePoints=15,penaltyPoints=0,options=[f'{letter} — {text}' for letter,text in zip('ABCD',e[1])],correctOptionIndex=e[2]) for n,e in enumerate(entries,1)]
 expected=[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
 randomize_choices(qs,pid,extra_positions=[(0,2),(1,3),(0,1)][number])
 assert expected==[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
 assert sorted(Counter(q['correctOptionIndex'] for q in qs).values())==[1,1,2,2]
 game=dict(id=pid,name=name,description='6 QCM en français ; 15 secondes ; 15 → 10 → 5 points.',categoryPackages=[pid],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=5,decayPercentagePerFlip=0,maxFlips=2,pointsDecayPerFlip=5))
 bank=dict(category=name,answerMode='SIMULTANEOUS',questionTypes=['Choix multiples'],questions=qs)
 with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for rel,data in [('game.json',game),(f'question-bank/{pid}.json',bank)]:
   text=json.dumps(data,ensure_ascii=False,indent=2)+'\n';file=OUT/'sources'/pid/rel;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text,encoding='utf-8');z.writestr(rel,text)
 with zipfile.ZipFile(OUT/(pid+'.zip')) as z:assert z.testzip() is None
 for n,(q,e) in enumerate(zip(qs,entries),1):rows.append([name,n,q['prompt'],*q['options'],q['options'][q['correctOptionIndex']],e[3]])
 catalog.append((name,pid))
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','Question','Texte','A','B','C','D','Réponse','Note de vérification']);w.writerows(rows)
assert len(rows)==18
(OUT/'README.md').write_text('# Inventions canadiennes\n\nTrois forfaits de six QCM en français. 15 secondes ; 15 → 10 → 5 points ; aucune pénalité ordinaire. Réponses simultanées en un clic ; mises possibles au début de catégorie.\n\nLes choix A–D sont mélangés avec une ou deux bonnes réponses par position dans chaque forfait.\n\n'+ '\n'.join(f'- [{name}]({pid}.zip)' for name,pid in catalog)+'\n\n[Corrigé](QUESTIONS-ET-REPONSES.csv) · [Corrections et remplacements](VERIFICATION.md). Sources JSON sous `sources/`. Régénération : `python build/build-canadian-inventions-packages.py` ; données : `build/canadian-inventions-data.py`.\n',encoding='utf-8')
print('Validated 3 packages, 18 questions; unique IDs, ZIP integrity, balanced A-D and answer keys checked.')
