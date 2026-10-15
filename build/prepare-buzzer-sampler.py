"""Create ten original low-latency buzzer candidates and their standalone sampler."""
from pathlib import Path
import math,wave,struct,json
RATE=44100
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'app/src/main/assets/tv/sounds'
styles=[('Ressort actuel',.68,'spring',190,700,14),('Mini boing',.34,'spring',230,850,19),('Ressort grave',.55,'spring',90,420,10),('Ressort cartoon',.48,'spring',320,1000,22),('Buzzer de plateau',.30,'square',165,0,0),('Double buzz',.42,'double',210,0,0),('Coup de klaxon',.35,'horn',310,0,0),('Arcade rétro',.26,'arcade',800,0,0),('Cloche de comptoir',.62,'bell',1420,0,0),('Éclair spatial',.45,'laser',1700,0,0)]
records=[]
for i,(name,duration,style,base,sweep,wobble) in enumerate(styles,1):
 samples=[];phase=0
 for n in range(round(duration*RATE)):
  t=n/RATE;env=min(1,t/.002)*min(1,(duration-t)/.035)
  freq=base
  if style=='spring':freq=base+sweep*math.exp(-t*5)*(1+.48*math.cos(2*math.pi*wobble*t))
  elif style=='arcade':freq=[1046.5,783.99,523.25][min(2,int(t/.075))]
  elif style=='laser':freq=170+base*math.exp(-t*9)
  phase+=2*math.pi*freq/RATE
  if style=='spring':tone=math.exp(-t*4.8)*(math.sin(phase+1.2*math.exp(-t*4)*math.sin(phase*2.7))+.22*math.sin(phase*2))
  elif style in ('square','double'):tone=(math.sin(phase)+.33*math.sin(phase*3)+.2*math.sin(phase*5))*(0 if style=='double' and .15<t<.22 else 1)*math.exp(-t*1.5)
  elif style=='horn':tone=(math.sin(phase)+.6*math.sin(phase*1.25)+.25*math.sin(phase*2))*math.exp(-t*2)
  elif style=='bell':tone=(math.sin(phase)+.35*math.sin(phase*2.76)+.15*math.sin(phase*5.4))*math.exp(-t*7)
  else:tone=math.sin(phase)*math.exp(-t*5)
  samples.append(tone*env)
 peak=max(abs(v) for v in samples);file=f'buzzer-{i:02}.wav'
 with wave.open(str(OUT/file),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(b''.join(struct.pack('<h',round(v/peak*24000)) for v in samples))
 if i==1:(OUT/file).write_bytes((OUT/'buzzer.wav').read_bytes())
 records.append(dict(file=file,name=name,duration=duration))
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TriviaParty — Choisir un buzzer</title><style>*{box-sizing:border-box}body{margin:0;background:#12121d;color:#f5f5fa;font:18px system-ui}main{max-width:1050px;margin:auto;padding:28px 20px}h1{font-size:clamp(28px,5vw,40px)}p{line-height:1.5;color:#bcc5d7}#sounds{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px}.card{background:#232333;padding:20px;border-radius:16px;border:2px solid transparent}.card.playing{border-color:#75d7cb}h2{font-size:21px;margin:0 0 8px}button{font:700 17px system-ui;border:0;border-radius:10px;padding:12px 22px;background:#75d7cb;color:#102724;cursor:pointer}button:focus-visible{outline:3px solid #ffd54f;outline-offset:4px}.meta{font-size:14px}#status{min-height:28px}#stop{background:#39394c;color:white}</style><main><h1>Quel buzzer pour TriviaParty ?</h1><p>Dix sons originaux, sans voix. Cliquez sur un son pour le comparer aux autres. Un seul joue à la fois. Le n° 1 reprend le ressort actuel. Votre choix ici ne modifie pas encore le buzzer de la partie.</p><button id="stop">Arrêter</button><p id="status" role="status">Choisissez un son à écouter.</p><section id="sounds"></section></main><script>
const sounds=RECORDS;const base=location.protocol==='file:'?'../app/src/main/assets/tv/sounds/':'/tv/sounds/';let current=null;const status=document.getElementById('status');function stop(){if(current){current.pause();current.currentTime=0;}document.querySelectorAll('.playing').forEach(c=>c.classList.remove('playing'));}document.getElementById('stop').onclick=()=>{stop();status.textContent='Lecture arrêtée.'};sounds.forEach((sound,i)=>{const card=document.createElement('article');card.className='card';const h=document.createElement('h2');h.textContent=(i+1)+'. '+sound.name;const info=document.createElement('p');info.className='meta';info.textContent=sound.duration.toLocaleString('fr-FR')+' s · '+sound.file;const button=document.createElement('button');button.textContent='Écouter';button.setAttribute('aria-label','Écouter '+sound.name);const audio=new Audio(base+sound.file);audio.preload='auto';button.onclick=()=>{stop();current=audio;card.classList.add('playing');status.textContent='Écoute : '+sound.name;audio.play().catch(()=>{card.classList.remove('playing');status.textContent='Lecture impossible. Vérifiez que les fichiers audio sont accessibles.'})};audio.onended=()=>card.classList.remove('playing');card.append(h,info,button);document.getElementById('sounds').append(card)});
</script></html>'''.replace('RECORDS',json.dumps(records,ensure_ascii=False))
(ROOT/'audio-bank/buzzer-sampler.html').write_text(page,encoding='utf8');(ROOT/'app/src/main/assets/tv/buzzer-sampler.html').write_text(page,encoding='utf8')
print('Created ten original buzzer candidates and the sampler page.')
