"""Fetch and locally transcribe the private audition candidates; no source media committed."""
from pathlib import Path
import sys,json,urllib.request,subprocess,wave,hashlib,re,html,time
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'build/movie-audition';CACHE=D/'expanded-sources';CACHE.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'build/audio-tools'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();WHISPER=D/'whisper-bin/Release/whisper-cli.exe';MODEL=D/'ggml-base.bin'
selection=ROOT/'audio-bank/movie-reactions-selection.json'
plan=json.loads((selection if selection.exists() else D/'expanded-plan.json').read_text(encoding='utf8'));results=[]
for n,r in enumerate(plan):
 try:
  name=r['file'];src=CACHE/(name+'.source')
  if r.get('preparedAsset'):
   prepared=(ROOT/r['preparedAsset']).resolve()
   assert prepared.is_relative_to((ROOT/'audio-bank/clips').resolve())
   assert hashlib.sha256(prepared.read_bytes()).hexdigest()==r['sha256']
   r['status']='existing_licensed_recording_verified';results.append(r)
   (D/'expanded-audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
   print(f'{n+1}/{len(plan)} {name}: existing licensed recording verified',flush=True)
   continue
  if r.get('needsFullCaption'):
   page=CACHE/(name+'.html')
   if not page.exists():page.write_bytes(urllib.request.urlopen(r['sourceUrl'],timeout=20).read())
   text=page.read_text(encoding='utf8')
   schema=re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)
   if schema:
    data=json.loads(schema.group(1));r['sourceDescription']=data.get('description','');r['downloadUrl']=data['contentUrl']
   actors=re.findall(r'href="/v/[^"]+"[^>]*>(.*?)</a>',text,re.S)
   r['voice']=' / '.join(dict.fromkeys(html.unescape(re.sub('<.*?>','',x)).strip() for x in actors)) or r['film']
  if not src.exists():
   req=urllib.request.Request(r['downloadUrl'],headers={'User-Agent':'TriviaPartyAudioPreview/1.0'})
   with urllib.request.urlopen(req,timeout=25) as response:src.write_bytes(response.read())
   time.sleep(.25)
  # Decode before trusting either the extension or a remote caption.
  full=CACHE/(name+'.wav')
  if not full.exists():subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-i',str(src),'-ar','16000','-ac','1',str(full)],check=True,capture_output=True)
  with wave.open(str(full)) as w:r['sourceDurationSeconds']=round(w.getnframes()/w.getframerate(),3)
  txt=CACHE/(name+'.txt')
  if not txt.exists():
   # Read the beginning of long scenes; keep them pending until a clean short segment is chosen.
   subprocess.run([str(WHISPER),'-m',str(MODEL),'-f',str(full),'-l',r['language'],'-nt','-otxt','-oj','-of',str(CACHE/name),'-d','16000','-t','4'],check=True,capture_output=True)
   generated=CACHE/(name+'.txt')
   assert generated.exists()
  r['transcript']=txt.read_text(encoding='utf8').strip()
  r['status']='transcribed_pending_editorial_check'
  results.append(r)
  print(f'{n+1}/{len(plan)} {name} {r["sourceDurationSeconds"]}s {r["transcript"][:130]}',flush=True)
 except Exception as error:
  r['status']='unavailable';r['error']=str(error);results.append(r);print(f'{n+1}/{len(plan)} {r["file"]} FAILED {error}',flush=True)
 (D/'expanded-audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
print('Completed source and speech audit.',flush=True)
