import json,html,re
from pathlib import Path
for k in ['kiev','william-tell']:
 j=json.loads(Path('build/winner-music/'+k+'-search.json').read_text(encoding='utf8'))
 for p in j['query']['pages'].values():
  if ('Mussorgsky - pictures' in p['title']) or ('military band' in p['title']):
   print(p['title']);m=p['imageinfo'][0]['extmetadata']
   for field in ['Artist','ImageDescription','Credit','LicenseShortName']:print(field,html.unescape(re.sub('<.*?>',' ',m.get(field,{}).get('value','')))[:650])
