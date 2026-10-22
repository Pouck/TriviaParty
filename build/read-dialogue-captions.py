import re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8');s=Path('build/dialogue-extracts/X1PiR7WfuWs/source.fr.vtt').read_text(encoding='utf8')
for block in s.split('\n\n'):
 lines=block.splitlines();t=next((l for l in lines if ' --> ' in l),'')
 fresh=[l for l in lines if '<c>' in l]
 if fresh:print(t.split(' align')[0],re.sub('<[^>]+>','',fresh[-1]))
