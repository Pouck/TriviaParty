"""Build a 100-clip human voice bank, keeping every source and license."""
import collections,concurrent.futures,hashlib,html,json,re,subprocess,sys,urllib.request,urllib.error,urllib.parse,wave,time,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BANK=ROOT/'audio-bank';CACHE=ROOT/'build/human-audio-cache'
sys.path.insert(0,str(ROOT/'build/audio-tools'))
import imageio_ffmpeg
FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
TARGET=BANK/'clips';TARGET.mkdir(exist_ok=True)
rows=json.loads((BANK/'CANDIDATES.json').read_text(encoding='utf8'))
import zipfile
pack=CACHE/'game-voice.zip'
if pack.exists():
    clips=[('G VICTORY.wav','good','Victory'),('GF VICTORY.wav','good','Victory'),('GC DISSAPOINITING.wav','bad','Well, that was disappointing'),('GC I DIDNT SEE THAT HAPPENING.wav','bad',"I didn't see that happening"),('GC THATS GOTTA HURT.wav','bad',"That's gotta hurt")]
    with zipfile.ZipFile(pack) as archive:
        for name,outcome,text in clips:
            local=CACHE/name;local.write_bytes(archive.read(name))
            rows.append({'language':'en','outcome':outcome,'text':text,'speaker':'Tim Rockk','voice':'Tim Rockk','sourceTitle':name,'sourceUrl':'https://opengameart.org/content/game-voice','downloadUrl':'https://opengameart.org/sites/default/files/all_game_voice_audio_files_0.zip','localSource':str(local),'license':'CC0','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/','attribution':'Tim Rockk, game voice, OpenGameArt.org; CC0','sourceType':'human_acted_game','film':None})

quotas={('fr','good'):35,('fr','bad'):35,('en','good'):10,('en','bad'):10,('es','good'):3,('es','bad'):2,('de','good'):2,('de','bad'):3}
selected=[];speaker_counts=collections.Counter();text_counts=collections.Counter()
for key,count in quotas.items():
 pool=[r for r in rows if (r['language'],r['outcome'])==key]
 if len(pool)<count:raise SystemExit(f'Need {count} recordings for {key}, found {len(pool)}')
 for _ in range(count):
  pool.sort(key=lambda r:(0 if r['sourceType']=='human_acted_game' else 1,text_counts[(r['language'],r['outcome'],r['text'])],speaker_counts[r['speaker']],r['sourceTitle']))
  r=dict(pool.pop(0));selected.append(r);text_counts[(r['language'],r['outcome'],r['text'])]+=1;speaker_counts[r['speaker']]+=1
# Use official compressed derivatives advertised by Wikimedia, not oversized originals.
wiki=[r for r in selected if r['sourceType']=='human_pronunciation']
derivative_cache=CACHE/'official-derivatives.json'
known=json.loads(derivative_cache.read_text(encoding='utf8')) if derivative_cache.exists() else {}
for offset in range(0,len(wiki),20):
    batch=wiki[offset:offset+20]
    if all(r['sourceTitle'] in known for r in batch):
        for r in batch:r['originalDownloadUrl']=r['downloadUrl'];r['downloadUrl']=known[r['sourceTitle']]
        continue
    params={'action':'query','format':'json','prop':'videoinfo','titles':'|'.join(r['sourceTitle'] for r in batch),'viprop':'derivatives'}
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TriviaPartyAudioBot/1.0 (+https://github.com/Pouck)'}),timeout=30) as response:pages=json.load(response)['query']['pages']
    by_title={p['title']:p for p in pages.values()}
    for r in batch:
        derivatives=by_title[r['sourceTitle']].get('videoinfo',[{}])[0].get('derivatives',[])
        audio=next((d for d in derivatives if d.get('transcodekey')=='ogg'),None)
        if audio is None:audio=next((d for d in derivatives if d.get('transcodekey')=='mp3'),None)
        if audio is None:raise RuntimeError('No official compressed derivative for '+r['sourceTitle'])
        r['originalDownloadUrl']=r['downloadUrl'];r['downloadUrl']=audio['src'];known[r['sourceTitle']]=audio['src']
    time.sleep(1)
derivative_cache.write_text(json.dumps(known,ensure_ascii=False),encoding='utf8')
request_lock=threading.Lock()
indices=collections.Counter()
for r in selected:
 indices[r['outcome']]+=1;r['file']=f"{r['outcome']}-{indices[r['outcome']]:02}.wav";r['leadInMs']=220;r['changes']='Trimmed boundary silence, 220 ms silent lead-in, loudness normalization, mono PCM 44.1 kHz; original speech and language retained.'
def prepare(r):
 cache=Path(r['localSource']) if r.get('localSource') else CACHE/(hashlib.sha256(r['downloadUrl'].encode()).hexdigest()[:20]+Path(r['sourceTitle']).suffix)
 if not cache.exists():
  for attempt in range(5):
   try:
    with request_lock, urllib.request.urlopen(urllib.request.Request(r['downloadUrl'],headers={'User-Agent':'TriviaPartyAudioBot/1.0 (+https://github.com/Pouck)'}),timeout=40) as res:
     cache.write_bytes(res.read())
     time.sleep(1.2)
    break
   except urllib.error.HTTPError as e:
    if "robot policy" in str(e).lower() or attempt==4:raise
    time.sleep(min(30,int(e.headers.get('Retry-After','10'))))
   except Exception:
    if attempt==4:raise
    time.sleep(2+attempt*2)
 dest=TARGET/r['file']
 filters='silenceremove=start_periods=1:start_duration=0.03:start_threshold=-48dB:stop_periods=0,adelay=220:all=1,loudnorm=I=-16:TP=-2:LRA=8'
 subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(cache),'-af',filters,'-ar','44100','-ac','1','-c:a','pcm_s16le',str(dest)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 with wave.open(str(dest),'rb') as w:r['durationSeconds']=round(w.getnframes()/w.getframerate(),3)
 assert .3<r['durationSeconds']<4.5,(r['sourceTitle'],r['durationSeconds'])
 r.pop('localSource',None)
 r['sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();r['status']='technical_checks_passed_audition_available';return r
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 records=[]
 for index,r in enumerate(pool.map(prepare,selected),1):
  records.append(r)
  if index%10==0:print(f'Prepared {index}/100 recordings',flush=True)
records.sort(key=lambda r:r['file'])
(BANK/'reactions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# Audio attribution and licenses','', 'These are original-language human recordings: pronunciation expressions plus five acted English game reactions. They are not film excerpts or synthetic/impersonated voices. Converted files retain their source license. Changes: boundary silence trimming, 220 ms lead-in, mono 44.1 kHz PCM and loudness normalization.','']
for r in records:
 lines+=['## '+r['file'],'',r['text']+' — '+r['language']+' — '+r['speaker'],'',r['attribution'],'','Source: '+r['sourceUrl'],'','License: '+r['license']+' — '+r['licenseUrl'],'']
(BANK/'ATTRIBUTION.md').write_text(chr(10).join(lines),encoding='utf8')
html_rows=[]
for r in records:
 esc=html.escape
 html_rows.append('<article data-outcome="'+r['outcome']+'" data-language="'+r['language']+'"><h3>'+esc(r['text'])+'</h3><p>'+esc(r['language']+' · '+r['speaker']+' · '+r['outcome'])+'</p><audio controls preload="none" src="clips/'+r['file']+'"></audio><p><a href="'+esc(r['sourceUrl'])+'">Source</a> · <a href="'+esc(r['licenseUrl'])+'">'+esc(r['license'])+'</a></p></article>')
(BANK/'index.html').write_text('<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>100 réactions — écoute</title><style>body{background:#151521;color:#eee;font:18px system-ui;margin:28px}h1{color:#ffd56b}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}article{background:#252539;padding:18px;border-radius:12px}article[data-outcome="good"]{border-left:5px solid #69c28a}article[data-outcome="bad"]{border-left:5px solid #e87583}audio{width:100%}a{color:#8ad5ff}button,select{font:inherit;padding:10px;margin:5px}small{color:#bbb}</style><h1>100 réactions humaines</h1><p>50 bonnes réponses · 50 mauvaises · 70 français, 20 anglais, 5 espagnol, 5 allemand.</p><p>Enregistrements de vraies personnes. La banque contient des expressions de prononciation et cinq réactions anglaises jouées par un comédien. Ce ne sont pas des dialogues de films.</p><label>Langue <select id="language"><option value="">Toutes</option><option>fr</option><option>en</option><option>es</option><option>de</option></select></label><label>Résultat <select id="outcome"><option value="">Tous</option><option value="good">Bonne réponse</option><option value="bad">Mauvaise réponse</option></select></label><button id="playSample">Écouter 10 extraits</button><button id="stopSample">Arrêter</button><p id="nowPlaying"></p><audio id="sampler" controls></audio><main>'+''.join(html_rows)+'</main><script>for(const select of document.querySelectorAll("select"))select.onchange=()=>{for(const row of document.querySelectorAll("article"))row.hidden=!!((language.value&&row.dataset.language!==language.value)||(outcome.value&&row.dataset.outcome!==outcome.value));};let sample=[];const sampler=document.getElementById("sampler");function nextSample(){const row=sample.shift();if(!row)return;document.getElementById("nowPlaying").textContent=row.querySelector("h3").textContent+" · "+row.querySelector("p").textContent;sampler.src=row.querySelector("audio").getAttribute("src");sampler.play().catch(()=>{});}document.getElementById("playSample").onclick=()=>{sample=Array.from(document.querySelectorAll("article")).filter(row=>!row.hidden).sort(()=>Math.random()-.5).slice(0,10);nextSample();};document.getElementById("stopSample").onclick=()=>{sample=[];sampler.pause();};sampler.onended=nextSample;for(const audio of document.querySelectorAll("audio"))audio.onplay=()=>{for(const other of document.querySelectorAll("audio"))if(other!==audio)other.pause();};</script></html>',encoding='utf8')
print('Prepared',len(records),'clips;',len(speaker_counts),'speakers;',len(text_counts),'different language/outcome expressions.')
