from pathlib import Path
s=Path('build/prepare-oscar-extracts.py').read_text(encoding='utf8').replace('build/dialogue-extracts/oscar','build/dialogue-extracts/oscar-vole').replace('oscar-02-augmentation.mp3','oscar-04-vole.mp3')
a=s.index('plan=[');b=s.index('\nrows=[]',a)
s=s[:a]+'''plan=[('01-non-monsieur',2.34,3.05,"Non, Monsieur !",'Réponse négative'),('02-cest-pas-possible',13.3,16.38,"Ho… han… enfin, c’est… c’est pas possible !",'Incrédulité'),('03-qui-aurait-pu-croire',31.72,34.78,"Mais qui aurait pu croire une chose pareille ?!",'Surprise')]'''+s[b:]
s=s.replace('deux dialogues','trois dialogues').replace('deux passages','trois passages').replace('Deux formats','Deux formats').replace('Oscar-deux-dialogues.zip','Oscar-vole-trois-dialogues.zip').replace('Prepared two extracts','Prepared three extracts')
s=s.replace("+' / 2'","+' / '+clips.length")
s=s.replace("if(sequence&&i===0){clips[1].currentTime=0;clips[1].play()", "if(sequence&&i<clips.length-1){clips[i+1].currentTime=0;clips[i+1].play()")
s=s.replace('Cliquez sur le second lecteur pour continuer.','Cliquez sur le lecteur suivant pour continuer.')
Path('build/prepare-oscar-vole-extracts.py').write_text(s,encoding='utf8')
