from pathlib import Path
import re,json,sys,urllib.request
sys.stdout.reconfigure(encoding='utf8');D=Path('build/classic-audio')
ids=['511026','436870','466573','446173','431601','449469','429856','443401','376973','430309','444082','393469','447602','396735']
cat=json.loads((D/'extended-catalog.json').read_text(encoding='utf8'));by={q['url'].split('/')[-1]:q for r in cat for q in r.get('quotes',[])}
for id in ids:
 q=by[id];p=D/(id+'.html')
 if not p.exists():p.write_bytes(urllib.request.urlopen(q['url'],timeout=20).read())
 s=p.read_text(encoding='utf8'); m=re.search(r'<h1.*?</h1>.*?(?=<audio)',s,re.S)
 plain=re.sub('<.*?>',' ',m.group(0) if m else '')
 print(id,re.sub(r'\s+',' ',plain)[:450])
