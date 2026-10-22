from pathlib import Path
import sys,json,subprocess
R=Path.cwd();D=R/'build/dialogue-extracts/X1PiR7WfuWs';D.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'build/audio-download-tools'));sys.path.insert(0,str(R/'build/audio-tools'));import yt_dlp,imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf8')
opts={'format':'bestaudio/best','outtmpl':str(D/'source.%(ext)s'),'noplaylist':True,'socket_timeout':25,'retries':1,'extractor_retries':1,'quiet':True,'noprogress':True,'writeautomaticsub':True,'writesubtitles':True,'subtitleslangs':['fr','fr-orig'],'skip_download':False}
with yt_dlp.YoutubeDL(opts) as y:info=y.extract_info('https://www.youtube.com/watch?v=X1PiR7WfuWs',download=True)
(D/'source-metadata.json').write_text(json.dumps({k:info.get(k) for k in ['id','title','webpage_url','uploader','duration','description','ext','requested_subtitles']},ensure_ascii=False,indent=2),encoding='utf8')
print(info['title'],info.get('duration'),'seconds',flush=True)
src=D/('source.'+info['ext']);wav=D/'source-16k.wav'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(src),'-ar','16000','-ac','1',str(wav)],check=True,capture_output=True)
W=R/'build/movie-audition'
subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(wav),'-l','fr','-otxt','-oj','-of',str(D/'transcript'),'-t','4'],check=True,capture_output=True)
print((D/'transcript.txt').read_text(encoding='utf8'),flush=True)
