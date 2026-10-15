"""Second offline speech check for caption mismatches and safe edit points."""
from pathlib import Path
import json,subprocess,sys
sys.stdout.reconfigure(encoding='utf8')
D=Path(__file__).resolve().parents[1]/'build/movie-audition';C=D/'expanded-sources';O=D/'speech-check';O.mkdir(exist_ok=True)
rows=json.loads((D/'expanded-audit.json').read_text(encoding='utf8'));out=[]
for i,r in enumerate(rows):
 name=r['file'];target=O/name
 if not target.with_suffix(target.suffix+'.txt').exists():
  subprocess.run([str(D/'whisper-bin/Release/whisper-cli.exe'),'-m',str(D/'ggml-small.bin'),'-f',str(C/(name+'.wav')),'-l',r['language'],'-nt','-otxt','-ojf','-ml','50','-sow','-of',str(target),'-d','16000','-t','4'],check=True,capture_output=True)
 text=target.with_suffix(target.suffix+'.txt').read_text(encoding='utf8').strip()
 out.append(dict(file=name,language=r['language'],text=text))
 (D/'verified-transcripts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'{i+1}/60 {name}: {text[:230]}',flush=True)
