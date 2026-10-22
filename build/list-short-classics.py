import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8');rows=json.loads(Path('build/classic-audio/extended-catalog.json').read_text(encoding='utf8'))
for r in rows:
 if r['actor'] in ['bourvil','jean-gabin','lino-ventura','philippe-noiret','pierre-richard','daniel-auteuil','gerard-depardieu','brigitte-bardot','annie-girardot']:
  for q in r.get('quotes',[]):
   if len(q['text'])<95: print(r['actor'],q['url'],q['text'])
