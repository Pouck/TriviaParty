import urllib.request,json
for url in ['https://sfxmint.com/api/v1/roles/bell','https://sfxmint.com/api/v1/sounds/wolf-howl-02']:
 try:
  with urllib.request.urlopen(url,timeout=15) as r: print(url, r.read().decode()[:2200])
 except Exception as e:print(type(e).__name__,e)
