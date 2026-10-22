from pathlib import Path
import subprocess,sys,array,math,json
R=Path.cwd();D=R/'build/winner-music';sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
for id in ['zarathustra','pomp']:
 raw=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(D/'sources'/(id+'.source')),'-ar','1000','-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
 a=array.array('f');a.frombytes(raw);sec=[math.sqrt(sum(x*x for x in a[i:i+1000])/len(a[i:i+1000])) for i in range(0,len(a),1000)]
 print(id,[(i,round(sec[i],3)) for i in range(45,86,3)] if id=='zarathustra' else [(i,round(sec[i],3)) for i in range(280,345,5)])
