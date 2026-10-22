from pathlib import Path
import json,re,hashlib
R=Path.cwd();D=R/'build/dialogue-extracts/X1PiR7WfuWs'
old=json.loads((D/'dialogues.json').read_text(encoding='utf8'));(D/'before-removal-hashes.json').write_text(json.dumps({r['id']:{k:r[k] for k in ['sha256','mp3Sha256']} for r in old},indent=2),encoding='utf8')
p=R/'build/export-requested-dialogues.py';s=p.read_text(encoding='utf8')
s=s.replace("for r in rows:\n start=", "rows=[r for r in rows if not r['id'].startswith(('03-','04-'))]\nfor r in rows:\n start=",1)
a=s.index('# Wider context');b=s.index("(D/'dialogues.json')",a);s=s[:a]+s[b:]
a=s.index(' if n==3:');b=s.index(" page+='</article>'",a);s=s[:a]+s[b:]
s=s.replace('sept dialogues','cinq dialogues').replace('sept passages demandés','cinq passages retenus').replace('sept extraits','cinq extraits').replace('sept dialogues','cinq dialogues').replace('La-Chevre-sept-dialogues.zip','La-Chevre-cinq-dialogues.zip')
s=s.replace('{n:02d} —','{r["id"][:2]} —')
s=s.replace('Extraits 3 et 4 légèrement rallongés. Les cinq autres extraits sont approuvés et inchangés.','Les extraits 3 et 4 ont été retirés. Les cinq extraits conservés sont approuvés et inchangés.')
s=s.replace("+' / 7'","+' / '+clips.length")
a=s.index('La troisième légende');b=s.index("\\n\\n'",a);s=s[:a]+'Les extraits originaux 3 et 4 ont été retirés à votre demande. Les cinq autres fichiers sont conservés à l’identique.'+s[b:]
s=s.replace("['index.html','README.md','dialogues.json','03-context.mp3']","['index.html','README.md','dialogues.json']")
s=s.replace('Exported seven WAV/MP3 pairs','Exported five WAV/MP3 pairs')
p.write_text(s,encoding='utf8')
audit=json.loads((D/'cut-audit.json').read_text(encoding='utf8'));audit=[r for r in audit if not r['id'].startswith(('03-','04-'))];(D/'cut-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
