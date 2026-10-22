from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf8');j=json.loads(Path('build/dialogue-extracts/X1PiR7WfuWs/transcript.json').read_text(encoding='utf8'))
for s in j['transcription']:
 a=s['offsets']['from']/1000;b=s['offsets']['to']/1000
 if (a<10) or (18<a<24) or (35<a<41) or (82<a<91) or (109<a<114) or (120<a<131) or (156<a<163):print(a,b,s['text'])
