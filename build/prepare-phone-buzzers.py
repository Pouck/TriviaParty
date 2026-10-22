import urllib.request, pathlib,sys,subprocess,json,hashlib,array,math,html
sys.path.insert(0,str(pathlib.Path('build/audio-tools').resolve()));import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();cache=pathlib.Path('build/phone-audio-originals');cache.mkdir(exist_ok=True)
out=pathlib.Path('app/src/main/assets/tv/phone-sounds');out.mkdir(exist_ok=True)
cc0='https://creativecommons.org/publicdomain/zero/1.0/'
items=[
('wolf','Loup','https://upload.wikimedia.org/wikipedia/commons/8/87/Wolf_howls.ogg','https://commons.wikimedia.org/wiki/File:Wolf_howls.ogg','US Fish and Wildlife Service','Public domain','https://www.fws.gov/',2.4),
('owl','Hibou','https://sfxmint.com/dl/animal-owl-01.mp3','https://sfxmint.com/sounds/animal-owl-01','SFXMint','CC0-1.0',cc0,1.4),
('rooster','Coq','https://sfxmint.com/dl/rooster-crow-02.mp3','https://sfxmint.com/sounds/rooster-crow-02','SFXMint','CC0-1.0',cc0,2.4),
('dog','Chien','https://sfxmint.com/dl/animal-dog-bark-25.mp3','https://sfxmint.com/sounds/animal-dog-bark-25','SFXMint','CC0-1.0',cc0,1.0),
('bells','Cloches','https://sfxmint.com/dl/instrument-bell-36.mp3','https://sfxmint.com/sounds/instrument-bell-36','SFXMint','CC0-1.0',cc0,1.8),
('coyote','Coyote','https://upload.wikimedia.org/wikipedia/commons/6/67/Pack_of_coyotes_howling.ogg','https://commons.wikimedia.org/wiki/File:Pack_of_coyotes_howling.ogg','Rybkovich','CC BY-SA 4.0','https://creativecommons.org/licenses/by-sa/4.0/',2.1),
('boat','Bateau','https://upload.wikimedia.org/wikipedia/commons/b/b4/WWS_Steamwhistle.ogg','https://commons.wikimedia.org/wiki/File:WWS_Steamwhistle.ogg','Work With Sounds / Konrad Gutkowski','CC BY 4.0','https://creativecommons.org/licenses/by/4.0/',1.8),
('train','Train à vapeur','https://upload.wikimedia.org/wikipedia/commons/5/51/WWS_SteamWhistle.ogg','https://commons.wikimedia.org/wiki/File:WWS_SteamWhistle.ogg','Work With Sounds / Konrad Gutkowski','CC BY 4.0','https://creativecommons.org/licenses/by/4.0/',1.8)]
manifest=[]
for ident,label,url,page,author,license,license_url,duration in items:
 src=cache/(ident+pathlib.Path(url).suffix)
 if not src.exists():
  req=urllib.request.Request(url,headers={'User-Agent':'TriviaParty/1.0 sound asset preparation'})
  with urllib.request.urlopen(req,timeout=25) as r:
   data=r.read()
   if 'text/' in r.headers.get('Content-Type',''):raise ValueError('Not audio '+url)
  src.write_bytes(data)
 pcm=subprocess.check_output([ff,'-v','error','-i',str(src),'-ac','1','-ar','44100','-f','s16le','-'])
 samples=array.array('h',pcm); peak=max(abs(v) for v in samples); threshold=peak*.08
 # Skip quiet ambience before the first clear sound, retaining 8 ms of attack.
 first=next((i for i,v in enumerate(samples) if abs(v)>=threshold),0);start=max(0,first-353)/44100
 target=out/(ident+'.mp3');gain=18000/max(1,peak)
 subprocess.run([ff,'-v','error','-y','-ss',str(start),'-i',str(src),'-t',str(duration),'-ac','1','-ar','44100','-af',f'volume={gain},afade=t=out:st={max(.1,duration-.04)}:d=0.04','-codec:a','libmp3lame','-b:a','96k',str(target)],check=True)
 manifest.append(dict(id=ident,label=label,source=url,page=page,author=author,license=license,license_url=license_url,processing=f'Mono MP3; onset trimmed at {start:.3f}s; up to {duration}s excerpt; gain adjusted and 40ms tail fade',sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size))
 print(ident,target.stat().st_size,flush=True)
pathlib.Path('audio-bank/phone-buzzers.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
credits='<meta charset="utf-8"><title>Sons des buzzers</title><h1>Sons des téléphones</h1><p>Extraits raccourcis, convertis en mono, volume ajusté et fin adoucie. Les sons SFXMint sont générés ou synthétisés; les autres sont des enregistrements.</p>'
for x in manifest:credits+=f'<p>{html.escape(x["label"])} — {html.escape(x["author"])} · <a href="{x["page"]}">Source</a> · <a href="{x["license_url"]}">{x["license"]}</a><br>{html.escape(x["processing"])}</p>'
pathlib.Path('app/src/main/assets/player/sound-credits.html').write_text(credits,encoding='utf8')

