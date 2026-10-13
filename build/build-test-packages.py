from pathlib import Path
import json,zipfile
out=Path('package-examples/tests-2026-10-11');out.mkdir(parents=True,exist_ok=True)
def mc():return dict(kind='multipleChoice',prompt='Quelle planète est surnommée la planète rouge ?',options=['A — Vénus','B — Mars','C — Jupiter','D — Saturne'],correctOptionIndex=1)
sets=[('01-qcm','Choix multiples',mc(),'SIMULTANEOUS','Mars'),('02-buzzer','Buzzer',dict(kind='textAnswer',prompt='Quelle est la capitale de la France ?',acceptableAnswers=['Paris']),'BUZZER','Paris'),('03-qui-suis-je','Qui suis-je ?',dict(kind='guessWho',prompt='Qui suis-je ?',clues=['Je suis une planète rocheuse.','Deux petits satellites tournent autour de moi.','Mon sol riche en oxyde de fer me donne une couleur caractéristique.','On me surnomme la planète rouge.'],acceptableAnswers=['Mars']),'BUZZER','Mars'),('04-chronologie','Chronologie — QCM',dict(kind='multipleChoice',prompt='Quel ordre va du plus ancien au plus récent ?\n• Fondation de Québec\n• Premier voyage de Jacques Cartier\n• Arrivée de Jean Cabot',options=['A — Cartier → Cabot → Québec','B — Québec → Cartier → Cabot','C — Cabot → Cartier → Québec','D — Cabot → Québec → Cartier'],correctOptionIndex=2),'SIMULTANEOUS','Cabot (1497) → Cartier (1534) → Québec (1608)'),('05-ordering','Ordre — compatibilité ancien format',dict(kind='ordering',prompt='Classez ces nombres du plus petit au plus grand.',items=[dict(id='three',text='Trois'),dict(id='one',text='Un'),dict(id='two',text='Deux')],correctOrderIds=['one','two','three']),'SIMULTANEOUS','Un → Deux → Trois'),('06-map-choice','Carte — repères',dict(kind='mapChoice',prompt='Choisissez le repère B sur cette carte de démonstration.',options=[dict(label=letter,xRatio=x,yRatio=y) for letter,x,y in [('A',.3,.3),('B',.5,.45),('C',.55,.65),('D',.4,.7)]],correctOptionIndex=1),'SIMULTANEOUS','B'),('07-wager','Mise — ancien format',dict(kind='wager',prompt=mc()['prompt'],subQuestion=mc()),'SIMULTANEOUS','Mars'),('08-speed-race','Course de vitesse',dict(kind='speedRace',prompt=mc()['prompt'],subQuestion=mc()),'SIMULTANEOUS','Mars')]
# Reuse an existing packaged geography map, including its local image.
with zipfile.ZipFile(next(Path('package-examples/geographie-2026-10-10').glob('*afrique*.zip'))) as z:
 bank=next(n for n in z.namelist() if n.startswith('question-bank/') and n.endswith('.json'));q=json.loads(z.read(bank))['questions'][0];q.pop('randomVariants',None)
 images={n:z.read(n) for n in z.namelist() if n.startswith('images/') and not n.endswith('/')}
 sets.append(('09-carte-qcm','Carte — image et lettres',q,'SIMULTANEOUS',q['options'][q['correctOptionIndex']]))
rows=[]
for slug,title,q,mode,answer in sets:
 pid='test-'+slug;name='TEST '+title;q.update(id=pid+'-q1',category=name,basePoints=20 if q['kind']=='guessWho' else 15,penaltyPoints=5 if q['kind']=='guessWho' else 0)
 if 'subQuestion' in q:q['subQuestion'].update(id=pid+'-sub',category=name,basePoints=15,penaltyPoints=0)
 game=dict(id=pid,name=name,description='Une question pour tester le rendu et les contrôles.',categoryPackages=[pid],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=20 if q['kind']=='guessWho' else 5,decayPercentagePerFlip=0,maxFlips=3 if q['kind']=='guessWho' else 2,pointsDecayPerFlip=5))
 category=dict(category=name,answerMode=mode,questionTypes=[title],questions=[q])
 entries={'game.json':json.dumps(game,ensure_ascii=False,indent=2).encode(),f'question-bank/{pid}.json':json.dumps(category,ensure_ascii=False,indent=2).encode()}
 if slug=='09-carte-qcm':entries.update(images)
 source=out/'sources'/pid
 with zipfile.ZipFile(out/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for rel,data in entries.items():z.writestr(rel,data);target=source/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 rows.append(f'| {name} | `{pid}.zip` | {answer} |')
(out/'README.md').write_text('# Forfaits de test — une question par forfait\n\nSélectionnez plusieurs forfaits pour enchaîner les écrans. Les mises de catégorie peuvent être proposées sur tous ces forfaits.\n\nL’ancien format « ordering » est automatiquement converti en QCM par l’application actuelle : il ne réactive pas les curseurs. Le forfait « Mise — ancien format » teste le format de question conservé ; pour tester les mises actuelles, utilisez le bouton de mise au début de la catégorie.\n\nCarte — repères utilise la carte schématique de secours ; Carte — image utilise une vraie illustration existante.\n\n| Forfait | Fichier | Réponse |\n|---|---|---|\n'+'\n'.join(rows)+'\n\nSources modifiables dans `sources/`. Les packages TEST peuvent être supprimés séparément dans l’application.\n',encoding='utf-8')
print(f'Created {len(sets)} one-question packages in {out.resolve()}')
