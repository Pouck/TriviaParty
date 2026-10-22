import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8');rows=json.loads(Path('build/classic-audio/extended-catalog.json').read_text(encoding='utf8'))
for r in rows:
 if r['actor'] in ['annie-girardot','brigitte-bardot','isabelle-adjani','catherine-deneuve','jean-rochefort','michel-serrault','philippe-noiret']:
  for q in r.get('quotes',[]):print(r['actor'],q['url'],q['text'])
