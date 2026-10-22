from pathlib import Path
import sys,subprocess,json
R=Path.cwd();D=R/'build/dialogue-extracts/grande-vadrouille';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
p=D/'ending-context.wav';subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af','atrim=start=33:end=40,asetpts=PTS-STARTPTS',str(p)],check=True,capture_output=True)
subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(p),'-l','fr','-otxt','-oj','-ml','20','-of',str(D/'ending-context'),'-t','4'],check=True,capture_output=True)
sys.stdout.reconfigure(encoding='utf8')
for s in json.loads((D/'ending-context.json').read_text(encoding='utf8'))['transcription']:print(round(s['offsets']['from']/1000+33,2),round(s['offsets']['to']/1000+33,2),s['text'])
