import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8')
r=json.loads(Path('build/movie-audition/all-bleeps.json').read_text(encoding='utf8'))
terms=['QuonLeCouvre','Carrelage','CaVaEtreBien','Epatant','Absolument','BonjourLaClasse','BackToMe','force-est','OfCourse','ConquerirLeMonde_short','PasDePalais','BonneNouvelle','VasDire','Ploucs','CaVaPlus','WereShit','bien-parti','connu-mieux','PuDeGaz','JsuisCoince','VoisOuBien','Anatoni']
for x in r:
 if x.get('lang')=='FR' and any(t.lower() in x['name_unique'].lower() for t in terms): print(json.dumps(x,ensure_ascii=False))
