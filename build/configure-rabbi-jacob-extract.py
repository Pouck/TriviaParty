from pathlib import Path
import wave
D=Path('build/dialogue-extracts/rabbi-jacob')
with wave.open(str(D/'source-16k.wav')) as w:print('Source duration:',w.getnframes()/w.getframerate())
s=Path('build/prepare-folie-des-grandeurs-extract.py').read_text(encoding='utf8').replace('build/dialogue-extracts/folie-des-grandeurs','build/dialogue-extracts/rabbi-jacob').replace('https://www.fufuworld.com/data/contents/common/sounds/grandeurs/folie-grandeurs-02-flatterie.mp3','https://www.fufuworld.com/data/contents/common/sounds/rabbi-jacob/rabbi-jacob-04-jewish.mp3').replace('Est-ce que vous pensez vraiment ce que vous dites ?',"Écoutez, ça fait rien, j’vous garde quand même !").replace('start=56.28;end=59.5','start=58.5;end=61.6').replace('pensez-vraiment-ce-que-vous-dites','je-vous-garde-quand-meme').replace('La Folie des grandeurs','Les Aventures de Rabbi Jacob').replace('56,28–59,50','58,50–61,60');Path('build/prepare-rabbi-jacob-extract.py').write_text(s,encoding='utf8')
