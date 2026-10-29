"""Retry identified Commons candidates via Special:FilePath after API thumbnail throttling."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=ROOT/'build/image-qsj-sampler/candidates/politicians-animals-more/candidate-metadata.json'
OUT=ROOT/'build/image-qsj-sampler/candidates/politicians-animals-more'
API='https://commons.wikimedia.org/w/api.php'
UA='TriviaParty/1.0 (private local game question bank; attribution recorded)'
class T(HTMLParser):
 def __init__(self):super().__init__();self.a=[]
 def handle_data(self,x):self.a.append(x)
def plain(s):
 p=T();p.feed(s or '');return re.sub(r'\s+',' ',html.unescape(' '.join(p.a))).strip()
def request(url):
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Referer':'https://commons.wikimedia.org/'})
 for n in range(5):
  try:
   with urllib.request.urlopen(req,timeout=45) as r:return r.read(),r.url,r.headers.get('Content-Type','')
  except Exception:
   if n==4:raise
   time.sleep(8*(n+1))
def main():
 d=json.loads(META.read_text(encoding='utf-8')); done=0
 for key,row in d.items():
  if not row.get('status','').startswith('download failed: 429'):continue
  try:
   file=row['file']; params=urllib.parse.urlencode({'action':'query','titles':file,'prop':'imageinfo','iiprop':'url|extmetadata|size','format':'json'})
   raw,_,_=request(API+'?'+params); page=next(iter(json.loads(raw)['query']['pages'].values())); info=page.get('imageinfo',[{}])[0]
   ext=info.get('extmetadata',{}); lic=plain(ext.get('LicenseShortName',{}).get('value',''))
   if not (lic.startswith(('CC BY','CC-BY','CC BY-SA','CC-BY-SA')) or lic in {'CC0','CC Zero','Public domain'}):
    row['status']='License excluded on retry: '+lic;continue
   name=file.removeprefix('File:').replace(' ','_'); direct='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(name,safe="()_',.-")+'?width=1200'
   blob,downloaded,ctype=request(direct)
   if not ctype.startswith('image/') or len(blob)<5000:raise ValueError('Non-image or undersized response: '+ctype)
   suffix=Path(urllib.parse.urlparse(downloaded).path).suffix.lower()
   if suffix not in {'.jpg','.jpeg','.png','.webp'}:suffix='.jpg'
   path=OUT/(key+suffix);path.write_bytes(blob)
   row.update({'candidate':path.relative_to(ROOT).as_posix(),'source':'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(file.replace(' ','_'),safe=":()_',.-"),
    'downloadedFrom':downloaded,'license':lic,'licenseUrl':plain(ext.get('LicenseUrl',{}).get('value','')),
    'creator':plain(ext.get('Artist',{}).get('value','')),'credit':plain(ext.get('Credit',{}).get('value','')),
    'imageDescription':plain(ext.get('ImageDescription',{}).get('value','')),'width':info.get('width'),'height':info.get('height'),
    'bytes':len(blob),'status':'Downloaded; pending visual inspection','review':'Pending visual inspection'})
   done+=1;print('OK',key,lic,len(blob),flush=True)
  except Exception as e:row['status']='Retry failed: '+str(e);print('FAIL',key,str(e),flush=True)
  time.sleep(2.5)
 META.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'downloaded':done,'requested':sum(str(x.get('status','')).startswith('Downloaded') for x in d.values()),'metadata':str(META)},ensure_ascii=False))
if __name__=='__main__':main()
