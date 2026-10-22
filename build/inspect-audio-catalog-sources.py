import pathlib,json,collections,sys
sys.stdout.reconfigure(encoding='utf8')
rows=json.loads(pathlib.Path('build/movie-audition/all-bleeps.json').read_text(encoding='utf8'))
print(collections.Counter(r['source_name'] for r in rows))
for p in pathlib.Path('build/movie-audition').glob('*metadata.json'):print(p.name,p.stat().st_size)
for p in pathlib.Path('build/movie-audition').glob('*.js'):
 t=p.read_text(encoding='utf8')
 import re
 found=[m.group(0)[:180] for m in re.finditer(r'.{0,50}(?:api/bleep|fetch\(|firebase|supabase|searchBleep|searchParams).{0,100}',t)]
 if found: print(p.name,found[:8])
