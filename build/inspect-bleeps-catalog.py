import json,pathlib
p=pathlib.Path('build/movie-audition/all-bleeps.json');d=json.loads(p.read_text(encoding='utf8'));print(type(d).__name__);print(str(d)[:1600])
