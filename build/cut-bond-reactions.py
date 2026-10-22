from pathlib import Path
import subprocess,sys
R=Path.cwd();D=R/'build/classic-audio';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
for id,start,end in [('bond-perfect',4.4,8),('bond-congratulations',14.0,16.7)]:
 dest=D/(id+'.wav');subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-loglevel','error','-i',str(D/'sources'/(id+'.wav')),'-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-2:LRA=9,adelay=220:all=1','-ac','1','-ar','44100',str(dest)],check=True,capture_output=True)
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(dest),'-l','en','-nt','-otxt','-of',str(D/(id+'-cut')),'-t','4'],check=True,capture_output=True)
 print(id,(D/(id+'-cut.txt')).read_text())

