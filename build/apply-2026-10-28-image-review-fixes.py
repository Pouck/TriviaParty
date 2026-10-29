from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'game-library/bank'
QUESTIONS=BANK/'questions.json'
CREDITS=BANK/'IMAGE-QSJ-MEDIA-CREDITS.json'
MEDIA=BANK/'media'
REVIEW=ROOT/'build/image-qsj-gallery/review-imported-2026-10-28-0312Z.json'
BACKUPS=ROOT/'review-backups'
CANDIDATES=ROOT/'build/image-qsj-sampler/candidates/review-2026-10-28-followup'
REPLACEMENTS=[
 {'key':'alps','answers':{'Alpes'},'file':'alps.jpg','title':'Mountain panorama of the Alps (Dolomites and Schlern)','creator':'Lukas Koester','license':'CC BY-SA 4.0','licenseUrl':'https://creativecommons.org/licenses/by-sa/4.0/','source':'https://commons.wikimedia.org/wiki/File:20-06-2020_-_Alps_panorama.jpg','note':'Replaced the weak landscape with a wide, color panorama clearly showing the Alps; left Review for user approval.'},
 {'key':'empire-state','answers':{'Empire State Building'},'file':'empire-state-exterior.jpg','title':'Exterior of the Empire State Building','creator':'Yair Haklai','license':'CC BY-SA 3.0','licenseUrl':'https://creativecommons.org/licenses/by-sa/3.0/','source':'https://commons.wikimedia.org/wiki/File:Exterior_of_the_Empire_State_Building-Manhattan-New_York.jpg','note':'Replaced the weak image with a clear exterior photo of the complete Empire State Building; left Review for user approval.'},
]
def main():
 bank=json.loads(QUESTIONS.read_text(encoding='utf-8'))
 credits=json.loads(CREDITS.read_text(encoding='utf-8'))
 review=json.loads(REVIEW.read_text(encoding='utf-8'))
 # Back up canonical files once, before mutating.
 BACKUPS.mkdir(parents=True,exist_ok=True)
 for src,name in ((QUESTIONS,'questions-before-2026-10-28-image-review-fixes.json'),(CREDITS,'credits-before-2026-10-28-image-review-fixes.json'),(REVIEW,'gallery-review-before-2026-10-28-image-review-fixes.json')):
  dest=BACKUPS/name
  if not dest.exists(): shutil.copyfile(src,dest)
 updated=[]
 for item in REPLACEMENTS:
  source=CANDIDATES/item['file']
  data=source.read_bytes()
  filename=hashlib.sha256(data).hexdigest()[:24]+'.jpg'
  dest=MEDIA/filename
  dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists(): dest.write_bytes(data)
  targets=[]
  for q in bank.get('questions',[]):
   if not (set(q.get('answers',[])) & item['answers']): continue
   for p in q.get('presentations',[]):
    if p.get('content',{}).get('imageRevealMode') and p.get('content',{}).get('imageUrl','').startswith('media/'):
     targets.append((q,p))
  if len(targets)!=1: raise RuntimeError(f"{item['key']}: expected exactly one target, found {len(targets)}")
  q,p=targets[0]
  old=p['content'].get('imageUrl')
  if old==f'media/{filename}': continue
  p['content']['imageUrl']=f'media/{filename}'
  credits[filename]={
   'filename':source.name,'title':item['title'],'creator':item['creator'],'credit':item['creator'],
   'license':item['license'],'licenseUrl':item['licenseUrl'],'source':item['source'],
   'downloadedFrom':f"https://commons.wikimedia.org/wiki/Special:Redirect/file/{item['source'].split('File:')[-1].replace(' ','_')}?width=1280",
   'localSource':str(source.relative_to(ROOT)).replace('\\','/'),'question':' | '.join(q.get('answers',[])),
   'category':p.get('legacyCategory',''),'visualReview':'Candidate inspected; suitable target image; pending user approval.'
  }
  review.setdefault('items',{})['gallery-'+filename.rsplit('.',1)[0]]={'rating':'review','note':item['note']}
  updated.append({'key':item['key'],'from':old,'to':f'media/{filename}','presentationId':p.get('id')})
 if updated:
  already={r.get('id') for r in bank.get('revisionHistory',[])}
  if '2026-10-28-latest-image-review-replacements' not in already:
   bank.setdefault('revisionHistory',[]).append({'id':'2026-10-28-latest-image-review-replacements','note':'Replaced weak Alps and Empire State Building images using visually checked Wikimedia Commons photos; both are marked Review in the image gallery for user approval.','updatedPresentations':len(updated),'presentationIds':[x['presentationId'] for x in updated]})
  QUESTIONS.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  CREDITS.write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  REVIEW.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'updated':updated,'backupDir':str(BACKUPS)},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
