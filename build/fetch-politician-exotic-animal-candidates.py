"""Fetch Commons image candidates for visual review; never edits the bank."""
from __future__ import annotations
import html, json, re, time, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/image-qsj-sampler/candidates/politicians-animals-more'
UA='TriviaParty/1.0 (local image review; attribution recorded; contact: private user project)'
WIKI='https://en.wikipedia.org/w/api.php'
COMMONS='https://commons.wikimedia.org/w/api.php'
POLITICIANS=[
 ('louis-riel','Louis Riel'),('rene-levesque','René Lévesque'),('robert-borden','Robert Borden'),('jean-chretien','Jean Chrétien'),
 ('margaret-thatcher','Margaret Thatcher'),('angela-merkel','Angela Merkel'),('indira-gandhi','Indira Gandhi'),('jawaharlal-nehru','Jawaharlal Nehru'),
 ('mao-zedong','Mao Zedong'),('ho-chi-minh','Ho Chi Minh'),('simon-bolivar','Simón Bolívar'),('eva-peron','Eva Perón'),
 ('golda-meir','Golda Meir'),('mustafa-kemal-ataturk','Mustafa Kemal Atatürk'),('kwame-nkrumah','Kwame Nkrumah'),('deng-xiaoping','Deng Xiaoping'),
 ('fidel-castro','Fidel Castro'),('emmanuel-macron','Emmanuel Macron'),('volodymyr-zelenskyy','Volodymyr Zelenskyy'),('jacinda-ardern','Jacinda Ardern'),
 ('benazir-bhutto','Benazir Bhutto'),
]
ANIMALS=[
 ('fennec-fox','Fennec fox'),('red-panda','Red panda'),('pangolin','Pangolin'),('okapi','Okapi'),('quokka','Quokka'),('axolotl','Axolotl'),
 ('narwhal','Narwhal'),('malayan-tapir','Malayan tapir'),('three-toed-sloth','Three-toed sloth'),('greater-flamingo','Greater flamingo'),
 ('ring-tailed-lemur','Ring-tailed lemur'),('meerkat','Meerkat'),('capybara','Capybara'),('komodo-dragon','Komodo dragon'),
 ('emperor-penguin','Emperor penguin'),('chameleon','Chameleon'),('giant-manta-ray','Giant manta ray'),('whale-shark','Whale shark'),
 ('platypus','Platypus'),('secretarybird','Secretarybird'),('shoebill','Shoebill'),('giant-anteater','Giant anteater'),
 ('wombat','Wombat'),('fossa','Fossa (animal)'),('aye-aye','Aye-aye'),
]
class Text(HTMLParser):
 def __init__(self): super().__init__();self.parts=[]
 def handle_data(self,d): self.parts.append(d)
def plain(x):
 p=Text();p.feed(x or '');return re.sub(r'\s+',' ',html.unescape(' '.join(p.parts))).strip()
def api(base,params):
 url=base+'?'+urllib.parse.urlencode(params);req=urllib.request.Request(url,headers={'User-Agent':UA})
 for n in range(6):
  try:
   with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
  except Exception:
   if n==5:raise
   time.sleep(5*(n+1))
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 groups=[('politician',POLITICIANS),('animal',ANIMALS)]; all_titles=[t for _,g in groups for _,t in g]
 pages=api(WIKI,{'action':'query','titles':'|'.join(all_titles),'prop':'pageimages','piprop':'name','redirects':1,'format':'json'})['query']['pages'].values()
 title_images={p['title']:p['pageimage'] for p in pages if p.get('pageimage')}
 missing_titles=[t for t in all_titles if t not in title_images]
 file_titles=['File:'+title_images[t].replace('_',' ') for t in title_images]
 infos=api(COMMONS,{'action':'query','titles':'|'.join(file_titles),'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':1000,'format':'json'})['query']['pages'].values()
 file_info={p['title'].replace('_',' '):p.get('imageinfo',[{}])[0] for p in infos}
 metadata={};success=0
 for kind,rows in groups:
  for key,title in rows:
   if title not in title_images:
    metadata[key]={'kind':kind,'title':title,'status':'No Wikipedia lead image'};continue
   fn='File:'+title_images[title].replace('_',' ');info=file_info.get(fn,{})
   if not info or not info.get('thumburl'):
    metadata[key]={'kind':kind,'title':title,'file':fn,'status':'No Commons image metadata'};continue
   ext=info.get('extmetadata',{});lic=plain(ext.get('LicenseShortName',{}).get('value',''))
   if not (lic.startswith(('CC BY','CC-BY','CC BY-SA','CC-BY-SA')) or lic in {'CC0','CC Zero','Public domain'}):
    metadata[key]={'kind':kind,'title':title,'file':fn,'license':lic,'status':'License excluded; needs manual review'};continue
   url=info['thumburl'].replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/')
   req=urllib.request.Request(url,headers={'User-Agent':UA,'Referer':'https://commons.wikimedia.org/'})
   try:
    with urllib.request.urlopen(req,timeout=45) as r:data=r.read()
   except urllib.error.HTTPError as e:
    metadata[key]={'kind':kind,'title':title,'file':fn,'license':lic,'status':f'download failed: {e.code}'};continue
   suffix=Path(urllib.parse.urlparse(url).path).suffix.lower()
   if suffix not in {'.jpg','.jpeg','.png','.webp'}:suffix='.jpg'
   path=OUT/(key+suffix);path.write_bytes(data);success+=1
   metadata[key]={'kind':kind,'title':title,'candidate':path.relative_to(ROOT).as_posix(),'commonsFile':fn,
    'source':'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(fn.replace(' ','_'),safe=':()_,-'),
    'downloadedFrom':url,'license':lic,'licenseUrl':plain(ext.get('LicenseUrl',{}).get('value','')),
    'creator':plain(ext.get('Artist',{}).get('value','')),'credit':plain(ext.get('Credit',{}).get('value','')),
    'bytes':len(data),'width':info.get('thumbwidth'),'height':info.get('thumbheight'),'review':'Pending visual inspection'}
   print('OK',kind,key,lic,len(data));time.sleep(.4)
 (OUT/'candidate-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'downloaded':success,'requested':len(all_titles),'missingWikipediaPages':missing_titles,'output':str(OUT)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
