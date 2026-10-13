"""Read every archive and record format, size, wording and illustration coverage."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,re,zipfile
ROOT=Path('package-examples');OUT=ROOT/'library-2026-10-12'
def group(name):
 for test,label in [(['musique','chanson','jazz'],'Musique'),(['super-héros','marvel'],'Super-héros'),(['bd et manga'],'BD et manga'),(['logique','énigmes','devinettes'],'Logique et énigmes'),(['contes','légendes','table ronde'],'Contes et légendes'),(['cuisine'],'Cuisine'),(['nature','oiseaux','insectes','animaux'],'Nature'),(['mythologie','odyssée'],'Mythologie'),(['architecture'],'Architecture'),(['arts'],'Arts'),(['cinéma'],'Cinéma'),(['littérature'],'Littérature'),(['géographie'],'Géographie'),(['inventions','sciences'],'Sciences'),(['jeux vidéo','jeu vidéo'],'Jeux vidéo'),(['histoire','canada','révolution'],'Histoire')]:
  if any(s in name.lower() for s in test):return label
 return 'Autres'
rows=[];counts=defaultdict(Counter);short=[];wordy=[];english=[];seen=set();duplicates=[]
for archive in ROOT.rglob('*.zip'):
 with zipfile.ZipFile(archive) as z:
  game=json.loads(z.read('game.json'));subject=group(game['name']);demo=any(s in str(archive) for s in ['tests-','demo'])
  for bank_file in z.namelist():
   if not bank_file.startswith('question-bank/') or not bank_file.endswith('.json'):continue
   bank=json.loads(z.read(bank_file));qs=bank['questions'];kinds=Counter(q['kind'] for q in qs)
   chronology=sum(q['kind']=='ordering' or (q['kind']=='multipleChoice' and len(q['options'])==4 and all('→' in o for o in q['options'])) for q in qs)
   images=sum(bool(q.get('imageUrl')) for q in qs);long=max((len(q['prompt'].split('\n')[0]) for q in qs),default=0)
   modes=dict(kinds);modes['chronologie']=chronology;modes['multipleChoice']=modes.get('multipleChoice',0)-(chronology if 'multipleChoice' in kinds else 0)
   if not demo:counts[subject].update({k:v for k,v in modes.items() if v>0})
   rows.append([game['name'],subject,len(qs),images,chronology,long,str(archive),'TEST/DEMO' if demo else 'NOUVEAU' if archive.parent==OUT else 'EXISTANT'])
   if len(qs)<5 and not demo:short.append((game['name'],len(qs)))
   for q in qs:
    if q['id'] in seen:duplicates.append(q['id'])
    seen.add(q['id'])
    if len(q['prompt'].split('\n')[0])>125:wordy.append((game['name'],q['id'],q['prompt'].split('\n')[0]))
    if re.match(r'^(Which|What|Who|Order these|Put these)\b',q['prompt']):english.append(q['id'])
with (OUT/'AUDIT-CATALOGUE.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Forfait','Sujet','Questions','Images','Chronologies','Longueur consigne max.','Chemin','Statut']);w.writerows(rows)
(OUT/'AUDIT.md').write_text('# Audit de toute la bibliothèque\n\n'+f'{len(rows)} archives parcourues ; {sum(r[2] for r in rows)} questions, y compris tests et démonstrations.\n\n'+'## Couverture par sujet, hors tests\n\n| Sujet | QCM | Buzzer | Qui suis-je ? | Chronologie |\n|---|---:|---:|---:|---:|\n'+'\n'.join(f"| {s} | {c['multipleChoice']} | {c['textAnswer']} | {c['guessWho']} | {c['chronologie']} |" for s,c in sorted(counts.items()))+'\n\n## Actions prises\n\n- Mythologies grecque et romaine : de courts anciens sets d’indices à de nouvelles séries de cinq QCM, cinq buzzer et cinq Qui suis-je ? par tradition.\n- Littérature, sciences, inventions et histoire : nouvelles séries buzzer et indices pour compléter les séries QCM déjà présentes.\n- Cuisine, BD, manga, super-héros, animation, légendes, explorateurs et nature : nouvelles familles déclarées avec trois formats.\n- Musique : chanson francophone, Québec, pop/rock, jazz/blues/soul, classique, instruments, films et comédies musicales.\n- Chronologies : dix séries de cinq questions, uniquement pour des dates ou séquences explicites ; 45 secondes minimum après lecture libre.\n- QCM/buzzer nouveaux : deux visuels et trois textes par forfait. Les indices restent textuels pour ne pas révéler immédiatement l’identité.\n- Regroupement de la sélection et alternance de sujets/formats conservés.\n\n## Anciennes séries courtes conservées\n\nLes nouvelles séries complètent les anciennes, qui restent disponibles pour mise à jour ou suppression par l’hôte. Certaines cartes régionales anciennes et certains Qui suis-je ? sont courts. Ils ne sont pas artificiellement remplis par des questions répétant la même image. Les séries de test et de démonstration sont volontairement exclues de cette liste.\n\n'+'\n'.join(f'- {name} : {n} questions.' for name,n in short)+'\n\n## Consignes anciennes à surveiller\n\nLes consignes les plus longues restent listées ci-dessous pour une révision ciblée ultérieure. Le mode cartes supprime déjà les répétitions de permutations et raccourcit la consigne sur l’écran de jeu. Les nouvelles formulations privilégient des phrases courtes.\n\n'+'\n'.join(f'- `{id}` : {prompt}' for _,id,prompt in wordy)+'\n\n## Contrôles\n\n'+f'- Identifiants de questions répétés entre archives : {len(duplicates)}.\n- Questions commençant par une consigne anglaise détectée : {len(english)}.\n'+'\n[Inventaire détaillé](AUDIT-CATALOGUE.csv) · [Nouveaux forfaits](README.md).\n',encoding='utf-8')
print(len(rows),'archives audited;',len(short),'legacy short sets;',len(wordy),'long headings;',len(duplicates),'duplicate question IDs;',len(english),'English prompts.')
