from pathlib import Path
import json,sys,urllib.request,subprocess,wave,concurrent.futures
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[1];D=R/'build/movie-audition';C=D/'expanded-sources'
sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
catalog=json.loads((D/'all-bleeps.json').read_text(encoding='utf8'))
ids={'good':['AsterixFilm_2_QuonLeCouvreDor','AsterixFilm_2_CarrelageMagnifique','AsterixFilm_2_CaVaEtreBien','LeDinerDeCons_MaisCestEpatantCa','LaClasse_4_Jacques_Absolument_5','TheMask_BonjourLaClasse','AmericanPie_ItsBackToMeNow','la-force-est-toujours-avec-lui','AmericanPie_OfCourseItCounts','MinusEtCortex_ConquerirLeMonde_short'],'bad':['AsterixFilm_2_PasDePalais','AsterixFilm_2_JeVoisPasEnQuoiCestUneBonneNouvelle','PamelaRose1_AttentionTuVasDireUneConnerie','PamelaRose1_JaiLimpressionVousNousPrenezPourDesPloucs','LaClasse_4_Jacques_CaVaPlusDuTout','AmericanPie_OhYouWereShit','pourtant-ctait-bien-parti','jai-connu-mieux','Spiderman94_TiensYaPuDeGaz','Aladdin_JafarJsuisCoince']}
old=json.loads((R/'audio-bank/movie-reactions-selection.json').read_text(encoding='utf8')); rows=[]
for outcome,names in ids.items():
 for i,name in enumerate(names):
  x=next(x for x in catalog if x['name_unique']==name and x['lang']=='FR')
  r=dict(file=f'{outcome}-{40+i:02}.wav',outcome=outcome,language='fr',film=x['source_name'],voice=(x['speaker_name']+' (version française)' if x['source_name'] in ['American Pie 2','The Mask','Minus et Cortex','Aladdin','Spiderman 1994 tv series'] else ' / '.join(v for v in [x['actor_name'],x['speaker_name']] if v)),text=x['name'],sourceUrl='https://www.bleeps.wtf/bleep/'+name,downloadUrl=x['sound'],sourceType='film_or_series_dialogue',usage='Private on-device audition; no redistribution permission asserted',audience='unreviewed',verification='Public catalog metadata and offline speech recognition; audience review pending.')
  assert r['file'] not in {o['file'] for o in old};assert r['downloadUrl'] not in {o['downloadUrl'] for o in old}
  rows.append(r)
(D/'expansion-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
def prepare(r):
 name=r['file'];src=C/(name+'.source');wav=C/(name+'.wav')
 if not src.exists():src.write_bytes(urllib.request.urlopen(r['downloadUrl'],timeout=30).read())
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(src),'-ar','16000','-ac','1',str(wav)],check=True,capture_output=True)
 with wave.open(str(wav)) as w:r['sourceDurationSeconds']=round(w.getnframes()/w.getframerate(),3)
 subprocess.run([str(D/'whisper-bin/Release/whisper-cli.exe'),'-m',str(D/'ggml-base.bin'),'-f',str(wav),'-l','fr','-nt','-otxt','-of',str(C/name),'-t','4'],check=True,capture_output=True)
 r['transcript']=(C/(name+'.txt')).read_text(encoding='utf8').strip()
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for r in pool.map(prepare,rows):print(r['file'],r['sourceDurationSeconds'],r['text'],'=>',r['transcript'],flush=True)
(D/'expansion-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
