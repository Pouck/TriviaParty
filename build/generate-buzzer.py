"""Short game-show buzzer, synthesized locally and bundled for TV playback."""
import math,struct,wave
from pathlib import Path
rate=44100; duration=.48; samples=[]
for n in range(int(rate*duration)):
    t=n/rate
    attack=min(1,t/.012);release=min(1,(duration-t)/.07)
    signal=sum(math.sin(2*math.pi*frequency*t)/weight for frequency,weight in [(150,1),(300,2),(450,3),(600,4)])
    samples.append(struct.pack('<h',int(11000*attack*release*signal)))
with wave.open(str(Path('app/src/main/assets/tv/sounds/buzzer.wav')),'wb') as out:
    out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate);out.writeframes(b''.join(samples))
print('Generated 0.48-second TV buzzer.')
