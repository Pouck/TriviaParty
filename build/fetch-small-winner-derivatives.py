from pathlib import Path
import json,urllib.request,time,sys,subprocess
R=Path.cwd();D=R/'build/winner-music';j=json.loads((D/'official-transcodes.json').read_text(encoding='utf8'));sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
# Request the lower-bandwidth MP3 derivatives offered by Commons, not the large originals.
for id,term in [('kiev','Modest Mussorgsky'),('william-tell','Gioachino Rossini')]:
 p=next(p for p in j['query']['pages'].values() if term in p['title']);url=next(d['src'] for d in p['videoinfo'][0]['derivatives'] if d.get('transcodekey')=='mp3')
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TriviaPartySampler/1.0'}),timeout=40) as res:(D/'sources'/(id+'.source')).write_bytes(res.read())
  print(id,'official compressed derivative downloaded',flush=True)
 except Exception as e:print(id,str(e),flush=True)
 time.sleep(3)
