from pathlib import Path
import sys,subprocess,json,concurrent.futures
R=Path.cwd();D=R/'build/dialogue-extracts/oscar-vole';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf8')
def run(item):
 id,start,end=item;wav=D/(id+'.wav');subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS',str(wav)],check=True,capture_output=True)
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(wav),'-l','fr','-otxt','-oj','-ml','16','-of',str(D/id),'-t','4'],check=True,capture_output=True)
 out=[]
 for r in json.loads((D/(id+'.json')).read_text(encoding='utf8'))['transcription']:out.append((round(start+r['offsets']['from']/1000,2),round(start+r['offsets']['to']/1000,2),r['text']))
 print(id,out,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[('first-context',1,4),('second-context',11.3,18),('third-context',31.8,36)]))
