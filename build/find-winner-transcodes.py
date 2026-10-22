from pathlib import Path
import urllib.request,urllib.parse,json,sys
sys.stdout.reconfigure(encoding='utf8');D=Path('build/winner-music');keys=['pomp','kiev','william-tell'];terms=['ELGAR Pomp and Circumstance','Modest Mussorgsky - pictures','military band version']
titles=[]
for key,term in zip(keys,terms):
 j=json.loads((D/(key+'-search.json')).read_text(encoding='utf8'));titles.append(next(p['title'] for p in j['query']['pages'].values() if term in p['title']))
u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','format':'json','prop':'videoinfo','viprop':'url|derivatives','titles':'|'.join(titles)})
j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'TriviaPartySampler/1.0'}),timeout=30));(D/'official-transcodes.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
for p in j['query']['pages'].values():
 print(p['title'])
 for d in p.get('videoinfo',[{}])[0].get('derivatives',[]):print(d.get('type'),d.get('transcodekey'),d.get('src'))
