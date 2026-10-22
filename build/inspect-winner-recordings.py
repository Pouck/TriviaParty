from pathlib import Path
import json,re,html,sys
sys.stdout.reconfigure(encoding='utf8')
for f in Path('build/winner-music').glob('*-search.json'):
 for p in json.loads(f.read_text(encoding='utf8')).get('query',{}).get('pages',{}).values():
  i=p['imageinfo'][0];m=i.get('extmetadata',{})
  def val(k):return re.sub('<.*?>',' ',html.unescape(m.get(k,{}).get('value',''))).strip()
  print(p['title'],'\n ARTIST',val('Artist')[:350],'\n DESC',val('ImageDescription')[:650],'\n LICENSE',val('LicenseShortName'),val('LicenseUrl'),'\n')
