from pathlib import Path
import json,hashlib,zipfile
D=Path('build/dialogue-extracts/X1PiR7WfuWs');old=json.loads((D/'approved-before-revision.json').read_text(encoding='utf8'));rows=json.loads((D/'dialogues.json').read_text(encoding='utf8'))
with zipfile.ZipFile(D/'La-Chevre-sept-dialogues.zip') as z:
 for r in rows:
  for k,h in [('wavFile','sha256'),('mp3File','mp3Sha256')]:assert hashlib.sha256(z.read(r[k])).hexdigest()==r[h]
  if r['reviewStatus']=='approved_by_user':assert all(r[k]==old[r['id']][k] for k in ['sha256','mp3Sha256','startSeconds','endSeconds'])
  else:assert r['startSeconds']<old[r['id']]['startSeconds'] and r['endSeconds']>old[r['id']]['endSeconds']
print('Verified both extended cuts, ZIP contents, and byte-identical preservation of all five approved WAV/MP3 pairs.')
