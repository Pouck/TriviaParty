import urllib.request,re,json,html,sys,concurrent.futures
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8');D=Path('build/classic-audio');D.mkdir(exist_ok=True)
actors=['bourvil','jean-gabin','lino-ventura','louis-de-funes','jean-paul-belmondo','philippe-noiret','brigitte-bardot','francoise-fabian','annie-girardot','jeanne-moreau','romy-schneider','daniel-auteuil','bernard-blier','gerard-depardieu','pierre-richard','jean-rochefort','michel-serrault','isabelle-adjani','emmanuelle-beart','juliette-binoche','sandrine-bonnaire','carole-bouquet','catherine-deneuve']
def fetch(a):
 try:
  p=D/(a+'.html')
  if not p.exists():p.write_bytes(urllib.request.urlopen('https://zonesons.com/'+a,timeout=25).read())
  s=p.read_text(encoding='utf8');links=[]
  for u,t in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',s,re.S):
   t=html.unescape(re.sub('<.*?>','',t)).strip()
   if re.search(r'/\d+$',u):links.append({'url':'https://zonesons.com'+u if u.startswith('/') else u,'text':t})
  return {'actor':a,'quotes':links,'pagination':list(set(re.findall(r'href="([^"]*(?:page=|/'+a+r'/)[^"]*)"',s)))}
 except Exception as e:return {'actor':a,'error':str(e)}
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(fetch,actors));(D/'actor-catalog.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
for r in results:print(r['actor'],len(r.get('quotes',[])),r.get('error',''),r.get('pagination',[])[:3]);print(' | '.join(q['text'] for q in r.get('quotes',[])[:12]))
