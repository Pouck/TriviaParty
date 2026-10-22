import urllib.request,re,json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8');D=Path('build/classic-audio')
urls={'bond-perfect':'https://clip.cafe/you-only-live-twice-1967/oh-thats-stirred-not-shaken-that-right/','bond-shocking':'https://clip.cafe/goldfinger-1964/positively-shocking/','bond-congratulations':'https://clip.cafe/the-man-with-the-golden-gun-1974/whats-the-matter-s422/'}
for name,u in urls.items():
 try:
  s=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode();(D/(name+'.html')).write_text(s,encoding='utf8')
  print(name,json.dumps(re.findall(r'<source[^>]+>|<video[^>]+>|"contentUrl"\s*:\s*"[^"]+"',s)[:10]))
 except Exception as e:print(name,str(e))
rows=json.loads((D/'extended-catalog.json').read_text(encoding='utf8'))
for r in rows:
 if r['actor'] in ['lino-ventura','bernard-blier','daniel-auteuil']:
  for q in r.get('quotes',[]):
   if 'sais' in q['text'] or 'compris' in q['text'] or 'Réfléchis' in q['text'] or 'C’est' in q['text'] or 'C\'est' in q['text']:print(r['actor'],q['url'],q['text'][:160])
