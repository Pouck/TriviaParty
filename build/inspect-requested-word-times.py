from pathlib import Path
import re,sys
sys.stdout.reconfigure(encoding='utf8');s=Path('build/dialogue-extracts/X1PiR7WfuWs/source.fr.vtt').read_text(encoding='utf8')
for block in s.split('\n\n'):
 if not re.search(r'00:00:(?:1[89]|2[0-4]|3[5-9]|4[01])|00:01:(?:2[2-9]|30|4[89]|5[0-3])|00:02:(?:0[0-8]|3[6-9]|4[0-2])',block):continue
 if '<c>' in block:print(block)
