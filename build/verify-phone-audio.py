import pathlib,sys,subprocess,array,json
sys.path.insert(0,str(pathlib.Path('build/audio-tools').resolve()));import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();result=[]
for p in pathlib.Path('app/src/main/assets/tv/phone-sounds').glob('*.mp3'):
 data=subprocess.check_output([ff,'-v','error','-i',str(p),'-ar','44100','-ac','1','-f','s16le','-'])
 values=array.array('h',data);duration=len(values)/44100;peak=max(map(abs,values));assert .3<duration<2.6 and 1000<peak<32767
 result.append({'id':p.stem,'duration':round(duration,3),'peak':peak})
assert len(result)==8
pathlib.Path('build/phone-audio-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
