import json,collections,pathlib
for name in ['audio-bank/movie-reactions-selection.json','audio-bank/movie-preview.json','build/movie-audition/reactions.json','build/movie-audition/expanded-audit.json']:
 p=pathlib.Path(name)
 if p.exists():
  rows=json.loads(p.read_text(encoding='utf8'));print(name,len(rows),dict(collections.Counter(r['outcome'] for r in rows)),len({r.get('film') for r in rows}))
p=pathlib.Path('audio-bank/movie-reactions-selection.json');rows=json.loads(p.read_text(encoding='utf8'))
for r in rows:print(r['file'],r['film'],r['text'])
print('SOURCE CACHE',len(list(pathlib.Path('build/movie-audition/expanded-sources').glob('*'))))
