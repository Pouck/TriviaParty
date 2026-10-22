from pathlib import Path
import sys,subprocess,json
R=Path.cwd();D=R/'build/dialogue-extracts/vadrouille-tea-for-two';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
p=D/'speech-context.wav';subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af','atrim=start=70:end=78,asetpts=PTS-STARTPTS',str(p)],check=True,capture_output=True)
subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(p),'-l','en','-oj','-otxt','-ml','20','-of',str(D/'speech-context'),'-t','4'],check=True,capture_output=True)
for r in json.loads((D/'speech-context.json').read_text(encoding='utf8'))['transcription']:print(round(70+r['offsets']['from']/1000,2),round(70+r['offsets']['to']/1000,2),r['text'])
