import urllib.request,re,json
from pathlib import Path
for name,url in [('download','https://zonesons.com/telecharger'),('bourvil','https://www.myinstants.com/search/?name=Bourvil')]:
 try:
  s=urllib.request.urlopen(url,timeout=25).read().decode();Path('build/classic-audio/'+name+'-download-page.html').write_text(s,encoding='utf8')
  if name=='download':print(json.dumps(re.findall(r'<script[^>]*src="([^"]+)"|<script[^>]*>(.*?)</script>',s,re.S)[-12:])[:4000])
  else:print(json.dumps(re.findall(r'onmousedown="([^"]+)"|href="(/en/instant/[^"]+)"|href="(/instant/[^"]+)"|class="instant-link[^>]*>(.*?)</a>',s,re.S)[:30],ensure_ascii=True))
 except Exception as e:print(name,str(e))
