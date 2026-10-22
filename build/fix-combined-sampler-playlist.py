from pathlib import Path
p=Path('build/prepare-combined-dialogue-sampler.py');s=p.read_text(encoding='utf8').replace("active=c.querySelector('audio');try{await active.play()}","active=c.querySelector('audio');if(auto)active.currentTime=0;try{await active.play()}");p.write_text(s,encoding='utf8')
