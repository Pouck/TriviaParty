from pathlib import Path
import json,zipfile,hashlib
D=Path('build/dialogue-extracts/vadrouille-tea-for-two');rows=json.loads((D/'dialogues.json').read_text(encoding='utf8'));assert len(rows)==2
with zipfile.ZipFile(D/'Vadrouille-Tea-for-Two-deux-dialogues.zip') as z:
 for r in rows:
  for k,h in [('wavFile','sha256'),('mp3File','mp3Sha256')]:assert hashlib.sha256(z.read(r[k])).hexdigest()==r[h]
print('Both WAV/MP3 pairs verified in the ZIP.')
