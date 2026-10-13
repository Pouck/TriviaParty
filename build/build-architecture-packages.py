from pathlib import Path
from collections import Counter
import csv, json, runpy, zipfile
from quiz_choice_order import randomize_choices

OUT=Path('package-examples/architecture-2026-10-11');OUT.mkdir(parents=True,exist_ok=True)
DATA=runpy.run_path('build/architecture-quiz-data.py')
photos={p['slug']:p for p in json.loads((OUT/'PHOTOS.json').read_text(encoding='utf-8'))}
catalog=[];rows=[];all_ids=set();prompts=set();illustrations=0
for mode,key in [('qcm','CHOICE'),('buzzer','BUZZER'),('qsj','GUESS')]:
 for number,(slug,title,entries) in enumerate(DATA[key]):
  pid=f'architecture-{mode}-{slug}-20261011'
  name=f'Architecture — {title} — '+{'qcm':'QCM','buzzer':'Buzzer','qsj':'Qui suis-je ?'}[mode]
  assert len(entries)==(3 if mode=='qsj' else 6)
  qs=[];images={};sources=[]
  for n,e in enumerate(entries,1):
   q=dict(id=f'{pid}-{n:02}',category=name,basePoints=20 if mode=='qsj' else 15,penaltyPoints=5 if mode=='qsj' else 0)
   assert q['id'] not in all_ids;all_ids.add(q['id'])
   if mode=='qcm':q.update(kind='multipleChoice',prompt=e['prompt'],options=[f'{letter} — {value}' for letter,value in zip('ABCD',e['options'])],correctOptionIndex=e['index'])
   elif mode=='buzzer':q.update(kind='textAnswer',prompt=e['prompt'],acceptableAnswers=e['answers'],allowFuzzyMatch=True)
   else:
    assert len(e['clues'])==4 and all(c.strip() for c in e['clues'])
    q.update(kind='guessWho',prompt='Qui suis-je ?',clues=e['clues'],acceptableAnswers=e['answers'])
   if e.get('image'):
    p=photos[e['image']];path='images/'+p['file'];q['imageUrl']=path;images[path]=(OUT/'assets'/p['file']).read_bytes();illustrations+=1
    assert len(images[path])<8*1024*1024
   qs.append(q)
   sources.append(dict(question=n,site=e['site'],verification=DATA['SOURCES'][e['site']],note=e.get('note',''),photo=photos[e['image']]['commons'] if e.get('image') else None))
  if mode!='qsj':assert sum('imageUrl' in q for q in qs)==3
  if mode=='qcm':
   expected=[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   randomize_choices(qs,pid,extra_positions=[(0,2),(1,3),(0,1)][number])
   assert expected==[q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in qs]
   assert sorted(Counter(q['correctOptionIndex'] for q in qs).values())==[1,1,2,2]
   assert all(len(set(q['options']))==4 for q in qs)
  game=dict(id=pid,name=name,description=f'{len(qs)} questions en français. '+('4 indices de 20 secondes ; 20 → 15 → 10 → 5 points ; erreur : −5 points.' if mode=='qsj' else '3 avec photo et 3 textuelles ; 15 secondes ; 15 → 10 → 5 points.'),categoryPackages=[pid],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=20 if mode=='qsj' else 5,decayPercentagePerFlip=0,maxFlips=3 if mode=='qsj' else 2,pointsDecayPerFlip=5))
  bank=dict(category=name,answerMode='SIMULTANEOUS' if mode=='qcm' else 'BUZZER',questionTypes=['Choix multiples' if mode=='qcm' else 'Réponse orale' if mode=='buzzer' else 'Qui suis-je ?'],questions=qs)
  with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
   for rel,value in [('game.json',game),(f'question-bank/{pid}.json',bank)]:
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n';f=OUT/'sources'/pid/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text,encoding='utf-8');z.writestr(rel,text)
   for rel,blob in images.items():
    f=OUT/'sources'/pid/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(blob);z.writestr(rel,blob)
  with zipfile.ZipFile(OUT/(pid+'.zip')) as z:
   assert z.testzip() is None
   assert set(z.namelist())=={'game.json',f'question-bank/{pid}.json',*images}
   assert all(q.get('imageUrl') is None or q['imageUrl'] in z.namelist() for q in qs)
  (OUT/'sources'/pid/'VERIFICATION.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  credits=[photos[e['image']] for e in entries if e.get('image')]
  (OUT/'sources'/pid/'PHOTOS.json').write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  for n,(q,e) in enumerate(zip(qs,entries),1):
   answer=q['options'][q['correctOptionIndex']] if mode=='qcm' else q['acceptableAnswers'][0]
   rows.append([name,n,q['prompt'],q.get('imageUrl',''),*q.get('clues',[]),*(['']*(4-len(q.get('clues',[])))),*q.get('options',['','','','']),answer,' | '.join(q.get('acceptableAnswers',[])),DATA['SOURCES'][e['site']],e.get('note','')])
  catalog.append(dict(name=name,id=pid,count=len(qs),mode=mode,images=len(images)))
assert len(catalog)==11 and len(rows)==51 and len(all_ids)==51 and illustrations==18
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','Question','Texte','Image',*['Indice '+str(n) for n in range(1,5)],'A','B','C','D','Réponse','Variantes acceptées','Source','Note']);w.writerows(rows)
(OUT/'CATALOGUE.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'README.md').write_text('# Architecture — onze forfaits\n\n51 questions en français : 18 QCM, 18 buzzer et 15 Qui suis-je ?. Les trois QCM et les trois buzzer alternent une question avec photo et une question textuelle (3 + 3 par forfait). Les 18 photographies sont intégrées aux ZIP et ne nécessitent pas Internet pendant la partie.\n\n## Réglages\n\n- QCM et buzzer : 15 secondes ; 15 → 10 → 5 points ; pas de pénalité ordinaire.\n- Qui suis-je ? : quatre indices textuels du plus difficile au plus facile, un nouvel indice toutes les 20 secondes ; 80 secondes au total ; 20 → 15 → 10 → 5 points. Erreur : −5 points, nouvelle tentative au prochain indice.\n- Réponse après buzzer : 10 secondes. QCM en un clic, avec les positions A–D mélangées et équilibrées.\n- Les photos ne sont affichées que sur le téléviseur, selon le fonctionnement actuel de l’application.\n\n## Forfaits\n\n| Forfait | Questions | Photos | Archive |\n|---|---:|---:|---|\n'+'\n'.join(f"| {c['name']} | {c['count']} | {c['images']} | [{c['id']}.zip]({c['id']}.zip) |" for c in catalog)+'\n\n## Contenu et sources\n\n[Questions, indices et corrigé](QUESTIONS-ET-REPONSES.csv) · [Vérification](VERIFICATION.md) · [Crédits photo](PHOTOS.md).\n\nTous les JSON et les images sont accessibles sous `sources/<identifiant>/`. Les fichiers `PHOTOS.json` et `VERIFICATION.json` dans ces dossiers sont des documents de référence et ne sont pas inclus dans les ZIP importables.\n\nDonnées : `build/architecture-quiz-data.py`. Régénérer : `python build/build-architecture-packages.py`. Télécharger les photos manquantes : `python build/download-architecture-images.py`. Les photos existantes sont mises en cache.\n\n## Images progressives\n\nLe format actuel révèle progressivement les indices textuels, mais son unique champ image affiche immédiatement la photo complète. Ces cinq forfaits Qui suis-je ? restent donc sans image. Une future variante « image mystère » pourrait révéler des portions d’une photo à chaque baisse de points ; elle nécessiterait une modification de l’application et du récepteur TV.\n',encoding='utf-8')
(OUT/'VERIFICATION.md').write_text('# Vérification — Architecture\n\nLes 51 questions ont été rédigées en français avec des réponses uniques et des sources institutionnelles. Les variantes de noms usuels et les appellations dans la langue d’origine sont acceptées pour les réponses orales. Les bons choix A–D du corrigé correspondent aux archives après mélange.\n\n## Points de vigilance résolus\n\n- Big Ben désigne précisément une cloche. La question illustrée demande expressément le nom courant de la tour, et « tour Elizabeth » est aussi accepté.\n- Le Guggenheim représenté est celui de New York (Frank Lloyd Wright), pas celui de Bilbao (Frank Gehry).\n- Chenonceau enjambe le Cher, pas la Loire.\n- L’urbanisme de Brasília est associé à Lúcio Costa ; la question porte sur les bâtiments conçus par Oscar Niemeyer.\n- La grande pyramide demandée dans Qui suis-je ? est celle de Khéops, pas l’ensemble des trois pyramides.\n- Sainte-Sophie est décrite par ses usages historiques sans faire dépendre un indice de son statut actuel.\n- Aucune date future d’achèvement de la Sagrada Família n’est annoncée.\n- L’escalier de Chambord n’est pas attribué avec certitude à Léonard de Vinci.\n- Les moaï sont des sculptures monumentales associées au patrimoine architectural et rituel de Rapa Nui ; ce ne sont pas des bâtiments.\n- Les questions avec photo ne supposent ni logo ni texte lisible sur l’image. Les vues générales ont été choisies pour la reconnaissance.\n\n## Répétitions et niveau\n\nCertains monuments célèbres reviennent dans les Qui suis-je ? et les autres formats, avec des indices ou une question différents. Les 51 formulations ne répètent pas une même question. Pour éviter qu’une première série facilite une autre, jouer les Qui suis-je ? avant les QCM et les buzzer lorsque plusieurs forfaits sont sélectionnés ensemble. Les buzzer sont volontairement plus accessibles ; les QCM combinent reconnaissance et connaissances.\n\n## Sources par site\n\n'+'\n'.join(f'- [{site}]({url})' for site,url in DATA['SOURCES'].items())+'\n\nSources complémentaires pour les détails des indices :\n\n- [Origines de Versailles](https://en.chateauversailles.fr/discover/history/great-characters/louis-xiii) et [André Le Nôtre](https://www.chateauversailles.fr/le-notre).\n- [Angkor Vat — Autorité nationale APSARA](https://apsaraauthority.gov.kh/2021/06/14/angkor-wat/).\n- [Cour des Lions — Patronat de l’Alhambra](https://www.alhambra-patronato.es/en/edificios-lugares/the-court-of-the-lions).\n- [Histoire de Chambord](https://www.chambord.org/fr/histoire/le-chateau/au-fil-de-lhistoire/).\n- [Statue d’Athéna de Phidias — Musée de l’Acropole](https://www.theacropolismuseum.gr/sites/default/files/2020-02/press_release_28_october_2019.pdf).\n\n## Photographies\n\nLes 18 fichiers proviennent de Wikimedia Commons sous licence libre ou du domaine public. Les auteurs, licences et pages de fichier sont conservés dans [PHOTOS.md](PHOTOS.md) et PHOTOS.json. Les photos sont des miniatures Wikimedia sans modification additionnelle.\n',encoding='utf-8')
print('Validated 11 ZIPs, 51 unique question IDs, 18 embedded photos, 3+3 image/text split per QCM/buzzer set, balanced choices and answer keys.')
