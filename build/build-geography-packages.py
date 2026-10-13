from pathlib import Path
import csv, hashlib, json, shutil, struct, zipfile

ROOT = Path(r'C:\Users\pierr\Documents\Codex\2026-10-05\i\outputs')
OUT = Path('package-examples/geographie-2026-10-10')
OUT.mkdir(parents=True, exist_ok=True)
# Reviewed visually against the source images. One question per image.
MAPS = {
 'afrique': ('Afrique', [
  ('01-afrique.png', 'Angola', 'B', 'Quelle lettre correspond à l’Angola sur la carte ?', {'A':'Cameroun','B':'Angola','C':'Zimbabwe','D':'Mozambique'}),
  ('02-afrique.png', 'Niger', 'C', 'Quelle lettre correspond au Niger sur la carte ?', {'A':'Mali','B':'Tchad','C':'Niger','D':'Mauritanie'}),
  ('03-afrique.png', 'Gabon', 'A', 'Quelle lettre correspond au Gabon sur la carte ?', {'A':'Gabon','B':'Kenya','C':'Ouganda','D':'République du Congo'}),
  ('afrique-abcd.png', 'Zambie', 'D', 'Quelle lettre correspond à la Zambie sur la carte ?', {'A':'Malawi','B':'Burkina Faso','C':'Namibie','D':'Zambie'})]),
 'asie': ('Asie', [
  ('04-asie.png', 'Népal', 'B', 'Quelle lettre correspond au Népal sur la carte ?', {'A':'Bhoutan','B':'Népal','C':'Sri Lanka','D':'Bangladesh'}),
  ('05-asie.png', 'Thaïlande', 'C', 'Quelle lettre correspond à la Thaïlande sur la carte ?', {'A':'Laos','B':'Myanmar (Birmanie)','C':'Thaïlande','D':'Cambodge'}),
  ('06-asie.png', 'Iran', 'A', 'Quelle lettre correspond à l’Iran sur la carte ?', {'A':'Iran','B':'Irak','C':'Repère ambigu sur le littoral du Levant — non sélectionné','D':'Syrie'}),
  ('07-asie.png', 'Yémen', 'D', 'Quelle lettre correspond au Yémen sur la carte ?', {'A':'Arabie saoudite','B':'Oman','C':'Émirats arabes unis','D':'Yémen'})]),
 'amerique-du-sud': ('Amérique du Sud', [
  ('11-amerique-sud.png', 'Uruguay', 'B', 'Quelle lettre correspond à l’Uruguay sur la carte ?', {'A':'Paraguay','B':'Uruguay','C':'Bolivie','D':'Colombie'}),
  ('12-amerique-sud.png', 'Suriname', 'C', 'Quelle lettre correspond au Suriname sur la carte ?', {'A':'Équateur','B':'Guyana','C':'Suriname','D':'Guyane française (territoire français)'})]),
 'etats-unis': ('États-Unis', [
  ('08-etats-unis.png', 'Tennessee', 'C', 'Quelle lettre correspond à l’État du Tennessee sur la carte ?', {'A':'Missouri','B':'Kentucky','C':'Tennessee','D':'Arkansas'}),
  ('09-etats-unis.png', 'Idaho', 'B', 'Quelle lettre correspond à l’État de l’Idaho sur la carte ?', {'A':'Iowa','B':'Idaho','C':'Illinois','D':'Ohio'}),
  ('10-etats-unis.png', 'Kansas', 'D', 'Quelle lettre correspond à l’État du Kansas sur la carte ?', {'A':'Wyoming','B':'Oklahoma','C':'Nebraska','D':'Kansas'})]),
 'europe': ('Europe', [
  ('europe-abcd.png', 'Roumanie', 'A', 'Quelle lettre correspond à la Roumanie sur la carte ?', {'A':'Roumanie','B':'Bulgarie','C':'Bosnie-Herzégovine','D':'Moldavie'}),
  ('europe-baltes-belarussie.png', 'Lituanie', 'B', 'Quelle lettre correspond à la Lituanie sur la carte ?', {'A':'Estonie','B':'Lituanie','C':'Lettonie','D':'Biélorussie (Bélarus)'}),
  ('europe-microetats-abcd.png', 'Monaco', 'D', 'Quelle lettre correspond à Monaco sur la carte ?', {'A':'Saint-Marin (position approximative)','B':'Andorre (position approximative)','C':'Vatican (position approximative)','D':'Monaco'}),
  ('europe-tchequie-slovaquie-croatie-slovenie.png', 'Croatie', 'C', 'Quelle lettre correspond à la Croatie sur la carte ?', {'A':'Tchéquie','B':'Slovaquie','C':'Croatie','D':'Slovénie supposée : flèche près de la frontière — non sélectionnée'})])
}
CAPITALS = [
 ('abbis abéba.png', 'Addis-Abeba', 'addis-abeba', ['Addis-Abeba','Addis Abeba']),
 ('bangkok.png', 'Bangkok', 'bangkok', ['Bangkok']),
 ('kaboul.png', 'Kaboul', 'kaboul', ['Kaboul']),
 ('lima.png', 'Lima', 'lima', ['Lima']),
 ('luxembourg.png', 'Luxembourg', 'luxembourg', ['Luxembourg']),
 ('ottawa.png', 'Ottawa', 'ottawa', ['Ottawa']),
 ('paris.png', 'Paris', 'paris', ['Paris']),
 ('port-au-prince.png', 'Port-au-Prince', 'port-au-prince', ['Port-au-Prince','Port au Prince']),
 ('saint marin.png', 'Saint-Marin', 'saint-marin', ['Saint-Marin','Saint Marin'])
]
TIMING = {'secondsPerFlip':5, 'decayPercentagePerFlip':0.0, 'maxFlips':2, 'pointsDecayPerFlip':5}
rows, audit, summaries = [], [], []

def write_json(path, data):
 path.parent.mkdir(parents=True, exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def make_package(slug, region, questions, images):
 package_id = 'geographie-'+slug+'-20261010'
 category_id = package_id
 category_name = 'Géographie - '+region
 source = OUT/'sources'/package_id
 source.mkdir(parents=True,exist_ok=True)
 buzzer = slug == 'capitales'
 game = {'id':package_id,'name':category_name,'description':('Capitales en rébus. Buzzez puis répondez à voix haute.' if buzzer else 'Repérez les lieux sur les cartes. Répondez avec A, B, C ou D.')+' 15 secondes par question ; 15, 10 puis 5 points.','categoryPackages':[category_id],'timingConfig':TIMING,'answerTimeSeconds':10}
 category = {'category':category_name,'answerMode':'BUZZER' if buzzer else 'SIMULTANEOUS','questionTypes':['Rébus de capitales' if buzzer else 'Choix multiples'],'questions':questions}
 write_json(source/'game.json',game)
 write_json(source/'question-bank'/f'{category_id}.json',category)
 for origin, destination in images:
  data = origin.read_bytes()
  assert data[:8]==b'\x89PNG\r\n\x1a\n',origin
  width,height=struct.unpack('>II',data[16:24])
  assert width>0 and height>0
  assert len(data)<=20*1024*1024
  target=source/destination; target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin,target)
  assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(data).digest()
 archive=OUT/f'geographie-{slug}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for file in sorted(source.rglob('*')):
   if file.is_file():z.write(file,file.relative_to(source).as_posix())
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  assert sum(info.file_size for info in z.infolist())<=150*1024*1024
 summaries.append((region,len(questions),archive.name,round(archive.stat().st_size/1024/1024,2)))

for slug,(region,items) in MAPS.items():
 questions,images=[],[]
 folder=ROOT/('Géographie - '+region)
 assert set(p.name for p in folder.iterdir() if p.is_file())==set(item[0] for item in items)
 for index,(filename,target,letter,prompt,labels) in enumerate(items,1):
  image=f'images/carte-{index:02d}.png'
  q={'kind':'multipleChoice','id':f'geo-{slug}-20261010-{index:02d}','category':'Géographie - '+region,'prompt':prompt,'imageUrl':image,'basePoints':15,'penaltyPoints':0,'options':['A','B','C','D'],'correctOptionIndex':'ABCD'.index(letter)}
  questions.append(q);images.append((folder/filename,image))
  rows.append([q['category'],filename,prompt,letter+' — '+target,' ; '.join(f'{k} : {v}' for k,v in labels.items())])
  audit.append({'sourceFolder':folder.name,'sourceFile':filename,'questionId':q['id'],'target':target,'correctLetter':letter,'labels':labels})
 make_package(slug,region,questions,images)
questions,images=[],[];folder=ROOT/'Géographie - Capitales'
assert set(p.name for p in folder.iterdir() if p.is_file())==set(item[0] for item in CAPITALS)
for index,(filename,answer,stem,accepted) in enumerate(CAPITALS,1):
 image=f'images/{stem}.png'
 q={'kind':'textAnswer','id':f'geo-capitales-20261010-{index:02d}','category':'Géographie - Capitales','prompt':'Quelle capitale ce rébus représente-t-il ?','imageUrl':image,'basePoints':15,'penaltyPoints':0,'acceptableAnswers':accepted,'allowFuzzyMatch':False}
 questions.append(q);images.append((folder/filename,image))
 rows.append([q['category'],filename,q['prompt'],answer,'Réponse orale ; validation par l’hôte'])
 audit.append({'sourceFolder':folder.name,'sourceFile':filename,'questionId':q['id'],'answer':answer})
make_package('capitales','Capitales',questions,images)
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Catégorie','Image source','Question','Réponse','Repères / remarques']);w.writerows(rows)
write_json(OUT/'verification-images.json',audit)
assert len(rows)==26 and len(set(item['questionId'] for item in audit))==26
report='''# Vérification des forfaits de géographie — 10 octobre 2026

Six forfaits importables, 26 images et 26 questions : une question par image. Les originaux sont conservés ; les copies incluses dans les ZIP portent des noms compatibles avec l’importateur.

## Règles appliquées

- Cartes : choix multiples simultanés, réponses exactement **A, B, C, D** ; une seule bonne lettre.
- États-Unis : les repères désignent des **États**, et non des pays ; les questions utilisent donc « État ».
- Capitales : rébus, buzzer et réponse orale, validée par l’hôte. Les noms attendus proviennent des fichiers.
- Chaque question : **15 secondes de recherche**, réparties en trois intervalles de 5 secondes : **15 points de 0 à moins de 5 s, 10 points de 5 à moins de 10 s, 5 points de 10 à moins de 15 s**. Aucune pénalité de points après une mauvaise réponse.
- Capitales : **10 secondes pour répondre après le buzzer**. Le temps de recherche et la valeur en points sont gelés au buzzer ; une erreur ou un dépassement reprend le temps de recherche restant. Ces 10 secondes peuvent donc porter la durée réelle de la question au-delà de 15 secondes.

## Corrections orthographiques

| Fichier source | Réponse retenue | Correction |
|---|---|---|
| `abbis abéba.png` | **Addis-Abeba** | « abbis » doit devenir « Addis » ; orthographe française harmonisée. La variante « Addis Abeba » est aussi acceptée. |
| `saint marin.png` | **Saint-Marin** | Majuscules et trait d’union. |
| `port-au-prince.png` | **Port-au-Prince** | Majuscules harmonisées. |
| Autres capitales | Bangkok, Kaboul, Lima, Luxembourg, Ottawa, Paris | Orthographe correcte ; capitalisation harmonisée. |

Références : [Éthiopie — France Diplomatie](https://www.diplomatie.gouv.fr/fr/information-par-pays/ethiopie/presentation-de-l-ethiopie), [Saint-Marin — France Diplomatie](https://www.diplomatie.gouv.fr/fr/information-par-pays/saint-marin/presentation-de-saint-marin).

## Erreurs, omissions et ambiguïtés relevées

1. **Afrique — les quatre images : frontière Soudan / Soudan du Sud absente.** Elles représentent cette zone comme un seul territoire. Les questions sélectionnées portent sur d’autres pays : Angola, Niger, Gabon et Zambie. Pour une carte pédagogique actuelle, rétablir cette séparation. Référence : [carte des États et capitales — France Diplomatie, juin 2026](https://www.diplomatie.gouv.fr/files/files/le-ministere/archives-et-traites/S%E2%80%99orienter%20dans%20les%20fonds%20et%20collections/carte-monde_etats_et_capitales_a3_2026-06.pdf).
2. **`12-amerique-sud.png`, D : Guyane française.** Ce repère désigne un territoire français, pas un pays indépendant. Le pays choisi pour la question est le **Suriname, C**. B correspond au **Guyana**, distinct de la Guyane française. Référence : [Guyane — Insee](https://www.insee.fr/fr/metadonnees/geographie/region/03-guyane).
3. **`06-asie.png`, C : flèche insuffisamment précise.** Son extrémité est près de la côte et de plusieurs petits territoires du Levant ; elle n’a pas le point de localisation net des autres petites zones. Aucun nom n’a été fixé pour C dans le corrigé d’audit. La question porte sur l’**Iran, A**, clairement repéré. Ajouter un point placé à l’intérieur du territoire voulu.
4. **`europe-tchequie-slovaquie-croatie-slovenie.png`, D : repère à préciser.** La lettre se trouve dans la zone autrichienne et sa flèche aboutit près de la frontière ; le nom du fichier suggère la Slovénie. La question porte sur la **Croatie, C**. Placer le point à l’intérieur de la Slovénie pour éviter une lecture « Autriche ».
5. **`europe-microetats-abcd.png` : localisations schématiques.** Les micro-États sont des points, sans contours ; A et C apparaissent très près du littoral dans l’encart italien. B est une position approximative dans les Pyrénées. La question porte sur **Monaco, D**. Des agrandissements locaux plus précis seraient préférables si ces autres lettres deviennent les bonnes réponses.
6. **Ottawa — rébus phonétiquement approximatif.** L’image se lit « eau + tas + voie », soit approximativement « o-ta-vwa », alors que le nom visé est Ottawa. Le nom du fichier a été conservé comme réponse demandée. Suggestion : remplacer la voie ferrée par une **oie** (« eau + tas + oie »), plus proche de « o-ta-wa ».
7. **Port-au-Prince — plusieurs princes.** Le rébus montre un port avec plusieurs princes : « port aux princes » est une lecture possible. Le contexte « capitale » permet normalement de retrouver Port-au-Prince ; un seul prince réduirait l’ambiguïté.
8. **Luxembourg — indice large.** L’image évoque « luxe + bourg », mais peut aussi être décrite comme une ville riche. Le contexte « capitale » est nécessaire. Aucune erreur d’orthographe dans la réponse.
9. **Lettres minuscules sur certaines cartes, majuscules sur les téléphones.** Les réponses A–D correspondent aux repères a–d de même lettre. Pour harmoniser les images, convertir ultérieurement tous les repères en majuscules.

Les frontières des illustrations sont schématiques : ce contrôle vérifie les pays sélectionnés et signale les problèmes visibles, sans certifier l’exactitude de chaque frontière ou de chaque territoire non sélectionné. **Aucune des 26 images n’a été omise.** Les zones ambiguës ne sont pas utilisées comme bonnes réponses. Les rébus signalés restent inclus conformément aux noms de fichiers fournis.

## Suggestions

- Essayer les rébus sur le téléviseur avec quelques joueurs : 15 secondes peuvent être courtes pour les indices phonétiques les moins directs.
- Pour varier les parties sans ajouter d’images, créer ultérieurement des variantes ciblant d’autres lettres, après correction des repères ambigus.
- Ne pas mélanger l’ordre des choix A–D sans mettre à jour l’index de la bonne réponse.
- Conserver `QUESTIONS-ET-REPONSES.csv` pour l’hôte : il contient les réponses, les correspondances de lettres et les noms de fichiers originaux.

## Importation

Copier les six ZIP sur le téléphone hôte, puis choisir **IMPORTER UN FORFAIT (.ZIP)** pour chaque fichier. Importer les ZIP individuels ; les dossiers `sources/` servent à la révision des JSON. Chaque ZIP contient `game.json`, `question-bank/` et `images/` à sa racine.

## Inventaire

| Forfait | Questions | ZIP | Taille (Mo) |
|---|---:|---|---:|
'''
for region,count,name,size in summaries:
 report+=f'| Géographie - {region} | {count} | `{name}` | {size} |\n'
(OUT/'RAPPORT-VERIFICATION.md').write_text(report,encoding='utf-8')
for row in summaries: print(row)
print('Total:',len(rows),'questions; ZIP CRC, image hashes and coverage validated.')
