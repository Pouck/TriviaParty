"""Original short positive/negative cues and a separate end-of-game fanfare."""
import math,struct,wave
from pathlib import Path
RATE=44100
def write(name,notes,duration):
    samples=[0.0]*int(duration*RATE)
    for start,frequency,length in notes:
        for n in range(int(length*RATE)):
            position=int(start*RATE)+n
            if position>=len(samples):break
            t=n/RATE
            envelope=min(1,t/.006)*math.exp(-t*7)*min(1,(length-t)/.045)
            samples[position]+=envelope*(math.sin(2*math.pi*frequency*t)+.18*math.sin(4*math.pi*frequency*t))
    scale=24000/max(max(abs(value) for value in samples),1)
    with wave.open(str(Path('app/src/main/assets/tv/sounds')/name),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(RATE)
        out.writeframes(b''.join(struct.pack('<h',int(value*scale)) for value in samples))
write('good-ping.wav',[(0,659.25,.22),(.1,987.77,.26)],.38)
write('bad-ping.wav',[(0,392,.21),(.11,233.08,.26)],.39)
write('game-end.wav',[(0,523.25,.3),(.17,659.25,.3),(.34,783.99,.3),(.52,1046.5,.65),(.52,659.25,.65),(.52,783.99,.65)],1.22)
print('Generated positive and negative pings and a separate end-of-game fanfare.')
