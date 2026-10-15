"""Normalize and render the curated private 60-clip bank; media remains outside Git."""
from pathlib import Path
import sys,json,subprocess,wave,hashlib,html,collections
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'build/movie-audition';C=D/'expanded-sources'
sys.path.insert(0,str(ROOT/'build/audio-tools'))
import imageio_ffmpeg
records=json.loads((ROOT/'audio-bank/movie-reactions-selection.json').read_text(encoding='utf8'))
assert all(any(r['outcome']==kind for r in records) for kind in ('good','bad'))
assert len({r['file'] for r in records})==len(records)
for r in records:
 file=r['file'];dest=D/file
 command=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(C/(file+'.wav'))]
 filters='silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,loudnorm=I=-18:TP=-2:LRA=9,adelay=220:all=1'
 if r.get('trimEndSeconds'):filters='atrim=end='+str(r['trimEndSeconds'])+',asetpts=PTS-STARTPTS,'+filters
 command+=['-af',filters,'-ar','44100','-ac','1','-c:a','pcm_s16le',str(dest)]
 subprocess.run(command,check=True,capture_output=True)
 with wave.open(str(dest)) as w:
  duration=w.getnframes()/w.getframerate();lead=w.readframes(round(w.getframerate()*.18))
  assert w.getnchannels()==1 and w.getsampwidth()==2
 assert .4<duration<9.1,(file,duration)
 assert max(abs(int.from_bytes(lead[i:i+2],'little',signed=True)) for i in range(0,len(lead),2))<200,file
 r['durationSeconds']=round(duration,3);r['sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
 r['captionNote']='Caption identifies the spoken excerpt; ellipses indicate edited/stumbled dialogue.'

(D/'reactions.json.new').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8');(D/'reactions.json.new').replace(D/'reactions.json')
films=sorted({r['film'] for r in records});counts=collections.Counter(r['language'] for r in records)
page="""<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Réactions cinéma — 72 extraits</title><style>*{box-sizing:border-box}body{max-width:1200px;margin:30px auto;padding:0 20px;background:#101827;color:#eff4ff;font:18px system-ui}h1{font-size:32px}#filters{display:flex;gap:10px;flex-wrap:wrap;position:sticky;top:0;background:#101827;padding:14px 0}select,input{padding:10px;border-radius:8px;max-width:100%;font:inherit}#clips{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:18px}article{padding:18px;border-radius:12px;background:#20314c}article[hidden]{display:none}h2{font-size:21px;margin-top:0}.caption{font-size:20px;line-height:1.45}audio{width:100%;margin:10px 0}a{color:#9cd5ff}.bad{border-left:7px solid #ff7777}.good{border-left:7px solid #72e49c}.meta{font-size:14px;color:#c1cce1}</style><h1>Réactions cinéma — 72 extraits</h1><p>36 bonnes réponses · 36 mauvaises réponses · 62 français · 8 anglais · 2 japonais. Voix et langues originales. Un seul extrait joue à la fois.</p><p>Le passage burgonde incertain a été remplacé par une autre réplique de Kaamelott, sur la magie. Les extraits précédemment appréciés sont conservés.</p><div id="filters"><select id="outcome"><option value="">Tous les résultats</option><option value="good">Bonnes réponses</option><option value="bad">Mauvaises réponses</option></select><select id="language"><option value="">Toutes les langues</option><option value="fr">Français</option><option value="en">Anglais</option><option value="ja">Japonais</option></select><select id="film"><option value="">Toutes les œuvres</option>"""
page+=''.join('<option>'+html.escape(f)+'</option>' for f in films)
page+='</select><input id="search" type="search" placeholder="Rechercher une réplique"><span id="count">72 extraits</span></div><main id="clips">'
for r in records:
 page+=f'<article class="{r["outcome"]}" data-film="{html.escape(r["film"],quote=True)}" data-language="{r["language"]}"><h2>{"✓ Bonne réponse" if r["outcome"]=="good" else "✗ Mauvaise réponse"} — {html.escape(r["film"])}</h2><p class="caption">{html.escape(r["text"])}</p><p class="meta">{html.escape(r["voice"])} · {r["durationSeconds"]} s · {r["file"]}</p><audio controls preload="none" src="/tv/sounds/{r["file"]}"></audio><a class="meta" href="{html.escape(r["sourceUrl"],quote=True)}">Source de l’extrait</a></article>'
page+="""</main><script>const cards=[...document.querySelectorAll('article')];let channel=null;const owner='audition-'+Math.random();try{channel=new BroadcastChannel('triviaparty-debug-audio');channel.onmessage=e=>{if(e.data&&e.data.type==='claim'&&e.data.owner!==owner)document.querySelectorAll('audio').forEach(a=>a.pause())}}catch(e){}document.querySelectorAll('audio').forEach(a=>a.addEventListener('play',()=>{document.querySelectorAll('audio').forEach(b=>{if(a!==b)b.pause()});if(channel)channel.postMessage({type:'claim',owner})}));const fields=['outcome','language','film','search'].map(id=>document.getElementById(id));function filter(){let shown=0;cards.forEach(c=>{const visible=(!fields[0].value||c.classList.contains(fields[0].value))&&(!fields[1].value||c.dataset.language===fields[1].value)&&(!fields[2].value||c.dataset.film===fields[2].value)&&(!fields[3].value||c.textContent.toLocaleLowerCase().includes(fields[3].value.toLocaleLowerCase()));c.hidden=!visible;if(visible)shown++;else c.querySelector('audio').pause()});document.getElementById('count').textContent=shown+' extraits'}fields.forEach(f=>f.addEventListener('input',filter));</script></html>"""
(D/'credits.html').write_text(page,encoding='utf8');(D/'index.html').write_text(page.replace('/tv/sounds/','./'),encoding='utf8')
(ROOT/'audio-bank/movie-preview.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print(f'Prepared {len(records)} clips, {len(films)} works, languages {dict(counts)}; longest {max(r["durationSeconds"] for r in records)} seconds.')
