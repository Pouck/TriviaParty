"""Cache freely licensed Wikimedia photographs and their attribution metadata."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, urllib.request, urllib.parse, html, re, time

OUT=Path('package-examples/arts-2026-10-11')
IMAGES=OUT/'assets';IMAGES.mkdir(parents=True,exist_ok=True)
SITES={
 'joconde':'Mona Lisa','naissance':'The Birth of Venus','menines':'Las Meninas','perle':'Girl with a Pearl Earring',
 'ronde':'The Night Watch','impression':'Impression, Sunrise','nuit':'The Starry Night','vague':'The Great Wave off Kanagawa',
 'david':'David (Michelangelo)','venus':'Venus de Milo','victoire':'Winged Victory of Samothrace','penseur':'The Thinker',
 'cene':'The Last Supper (Leonardo)','gothic':'American Gothic','liberte':'Liberty Leading the People','radeau':'The Raft of the Medusa',
 'baiser':'The Kiss (Klimt)','cri':'The Scream','olympia':'Olympia (Manet)','galette':'Bal du moulin de la Galette',
 'discobole':'Discobolus','laocoon':'Laocoon and His Sons','pieta':'Pietà (Michelangelo)','danseuse':'Little Dancer of Fourteen Years'
}
OVERRIDES={}
def get(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TriviaParty/1.0 (educational quiz; attribution retained)'}),timeout=45) as response:return response.read()
  except Exception:
   if attempt==3:raise
   time.sleep(5*(attempt+1))
def api(host,params):return json.loads(get('https://'+host+'/w/api.php?'+urllib.parse.urlencode(dict(action='query',format='json',**params))))
def plain(value):return html.unescape(re.sub('<[^>]+>','',value)).strip()
def download(item):
 slug,title=item;meta=IMAGES/(slug+'.json')
 if meta.exists():
  cached=json.loads(meta.read_text(encoding='utf-8'))
  if slug not in OVERRIDES or urllib.parse.unquote(cached['commons'].split('File:',1)[1]).replace('_',' ')==OVERRIDES[slug]:return cached
 if slug in OVERRIDES:filename=OVERRIDES[slug]
 else:
  page=next(iter(api('en.wikipedia.org',dict(prop='pageimages',titles=title,redirects=1,pithumbsize=1600))['query']['pages'].values()))
  filename=page['pageimage']
 info=next(iter(api('commons.wikimedia.org',dict(prop='imageinfo',titles='File:'+filename,iiprop='url|extmetadata',iiurlwidth=1600))['query']['pages'].values()))['imageinfo'][0]
 ext=info['extmetadata'];license=plain(ext.get('LicenseShortName',{}).get('value',''))
 assert 'CC' in license or 'Public domain' in license, (filename,license)
 image=get(info.get('thumburl',info['url']))
 assert image.startswith(b'\xff\xd8') or image.startswith(b'\x89PNG') or image[0:4]==b'RIFF',filename
 suffix='.jpg' if image.startswith(b'\xff\xd8') else '.png' if image.startswith(b'\x89PNG') else '.webp'
 target=IMAGES/(slug+suffix);target.write_bytes(image)
 record=dict(slug=slug,title=title,file=target.name,commons=info['descriptionurl'],download=info.get('thumburl',info['url']),artist=plain(ext.get('Artist',{}).get('value','')),license=license,licenseUrl=ext.get('LicenseUrl',{}).get('value',''),credit=plain(ext.get('Credit',{}).get('value','')),changes='Aucune modification ; miniature Wikimedia.')
 meta.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(slug,license,len(image),flush=True)
 return record
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=1) as pool:records=list(pool.map(download,SITES.items()))
 (OUT/'PHOTOS.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (OUT/'PHOTOS.md').write_text('# Crédits photographiques\n\nPhotographies Wikimedia Commons intégrées aux archives pour utilisation hors ligne. Aucun recadrage ni retouche. Les miniatures sont fournies par Wikimedia.\n\n'+'\n\n'.join(f"## {r['title']}\n\n[{r['file']}]({r['commons']}) — {r['artist']} — [{r['license']}]({r['licenseUrl'] or r['commons']}).\n\n{r['changes']}" for r in records)+'\n',encoding='utf-8')
 print('Cached and attributed',len(records),'photographs.')
