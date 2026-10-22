from pathlib import Path
import re,json,urllib.request,html,sys,subprocess,wave,hashlib,concurrent.futures
sys.stdout.reconfigure(encoding='utf8');R=Path.cwd();D=R/'build/classic-audio';S=D/'sources';S.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
cat=json.loads((D/'extended-catalog.json').read_text(encoding='utf8'));by={q['url'].split('/')[-1]:q for row in cat for q in row.get('quotes',[])}
# Source excerpts are kept separate from the installed bank until listening review.
choices=[('511026','good','Louis de Funès','strong'),('436870','good','Jean Rochefort','strong'),('446173','good','Philippe Noiret','strong'),('431601','good','Gérard Depardieu','strong'),('376973','good','Brigitte Bardot','strong'),('443401','good','Catherine Deneuve','edit_needed'),('447602','good','Bourvil','optional'),('393469','bad','Bourvil','strong'),('444082','bad','Jean Gabin','strong'),('430309','bad','Jean-Paul Belmondo','strong'),('449469','bad','Isabelle Adjani','optional'),('429856','good','Annie Girardot','edit_needed'),('396735','bad','Pierre Richard','edit_needed'),('511412','bad','Michel Serrault','speaker_check'),('434148','bad','Daniel Auteuil','edit_needed'),('447131','bad','Bernard Blier','speaker_check'),('449576','bad','Lino Ventura','speaker_check')]
rows=[]
for id,outcome,actor,priority in choices:
 q=by[id];p=D/(id+'.html')
 if not p.exists():p.write_bytes(urllib.request.urlopen(q['url'],timeout=25).read())
 s=p.read_text(encoding='utf8');audio=re.search(r'<audio[^>]+src="([^"]+)"',s)
 title=html.unescape(re.sub('<.*?>','',re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S).group(1))).strip()
 m=re.search(r'<h1.*?</h1>.*?(?=<audio)',s,re.S);credit=html.unescape(re.sub('<.*?>',' ',m.group(0)));credit=re.sub(r'\s+',' ',credit).strip()
 # Breadcrumb immediately before the individual numbered page identifies the film.
 links=re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',s,re.S)
 film=next((html.unescape(re.sub('<.*?>','',t)).strip() for u,t in links if u.rstrip('/')==q['url'].replace('https://zonesons.com','').rsplit('/',1)[0]),'')
 rows.append(dict(id='classic-'+id,file='classic-'+id+'.wav',outcome=outcome,language='fr',film=film,requestedActor=actor,sourceCredit=credit.split('—',1)[-1].strip(),text=title,sourceUrl=q['url'],downloadUrl='https://zonesons.com'+html.unescape(audio.group(1)),priority=priority,audience='unreviewed',status='audition_only',usage='Private audition only; no redistribution permission asserted'))
for name,outcome,actor,film in [('bond-perfect','good','Sean Connery','You Only Live Twice (1967)'),('bond-shocking','bad','Sean Connery','Goldfinger (1964)'),('bond-congratulations','good','Bernard Lee','The Man with the Golden Gun (1974)')]:
 s=(D/(name+'.html')).read_text(encoding='utf8');url=re.search(r'<link rel="canonical" href="([^"]+)"',s)
 video=re.search(r'<source src="([^"]+)" type="video/mp4"',s).group(1)
 rows.append(dict(id=name,file=name+'.wav',outcome=outcome,language='en',film=film,requestedActor=actor,sourceCredit=actor,text={'bond-perfect':'Perfect. Cheers.','bond-shocking':'Shocking! Positively shocking!','bond-congratulations':'Well done. Congratulations.'}[name],sourceUrl=url.group(1) if url else video.rsplit('/videos',1)[0],downloadUrl=video,priority='edit_needed',audience='unreviewed',status='audition_only',usage='Private audition only; no redistribution permission asserted'))
(D/'plan.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
def fetch(r):
 try:
  src=S/(r['id']+'.source')
  if not src.exists():src.write_bytes(urllib.request.urlopen(urllib.request.Request(r['downloadUrl'],headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read())
  wav=S/(r['id']+'.wav')
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(src),'-ar','16000','-ac','1',str(wav)],check=True,capture_output=True)
  with wave.open(str(wav)) as w:r['sourceDurationSeconds']=round(w.getnframes()/w.getframerate(),3)
  prefix=S/r['id']
  subprocess.run([str(R/'build/movie-audition/whisper-bin/Release/whisper-cli.exe'),'-m',str(R/'build/movie-audition/ggml-base.bin'),'-f',str(wav),'-l',r['language'],'-nt','-otxt','-oj','-of',str(prefix),'-t','4'],check=True,capture_output=True)
  r['transcript']=(S/(r['id']+'.txt')).read_text(encoding='utf8').strip();print(r['id'],r['sourceDurationSeconds'],r['transcript'],flush=True)
 except Exception as e:r['status']='unavailable';r['error']=str(e);print(r['id'],str(e),flush=True)
 return r
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=2).map(fetch,rows));(D/'audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
