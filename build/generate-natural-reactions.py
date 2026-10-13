"""Replace desktop recordings with alternative speech voices and protected lead-ins."""
import concurrent.futures,json,pathlib,subprocess,sys,time,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'build/audio-tools'))
import imageio_ffmpeg
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
phrases=json.loads((ROOT/'build/answer-reactions.json').read_text(encoding='utf8'))
target=ROOT/'app/src/main/assets/tv/sounds';source=ROOT/'build/natural-voice-source';source.mkdir(exist_ok=True)
def generate(task):
    outcome,index,text=task
    language='de' if text.startswith(('Das ','Ja!')) else 'en-US' if text.startswith('What ') else 'en-GB' if text.startswith('Two ') else 'ru' if text=='Niet!' else 'fr'
    spoken='Нет!' if language=='ru' else text
    url='https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl='+language+'&q='+urllib.parse.quote(spoken)
    for attempt in range(3):
        try:
            response=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)
            blob=response.read();assert response.headers.get('Content-Type','').startswith('audio/') and len(blob)>1000
            break
        except Exception:
            if attempt==2:raise
            time.sleep(1)
    stem=f'{outcome}-{index:02}';mp3=source/f'{stem}.mp3';mp3.write_bytes(blob)
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(mp3),'-af','adelay=220,loudnorm=I=-16:TP=-2:LRA=8','-ar','44100','-ac','1','-c:a','pcm_s16le',str(target/f'{stem}.wav')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    return dict(outcome=outcome,file=stem+'.wav',text=text,language=language.split('-')[0],voice='Google speech '+language,leadInMs=220)
tasks=[(outcome,index,text) for outcome,values in phrases.items() for index,text in enumerate(values,1)]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(generate,tasks))
(target/'reactions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
confirmation=generate(('enabled',1,'Le son est activé !'))
(target/confirmation['file']).replace(target/'enabled.wav')
print(f'Generated {len(records)} recordings; {len({r["voice"] for r in records})} voices; 220 ms lead-in; loudness normalized.')
