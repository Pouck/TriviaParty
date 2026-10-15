"""Apply the editable French Markdown audience list; preserve it when adding clips."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
selection=ROOT/'audio-bank/movie-reactions-selection.json'
notes=ROOT/'audio-bank/REACTIONS-A-ANNOTER.md'
rows=json.loads(selection.read_text(encoding='utf8'))
existing={}
if notes.exists():
 for line in notes.read_text(encoding='utf8').splitlines():
  if not re.match(r'\| (good|bad)-\d+\.wav \|',line):continue
  parts=[v.strip() for v in line.strip().strip('|').split('|')]
  if len(parts)!=7:raise ValueError('Chaque ligne doit conserver ses sept colonnes : '+line)
  if parts[4] not in ('oui','non','à vérifier'):raise ValueError('Valeur attendue : oui, non ou à vérifier : '+line)
  if parts[0] in existing:raise ValueError('Identifiant répété : '+parts[0])
  existing[parts[0]]=parts
restricted={'good-72.wav':'grossièreté','good-78.wav':'allusion à la séduction','good-93.wav':'allusion à la séduction','good-96.wav':'grossièreté légère','bad-70.wav':'grossièreté','bad-92.wav':'grossièreté légère','bad-99.wav':'menace / humour noir','good-63.wav':'grossièreté','bad-62.wav':'grossièreté'}
header='''# Réactions vocales — annotations du public

Modifiez uniquement les trois dernières colonnes. Les classements proposés restent à votre appréciation.

- **Exclure : oui** → exclu lorsque « Répliques tout public uniquement » est activé au démarrage.
- **Exclure : non** → autorisé avec ce filtre, y compris les taquineries sans grossièreté.
- **Exclure : à vérifier** → exclu avec ce filtre en attendant votre décision.
- Sans le filtre, toutes les répliques restent disponibles. Vos commentaires sont conservés.
- Évitez le caractère barre verticale dans les commentaires ; utilisez une virgule.

Après annotation : `python build/apply-reaction-audiences.py`, puis réinstaller la banque sur le téléphone avec `python build/install-movie-audition.py --serial IDENTIFIANT_ADB` et relancer l’application. Le fichier seul ne modifie pas une banque déjà installée.

| Fichier | Résultat | Œuvre | Réplique | Exclure | Étiquettes | Commentaire |
| --- | --- | --- | --- | --- | --- | --- |
'''
lines=[]
for r in rows:
 parts=existing.get(r['file'])
 if not parts:
  reason=restricted.get(r['file'],'')
  parts=[r['file'],'Bonne' if r['outcome']=='good' else 'Mauvaise',r['film'],r['text'].replace('|','/'),'oui' if reason else ('non' if r.get('audience')=='all' else 'à vérifier'),reason,'']
 r['audience']={'oui':'mature','non':'all','à vérifier':'unreviewed'}[parts[4]]
 r['audienceTags']=parts[5];r['audienceNote']=parts[6]
 lines.append('| '+' | '.join(parts)+' |')
notes.write_text(header+'\n'.join(lines)+'\n',encoding='utf8')
selection.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for p in [ROOT/'audio-bank/movie-preview.json',ROOT/'build/movie-audition/reactions.json']:
 if p.exists():
  manifest=json.loads(p.read_text(encoding='utf8'));byid={r['file']:r for r in rows}
  for r in manifest:
   source=byid.get(r['file'])
   if source:
    for k in ('audience','audienceTags','audienceNote'):r[k]=source[k]
  p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'Applied audience annotations for {len(rows)} clips; {sum(r["audience"]=="all" for r in rows)} allowed with the filter.')
