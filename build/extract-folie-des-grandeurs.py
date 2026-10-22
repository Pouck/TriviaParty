from pathlib import Path
import sys,urllib.request,subprocess,json
R=Path.cwd();D=R/'build/dialogue-extracts/folie-des-grandeurs';D.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
p=D/'source.mp3'
if not p.exists():p.write_bytes(urllib.request.urlopen('https://www.fufuworld.com/data/contents/common/sounds/grandeurs/folie-grandeurs-02-flatterie.mp3',timeout=30).read())
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(p),'-ar','16000','-ac','1',str(D/'source-16k.wav')],check=True,capture_output=True)
W=R/'build/movie-audition';subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(D/'source-16k.wav'),'-l','fr','-otxt','-oj','-ml','40','-of',str(D/'transcript'),'-t','4'],check=True,capture_output=True)
sys.stdout.reconfigure(encoding='utf8')
for r in json.loads((D/'transcript.json').read_text(encoding='utf8'))['transcription']:print(r['offsets'],r['text'])
