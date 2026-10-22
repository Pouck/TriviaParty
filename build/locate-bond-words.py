from pathlib import Path
import subprocess,json,sys
sys.stdout.reconfigure(encoding='utf8');R=Path.cwd();D=R/'build/classic-audio';W=R/'build/movie-audition'
for id in ['bond-perfect','bond-congratulations']:
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(D/'sources'/(id+'.wav')),'-l','en','-nt','-oj','-ml','1','-of',str(D/'sources'/(id+'-words')),'-t','4'],check=True,capture_output=True)
 j=json.loads((D/'sources'/(id+'-words.json')).read_text(encoding='utf8'))
 for s in j['transcription']:
  if any(x in s['text'].lower() for x in ['perfect','cheers','well','done','congrat','thank']):print(id,s['offsets'],s['text'])
