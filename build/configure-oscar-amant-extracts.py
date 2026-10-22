from pathlib import Path
s=Path('build/prepare-oscar-extracts.py').read_text(encoding='utf8').replace("build/dialogue-extracts/oscar'","build/dialogue-extracts/oscar-amant'").replace('oscar-02-augmentation.mp3','oscar-05-amant.mp3')
a=s.index('plan=[');b=s.index('\nrows=[]',a)
s=s[:a]+'''plan=[('01-vous-restez-vous-sortez',47.85,50.25,"Ou, plutôt, non ! Vous, restez, et vous, sortez !",'Changement de décision'),('02-reflechir-dans-la-cuisine',56.85,59.25,"Allez réfléchir à ça dans la cuisine, vous !",'Mauvaise réponse')]'''+s[b:]
s=s.replace('Oscar-deux-dialogues.zip','Oscar-amant-deux-dialogues.zip');Path('build/prepare-oscar-amant-extracts.py').write_text(s,encoding='utf8')
