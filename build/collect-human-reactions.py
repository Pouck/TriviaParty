"""Collect a provenance-checked bank of real spoken expressions (not film dialogue)."""
import concurrent.futures,html,json,re,sys,time,urllib.parse,urllib.request,urllib.error,subprocess,hashlib,collections,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'audio-bank';CACHE=ROOT/'build/human-audio-cache';OUT.mkdir(exist_ok=True);CACHE.mkdir(exist_ok=True)
UA={'User-Agent':'TriviaPartyAudioBot/1.0 (+https://github.com/Pouck)'}
WORDS={
'fr':{'good':['bravo','excellent','parfait','super','magnifique','formidable','fantastique','génial','exact','correct','oui','félicitations','superbe','bien','réussi','incroyable','merveilleux'],
'bad':['non','faux','incorrect','dommage','raté','perdu','erreur','impossible','désolé','presque','malheureusement','échec','zut','aïe','recommencez','hélas']},
'en':{'good':['excellent','brilliant','correct','yes','perfect','wonderful','amazing','fantastic','great','congratulations','well done'],
'bad':['no','wrong','incorrect','oops','unfortunately','sorry','try again','not quite','almost','nope']},
'es':{'good':['bravo','excelente','perfecto','sí','bien','fantástico'], 'bad':['no','incorrecto','mal','error','lástima']},
'de':{'good':['ausgezeichnet','wunderbar','richtig','ja','prima','super'], 'bad':['nein','falsch','leider','schade','Fehler']}}
CODES={'fr':('Q150','fra'),'en':('Q1860','eng'),'es':('Q1321','spa'),'de':('Q188','deu')}
request_lock=threading.Lock()
def fetch(url):
 for attempt in range(6):
  try:
   with request_lock:
    time.sleep(.9)
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=35) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code==429:
    time.sleep(min(45,int(e.headers.get('Retry-After','15'))+attempt*5))
   elif attempt==5:raise
   else:time.sleep(2+attempt*3)
  except Exception:
   if attempt==5:raise
   time.sleep(2+attempt*3)
 raise RuntimeError('Source request remained unavailable: '+url)

def api(params):return json.loads(fetch('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','format':'json',**params})))
def plain(s):return html.unescape(re.sub('<[^>]+>',' ',s)).strip()
def search(task):
 language,outcome,word=task;key=hashlib.sha256(('v2'+repr(task)).encode()).hexdigest()[:16];cache=CACHE/(key+'.json')
 if cache.exists():return json.loads(cache.read_text(encoding='utf8'))
 qid,iso=CODES[language]
 query='intitle:"'+word+'" intitle:"('+iso+')" filetype:audio'
 d=api({'list':'search','srnamespace':6,'srlimit':50,'srsearch':query});titles=[]
 for item in d.get('query',{}).get('search',[]):
  title=item['title'];stem=title.rsplit('.',1)[0]
  if not(title.startswith('File:LL-'+qid+' ('+iso+')-') or title.lower().startswith('file:'+language+'-')):continue
  tail=stem.casefold()
  # Reject compound words, personal names and verb forms that differ from the intended reaction.
  suffix='-'+word.casefold()
  if not(tail.endswith(suffix) or tail.endswith(suffix+'!') or tail.endswith(suffix+' (adjectif)')):continue
  titles.append(title)
 results=[]
 if titles:
  data=api({'prop':'imageinfo','titles':'|'.join(titles),'iiprop':'url|extmetadata|size'})
  for page in data.get('query',{}).get('pages',{}).values():
   info=page.get('imageinfo',[{}])[0];m=info.get('extmetadata',{});v=lambda k:plain(str(m.get(k,{}).get('value','')))
   license=v('LicenseShortName');license_url=v('LicenseUrl')
   if license not in ['CC BY-SA 4.0','CC BY-SA 3.0','CC BY 4.0','CC BY 3.0','CC0'] or v('Restrictions'):continue
   title=page['title'];speaker=title.split(')-',1)[-1].rsplit('-'+word,1)[0] if title.startswith('File:LL-') else v('Artist')
   speaker_match=re.search(r'Speaker:\s*(.*?)\s*Recorder:',v('Artist'),re.S)
   if speaker_match:speaker=speaker_match.group(1)
   speaker=' '.join(plain(speaker).split());results.append({'language':language,'outcome':outcome,'text':word,'speaker':speaker,'voice':speaker,'sourceTitle':title,'sourceUrl':info.get('descriptionurl'),'downloadUrl':info.get('url'),'license':license,'licenseUrl':license_url,'attribution':v('Artist'),'sourceType':'human_pronunciation','film':None})
 cache.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8');return results
if __name__=='__main__':
 tasks=[(lang,outcome,word) for lang,groups in WORDS.items() for outcome,words in groups.items() for word in words]
 candidates=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for batch in pool.map(search,tasks):candidates.extend(batch)
 (OUT/'CANDIDATES.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding='utf8')
 print('Eligible source recordings:',len(candidates));print(collections.Counter((r['language'],r['outcome']) for r in candidates))
