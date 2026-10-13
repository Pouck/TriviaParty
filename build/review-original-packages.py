"""Reviewed French starter sets; stable IDs allow in-place updates."""
from pathlib import Path
import csv,json,zipfile
from quiz_choice_order import randomize_choices
assets=Path('app/src/main/assets');output=Path('package-examples/forfaits-originaux')
visual_root=Path('package-examples/library-2026-10-12/assets')
visuals={p['slug']:p for f in visual_root.glob('*.json') for p in [json.loads(f.read_text(encoding='utf-8'))]}
def q(prompt,correct,other,image=None):return (prompt,correct,other,image)
REVISED={
 'gaming-history':{
  'q1':q('En quelle année la NES sort-elle en Amérique du Nord ?','1985',['1983','1987','1989']),
  'q2':q('Qui a créé Mario ?','Shigeru Miyamoto',['Hideo Kojima','Satoru Iwata','Gabe Newell'],'mushroom'),
  'q6':q('Quel jeu de blocs est célèbre sur Game Boy ?','Tetris',['Super Mario Land','Pokémon Rouge et Bleu','Donkey Kong']),
  'q7':q('Quelle console de salon est commercialisée en 1972 ?','Magnavox Odyssey',['Atari 2600','ColecoVision','Fairchild Channel F']),
  'q8':q('En quelle année sort la version complète de Minecraft ?','2011',['2009','2010','2012'],'blocks'),
 },
 'pop-culture':{
  'q4':q('Classez ces consoles selon leur sortie.','Nintendo 64 → PlayStation 2 → Xbox 360 → Nintendo Switch',[
   'Nintendo Switch → Xbox 360 → PlayStation 2 → Nintendo 64','PlayStation 2 → Nintendo 64 → Xbox 360 → Nintendo Switch','Nintendo 64 → PlayStation 2 → Nintendo Switch → Xbox 360']),
  'q13':q('Quel film de James Cameron se déroule sur Pandora ?','Avatar',['Avengers: Endgame','Titanic','Star Wars: Le Réveil de la Force'],'forest'),
  'q14':q('Quel groupe a enregistré Bohemian Rhapsody ?','Queen',['The Beatles','Led Zeppelin','The Rolling Stones'],'guitar'),
  'q15':q('Quel super-héros est Tony Stark ?','Iron Man',['Captain America','Thor','Spider-Man']),
  'q16':q('Quel artiste chante Blinding Lights ?','The Weeknd',['Bruno Mars','Usher','Justin Timberlake']),
 },
 'science-tech':{
  'q5':q('Quel langage informatique porte le nom d’une île indonésienne ?','Java',['Python','C++','JavaScript'],'island'),
  'q17':q('Quel est le symbole chimique de l’or ?','Au',['Ag','Fe','Gd']),
  'q18':q('Quelle entreprise a créé l’iPhone ?','Apple',['Microsoft','Amazon','Google']),
  'q19':q('Comment appelle-t-on le passage de l’eau liquide à la glace ?','La solidification',['La fusion','L’évaporation','La sublimation'],'snow'),
  'q20':q('Quelle planète est la plus proche du Soleil ?','Mercure',['Vénus','Mars','La Terre']),
 },
 'video-game-maps':{
  'q21':q('Quel jeu construit ses paysages avec des blocs ?','Minecraft',['Tetris','Portal','Fortnite'],'blocks'),
  'q22':q('Quel royaume est au centre de The Legend of Zelda ?','Hyrule',['Le Royaume Champignon','Tamriel','Midgar'],'castle'),
  'q23':q('Dans quel jeu peut-on construire pendant un Battle Royale ?','Fortnite',['Overwatch','Rocket League','Gran Turismo']),
  'q24':q('Classez ces jeux selon leur première sortie.','Pokémon Rouge/Bleu → Skyrim → Elden Ring',[
   'Elden Ring → Skyrim → Pokémon Rouge/Bleu','Skyrim → Pokémon Rouge/Bleu → Elden Ring','Pokémon Rouge/Bleu → Elden Ring → Skyrim']),
  'q25':q('Quelle ville est au centre de Cyberpunk 2077 ?','Night City',['Raccoon City','Neo-Tokyo','Gotham City']),
 },
 'world-geography':{
  'q3':q('Dans quel pays se trouve ce monument ?','La France',['L’Italie','Le Japon','Le Brésil'],'eiffel'),
  'q9':q('Quelle est la capitale de l’Australie ?','Canberra',['Sydney','Melbourne','Brisbane']),
  'q10':q('Quel est le plus grand pays par superficie totale ?','La Russie',['Le Canada','Les États-Unis','Le Brésil']),
  'q11':q('Quel fleuve traverse Le Caire ?','Le Nil',['L’Amazone','Le Yangtsé','Le Mississippi']),
  'q12':q('Quelle chaîne de montagnes contient l’Everest ?','L’Himalaya',['Les Andes','Les Alpes','L’Atlas'],'everest'),
 },
}
SUBJECT={'gaming-history':'Jeux vidéo','pop-culture':'Culture populaire','science-tech':'Sciences','video-game-maps':'Jeux vidéo','world-geography':'Géographie'}
rows=[]
for number,category_file in enumerate(sorted((assets/'question-bank').glob('*.json'))):
 category=json.loads(category_file.read_text(encoding='utf-8-sig'));slug=category_file.stem;package_id='original-'+slug
 images={};credits=[]
 for question in category['questions']:
  qid=question['id'];prompt,correct,other,image=REVISED[slug][qid]
  question.clear();question.update(kind='multipleChoice',id=qid,category=category['category'],prompt=prompt,basePoints=15,penaltyPoints=0,
   options=[f'{letter} — {value}' for letter,value in zip('ABCD',[correct,*other])],correctOptionIndex=0)
  if image:
   p=visuals[image];rel='images/'+p['file'];question['imageUrl']=rel;images[rel]=(visual_root/p['file']).read_bytes();credits.append(p)
 randomize_choices(category['questions'],package_id,extra_positions=(number%4,))
 category.update(subject=SUBJECT[slug],answerMode='SIMULTANEOUS',questionTypes=['Choix multiples'])
 category_file.write_text(json.dumps(category,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 game=dict(id=package_id,name=category['category'],description='Ensemble de questions original révisé : français, 15 points, deux visuels et trois textes.',categoryPackages=[slug],
  timingConfig=dict(secondsPerFlip=5,decayPercentagePerFlip=0,maxFlips=2,pointsDecayPerFlip=5),answerTimeSeconds=10)
 entries={'game.json':game,f'question-bank/{category_file.name}':category};output.mkdir(parents=True,exist_ok=True);destination=output/(package_id+'.zip')
 with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
  for name,data in entries.items():archive.writestr(name,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
  for name,blob in images.items():archive.writestr(name,blob)
  archive.writestr('images/credits.json',json.dumps(credits,ensure_ascii=False,indent=2)+'\n')
 bundled=assets/'original-packages'/destination.name;bundled.parent.mkdir(parents=True,exist_ok=True);bundled.write_bytes(destination.read_bytes())
 source=output/'sources'/package_id
 for name,data in entries.items():
  target=source/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for name,blob in images.items():
  target=source/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
 for question in category['questions']:rows.append([game['name'],question['id'],question['prompt'],*question['options'],question['options'][question['correctOptionIndex']]])
 print(destination.resolve())
with (output/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','ID','Question','A','B','C','D','Réponse']);w.writerows(rows)
