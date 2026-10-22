from pathlib import Path
import wave,array,math,subprocess,sys
D=Path('build/dialogue-extracts/X1PiR7WfuWs');w=wave.open(str(D/'source-16k.wav'));w.setpos(int(35.5*16000));a=array.array('h',w.readframes(int(3.5*16000)))
for i in range(0,len(a),1600):
 x=a[i:i+1600];print(round(35.5+i/16000,1),round(math.sqrt(sum(v*v for v in x)/len(x))/32768,3))
