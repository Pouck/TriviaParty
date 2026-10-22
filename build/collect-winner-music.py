from pathlib import Path
import json,urllib.request,re,html,concurrent.futures,sys,subprocess,time,urllib.error
R=Path.cwd();D=R/'build/winner-music';S=D/'sources';S.mkdir(exist_ok=True);sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf8')
choices=[('zarathustra','Also Sprach Zarathustra - Einleitung.ogg','Richard Strauss','Ainsi parlait Zarathoustra — lever du soleil','Monumental, théâtral ; une révélation du grand gagnant.'),('te-deum','Charpentier, Te Deum (Prelude).ogg','Marc-Antoine Charpentier','Te Deum — prélude','Royal, lumineux ; un podium très cérémoniel.'),('fireworks','George Frideric Handel - Music for the Royal Fireworks 4 (La Rejouissance).ogg','Georg Friedrich Händel','La Réjouissance — Musique pour les feux d’artifice royaux','Festif, élégant ; une victoire joyeuse.'),('aida','Aida-Trompeten.ogg','Giuseppe Verdi','Aïda — marche triomphale','Cuivres éclatants ; une entrée de champion.'),('pomp','ELGAR Pomp and Circumstance in D, Opus 39, No. 1 - United States Marine Band.mp3','Edward Elgar','Pomp and Circumstance — marche nº 1','Solennel, majestueux ; une remise de trophée.'),('kiev','Modest Mussorgsky - pictures at an exhibition - x. la grande porte de kiev - allegro alla breve. maestoso. con grandezza.ogg','Modeste Moussorgski','La Grande Porte de Kiev','Massif, noble ; une victoire épique.'),('william-tell','Gioachino Rossini, William Tell Overture (military band version, 2000).ogg','Gioachino Rossini','Guillaume Tell — finale','Vif, héroïque ; une arrivée victorieuse et enjouée.')]
rows=[]
for id,title,composer,label,mood in choices:
 pages=json.loads((D/(id+'-search.json')).read_text(encoding='utf8'))['query']['pages'].values();p=next(p for p in pages if p['title']=='File:'+title);i=p['imageinfo'][0];m=i['extmetadata']
 def val(k):return html.unescape(re.sub('<.*?>',' ',m.get(k,{}).get('value',''))).strip()
 rows.append(dict(id=id,composer=composer,title=label,mood=mood,sourceTitle=p['title'],sourceUrl=i['descriptionurl'],downloadUrl=i['url'],credit=val('Artist'),description=val('ImageDescription'),license=val('LicenseShortName'),licenseUrl=val('LicenseUrl'),sourceCreditHtml=m.get('Credit',{}).get('value','')))
def get(r):
 p=S/(r['id']+'.source')
 if not p.exists():
  for attempt in range(3):
   try:
    with urllib.request.urlopen(urllib.request.Request(r['downloadUrl'],headers={'User-Agent':'TriviaPartySampler/1.0'}),timeout=45) as res:p.write_bytes(res.read())
    time.sleep(2);break
   except urllib.error.HTTPError as error:
    if error.code!=429 or attempt==2:raise
    delay=max(30,int(error.headers.get('Retry-After','30')))
    if delay>60:raise
    print(r['id'],'rate limited; waiting',delay,'seconds',flush=True);time.sleep(delay)
 probe=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(p)],capture_output=True,text=True)
 match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',probe.stderr);r['sourceDurationSeconds']=sum(float(v)*unit for v,unit in zip(match.groups(),[3600,60,1]));print(r['id'],r['sourceDurationSeconds'],r['description'][:100],flush=True);return r
transcodes=json.loads((D/'official-transcodes.json').read_text(encoding='utf8'))
for r in rows:
 if r['id']=='pomp':
  info=next(p for p in transcodes['query']['pages'].values() if p['title']==r['sourceTitle'])
  r['downloadUrl']=next(d['src'] for d in info['videoinfo'][0]['derivatives'] if d.get('transcodekey')=='ogg')
results=[]
for r in rows:
 try:results.append(get(r))
 except Exception as e:print(r['id'],'unavailable:',str(e),flush=True)
rows=results
(D/'source-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
