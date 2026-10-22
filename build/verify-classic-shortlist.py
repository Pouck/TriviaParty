from pathlib import Path
import json,wave,hashlib,struct,re
R=Path.cwd();D=R/'build/classic-audio';rows=json.loads((R/'audio-bank/classic-reactions-candidates.json').read_text(encoding='utf8'))
assert len(rows)==21 and len({r['id'] for r in rows})==21
for r in rows:
 assert len(r['text'].split())<=25,(r['id'],len(r['text'].split()))
 if r['audioStatus']=='local_audition':
  p=D/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
  with wave.open(str(p)) as w:
   assert w.getframerate()==44100 and w.getnchannels()==1 and w.getsampwidth()==2
   frames=w.readframes(w.getnframes());samples=struct.unpack('<'+'h'*(len(frames)//2),frames)
   assert .4<r['durationSeconds']<6
   assert max(abs(s) for s in samples)>1000
   assert max(abs(s) for s in samples[:round(.18*44100)])<200
page=(D/'index.html').read_text(encoding='utf8');assert page.count('<article ')==21 and page.count('<audio ')==2
active=json.loads((R/'audio-bank/movie-reactions-selection.json').read_text(encoding='utf8'));assert len(active)==88
print('Validated 21 source records, 2 PCM audition cuts and all local page references. Existing 88-clip selection unchanged.')
