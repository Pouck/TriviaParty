import json,pathlib,sys
sys.stdout.reconfigure(encoding='utf8');d=json.loads(pathlib.Path('build/movie-audition/all-bleeps.json').read_text(encoding='utf8'))
films=['Le Boulet','Aladdin','Denis la malice','The Expendables 2','Rambo 3','The Hateful Eight','Les Guignols - Putain 20 ans!','Spiderman 1994 tv series','Batman contre le fantôme masqué','American Pie 2','Pinky and the Brain','Minus et Cortex','EuroTrip']
for r in d:
 if r['source_name'] in films:print(r['name_unique'],'|',r['lang'],'|',r['source_name'],'|',r['name'])
