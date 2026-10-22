from pathlib import Path
import json,hashlib
R=Path.cwd();D=R/'build/dialogue-extracts/X1PiR7WfuWs';rows=json.loads((D/'cut-audit.json').read_text(encoding='utf8'));old=json.loads((D/'dialogues.json').read_text(encoding='utf8'))
(D/'approved-before-revision.json').write_text(json.dumps({r['id']:{k:r[k] for k in ['sha256','mp3Sha256','startSeconds','endSeconds']} for r in old},indent=2),encoding='utf8')
for r in rows:
 if r['id'].startswith('03-'):r.update(startSeconds=36.35,endSeconds=37.8,reviewStatus='slightly_extended_for_review')
 elif r['id'].startswith('04-'):r.update(startSeconds=83.45,endSeconds=90.4,reviewStatus='slightly_extended_for_review')
 else:r['reviewStatus']='approved_by_user'
(D/'cut-audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Retain the approved clips exactly; only revised cuts need to be rendered again.
p=R/'build/export-requested-dialogues.py';s=p.read_text(encoding='utf8')
a=" subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source.webm')"
s=s.replace(a," if r.get('reviewStatus')!='approved_by_user' or not wav.exists() or not mp3.exists():\n  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(D/'source.webm')",1)
b=" subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libmp3lame'"
s=s.replace(b,"  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libmp3lame'",1)
s=s.replace("r['verificationNote']+=' Cut ends at « ridicule », before the next sentence.'","r['verificationNote']+=' Boundaries extended slightly after user listening feedback.'")
s=s.replace('Le quatrième extrait s’arrête à « ridicule », avant la suite de la phrase.','Les limites des extraits 3 et 4 ont été légèrement élargies après votre écoute ; les cinq autres extraits sont approuvés et conservés à l’identique.')
s=s.replace('<p class="intro">Extraits préparés pour écoute ; la banque du jeu n’a pas été modifiée.</p>','<p class="intro">Extraits 3 et 4 légèrement rallongés. Les cinq autres extraits sont approuvés et inchangés. La banque du jeu n’a pas été modifiée.</p>')
p.write_text(s,encoding='utf8')
