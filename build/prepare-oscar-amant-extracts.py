from pathlib import Path
import sys,json,subprocess,wave,hashlib,base64,html,zipfile,struct
R=Path.cwd();D=R/'build/dialogue-extracts/oscar-amant';O=D/'clips';O.mkdir(exist_ok=True);sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf8');url='https://www.fufuworld.com/data/contents/common/sounds/oscar/oscar-05-amant.mp3'
plan=[('01-vous-restez-vous-sortez',47.85,50.25,"Ou, plutôt, non ! Vous, restez, et vous, sortez !",'Changement de décision'),('02-reflechir-dans-la-cuisine',56.85,59.25,"Allez réfléchir à ça dans la cuisine, vous !",'Mauvaise réponse')]
rows=[]
for id,start,end,text,use in plan:
 wav=O/(id+'.wav');mp3=wav.with_suffix('.mp3');duration=end-start
 filters=f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-2:LRA=9,afade=t=in:d=0.005,afade=t=out:st={duration-.012}:d=0.012,adelay=220:all=1'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source.mp3'),'-af',filters,'-ar','44100','-ac','1','-c:a','pcm_s16le',str(wav)],check=True,capture_output=True)
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','128k',str(mp3)],check=True,capture_output=True)
 with wave.open(str(wav)) as w:
  seconds=round(w.getnframes()/w.getframerate(),3);a=struct.unpack('<'+'h'*w.getnframes(),w.readframes(w.getnframes()));assert max(abs(x) for x in a[:int(.18*44100)])<200;assert max(abs(x) for x in a)>1000
 r=dict(id=id,text=text,suggestedUse=use,film='Oscar',sourceUrl=url,startSeconds=start,endSeconds=end,durationSeconds=seconds,wavFile='clips/'+wav.name,mp3File='clips/'+mp3.name,sha256=hashlib.sha256(wav.read_bytes()).hexdigest(),mp3Sha256=hashlib.sha256(mp3.read_bytes()).hexdigest(),changes='Original spoken excerpt; mono PCM 44.1 kHz, -18 LUFS target / -2 dBTP, 220 ms lead-in, 5 ms fade-in and 12 ms fade-out; MP3 128 kbps copy.',status='extracted_for_review',boundaryNote='Brief original spoken lead-in retained; no internal dialogue spliced or rewritten.',usage='Private local extraction from user-provided source; no redistribution permission asserted')
 rows.append(r)
 W=R/'build/movie-audition';subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-small.bin'),'-f',str(wav),'-l','fr','-otxt','-of',str(D/(id+'-check')),'-t','4'],check=True,capture_output=True)
 r['transcript']=(D/(id+'-check.txt')).read_text(encoding='utf8').strip();print(id,seconds,r['transcript'],flush=True)
(D/'dialogues.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Oscar — deux dialogues</title><style>*{box-sizing:border-box}body{max-width:960px;margin:30px auto;padding:0 20px;background:#101827;color:#eef4ff;font:18px/1.5 system-ui}h1{font-size:34px;line-height:1.2}article{background:#20314a;border:1px solid #40516c;border-radius:14px;margin:22px 0;padding:22px}h2{font-size:23px;line-height:1.45;margin:10px 0}a{color:#a4d8ff}audio{width:100%;margin:14px 0}.meta{font-size:15px;color:#bccbdd}button{font:inherit;background:#e8bd69;color:#151c29;padding:12px 18px;border:0;border-radius:9px;margin-right:10px;cursor:pointer}</style><h1>Oscar — deux dialogues</h1><p>Les deux passages demandés, avec les voix d’origine et un volume harmonisé.</p><p><a href="./Oscar-amant-deux-dialogues.zip">Télécharger WAV + MP3</a> · <a href="'''+html.escape(url,quote=True)+'''">Écouter la source</a></p><button id="all">Tout écouter</button><button id="stop">Arrêter</button><p id="status" role="status" aria-live="polite"></p>'''
for i,r in enumerate(rows,1):
 data=base64.b64encode((D/r['mp3File']).read_bytes()).decode();page+=f'<article><p class="meta">{i:02d} · {r["suggestedUse"]} · {r["durationSeconds"]} s</p><h2>{html.escape(r["text"])}</h2><audio controls preload="none" data-number="{i}" src="data:audio/mpeg;base64,{data}"></audio><p><a download href="./{r["wavFile"]}">WAV</a> · <a download href="./{r["mp3File"]}">MP3</a></p><p class="meta">Passage source : {r["startSeconds"]:.2f}–{r["endSeconds"]:.2f} s.</p></article>'
page+='''<p class="meta">Extraits préparés pour écoute. La banque du jeu n’a pas été modifiée.</p><script>const clips=[...document.querySelectorAll('audio')],status=document.querySelector('#status');let sequence=false;function stop(){sequence=false;clips.forEach(a=>{a.pause();a.currentTime=0});status.textContent='Écoute arrêtée.'}clips.forEach((a,i)=>{a.onplay=()=>{clips.forEach(b=>{if(b!==a)b.pause()});status.textContent='Dialogue '+(i+1)+' / 2'};a.onended=()=>{if(sequence&&i===0){clips[1].currentTime=0;clips[1].play().catch(()=>{sequence=false;status.textContent='Cliquez sur le second lecteur pour continuer.'})}else{sequence=false;status.textContent='Écoute terminée.'}}});document.querySelector('#all').onclick=()=>{stop();sequence=true;clips[0].play().catch(()=>{sequence=false;status.textContent='Cliquez sur le premier lecteur pour démarrer.'})};document.querySelector('#stop').onclick=stop;</script></html>'''
(D/'index.html').write_text(page,encoding='utf8')
readme='# Oscar — deux dialogues\n\nSource fournie : '+url+'\n\nOuvrir index.html pour écouter. Les limites sont conservées dans dialogues.json. Deux formats : WAV mono 44,1 kHz et MP3 128 kb/s. Volume harmonisé, très courts fondus de bord et amorce de 220 ms. Les voix originales restent inchangées ; aucune synthèse. La banque du jeu reste inchangée.\n\n'
for r in rows:readme+=f'- {r["id"]} : source {r["startSeconds"]}–{r["endSeconds"]} s ; fichier de {r["durationSeconds"]} s.\n'
(D/'README.md').write_text(readme,encoding='utf8')
with zipfile.ZipFile(D/'Oscar-amant-deux-dialogues.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for r in rows:
  for k in ['wavFile','mp3File']:z.write(D/r[k],r[k])
 for name in ['index.html','dialogues.json','README.md']:z.write(D/name,name)
print('Prepared two extracts, preview and download bundle.',flush=True)
