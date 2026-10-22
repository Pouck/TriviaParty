from pathlib import Path
import sys,subprocess,re,json
R=Path.cwd();sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
for p in (R/'build/winner-music/sources').glob('*.source'):
 if p.stem not in ['zarathustra','aida']:continue
 r=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(p),'-af','silencedetect=noise=-35dB:d=0.3','-f','null','-'],capture_output=True,text=True)
 print(p.stem,re.findall(r'silence_(?:start|end): [\d.]+',r.stderr)[-12:])
