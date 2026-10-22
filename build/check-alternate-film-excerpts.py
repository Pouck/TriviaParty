from pathlib import Path
import sys,json,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'build/audio-download-tools'));sys.path.insert(0,str(R/'build/audio-tools'));import yt_dlp,imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf8');D=R/'build/classic-audio/alternate-sources';W=R/'build/movie-audition'
for id in ['aMnlYxL0rcU','n9yajuKXJ3Y','f8mS9JXovpQ','qmUPQxd-_sA']:
 try:
  with yt_dlp.YoutubeDL({'format':'bestaudio/best','outtmpl':str(D/(id+'.%(ext)s')),'quiet':True,'noprogress':True,'socket_timeout':15,'retries':0,'extractor_retries':0,'noplaylist':True}) as y:info=y.extract_info('https://www.youtube.com/watch?v='+id,download=True)
  src=next(p for p in D.glob(id+'.*') if p.suffix not in ['.json','.wav','.txt','.part']);wav=D/(id+'.wav')
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-loglevel','error','-i',str(src),'-ar','16000','-ac','1',str(wav)],check=True,capture_output=True)
  subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(wav),'-l','fr','-otxt','-oj','-of',str(D/(id+'-transcript')),'-t','4'],check=True,capture_output=True)
  print(id,info.get('title'),(D/(id+'-transcript.txt')).read_text(encoding='utf8')[:2400],flush=True)
 except Exception as e:print(id,str(e)[:200],flush=True)
