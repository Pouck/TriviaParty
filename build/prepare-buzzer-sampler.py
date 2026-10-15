"""Create twenty buzzer candidates and twenty correct-answer effects with audition pages."""
from pathlib import Path
import math,wave,struct,json
RATE=44100
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'app/src/main/assets/tv/sounds'
styles=[('Ressort actuel',.68,'spring',190,700,14),('Mini boing',.34,'spring',230,850,19),('Ressort grave',.55,'spring',90,420,10),('Ressort cartoon',.48,'spring',320,1000,22),('Buzzer de plateau',.30,'square',165,0,0),('Double buzz',.42,'double',210,0,0),('Coup de klaxon',.35,'horn',310,0,0),('Arcade rétro',.26,'arcade',800,0,0),('Cloche de comptoir',.62,'bell',1420,0,0),('Éclair spatial',.45,'laser',1700,0,0),('Rebond en caoutchouc',.52,'rubber',145,0,0),('Corde pincée',.36,'pluck',440,0,0),('Toc de bois',.22,'wood',650,0,0),('Trille de jeu',.38,'trill',740,0,0),('Sifflet express',.28,'whistle',1250,0,0),('Robot rigolo',.44,'robot',250,0,0),('Canard cartoon',.40,'duck',320,0,0),('Zip ascendant',.29,'zip',240,0,0),('Sonnerie rétro',.46,'phone',480,0,0),('Mini cuivre',.39,'brass',233,0,0)]
records=[]
for i,(name,duration,style,base,sweep,wobble) in enumerate(styles,1):
 samples=[];phase=0
 for n in range(round(duration*RATE)):
  t=n/RATE;env=min(1,t/.002)*min(1,(duration-t)/.035)
  freq=base
  if style=='spring':freq=base+sweep*math.exp(-t*5)*(1+.48*math.cos(2*math.pi*wobble*t))
  elif style=='arcade':freq=[1046.5,783.99,523.25][min(2,int(t/.075))]
  elif style=='laser':freq=170+base*math.exp(-t*9)
  elif style=='rubber':freq=base+650*math.exp(-t*7)*abs(math.cos(2*math.pi*9*t))
  elif style=='trill':freq=base*(1.25 if int(t*25)%2 else 1)
  elif style=='whistle':freq=base+220*math.sin(math.pi*t/duration)
  elif style=='robot':freq=base*[1,1.5,.75,2][min(3,int(t*9))]
  elif style=='duck':freq=base+110*math.sin(2*math.pi*8*t)*math.exp(-t*3)
  elif style=='zip':freq=base+1800*(t/duration)**1.4
  phase+=2*math.pi*freq/RATE
  if style=='spring':tone=math.exp(-t*4.8)*(math.sin(phase+1.2*math.exp(-t*4)*math.sin(phase*2.7))+.22*math.sin(phase*2))
  elif style in ('square','double'):tone=(math.sin(phase)+.33*math.sin(phase*3)+.2*math.sin(phase*5))*(0 if style=='double' and .15<t<.22 else 1)*math.exp(-t*1.5)
  elif style=='horn':tone=(math.sin(phase)+.6*math.sin(phase*1.25)+.25*math.sin(phase*2))*math.exp(-t*2)
  elif style=='phone':tone=(math.sin(phase)+math.sin(phase*1.5))*(.3+.7*max(0,math.sin(2*math.pi*22*t)))
  elif style=='brass':tone=(math.sin(phase)+.45*math.sin(phase*2)+.25*math.sin(phase*3)+.15*math.sin(phase*4))*math.exp(-t*3)
  elif style=='duck':tone=(math.sin(phase)+.6*math.sin(phase*3)+.4*math.sin(phase*5))*math.exp(-t*5)
  elif style=='robot':tone=(math.sin(phase)+.4*math.sin(phase*3))*(.6+.4*math.sin(2*math.pi*35*t))
  elif style=='wood':tone=(math.sin(phase)+.6*math.sin(phase*1.73)+.3*math.sin(phase*3.2))*math.exp(-t*24)
  elif style=='pluck':tone=(math.sin(phase)+.3*math.sin(phase*2)+.2*math.sin(phase*3))*math.exp(-t*11)
  elif style=='rubber':tone=(math.sin(phase)+.25*math.sin(phase*2))*math.exp(-t*6)
  elif style=='bell':tone=(math.sin(phase)+.35*math.sin(phase*2.76)+.15*math.sin(phase*5.4))*math.exp(-t*7)
  else:tone=math.sin(phase)*math.exp(-t*5)
  samples.append(tone*env)
 peak=max(abs(v) for v in samples);file=f'buzzer-{i:02}.wav'
 with wave.open(str(OUT/file),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(b''.join(struct.pack('<h',round(v/peak*24000)) for v in samples))
 if i==1:(OUT/file).write_bytes((OUT/'buzzer.wav').read_bytes())
 records.append(dict(file=file,name=name,duration=duration))
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TriviaParty — Choisir un buzzer</title><style>*{box-sizing:border-box}body{margin:0;background:#12121d;color:#f5f5fa;font:18px system-ui}main{max-width:1050px;margin:auto;padding:28px 20px}h1{font-size:clamp(28px,5vw,40px)}p{line-height:1.5;color:#bcc5d7}#sounds{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px}.card{background:#232333;padding:20px;border-radius:16px;border:2px solid transparent}.card.playing{border-color:#75d7cb}h2{font-size:21px;margin:0 0 8px}button{font:700 17px system-ui;border:0;border-radius:10px;padding:12px 22px;background:#75d7cb;color:#102724;cursor:pointer}button:focus-visible{outline:3px solid #ffd54f;outline-offset:4px}.meta{font-size:14px}#status{min-height:28px}#stop{background:#39394c;color:white}</style><main><h1>Quel buzzer pour TriviaParty ?</h1><p>Vingt sons originaux, sans voix. Cliquez sur un son pour le comparer aux autres. Un seul joue à la fois. Le n° 1 reprend le ressort actuel. Votre choix ici ne modifie pas encore le buzzer de la partie.</p><button id="stop">Arrêter</button><p id="status" role="status">Choisissez un son à écouter.</p><section id="sounds"></section></main><script>
const sounds=RECORDS;const base=location.protocol==='file:'?'../app/src/main/assets/tv/sounds/':'/tv/sounds/';let current=null;const status=document.getElementById('status');function stop(){if(current){current.pause();current.currentTime=0;}document.querySelectorAll('.playing').forEach(c=>c.classList.remove('playing'));}document.getElementById('stop').onclick=()=>{stop();status.textContent='Lecture arrêtée.'};sounds.forEach((sound,i)=>{const card=document.createElement('article');card.className='card';const h=document.createElement('h2');h.textContent=(i+1)+'. '+sound.name;const info=document.createElement('p');info.className='meta';info.textContent=sound.duration.toLocaleString('fr-FR')+' s · '+sound.file;const button=document.createElement('button');button.textContent='Écouter';button.setAttribute('aria-label','Écouter '+sound.name);const audio=new Audio(base+sound.file);audio.preload='auto';button.onclick=()=>{stop();current=audio;card.classList.add('playing');status.textContent='Écoute : '+sound.name;audio.play().catch(()=>{card.classList.remove('playing');status.textContent='Lecture impossible. Vérifiez que les fichiers audio sont accessibles.'})};audio.onended=()=>card.classList.remove('playing');card.append(h,info,button);document.getElementById('sounds').append(card)});
</script></html>'''.replace('RECORDS',json.dumps(records,ensure_ascii=False))
(ROOT/'audio-bank/buzzer-sampler.html').write_text(page,encoding='utf8');(ROOT/'app/src/main/assets/tv/buzzer-sampler.html').write_text(page,encoding='utf8')
print('Created twenty original buzzer candidates and the sampler page.')

# Bright, playful approval cues. The original cue remains candidate 1.
success_styles=[
 ('Réussite actuelle','bell',[523.25,659.25,783.99,1046.5],.84),
 ('Ding cristallin','bell',[1046.5],.46),('Double ding','bell',[880,1174.66],.58),
 ('Trio joyeux','bell',[659.25,830.61,987.77],.66),('Petite victoire','brass',[523.25,659.25,783.99,1046.5],.82),
 ('Marimba souriant','marimba',[523.25,783.99,1046.5],.65),('Xylophone pétillant','marimba',[783.99,987.77,1174.66,1567.98],.70),
 ('Bonus arcade','arcade',[523.25,659.25,783.99,1046.5,1318.51],.62),
 ('Pièce gagnée','arcade',[987.77,1318.51],.42),('Niveau réussi','arcade',[392,523.25,659.25,783.99,1046.5],.82),
 ('Accord chaleureux','chord',[523.25,659.25,783.99],.68),('Grand sourire','chord',[392,493.88,587.33,783.99],.83),
 ('Cascade lumineuse','bell',[1046.5,1318.51,1567.98,2093],.73),('Corde gagnante','pluck',[440,554.37,659.25],.59),
 ('Bravo malicieux','marimba',[523.25,783.99,659.25,1046.5],.78),('Mini fanfare','brass',[392,392,523.25,659.25,783.99],.92),
 ('Magie scintillante','bell',[783.99,1174.66,1567.98,1975.53],.85),('Succès futuriste','synth',[523.25,783.99,1046.5],.64),
 ('Carillon triomphant','bell',[659.25,783.99,1046.5,1318.51],1.02),('Victoire ensoleillée','chord',[523.25,659.25,783.99,1046.5],.93)]
successes=[]
for i,(name,style,notes,duration) in enumerate(success_styles,1):
 samples=[0.0]*round(duration*RATE)
 spacing=0 if style=='chord' else min(.12,(duration-.30)/max(1,len(notes)-1))
 for j,freq in enumerate(notes):
  start=round(j*spacing*RATE)
  for n in range(len(samples)-start):
   t=n/RATE;end=(len(samples)-start-n)/RATE
   env=min(1,t/.002)*min(1,end/.04)*math.exp(-t*(9 if style in ('pluck','marimba') else 5))
   phase=2*math.pi*freq*t
   if style=='bell':tone=math.sin(phase)+.25*math.sin(phase*2.01)+.12*math.sin(phase*3.99)
   elif style=='marimba':tone=math.sin(phase)+.35*math.sin(phase*4)*math.exp(-t*18)
   elif style=='brass':tone=math.sin(phase)+.45*math.sin(phase*2)+.22*math.sin(phase*3)
   elif style=='arcade':tone=math.sin(phase)+.33*math.sin(phase*3)+.20*math.sin(phase*5)
   elif style=='synth':tone=math.sin(phase+.7*math.sin(2*math.pi*freq*2*t)*math.exp(-t*10))
   else:tone=math.sin(phase)+.2*math.sin(phase*2)+.1*math.sin(phase*3)
   samples[start+n]+=tone*env
 peak=max(abs(x) for x in samples);file=f'success-{i:02}.wav'
 with wave.open(str(OUT/file),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(b''.join(struct.pack('<h',round(v/peak*24000)) for v in samples))
 if i==1:(OUT/file).write_bytes((OUT/'good-ping.wav').read_bytes())
 successes.append(dict(file=file,name=name,duration=duration))
success_page=page.replace(json.dumps(records,ensure_ascii=False),json.dumps(successes,ensure_ascii=False)).replace('Choisir un buzzer','Bonne réponse').replace('Quel buzzer pour TriviaParty ?','Quel son pour une bonne réponse ?').replace('Le n° 1 reprend le ressort actuel. Votre choix ici ne modifie pas encore le buzzer de la partie.','Le n° 1 est le signal de réussite actuel. Ces effets précèdent les commentaires vocaux. L’écoute ne modifie pas le son de la partie.')
nav='<p><a style="color:#b9d6ff" href="OTHER">OTHERLABEL</a></p>'
page=page.replace('<button id="stop">',nav.replace('OTHERLABEL','Sons de bonne réponse →').replace('OTHER','success-sampler.html' )+'<button id="stop">')
success_page=success_page.replace('<button id="stop">',nav.replace('OTHERLABEL','← Sons de buzzer').replace('OTHER','buzzer-sampler.html')+'<button id="stop">')
for file,content in [('buzzer-sampler.html',page),('success-sampler.html',success_page)]:
 (ROOT/'audio-bank'/file).write_text(content,encoding='utf8')
 # Route aliases with .html make the cross-links work on both servers.
 (ROOT/'app/src/main/assets/tv'/file).write_text(content,encoding='utf8')
print('Created twenty correct-answer effects and the linked sampler page.')
