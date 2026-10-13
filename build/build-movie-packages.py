from pathlib import Path
from collections import Counter
from itertools import permutations
import csv,json,random,runpy,zipfile
from quiz_choice_order import randomize_choices

DATA=runpy.run_path('build/movie-quiz-data.py')
OUT=Path('package-examples/cinema-2026-10-11');OUT.mkdir(parents=True,exist_ok=True)
catalog=[];rows=[];ids=set()
for mode,key in [('qcm','CHOICE'),('buzzer','BUZZER'),('qsj','GUESS'),('chronologie','CHRONOLOGY')]:
 for number,(slug,title,entries) in enumerate(DATA[key]):
  pid=f'cinema-{mode}-{slug}-20261011';name=f'Cinéma — {title} — '+{'qcm':'QCM','buzzer':'Buzzer','qsj':'Qui suis-je ?','chronologie':'Chronologie'}[mode]
  assert 5<=len(entries)<=10
  qs=[];references=[]
  for n,e in enumerate(entries,1):
   q=dict(id=f'{pid}-{n:02}',category=name,basePoints=20 if mode=='qsj' else 15,penaltyPoints=5 if mode=='qsj' else 0)
   assert q['id'] not in ids;ids.add(q['id'])
   note=e.get('note','')
   if mode=='qsj':
    assert len(e['clues'])==4 and len(set(e['clues']))==4
    q.update(kind='guessWho',prompt='Qui suis-je ?',clues=e['clues'],acceptableAnswers=e['answers'])
   elif mode=='buzzer':q.update(kind='textAnswer',prompt=e['prompt'],acceptableAnswers=e['answers'],allowFuzzyMatch=True)
   elif mode=='qcm':q.update(kind='multipleChoice',prompt=e['prompt'],options=[f'{letter} — {v}' for letter,v in zip('ABCD',e['options'])],correctOptionIndex=e['index'])
   else:
    films=e['films'];assert len(films)==3 and len({year for _,year in films})==3
    correct=[film for film,_ in sorted(films,key=lambda item:item[1])]
    options=[' → '.join(order) for order in list(permutations(correct))[:4]]
    display=correct.copy();random.Random(q['id']).shuffle(display)
    # Never let the displayed event list reveal the entire correct sequence.
    if display==correct:display=display[1:]+display[:1]
    q.update(kind='multipleChoice',prompt=e['theme']+' — du plus ancien au plus récent :\n'+'\n'.join('• '+film for film in display),options=[f'{letter} — {value}' for letter,value in zip('ABCD',options)],correctOptionIndex=0)
    note+=' Corrigé : '+' → '.join(f'{film} ({year})' for film,year in sorted(films,key=lambda item:item[1]))
   qs.append(q)
   references.append(dict(question=n,sources=[DATA['SOURCES'][s] for s in e['sources']],note=note))
  if mode in ('qcm','chronologie'):
   expected=[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   extras=() if len(qs)%4==0 else [(0,2),(1,3)][number]
   randomize_choices(qs,pid,extra_positions=extras)
   assert expected==[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   distribution=Counter(q['correctOptionIndex'] for q in qs)
   assert len(distribution)==4 and max(distribution.values())-min(distribution.values())<=1
  segment=20 if mode=='qsj' else 10 if mode=='chronologie' else 5
  max_flips=3 if mode=='qsj' else 2
  description=f'{len(qs)} questions en français. '+('4 indices de 20 secondes ; 20 → 15 → 10 → 5 points ; erreur : −5 points.' if mode=='qsj' else 'Lecture libre puis 30 secondes ; 15 → 10 → 5 points.' if mode=='chronologie' else '15 secondes ; 15 → 10 → 5 points.')
  game=dict(id=pid,name=name,description=description,categoryPackages=[pid],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=segment,decayPercentagePerFlip=0,maxFlips=max_flips,pointsDecayPerFlip=5))
  bank=dict(category=name,subject='Cinéma',answerMode='BUZZER' if mode in ('buzzer','qsj') else 'SIMULTANEOUS',questionTypes=['Qui suis-je ?' if mode=='qsj' else 'Réponse orale' if mode=='buzzer' else 'Choix multiples'],questions=qs)
  with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
   for rel,value in [('game.json',game),(f'question-bank/{pid}.json',bank)]:
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n';target=OUT/'sources'/pid/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8');z.writestr(rel,text)
  with zipfile.ZipFile(OUT/(pid+'.zip')) as z:assert z.testzip() is None
  (OUT/'sources'/pid/'VERIFICATION.json').write_text(json.dumps(references,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  for n,(q,r) in enumerate(zip(qs,references),1):
   answer=q['options'][q['correctOptionIndex']] if q['kind']=='multipleChoice' else q['acceptableAnswers'][0]
   rows.append([name,n,q['prompt'],*q.get('clues',[]),*(['']*(4-len(q.get('clues',[])))),*q.get('options',['','','','']),answer,' | '.join(q.get('acceptableAnswers',[])),' | '.join(r['sources']),r['note']])
  catalog.append(dict(id=pid,name=name,mode=mode,count=len(qs)))
assert len(catalog)==10 and len(rows)==70 and len(ids)==70
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','Question','Texte',*['Indice '+str(i) for i in range(1,5)],'A','B','C','D','Réponse','Variantes acceptées','Sources','Note et dates']);w.writerows(rows)
(OUT/'CATALOGUE.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'README.md').write_text('# Cinéma — dix forfaits\n\n70 questions en français : trois QCM de huit questions, trois séries buzzer de huit questions, deux Qui suis-je ? de cinq questions et deux chronologies de six questions. Cinéma américain, animation, films français et québécois ; difficulté accessible à intermédiaire, avec quelques questions plus exigeantes. Questions textuelles, sans image ni connexion Internet requise.\n\n## Réglages\n\n- QCM et buzzer : 15 secondes ; 15 → 10 → 5 points ; aucune pénalité ordinaire. Réponse après buzzer : 10 secondes.\n- Qui suis-je ? : quatre indices de 20 secondes (80 secondes au total) ; 20 → 15 → 10 → 5 points ; erreur : −5 points, nouvelle tentative au prochain indice.\n- Chronologies : QCM en un clic. Lecture libre avant le départ du chronomètre par l’hôte, puis 30 secondes ; 15 → 10 → 5 points, par tranches de 10 secondes. Le téléviseur réordonne les trois films lors de la révélation.\n- Bonnes réponses réparties à égalité entre A–D pour chaque QCM de huit questions, et une ou deux par position pour les chronologies.\n- Sujet déclaré « Cinéma » pour l’ordre équilibré des catégories.\n\n| Forfait | Questions | Archive |\n|---|---:|---|\n'+'\n'.join(f"| {c['name']} | {c['count']} | [{c['id']}.zip]({c['id']}.zip) |" for c in catalog)+'\n\n[Questions, indices et corrigé](QUESTIONS-ET-REPONSES.csv) · [Sources et vérification](VERIFICATION.md).\n\nLes sources JSON modifiables sont dans `sources/<identifiant>/game.json` et `question-bank/<identifiant>.json`. Les documents VERIFICATION.json ne font pas partie des ZIP importables.\n\nDonnées : `build/movie-quiz-data.py`. Régénération : `python build/build-movie-packages.py`.\n',encoding='utf-8')
print('Validated 10 packages, 70 unique question IDs, balanced A-D, complete sources, 12 unambiguous release chronologies and scoring settings.')
