from pathlib import Path
import json,hashlib,collections
R=Path.cwd();D=R/'build/movie-audition';rows=json.loads((D/'reactions.json').read_text(encoding='utf8'));before=json.loads((D/'pre-expansion-hashes.json').read_text())
assert all(hashlib.sha256((D/f).read_bytes()).hexdigest()==h for f,h in before.items())
assert len(rows)==88 and collections.Counter(r['outcome'] for r in rows)=={'good':44,'bad':44}
assert len({r['sha256'] for r in rows})==88
assert all(r['audience']=='unreviewed' for r in rows if r['file'] not in before)
p=R/'audio-bank/README.md';s=p.read_text(encoding='utf8');start=s.index('## Banque de secours')
s='''# Banque cinéma privée : 88 extraits préparés

La sélection comporte **44 réactions positives et 44 négatives**, tirées de 28 œuvres : 78 extraits en français, 8 en anglais et 2 en japonais. L’expansion du 15 octobre 2026 ajoute 16 extraits sans modifier les 72 fichiers précédents ni leurs annotations. Certaines additions sont des versions françaises de films ou séries étrangers ; les voix ne sont ni synthétisées ni imitées.

- Écouter et filtrer : `../build/movie-audition/index.html`.
- Sélection, sources et découpes : `movie-reactions-selection.json`.
- Manifeste, durées et empreintes : `movie-preview.json`.
- Annoter : `REACTIONS-A-ANNOTER.md`. Les 16 ajouts sont « à vérifier » et restent exclus du filtre tout public jusqu’à votre décision.
- Préparer : `python build/prepare-movie-audition.py`.
- Vérifier dans Chrome : `node build/check-movie-audition.cjs`.
- Installer : `python build/install-movie-audition.py --serial SERIAL`, puis relancer l’application. La préparation seule ne change pas la banque du téléphone.

Les médias restent dans `build/movie-audition/` ; ils ne sont ni publiés dans GitHub ni incorporés à l’APK. Aucun droit de redistribution n’est affirmé. Après installation, la lecture utilise le stockage privé du téléphone.

Le tirage épuise les clips d’un résultat avant de répéter et privilégie une autre voix et une autre œuvre. Le volume est normalisé et une amorce de 220 ms protège le début des mots. Les nouveaux extraits ont été décodés et confrontés aux légendes sources par reconnaissance vocale locale ; une écoute humaine reste à faire, notamment pour les dialogues bruités ou les échanges à plusieurs voix.

'''+s[start:];p.write_text(s,encoding='utf8')
print('Validated 88 unique clips; all 72 original audio hashes unchanged; 16 new audience reviews pending.')
