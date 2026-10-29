"""Find review-only Commons photo candidates for user-flagged animals, landscapes, and landmarks."""
import html,json,re,time,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/image-qsj-sampler/candidates/review-replacements-2026-10-27';API='https://commons.wikimedia.org/w/api.php';UA='TriviaParty/1.0 (private image review; attribution retained)'
TARGETS=[
 ('monarch-butterfly-single','monarch butterfly close up photograph one butterfly'),
 ('beaver-single','North American beaver on river bank single animal photograph'),
 ('domestic-pig-single','domestic pig single adult animal photograph'),
 ('sperm-whale-single','sperm whale swimming one whale photograph'),
 ('horse-single','horse standing in pasture single horse photograph'),
 ('walden-pond','Walden Pond Massachusetts landscape photograph'),
 ('st-pauls-cathedral-full','Saint Pauls Cathedral London full exterior photograph'),
 ('versailles-palace-full','Palace of Versailles front facade full exterior photograph'),
 ('tokyo-skytree-full','Tokyo Skytree full tower from ground photograph'),
 ('empire-state-building-full','Empire State Building full building street photograph'),
 ('st-peters-basilica-full','Saint Peters Basilica Vatican full facade square photograph'),
 ('holy-sepulchre-full','Church of Holy Sepulchre Jerusalem full exterior photograph'),
 ('pantheon-rome-full','Pantheon Rome full exterior front photograph'),
]
class T(HTMLParser):
 def __init__(self):super().__init__();self.x=[]
 def handle_data(self,s):self.x.append(s)
def plain(s):
 p=T();p.feed(s or '');return re.sub(r'\s+',' ',html.unescape(' '.join(p.x))).strip()
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Referer':'https://commons.wikimedia.org/'})
 for n in range(5):
  try:
   with urllib.request.urlopen(req,timeout=45) as r:return r.read(),r.url,r.headers.get('Content-Type','')
  except Exception:
   if n==4:raise
   time.sleep(10*(n+1))
def main():
 OUT.mkdir(parents=True,exist_ok=True);results={}
 for key,query in TARGETS:
  try:
   params=urllib.parse.urlencode({'action':'query','format':'json','generator':'search','gsrsearch':query,'gsrnamespace':6,'gsrlimit':12,'prop':'imageinfo','iiprop':'url|extmetadata|size|mime','iiurlwidth':1200})
   raw,_,_=fetch(API+'?'+params);pages=list(json.loads(raw).get('query',{}).get('pages',{}).values())
   tokens=set(re.findall(r'[a-z0-9]+',query.casefold()))-{'single','photograph','photo','one','full','from','the','of','at','in','and'}
   pages.sort(key=lambda p:(-len(tokens&set(re.findall(r'[a-z0-9]+',p.get('title','').casefold()))),p.get('index',999)))
   chosen=None
   for p in pages:
    i=p.get('imageinfo',[{}])[0];ext=i.get('extmetadata',{});lic=plain(ext.get('LicenseShortName',{}).get('value',''))
    if not i.get('mime','').startswith('image/') or not (lic.startswith(('CC BY','CC-BY','CC BY-SA','CC-BY-SA')) or lic in {'CC0','CC Zero','Public domain'}):continue
    chosen=(p,i,ext,lic);break
   if not chosen:results[key]={'query':query,'status':'No licensed photo result'};continue
   p,i,ext,lic=chosen;filename=p['title'].removeprefix('File:').replace(' ','_');url='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(filename,safe="()_',.-")+'?width=1200'
   blob,downloaded,ctype=fetch(url)
   if not ctype.startswith('image/') or len(blob)<5000:raise ValueError('invalid image response '+ctype)
   suffix=Path(urllib.parse.urlparse(downloaded).path).suffix.lower()
   if suffix not in {'.jpg','.jpeg','.png','.webp'}:suffix='.jpg'
   path=OUT/(key+suffix);path.write_bytes(blob);source='https://commons.wikimedia.org/wiki/'+urllib.parse.quote(p['title'].replace(' ','_'),safe=":()_',.-")
   results[key]={'query':query,'candidate':path.relative_to(ROOT).as_posix(),'commonsFile':p['title'],'source':source,'downloadedFrom':downloaded,'license':lic,'licenseUrl':plain(ext.get('LicenseUrl',{}).get('value','')),'creator':plain(ext.get('Artist',{}).get('value','')),'credit':plain(ext.get('Credit',{}).get('value','')),'description':plain(ext.get('ImageDescription',{}).get('value','')),'width':i.get('width'),'height':i.get('height'),'bytes':len(blob),'review':'Pending visual review'}
   print('OK',key,lic,p['title'],flush=True)
  except Exception as e:results[key]={'query':query,'status':str(e)};print('FAIL',key,str(e),flush=True)
  time.sleep(2)
 (OUT/'candidate-metadata.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'downloaded':sum('candidate'in x for x in results.values()),'targets':len(TARGETS),'output':str(OUT)},ensure_ascii=False))
if __name__=='__main__':main()
