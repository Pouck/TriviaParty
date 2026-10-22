exec(open('build/find-classic-voices.py',encoding='utf-8-sig').read().split('results=list')[0])
base=json.loads((D/'actor-catalog.json').read_text(encoding='utf8'));jobs=[]
for r in base:
 if 'error' in r:continue
 pages=[int(n) for u in r['pagination'] for n in re.findall(r'page-(\d+)',u)]
 maxpage=max(pages,default=1)
 for n in range(2,min(maxpage,6)+1):jobs.append(r['actor']+'/page-'+str(n)+'/')
def more(a):
 try:
  p=D/(a.replace('/','_')+'.html')
  if not p.exists():p.write_bytes(urllib.request.urlopen('https://zonesons.com/'+a,timeout=25).read())
  s=p.read_text(encoding='utf8');quotes=[]
  for u,t in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',s,re.S):
   if re.search(r'/\d+$',u):quotes.append({'url':'https://zonesons.com'+u,'text':html.unescape(re.sub('<.*?>','',t)).strip()})
  return {'actor':a.split('/')[0],'page':a,'quotes':quotes}
 except Exception as e:return {'actor':a,'error':str(e)}
rows=base+list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(more,jobs));(D/'extended-catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
pattern=r'bravo|formidable|raison|gagn|bien jou|excellent|parfait|génie|imbécile|idiot|tromp|erreur|raté|compris|nul|intellig|magnifique|merveille|faux|vrai|connerie|appris|félicit|savant|recommenc|faute|rien compris|génial'
for r in rows:
 for q in r.get('quotes',[]):
  if re.search(pattern,q['text'],re.I) and len(q['text'])<205:print(r['actor'],q['url'],q['text'])
