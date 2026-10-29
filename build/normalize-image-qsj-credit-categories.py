from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'game-library/bank'
QUESTIONS=BANK/'questions.json'
CREDITS=BANK/'IMAGE-QSJ-MEDIA-CREDITS.json'
BACKUPS=ROOT/'review-backups'

def main():
 bank=json.loads(QUESTIONS.read_text(encoding='utf-8'))
 credits=json.loads(CREDITS.read_text(encoding='utf-8'))
 canonical={}
 for q in bank.get('questions',[]):
  for p in q.get('presentations',[]):
   c=p.get('content',{})
   u=c.get('imageUrl','')
   if not c.get('imageRevealMode') or not u.startswith('media/'): continue
   cat=p.get('legacyCategory','')
   if p.get('legacyPackageId') in {'image-qsj-animaux','image-qsj-figures-politiques'}:
    canonical[u.split('/',1)[1]]=cat
 changed=[]
 for filename,category in canonical.items():
  if filename in credits and credits[filename].get('category') != category:
   credits[filename]['category']=category
   changed.append(filename)
 if changed:
  BACKUPS.mkdir(parents=True,exist_ok=True)
  backup=BACKUPS/'credits-before-canonical-animal-politician-categories-2026-10-28.json'
  if not backup.exists(): shutil.copyfile(CREDITS,backup)
  CREDITS.write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'imagesChecked':len(canonical),'creditCategoriesUpdated':len(changed),'backup':str(backup) if changed else None},indent=2))
if __name__=='__main__': main()
