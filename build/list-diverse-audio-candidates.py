import json,pathlib,sys
sys.stdout.reconfigure(encoding='utf8')
d=json.loads(pathlib.Path('build/movie-audition/all-bleeps.json').read_text(encoding='utf8'));used={r['downloadUrl'] for r in json.loads(pathlib.Path('audio-bank/movie-reactions-selection.json').read_text(encoding='utf8'))}
for r in d:
 if r['sound'] in used or r['source_name'] not in ['La Classe Américaine','Astérix et Obélix: Mission Cléopâtre','Le Boulet','Le Roi Lion','Aladdin','American Psycho','Dude, Where\'s My Car ?','The Mask','Ace Ventura When Nature Calls']:continue
 if r['source_name']=='American Psycho' and not any(x in r['name'].lower() for x in ['bien','parfait','super','beau','génial','wrong','great','bon','très','raté','you','compr']):continue
 print(r['name_unique'],'|',r['source_name'],'|',r['name'])
print('Existing low IDs:',[p.name for p in pathlib.Path('build/movie-audition').glob('*.wav') if int(p.stem.split('-')[-1])<60])
