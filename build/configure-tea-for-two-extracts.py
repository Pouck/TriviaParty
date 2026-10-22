from pathlib import Path
s=Path('build/prepare-vadrouille-extracts.py').read_text(encoding='utf8').replace('build/dialogue-extracts/grande-vadrouille','build/dialogue-extracts/vadrouille-tea-for-two').replace('grande-vadrouille-01-mauvais.mp3','grande-vadrouille-04-tea-for-two.mp3')
a=s.index('plan=[');b=s.index('\nrows=[]',a)
s=s[:a]+'''plan=[('01-i-dont-know',71.10,75.10,"I don’t know! And if you don’t know, I don’t know, non ?",'Incertitude'),('02-i-dont-understand',75.12,76.95,"I don’t understand!",'Incompréhension')]'''+s[b:]
s=s.replace("str(W/'ggml-small.bin')","str(W/'ggml-base.bin')").replace("'-l','fr'","'-l','en'").replace('La-Grande-Vadrouille-deux-dialogues.zip','Vadrouille-Tea-for-Two-deux-dialogues.zip')
s=s.replace("film='La Grande Vadrouille',","film='La Grande Vadrouille',language='en',")
Path('build/prepare-tea-for-two-extracts.py').write_text(s,encoding='utf8')
