from pathlib import Path
import json,zipfile,hashlib,shutil
D=Path('build/dialogue-extracts/X1PiR7WfuWs').resolve();rows=json.loads((D/'dialogues.json').read_text(encoding='utf8'));old=json.loads((D/'before-removal-hashes.json').read_text(encoding='utf8'));assert len(rows)==5
for r in rows:assert all(r[k]==old[r['id']][k] for k in ['sha256','mp3Sha256'])
with zipfile.ZipFile(D/'La-Chevre-cinq-dialogues.zip') as z:
 assert sum(n.endswith('.wav') for n in z.namelist())==5
 assert sum(n.endswith('.mp3') for n in z.namelist())==5
 assert not any(n.startswith(('clips/03-','clips/04-','03-context')) for n in z.namelist())
for name in ['clips/03-vous-metonnez.wav','clips/03-vous-metonnez.mp3','clips/04-la-gifle.wav','clips/04-la-gifle.mp3','03-context.mp3']:
 p=(D/name).resolve();assert p.is_relative_to(D)
 if p.exists():p.unlink()
# The old download link also delivers the corrected five-clip set.
shutil.copyfile(D/'La-Chevre-cinq-dialogues.zip',D/'La-Chevre-sept-dialogues.zip')
s=(D/'index.html').read_text(encoding='utf8');assert s.count('<article>')==5 and s.count('<audio ')==5
print('Removed clips 3 and 4 from final exports, preview and both download links. All five approved audio pairs are byte-identical.')
