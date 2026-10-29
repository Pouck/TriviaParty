"""Search Wikimedia Commons for review-only exotic animal photo candidates."""
import html, json, re, time, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/image-qsj-sampler/candidates/exotic-animal-search'
API='https://commons.wikimedia.org/w/api.php'
UA='TriviaParty/1.0 (local image review; attribution recorded; contact: private user project)'
TARGETS=[('red-panda','red panda animal'),('fennec-fox','fennec fox animal'),('axolotl','axolotl animal'),('narwhal','narwhal animal'),('quokka','quokka animal'),('malayan-tapir','Malayan tapir animal'),('three-toed-sloth','three-toed sloth animal'),('capybara','capybara animal'),('komodo-dragon','Komodo dragon animal'),('chameleon','chameleon animal'),('whale-shark','whale shark animal'),('platypus','platypus animal')]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.s=[]
 def handle_data(self,x):self.s.append(x)
def plain(x):
 p=Text();p.feed(x or '');return re.sub(r'\s+',' ',html.unescape(' '.join(p.s))).strip()
def call(params):
 req=urllib.request.Request(API+'?'+urllib.parse.urlencode(params),headers={'User-Agent':UA})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
def main():
 OUT.mkdir(parents=True,exist_ok=True); result={}
 for key,term in TARGETS:
  try:
   rows=call({'action':'query','generator':'search','gsrsearch':term,'gsrnamespace':6,'gsrlimit':15,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':1100,'format':'json'}).get('query',{}).get('pages',{}).values()
   choices=[]
   for row in rows:
    info=row.get('imageinfo',[{}])[0]; ext=info.get('extmetadata',{}); lic=plain(ext.get('LicenseShortName',{}).get('value',''))
    if info.get('mime') not in ('image/jpeg','image/png','image/webp'):continue
    if not (lic.startswith(('CC BY','CC-BY','CC BY-SA','CC-BY-SA')) or lic in {'CC0','CC Zero','Public domain'}):continue
    choices.append((row,info,ext,lic))
   if not choices: result[key]={'title':term,'status':'No licensed photo candidate found'};continue
   row,info,ext,lic=choices[0]; url=info['thumburl'].replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/')
   req=urllib.request.Request(url,headers={'User-Agent':UA,'Referer':'https://commons.wikimedia.org/'})
   with urllib.request.urlopen(req,timeout=45) as r:blob=r.read()
   path=OUT/(key+Path(urllib.parse.urlparse(url).path).suffix.lower());path.write_bytes(blob)
   file='File:'+row['title'].removeprefix('File:')
   source='https://commons.wikimedia.org/wiki/'+urllib.parse.quote(file.replace(' ','_'),safe=':()_,-')
   result[key]={'title':term,'candidate':path.relative_to(ROOT).as_posix(),'commonsFile':file,'source':source,'downloadedFrom':url,
    'license':lic,'licenseUrl':plain(ext.get('LicenseUrl',{}).get('value','')),'creator':plain(ext.get('Artist',{}).get('value','')),
    'credit':plain(ext.get('Credit',{}).get('value','')),'width':info.get('thumbwidth'),'height':info.get('thumbheight'),'bytes':len(blob),'review':'Pending visual inspection'}
   print('OK',key,lic,row['title']);time.sleep(.5)
  except Exception as e: result[key]={'title':term,'status':str(e)};print('FAIL',key,str(e))
 (OUT/'candidate-metadata.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'downloaded':sum('candidate' in x for x in result.values()),'requested':len(TARGETS),'output':str(OUT)},ensure_ascii=False))
if __name__=='__main__':main()
