from pathlib import Path
import json,zipfile,hashlib
D=Path('build/dialogue-extracts/oscar-vole');rows=json.loads((D/'dialogues.json').read_text(encoding='utf8'));assert len(rows)==3
with zipfile.ZipFile(D/'Oscar-vole-trois-dialogues.zip') as z:
 for r in rows:
  for k,h in [('wavFile','sha256'),('mp3File','mp3Sha256')]:assert hashlib.sha256(z.read(r[k])).hexdigest()==r[h]
print('All three WAV/MP3 pairs verified in the ZIP.')
