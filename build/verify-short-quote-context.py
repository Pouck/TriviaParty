from pathlib import Path
import subprocess,sys
R=Path.cwd();D=R/'build/dialogue-extracts/X1PiR7WfuWs';W=R/'build/movie-audition';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
wav=D/'wide-context.wav';subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af','atrim=start=28:end=43,asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-2:LRA=9',str(wav)],check=True,capture_output=True)
subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(wav),'-l','fr','-otxt','-oj','-of',str(D/'wide-context-small'),'-t','4'],check=True,capture_output=True)
sys.stdout.reconfigure(encoding='utf8');print((D/'wide-context-small.txt').read_text(encoding='utf8'))
