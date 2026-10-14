"""Normalize locally downloaded film samples for a private Pixel audition (no media committed)."""
from pathlib import Path
import sys,subprocess,json,wave,hashlib,html
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'build/audio-tools'))
import imageio_ffmpeg
BANK=ROOT/'build/movie-audition';FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
# Only sources successfully downloaded; the rest of the approved shortlist remains pending.
clips=[
('good-62.wav','good','fr','Le Dîner de cons','Thierry Lhermitte / Pierre Brochant','Il a une belle tête de vainqueur','diner','LeDinerDeCons_UneBelleTeteDeVainqueur'),
('good-63.wav','good','fr','Kaamelott','Guillaume Briat / Le Roi burgonde','Arthour ! On est fort en pomme.','kaamelott',None),
('good-67.wav','good','fr','Le Dîner de cons','Jacques Villeret / François Pignon','Alors ça, c’est très tordu mais bougrement intelligent !','diner-clever','LeDinerDeCons_TorduMaisBougrementIntelligent'),
('bad-65.wav','bad','fr','Le Dîner de cons','Daniel Prévost / Lucien Cheval','Oh, le con !','diner-bad','LeDinerDeCons_OhhhLeCon'),
('bad-66.wav','bad','fr','Astérix et Obélix : Mission Cléopâtre','Jean Benguigui / Malococsis','Je crois que vous n’avez pas très bien compris mon problème.','asterix-bad','AsterixFilm_2_JeCroisQueVousNavezPasBienComprisMonPb'),
]
records=[]
for file,outcome,language,film,voice,text,source,bleep in clips:
 dest=BANK/file
 filters='silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,loudnorm=I=-18:TP=-2:LRA=9,adelay=220:all=1'
 subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(BANK/(source+'.source')),'-af',filters,'-ar','44100','-ac','1','-c:a','pcm_s16le',str(dest)],check=True)
 with wave.open(str(dest)) as w:
  seconds=w.getnframes()/w.getframerate();lead=w.readframes(int(.18*w.getframerate()))
 assert .4<seconds<12
 assert max(abs(int.from_bytes(lead[i:i+2],'little',signed=True)) for i in range(0,len(lead),2))<200
 page='https://www.bleeps.wtf/bleep/'+bleep if bleep else 'https://github.com/2ec0b4/kaamelott-soundboard/blob/master/sounds/fort_en_pomme_2.mp3'
 records.append(dict(file=file,outcome=outcome,language=language,film=film,voice=voice,text=text,sourceUrl=page,durationSeconds=round(seconds,3),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),usage='Private on-device audition; no redistribution permission asserted'))
 print(file,round(seconds,2),film)
(BANK/'reactions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
intro="""<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Essai des répliques</title><style>body{max-width:850px;margin:32px auto;padding:0 20px;background:#101827;color:#eff4ff;font:20px system-ui}article{padding:18px;margin:18px 0;border-radius:12px;background:#20314c}h2{font-size:22px}audio{width:100%}a{color:#9cd5ff}.bad{border-left:8px solid #ff7777}.good{border-left:8px solid #72e49c}</style><h1>Essai des répliques — 5 extraits</h1><p>Banque privée installée sur le Pixel. Les autres candidats de la sélection restent en attente de fichiers accessibles. Un seul extrait joue à la fois.</p>"""
for r in records:
 intro+=f'<article class="{r["outcome"]}"><h2>{"✓ Bonne réponse" if r["outcome"]=="good" else "✗ Mauvaise réponse"} — {html.escape(r["film"])}</h2><p>{html.escape(r["text"])}</p><p>{html.escape(r["voice"])} · {r["durationSeconds"]} s</p><audio controls preload="none" src="/tv/sounds/{r["file"]}"></audio><p><a href="{html.escape(r["sourceUrl"])}">Source</a></p></article>'
intro+="""<script>document.querySelectorAll('audio').forEach(a=>a.addEventListener('play',()=>document.querySelectorAll('audio').forEach(b=>{if(a!==b)b.pause()})))</script></html>"""
(BANK/'credits.html').write_text(intro,encoding='utf8')

(BANK/"index.html").write_text(intro.replace("/tv/sounds/","./"),encoding="utf8")
