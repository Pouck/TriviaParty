from pathlib import Path
import json
D=Path('build/classic-audio')
for id in ['bond-perfect','bond-congratulations']:
 j=json.loads((D/'sources'/(id+'.json')).read_text(encoding='utf8'))
 print(id)
 for t in j['transcription']: print(t['offsets'],t['text'])
