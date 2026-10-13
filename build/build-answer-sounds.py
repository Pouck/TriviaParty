"""Short original answer cues. No external recordings or music required."""
import math, struct, wave
from pathlib import Path
out=Path('app/src/main/assets/tv/sounds'); out.mkdir(parents=True,exist_ok=True)
for name,notes in [('good',[(660,.12),(880,.22)]),('bad',[(260,.16),(180,.24)])]:
    samples=[]; rate=22050
    for frequency,duration in notes:
        length=int(rate*duration)
        for i in range(length):
            envelope=min(1,i/(rate*.015),(length-i)/(rate*.035))
            samples.append(struct.pack('<h',int(10000*envelope*math.sin(2*math.pi*frequency*i/rate))))
    with wave.open(str(out/(name+'.wav')),'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(b''.join(samples))
