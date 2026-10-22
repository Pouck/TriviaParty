from pathlib import Path
import json,zipfile,hashlib
D=Path('build/dialogue-extracts');rows=json.loads((D/'sampler-manifest.json').read_text(encoding='utf8'));assert len(rows)==21 and len({r['id'] for r in rows})==21
assert not any(r['extractionFolder']=='X1PiR7WfuWs' and r['originalId'].startswith(('03-','04-')) for r in rows)
with zipfile.ZipFile(D/'Repliques-cinema-21-extraits.zip') as z:
 assert sum(n.endswith('.wav') for n in z.namelist())==21
 assert sum(n.endswith('.mp3') for n in z.namelist())==21
 for r in rows:
  for key,h in [('wavFile','sha256'),('mp3File','mp3Sha256')]:assert hashlib.sha256(z.read(r[key])).hexdigest()==r[h]
print('ZIP verified: 21 WAVs, 21 MP3s, sampler and manifest; rejected clips excluded; every audio hash matches its original extract.')
