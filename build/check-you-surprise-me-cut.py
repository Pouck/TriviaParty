from pathlib import Path
import sys,subprocess
R=Path.cwd();D=R/'build/dialogue-extracts/X1PiR7WfuWs';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
for id,start,end in [('short-context',35.3,39.3),('short-early',35.7,37.25),('short-late',36.55,37.8)]:
 wav=D/(id+'.wav');subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-2:LRA=9',str(wav)],check=True,capture_output=True)
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(wav),'-l','fr','-otxt','-of',str(D/id),'-t','4'],check=True,capture_output=True)
 print(id,(D/(id+'.txt')).read_text(encoding='utf8'))
