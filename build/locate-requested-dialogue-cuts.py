from pathlib import Path
import subprocess,json,sys,concurrent.futures
R=Path.cwd();D=R/'build/dialogue-extracts/X1PiR7WfuWs';O=D/'clips';O.mkdir(exist_ok=True);sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf8')
rows=[('01-cest-fini-oui',6.05,7.25,"C’est fini, oui ?"),('02-doigt-dans-loeil',18.75,23.18,"Alors là, mon vieux, vous vous foutez complètement le doigt dans l’œil."),('03-vous-metonnez',36.45,37.55,"Vous m’étonnez."),('04-la-gifle',83.55,90.16,"C’est la première fois que je prends une gifle devant tout le monde. Et c’est grâce à vous. Vous l’avez fait exprès. — Mais pas du tout. — Si, vous l’avez fait exprès pour me rendre ridicule."),('05-cest-un-malentendu',110.65,112.92,"C’est un malentendu, il n’y a pas de raison de s’énerver."),('06-ne-nous-fachons-pas',123.7,128.85,"Non, ça va, ça va, ne nous fâchons pas."),('07-beaucoup-de-choses',157.55,161.05,"Je crois qu’on a beaucoup de choses à se dire tous les deux.")]
W=R/'build/movie-audition';records=[]
def check(row):
 id,start,end,text=row;wav=O/(id+'-draft.wav')
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source-16k.wav'),'-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS','-ar','16000','-ac','1',str(wav)],check=True,capture_output=True)
 subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(wav),'-l','fr','-otxt','-oj','-of',str(O/(id+'-check')),'-t','4'],check=True,capture_output=True)
 transcript=(O/(id+'-check.txt')).read_text(encoding='utf8').strip();print(id,transcript,flush=True)
 return dict(id=id,startSeconds=start,endSeconds=end,requestedText=text,transcript=transcript)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(check,rows))
(D/'cut-audit.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
