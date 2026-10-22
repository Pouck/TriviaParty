import sys,json,subprocess
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'build/audio-download-tools'));sys.path.insert(0,str(R/'build/audio-tools'));import yt_dlp,imageio_ffmpeg
D=R/'build/classic-audio/alternate-sources';src=next(p for p in D.glob('bourvil-corniaud.*') if p.suffix not in ['.json','.part']);wav=D/'bourvil-full.wav'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-loglevel','error','-i',str(src),'-ar','16000','-ac','1',str(wav)],check=True,capture_output=True)
W=R/'build/movie-audition';subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(wav),'-l','fr','-otxt','-oj','-of',str(D/'bourvil-transcript'),'-t','4'],check=True,capture_output=True)
print((D/'bourvil-transcript.txt').read_text(encoding='utf8'),flush=True)
queries=['Carambolages Louis de Funes vous etes formidable','Alexandre le bienheureux il faut feter ca','Le retour du grand blond Rochefort vous m avez cueilli']
results=[]
with yt_dlp.YoutubeDL({'quiet':True,'extract_flat':True,'socket_timeout':15,'retries':0}) as y:
 for q in queries:
  try:
   info=y.extract_info('ytsearch3:'+q,download=False);entries=[{k:e.get(k) for k in ['id','title','url','duration','channel']} for e in info['entries']];results.append({'query':q,'entries':entries});print(q,json.dumps(entries,ensure_ascii=True),flush=True)
  except Exception as e:print(str(e)[:150])
(D/'quote-search-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
