"""Original spring buzzer, bright success bells, dark failure sting and finale."""
import math,random,struct,wave
from pathlib import Path
RATE=44100
OUT=Path('app/src/main/assets/tv/sounds');OUT.mkdir(parents=True,exist_ok=True)
def save(name,samples):
    peak=max(max(abs(x) for x in samples),.001)
    with wave.open(str(OUT/name),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,x/peak)) * 27000)) for x in samples))
def bells(notes,duration):
    out=[0.0]*int(duration*RATE)
    for start,freq,length in notes:
        for n in range(int(length*RATE)):
            j=int(start*RATE)+n
            if j>=len(out):break
            t=n/RATE;env=min(1,t/.003)*math.exp(-t*5)*min(1,(length-t)/.05)
            out[j]+=env*(math.sin(2*math.pi*freq*t)+.3*math.sin(2*math.pi*freq*2.01*t)+.12*math.sin(2*math.pi*freq*3.99*t))
    return out
# Bouncy spring: damped pitch wobble and frequency-modulated metallic overtones.
phase=0;spring=[];duration=.68
for n in range(int(duration*RATE)):
    t=n/RATE;frequency=190+700*math.exp(-t*5)*(1+.48*math.cos(2*math.pi*14*t))
    phase+=2*math.pi*frequency/RATE
    env=min(1,t/.004)*math.exp(-t*4.8)*min(1,(duration-t)/.06)
    spring.append(env*(math.sin(phase+1.2*math.exp(-t*4)*math.sin(phase*2.7))+.22*math.sin(phase*2)))
save('buzzer.wav',spring)
save('good-ping.wav',bells([(0,523.25,.5),(.09,659.25,.5),(.18,783.99,.5),(.30,1046.5,.5),(.30,659.25,.5),(.41,1567.98,.38)],.84))
# Descending minor sting: low growl, tritone tension, soft attack; no sudden loud jump.
rng=random.Random(13);bad=[];phase=0;duration=.8
for n in range(int(duration*RATE)):
    t=n/RATE;freq=210-90*min(1,t/.58);phase+=2*math.pi*freq/RATE
    env=min(1,t/.025)*math.exp(-t*2.1)*min(1,(duration-t)/.15)
    tone=math.sin(phase)+.28*math.sin(phase*2)+.16*math.sin(phase*3)+.45*math.sin(phase/math.sqrt(2))+.22*math.sin(phase/2)
    bad.append(env*(tone+.035*rng.uniform(-1,1)))
save('bad-ping.wav',bad)
save('game-end.wav',bells([(0,523.25,.3),(.17,659.25,.3),(.34,783.99,.3),(.52,1046.5,.65),(.52,659.25,.65),(.52,783.99,.65)],1.22))
print('Generated original spring buzzer, sparkling major success cue, ominous descending failure cue and finale.')
