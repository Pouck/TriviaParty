from pathlib import Path
import json
p=Path('build/classic-audio/alternate-sources/bourvil-transcript.json');r=json.loads(p.read_text(encoding='utf8'))
for s in r['transcription']:
 if 'marcher' in s['text']:print(s['offsets'],s['text'])
