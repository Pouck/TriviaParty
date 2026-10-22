import urllib.request,http.cookiejar,json
from pathlib import Path
r=json.loads(Path('build/classic-audio/plan.json').read_text(encoding='utf8'))[0]
op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
for url in [r['sourceUrl'],r['downloadUrl']]:
 try:
  res=op.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':r['sourceUrl']}),timeout=20);print(res.status,res.headers.get('Content-Type'),len(res.read()))
 except urllib.error.HTTPError as e:print(e.code,e.read(350).decode(errors='replace'))
