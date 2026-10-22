from pathlib import Path
import urllib.request,time
p=Path('build/movie-audition/ggml-small.bin')
if not p.exists():
 req=urllib.request.Request('https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin',headers={'User-Agent':'TriviaPartyAudioTools/1.0'})
 with urllib.request.urlopen(req,timeout=45) as r, p.with_suffix('.download').open('wb') as out:
  while chunk:=r.read(1024*1024):out.write(chunk)
 p.with_suffix('.download').replace(p)
print('Downloaded multilingual speech model:',p.stat().st_size,'bytes',flush=True)
