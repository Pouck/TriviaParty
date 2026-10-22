from pathlib import Path
import sys,subprocess,json,concurrent.futures
R=Path.cwd();D=R/'build/dialogue-extracts/vadrouille-tea-for-two';W=R/'build/movie-audition';sys.stdout.reconfigure(encoding='utf8')
def run(config):
 name,model,lang=config;prefix=D/('transcript-'+name)
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/model),'-f',str(D/'source-16k.wav'),'-l',lang,'-otxt','-oj','-of',str(prefix),'-t','4'],check=True,capture_output=True)
 print(name,flush=True)
 for s in json.loads(prefix.with_suffix('.json').read_text(encoding='utf8'))['transcription']:print(s['offsets'],s['text'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[('french','ggml-small.bin','fr'),('english-base','ggml-base.bin','en')]))
