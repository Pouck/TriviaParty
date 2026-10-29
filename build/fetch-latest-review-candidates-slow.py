import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'build/image-qsj-sampler/candidates/latest-review-2026-10-27';out.mkdir(parents=True,exist_ok=True)
queries={
 'butterfly':'monarch butterfly close up wings open',
 'beaver':'North American beaver animal',
 'horse':'horse full body natural pasture',
 'pig':'domestic pig adult full body',
 'sperm-whale':'sperm whale underwater full body',
 'whale-shark':'whale shark swimming underwater',
 'walden':'Walden Pond Thoreau cabin',
 'st-pauls':'St Paul Cathedral London full exterior facade',
 'versailles':'Palace of Versailles full facade exterior',
 'tokyo-skytree':'Tokyo Skytree full tower',
 'empire-state':'Empire State Building full tower',
 'st-peters':'St Peters Basilica Vatican facade exterior',
 'holy-sepulchre':'Church of Holy Sepulchre Jerusalem exterior',
 'pantheon':'Pantheon Rome exterior facade',
}
UA='TriviaParty/1.0 (private game image review; attribution retained)'
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Referer':'https://commons.wikimedia.org/'})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read()
def plain(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()
results=[]
for key,query in queries.items():
 try:
  url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','format':'json','generator':'search','gsrsearch':query,'gsrnamespace':6,'gsrlimit':20,'prop':'imageinfo','iiprop':'url|extmetadata|size|mime','iiurlwidth':800})
  pages=list(json.loads(fetch(url)).get('query',{}).get('pages',{}).values())
  tokens=[x for x in re.findall(r'[a-z0-9]+',query.casefold()) if len(x)>2 and x not in {'full','photo','image','exterior'}]
  def score(p):
   title=p.get('title','').casefold()
   return (sum(1 for t in tokens if t in title),-p.get('index',999))
  pages.sort(key=score,reverse=True)
  chosen=None
  for p in pages:
   info=(p.get('imageinfo') or [{}])[0];meta=info.get('extmetadata',{})
   lic=plain(meta.get('LicenseShortName',{}).get('value','')).casefold()
   if not info.get('thumburl') or not info.get('mime','').startswith('image/'):continue
   if not (lic.startswith(('cc by','cc-by','cc0')) or 'public domain' in lic):continue
   title=p.get('title','').casefold()
   if sum(1 for t in tokens if t in title)<1:continue
   chosen=(p,info,meta,lic);break
  if not chosen:print('NONE',key,flush=True)
  else:
   p,info,meta,lic=chosen
   blob=fetch(info['thumburl']); ext=Path(urllib.parse.urlparse(info['thumburl']).path).suffix or '.jpg'
   path=out/f'{key}{ext}';path.write_bytes(blob)
   obj={'key':key,'query':query,'candidate':path.relative_to(root).as_posix(),'commonsFile':p['title'],'source':info.get('descriptionurl'),'downloadUrl':info['thumburl'],'license':plain(meta.get('LicenseShortName',{}).get('value','')),'licenseUrl':plain(meta.get('LicenseUrl',{}).get('value','')),'creator':plain(meta.get('Artist',{}).get('value','')),'credit':plain(meta.get('Credit',{}).get('value','')),'description':plain(meta.get('ImageDescription',{}).get('value','')),'review':'Pending visual review'}
   results.append(obj);print('OK',key,p['title'],flush=True)
 except Exception as e:
  print('ERR',key,type(e).__name__,str(e),flush=True)
  if '429' in str(e):break
 time.sleep(6)
(out/'candidate-metadata.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('downloaded',len(results),flush=True)
