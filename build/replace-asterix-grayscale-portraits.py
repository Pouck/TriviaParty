"""Replace grayscale Astérix drawings with reviewed full-color character art."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'game-library/bank/questions.json'
CREDITS=ROOT/'game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json'
CANDIDATES=ROOT/'build/image-qsj-sampler/candidates/asterix-color'
REVISION='2026-10-27-replaced-asterix-grayscale-with-color-art'
# answer, old canonical media, reviewed color source, source page, direct image, owner, source description
ITEMS=[
 ('Astérix','12c4f6d56d16b9f893d04bbc.png','asterix.png','https://www.salvat.com/asterix-86','https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes2.png','Les Éditions Albert René / Goscinny-Uderzo','Salvat licensed character gallery'),
 ('Obélix','fb4df522418d73fa0728088c.png','obelix-color.png','https://imgbin.com/png/MVnURjXd/obelix-asterix-cartoon-comic-book-comics-png','https://cdn.imgbin.com/25/25/5/imgbin-obelix-asterix-cartoon-comic-book-comics-asterix-and-obelix-CN81BUgtyeE0nin5Gv2zMMU8M.jpg','Les Éditions Albert René / Goscinny-Uderzo','Classic single-character comic illustration; checkerboard preview removed'),
 ('Idéfix','8b31f2b50617aa358f7d0dd1.png','idefix-color-clean.png','https://imgbin.com/png/FAPehcsR/obelix-getafix-dogmatix-falbala-png','https://cdn.imgbin.com/14/6/12/imgbin-obelix-getafix-dogmatix-falbala-asterix-XuN9nY1zJwq3sYWWmJq7MJM62.jpg','Les Éditions Albert René / Goscinny-Uderzo','Classic single-character comic illustration; checkerboard preview removed'),
 ('Panoramix','15584210ce0308740651940f.png','panoramix-color-clean.png','https://www.pngwing.com/en/free-png-pmcwe','https://w7.pngwing.com/pngs/243/1000/png-transparent-getafix-obelix-jules-cesar-asterix-dogmatix-getafix-comics-food-vertebrate.png','Les Éditions Albert René / Goscinny-Uderzo','Classic single-character comic illustration; checkerboard preview removed'),
 ('Falbala','42fb51ddf7ad6aa27edc23ff.png','falbala.png','https://www.salvat.com/asterix-86','https://www.salvat.com/img/cms/Ast%C3%A9rix%202024/personajes6.png','Les Éditions Albert René / Goscinny-Uderzo','Salvat licensed character gallery'),
]

bank=json.loads(BANK.read_text(encoding='utf-8'))
credits=json.loads(CREDITS.read_text(encoding='utf-8'))
if any(x.get('id')==REVISION for x in bank.get('revisionHistory',[])):
 raise SystemExit('Color portrait replacement already applied')
backup=ROOT/'review-backups';backup.mkdir(exist_ok=True)
(backup/'questions-before-asterix-color-replacements-2026-10-27.json').write_text(BANK.read_text(encoding='utf-8'),encoding='utf-8')
(backup/'credits-before-asterix-color-replacements-2026-10-27.json').write_text(CREDITS.read_text(encoding='utf-8'),encoding='utf-8')
added=[]
for answer,old_name,candidate_name,source,direct,creator,source_desc in ITEMS:
 candidate=CANDIDATES/candidate_name
 if not candidate.is_file(): raise FileNotFoundError(candidate)
 data=candidate.read_bytes();new_name=hashlib.sha256(data).hexdigest()[:24]+candidate.suffix.lower()
 target=ROOT/'game-library/bank/media'/new_name;target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copyfile(candidate,target)
 old_url='media/'+old_name;new_url='media/'+new_name;matches=[]
 for q in bank['questions']:
  for p in q.get('presentations',[]):
   if (p.get('content') or {}).get('imageUrl')==old_url:
    p['content']['imageUrl']=new_url;matches.append((q,p))
 if len(matches)!=1: raise ValueError(f'{answer}: expected exactly one old presentation, found {len(matches)}')
 q,p=matches[0]
 for fact in q.get('imageFacts',{}).get('facts',[]):
  if fact.get('kind')=='media_creator':
   fact['value']=creator;fact['sourceUrl']=source
 source_bytes=len(data)
 credits[new_name]={
  'filename':candidate_name,'title':f'{answer} — full-color character artwork','creator':creator,
  'credit':f'© {creator}','license':'Copyrighted character artwork; rights reserved; private local use only',
  'licenseUrl':source,'source':source,'downloadedFrom':direct,'localSource':source_desc,
  'question':answer,'category':p.get('legacyCategory',''),
  'visualReview':'Approved: full-color, canonical single character with no lettering or second subject. Checkerboard preview background was removed where present; the character art itself was retained. Private local gameplay only; do not redistribute.'}
 added.append({'answer':answer,'presentationId':p['id'],'oldImage':old_url,'newImage':new_url,'bytes':source_bytes})

bank.setdefault('revisionHistory',[]).append({
 'id':REVISION,
 'note':'Replaced all five grayscale Astérix character portraits (Astérix, Obélix, Idéfix, Panoramix, Falbala) with reviewed full-color single-character art. The default white-background line drawings were not suitable for the progressive blur reveal. Replacement assets and source/license notes are recorded; rights reserved and private-local-gameplay-only.',
 'createdQuestions':0,'addedPresentationsToExistingQuestions':len(added),
 'presentationIds':[x['presentationId'] for x in added]})
BANK.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
CREDITS.write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'replaced':added},ensure_ascii=False,indent=2))
