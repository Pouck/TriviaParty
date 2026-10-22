from pathlib import Path
import subprocess,sys,json
R=Path.cwd();D=R/'build/dialogue-extracts/oscar';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf8')
for id,start,end in [('first-context',10,16),('second-context',33.7,38.3)]:
 wav=D/(id+'.wav');subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS',str(wav)],check=True,capture_output=True)
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(wav),'-l','fr','-oj','-otxt','-ml','20','-of',str(D/id),'-t','4'],check=True,capture_output=True)
 for r in json.loads((D/(id+'.json')).read_text(encoding='utf8'))['transcription']:print(id,round(start+r['offsets']['from']/1000,2),round(start+r['offsets']['to']/1000,2),r['text'])
