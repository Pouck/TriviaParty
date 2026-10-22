from pathlib import Path
import subprocess,sys,json,concurrent.futures
R=Path.cwd();D=R/'build/dialogue-extracts/X1PiR7WfuWs';W=R/'build/movie-audition';sys.stdout.reconfigure(encoding='utf8')
items=[('context',D/'short-context.wav')]+[(p.stem.replace('-draft',''),p) for p in (D/'clips').glob('*-draft.wav')]
def run(item):
 id,wav=item;prefix=D/'clips'/(id+'-small')
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(wav),'-l','fr','-otxt','-oj','-of',str(prefix),'-t','4'],check=True,capture_output=True)
 print(id,(prefix.with_suffix('.txt')).read_text(encoding='utf8').strip(),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,items))
