import json,collections,pathlib
rows=json.loads(pathlib.Path('audio-bank/movie-reactions-selection.json').read_text(encoding='utf8'))
print(json.dumps([(r['file'],r['film'],r['text']) for r in rows[29:]],ensure_ascii=True))
print('Whisper',pathlib.Path('build/movie-audition/whisper-bin/Release/whisper-cli.exe').exists(),pathlib.Path('build/movie-audition/ggml-base.bin').exists())
for n in ['expanded-plan.json','bleeps-candidates.json','bleeps-search.json','french-candidates.json','source-repos.json']:
 p=pathlib.Path('build/movie-audition')/n
 if p.exists(): print(n,p.stat().st_size,p.read_text(encoding='utf8')[:180])
