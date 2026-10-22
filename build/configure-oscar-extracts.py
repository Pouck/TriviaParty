from pathlib import Path
p=Path('build/prepare-vadrouille-extracts.py');s=p.read_text(encoding='utf8')
s=s.replace('build/dialogue-extracts/grande-vadrouille','build/dialogue-extracts/oscar').replace('https://www.fufuworld.com/data/contents/common/sounds/vadrouille/grande-vadrouille-01-mauvais.mp3','https://www.fufuworld.com/data/contents/common/sounds/oscar/oscar-02-augmentation.mp3')
a=s.index('plan=[');b=s.index('\nrows=[]',a)
s=s[:a]+'''plan=[('01-vous-vous-foutez-de-moi',10.15,13.5,"Dites, vous vous foutez de moi, là ?",'Réaction ironique'),('02-reponse-defavorable',34.05,37.45,"Bon alors, si je comprends bien, votre réponse est défavorable !",'Mauvaise réponse')]'''+s[b:]
s=s.replace('La Grande Vadrouille','Oscar').replace('La-Grande-Vadrouille-deux-dialogues.zip','Oscar-deux-dialogues.zip')
s=s.replace("status='extracted_for_review'","status='extracted_for_review',boundaryNote='Brief original spoken lead-in retained; no internal dialogue spliced or rewritten.'")
Path('build/prepare-oscar-extracts.py').write_text(s,encoding='utf8')
