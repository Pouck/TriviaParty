from pathlib import Path
s=Path('build/prepare-vadrouille-extracts.py').read_text(encoding='utf8').replace('build/dialogue-extracts/grande-vadrouille','build/dialogue-extracts/vadrouille-prisonnier').replace('grande-vadrouille-01-mauvais.mp3','grande-vadrouille-05-prisonnier.mp3')
a=s.index('plan=[');b=s.index('\nrows=[]',a)
s=s[:a]+'''plan=[('01-explication-ne-suffit-pas',41.55,43.22,"Votre explication ne me suffit pas !",'Réponse insuffisante'),('02-cest-pourtant-clair',43.22,44.35,"C’est pourtant clair !",'Réaction ironique')]'''+s[b:]
s=s.replace('La-Grande-Vadrouille-deux-dialogues.zip','Vadrouille-prisonnier-deux-dialogues.zip').replace("'-l','fr','-otxt'","'-l','fr','-mc','0','-otxt'")
Path('build/prepare-vadrouille-prisonnier-extracts.py').write_text(s,encoding='utf8')
