from __future__ import annotations
import json, pathlib, re, time, urllib.parse, urllib.request
root=pathlib.Path(__file__).resolve().parents[1]
queries={
'1cc9204eb170bf97dcc0f0e2':'single sperm whale full body underwater clear side view',
'21d6b549c29587d765d12429':'Mont Blanc mountain summit French Alps clear recognizable peak',
'aed7637f488619c12fa97055':'Walden Pond Massachusetts recognizable pond shoreline Thoreau cabin',
'2a65c03d10e17393c0c48c53':'Naruto Uzumaki official portrait single character high resolution color',
'3ab20facd9aa97e9dc25897d':'Sakura Haruno official portrait single character high resolution color',
'f0e880d4910cd046ce6a6cd2':'Aladdin Disney official animation single character',
'11ae8097d9021d27e5625c56':'Goofy Disney official animation single character',
'86eb08054addcc2881e3f5d1':'Mickey Mouse Disney official animation single character',
'd8c5d1c0bd99862057f6ac6a':'Stitch Disney official animation single character',
'e5529eb90f0feccd9d129802':'Bo Peep Toy Story official animation single character',
'bcb256c0af4353edddac0588':'Joy Inside Out official animation single character',
'164961ce1a1455f433fac6d2':'Mr Incredible official Pixar animation single character',
'6df2c3d087af93c5a870246c':'Cleopatra sculpture bust museum photograph',
'4bb7e80557667fc0b727942d':'Julius Caesar bust museum photograph',
'63ccb87c6e754b35c8a1961d':'aurora borealis sky photograph no text landscape',
}
out=root/'build/image-qsj-sampler/candidates/latest-review-2026-10-28-round2';out.mkdir(parents=True,exist_ok=True);rows=[]
for ident,q in queries.items():
 params={'action':'query','generator':'search','gsrsearch':'filetype:bitmap '+q,'gsrnamespace':6,'gsrlimit':4,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':700,'format':'json'}
 url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={'User-Agent':'TriviaPartyImageReview/1.0 (local private game review)'})
 try:
  with urllib.request.urlopen(req,timeout=30) as res:doc=json.load(res)
  pages=sorted((doc.get('query',{}).get('pages',{}) or {}).values(),key=lambda x:x.get('index',999))[:3]
  for rank,page in enumerate(pages,1):
   info=(page.get('imageinfo') or [{}])[0]; thumb=info.get('thumburl') or info.get('url')
   if not thumb:continue
   ext=pathlib.Path(urllib.parse.urlparse(thumb).path).suffix or '.jpg'; dest=out/f'{ident}-{rank}{ext}'
   rq=urllib.request.Request(thumb,headers={'User-Agent':'TriviaPartyImageReview/1.0'})
   with urllib.request.urlopen(rq,timeout=45) as res:dest.write_bytes(res.read())
   meta=info.get('extmetadata',{})
   def val(k):return re.sub('<[^>]+>',' ',meta.get(k,{}).get('value','')).strip()
   rows.append({'imageId':ident,'query':q,'rank':rank,'file':str(dest.relative_to(root)),'title':page.get('title',''),'artist':val('Artist'),'license':val('LicenseShortName'),'licenseUrl':val('LicenseUrl'),'source':info.get('descriptionurl')})
  print(ident,len(pages))
 except Exception as e:print(ident,'ERROR',e)
 time.sleep(.35)
(out/'candidate-metadata.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('total',len(rows),'directory',out)
