import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8');rows=json.loads(Path('audio-bank/reactions.json').read_text(encoding='utf8'))
for r in rows:
 if r['language']=='fr' and len(r['text'].split())<=2 and r['durationSeconds']<1.8:print(r['outcome'],r['file'],r['text'],r['durationSeconds'])
