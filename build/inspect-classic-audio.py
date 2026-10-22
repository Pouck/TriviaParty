import urllib.request,re,json
from pathlib import Path
u='https://zonesons.com/vieux-films/la-traversee-de-paris-1956/393835'
s=urllib.request.urlopen(u,timeout=25).read().decode();Path('build/classic-source-sample.html').write_text(s,encoding='utf8')
for pattern in [r'<audio.*?</audio>',r'<source[^>]+>',r'.{0,90}\\.mp3.{0,130}',r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>']:
 hits=re.findall(pattern,s,re.S)
 print(json.dumps(hits[:35],ensure_ascii=True))
