from pathlib import Path
import subprocess,sys,json
R=Path.cwd();D=R/'build/dialogue-extracts/vadrouille-prisonnier';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
p=D/'speech-context.wav';subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af','atrim=start=40:end=45,asetpts=PTS-STARTPTS',str(p)],check=True,capture_output=True)
subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(p),'-l','fr','-mc','0','-oj','-otxt','-ml','18','-of',str(D/'speech-context'),'-t','4'],check=True,capture_output=True)
sys.stdout.reconfigure(encoding='utf8')
for r in json.loads((D/'speech-context.json').read_text(encoding='utf8'))['transcription']:print(round(40+r['offsets']['from']/1000,2),round(40+r['offsets']['to']/1000,2),r['text'])
