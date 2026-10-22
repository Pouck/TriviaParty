import sys,json
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'build/audio-download-tools'));sys.path.insert(0,str(R/'build/audio-tools'))
import yt_dlp,imageio_ffmpeg
D=R/'build/classic-audio/alternate-sources';D.mkdir(exist_ok=True)
for name,url in [('bourvil-corniaud','https://www.youtube.com/watch?v=FNVQg0DBLwo'),('bourvil-report','https://www.dailymotion.com/video/x9gnvgi')]:
 try:
  opts={'format':'bestaudio/best','outtmpl':str(D/(name+'.%(ext)s')),'noplaylist':True,'socket_timeout':15,'retries':0,'extractor_retries':0,'quiet':True,'ffmpeg_location':imageio_ffmpeg.get_ffmpeg_exe()}
  with yt_dlp.YoutubeDL(opts) as y:
   info=y.extract_info(url,download=True)
   (D/(name+'-metadata.json')).write_text(json.dumps({k:info.get(k) for k in ['title','webpage_url','uploader','duration','ext','requested_downloads']},ensure_ascii=False,indent=2),encoding='utf8')
   print(name,'downloaded',info.get('duration'),flush=True)
 except Exception as e: print(name,'unavailable:',str(e)[:350],flush=True)
