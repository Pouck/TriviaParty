import json, pathlib, re, time, urllib.parse, urllib.request
root=pathlib.Path(__file__).resolve().parents[1]
review=json.loads(pathlib.Path(r'C:\Users\pierr\Downloads\qsj-image-gallery-review (1).json').read_text(encoding='utf-8'))['items']
bank=json.loads((root/'game-library/bank/questions.json').read_text(encoding='utf-8'))
# Curated search phrases keep candidates tied to the exact subject and favor clear full subjects.
queries={
 'c1f2c9466e370c200dd2184e':'Swiss Alps mountain landscape panorama',
 'b28c7c9edec934193f58c724':'European beaver portrait natural habitat',
 '2a65c03d10e17393c0c48c53':'Naruto Uzumaki official character portrait',
 'd8c5d1c0bd99862057f6ac6a':'Stitch Lilo official Disney character',
 'a8a4ca7a7a832c050aeed815':'monarch butterfly close up single butterfly',
 '984fed4911d4c6a30122b9b4':'horse full body standing pasture',
 'b6e59b4a90f53870e1739feb':'domestic pig full body adult',
 '1cc9204eb170bf97dcc0f0e2':'sperm whale full body underwater',
 '84b0e86e70eb9fb1e5da2afd':'Loki Marvel Cinematic Universe official portrait',
 'bc33a1e187245e8a19ae871d':'whale shark underwater full body diver',
 '4a4187890b0580c8b2ea862b':'Forbidden City Beijing wide exterior panorama',
 '86eb08054addcc2881e3f5d1':'Mickey Mouse single character official art',
 '11ae8097d9021d27e5625c56':'Goofy Disney single character official art',
 'bcb256c0af4353edddac0588':'Joy Inside Out single character official art',
 '201d3df3ddab5518a13bc7ba':'Ant-Man Marvel Cinematic Universe character official',
 'ef72f671ab0c46b59e9e90d5':'Deadpool Marvel cinematic character single portrait',
 'd344f8f058c096d8737399a7':'Star-Lord Peter Quill Guardians of the Galaxy portrait',
 'db06decbc64100ab81a37ddf':'Bane DC Comics character official portrait',
 '3ab20facd9aa97e9dc25897d':'Sakura Haruno official character portrait',
 'f0e880d4910cd046ce6a6cd2':'Aladdin Disney animated character portrait single',
 'e5529eb90f0feccd9d129802':'Bo Peep Toy Story single character portrait',
 '164961ce1a1455f433fac6d2':'Mr Incredible single character official portrait',
 'cd326e64992356dbc7d2d73c':'St Paul Cathedral London complete west facade exterior',
 '778aef5e60e4d89f95c4c4cf':'Palace of Versailles complete facade exterior wide',
 '377ec32b339426fe0553e788':'Rietveld Schroder House complete exterior',
 '157512497bddfe71f86c8bea':'Tokyo Skytree complete tower view',
 '754d1f595ba91382fdd204f5':'Empire State Building complete tower skyline',
 'cbc feb8d76562fc119bac3cc':'St Peters Basilica Vatican complete facade exterior',
 '0c1c9caab01612d357595fa5':'Church of Holy Sepulchre Jerusalem exterior complete',
 '43687e3fb3f2de203d8502ce':'Lloyds Building London exterior full building',
 '46ddcdca1bb47eff0128d676':'Pantheon Rome exterior complete front',
 'aed7637f488619c12fa97055':'Walden Pond Massachusetts landscape shore',
 '6df2c3d087af93c5a870246c':'Cleopatra ancient Egyptian queen bust portrait',
 '4bb7e80557667fc0b727942d':'Julius Caesar Roman bust sculpture portrait',
}
# fix typo if present
queries['cbcfeb8d76562fc119bac3cc']='St Peters Basilica Vatican complete facade exterior'
out=root/'build/image-qsj-sampler/candidates/latest-review-2026-10-27'
out.mkdir(parents=True,exist_ok=True)
results=[]
for image_id, q in queries.items():
    params={'action':'query','generator':'search','gsrsearch':'filetype:bitmap '+q,'gsrnamespace':6,'gsrlimit':5,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':700,'format':'json'}
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'User-Agent':'TriviaPartyImageReview/1.0 (local private game review)'})
    try:
        with urllib.request.urlopen(req,timeout=30) as res: doc=json.load(res)
        pages=sorted((doc.get('query',{}).get('pages',{}) or {}).values(),key=lambda x:x.get('index',999))[:3]
        for n,page in enumerate(pages,1):
            info=(page.get('imageinfo') or [{}])[0]
            thumb=info.get('thumburl') or info.get('url')
            if not thumb: continue
            ext=pathlib.Path(urllib.parse.urlparse(thumb).path).suffix or '.jpg'
            path=out/f'{image_id}-{n}{ext}'
            rq=urllib.request.Request(thumb,headers={'User-Agent':'TriviaPartyImageReview/1.0 (local private game review)'})
            with urllib.request.urlopen(rq,timeout=45) as res: path.write_bytes(res.read())
            meta=info.get('extmetadata',{})
            def val(k): return re.sub('<[^>]+>',' ',meta.get(k,{}).get('value','')).strip()
            results.append({'reviewImageId':image_id,'query':q,'rank':n,'file':str(path.relative_to(root)),'title':page.get('title',''),'description':val('ImageDescription'),'artist':val('Artist'),'license':val('LicenseShortName'),'licenseUrl':val('LicenseUrl'),'source':info.get('descriptionurl'),'downloadUrl':thumb})
        print(f'{image_id}: {len(pages)} found')
    except Exception as e:
        print(f'{image_id}: ERROR {e}')
    time.sleep(.35)
(root/'build/image-qsj-sampler/candidates/latest-review-2026-10-27/candidate-metadata.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('candidates',len(results),'out',out)
