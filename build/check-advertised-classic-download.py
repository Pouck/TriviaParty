import re,base64,urllib.request
from pathlib import Path
s=Path('build/classic-audio/511026.html').read_text(encoding='utf8')
x=re.search(r'href="/telecharger#([^"]+)"',s).group(1)
u='https://zonesons.com'+base64.b64decode(x).decode()
try:
 r=urllib.request.urlopen(u,timeout=20);print(r.status,r.headers.get('content-type'),len(r.read()))
except Exception as e:print(type(e).__name__,str(e))
