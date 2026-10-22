import urllib.request,urllib.parse,json,sys,concurrent.futures
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8');D=Path('build/winner-music');D.mkdir(exist_ok=True)
queries={'zarathustra':'Also Sprach Zarathustra Einleitung filetype:audio','te-deum':'Charpentier Te Deum filetype:audio','aida':'Triumphal March Aida filetype:audio','fireworks':'Handel La Rejouissance filetype:audio','pomp':'Elgar Pomp Circumstance No 1 filetype:audio','hallelujah':'Handel Hallelujah chorus filetype:audio'}
def get(kq):
 k,q=kq;params={'action':'query','format':'json','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':4,'prop':'imageinfo','iiprop':'url|extmetadata|size'}
 u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
 try:
  j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'TriviaPartySampler/1.0 (private audio comparison)'}),timeout=30));(D/(k+'-search.json')).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
  for p in j.get('query',{}).get('pages',{}).values():
   i=p.get('imageinfo',[{}])[0];m=i.get('extmetadata',{});print(k,p['title'],m.get('LicenseShortName',{}).get('value'),i.get('url'),flush=True)
 except Exception as e:print(k,str(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,queries.items()))
