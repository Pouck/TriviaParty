from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'game-library/bank'
QUESTIONS=BANK/'questions.json'; CREDITS=BANK/'IMAGE-QSJ-MEDIA-CREDITS.json'; MEDIA=BANK/'media'
OLD_REVIEW=ROOT/'build/image-qsj-gallery/review-imported-2026-10-28-0312Z.json'
NEW_REVIEW=ROOT/'build/image-qsj-gallery/review-imported-2026-10-28-1341Z.json'
LATEST_EXPORT=Path(r'C:\Users\pierr\Downloads\qsj-image-gallery-review (4).json')
CAND=ROOT/'build/image-qsj-sampler/candidates/review-2026-10-28-round2'
BACKUPS=ROOT/'review-backups'
REV='2026-10-28-latest-gallery-review-replacements'

def image_file(name:str)->tuple[str,bytes]:
 data=(CAND/name).read_bytes(); ext=Path(name).suffix.lower(); filename=hashlib.sha256(data).hexdigest()[:24]+ext
 dest=MEDIA/filename; dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists(): dest.write_bytes(data)
 return filename,data

def main():
 bank=json.loads(QUESTIONS.read_text(encoding='utf-8'))
 credits=json.loads(CREDITS.read_text(encoding='utf-8'))
 old_review=json.loads(OLD_REVIEW.read_text(encoding='utf-8'))
 latest=json.loads(LATEST_EXPORT.read_text(encoding='utf-8'))
 BACKUPS.mkdir(parents=True,exist_ok=True)
 for src,name in ((QUESTIONS,'questions-before-review4-replacements-2026-10-28.json'),(CREDITS,'credits-before-review4-replacements-2026-10-28.json'),(OLD_REVIEW,'gallery-review-before-review4-import-2026-10-28.json')):
  dst=BACKUPS/name
  if not dst.exists(): shutil.copyfile(src,dst)
 # Seed from previous imported review, then let the newest export override it.
 review_items={**old_review.get('items',{}),**latest.get('items',{})}
 questions=bank.get('questions',[]); changed=[]; new_review_entries=[]
 # Replace the weak panoramic Alps presentation with a distinct Matterhorn question, retaining its MC question.
 alps_q=next((q for q in questions if q.get('id')=='geo-chaines-de-montagnes-20261010-06'),None)
 if alps_q:
  alps_q['presentations']=[p for p in alps_q.get('presentations',[]) if p.get('id')!='image-qsj-alps']
  alps_q['legacyIds']=[x for x in alps_q.get('legacyIds',[]) if x!='image-qsj-alps']
 if not any(q.get('id')=='image-qsj-landscape-matterhorn' for q in questions):
  filename,_=image_file('matterhorn.jpg')
  matterhorn={
   'id':'image-qsj-landscape-matterhorn','legacyIds':['image-qsj-landscape-matterhorn'],
   'topics':['Géographie','Paysages célèbres'],'prompt':'Quel sommet alpin célèbre est reconnaissable à sa silhouette pyramidale ?',
   'answers':['Le Cervin','Cervin','Matterhorn','Mont Cervin'],'content':{},
   'presentations':[{'id':'image-qsj-landscape-matterhorn','label':'Qui suis-je ? — image','answerMode':'BUZZER','topic':'Géographie','legacyCategory':'Géographie — Paysages célèbres — Qui suis-je ?','legacyPackageId':'image-qsj-paysages-celebres','content':{'kind':'guessWho','prompt':'Qui suis-je ?','clues':[],'imageRevealMode':'PIXELATE','imageRevealSteps':6,'imageUrl':'media/'+filename,'basePoints':30,'penaltyPoints':0}}],
   'explanation':'Le Cervin, appelé Matterhorn en allemand et en anglais, est un sommet emblématique des Alpes suisses, près de Zermatt.',
   'legacyReviews':[],
   'imageFacts':{'subjectType':'landscape','subjectTitle':'Le Cervin (Matterhorn)','frenchTitle':'Le Cervin','facts':[{'kind':'subject_title','value':'Peak of Matterhorn in Swiss Alps','sourceUrl':'https://commons.wikimedia.org/wiki/File:Peak_of_Matterhorn.jpg'},{'kind':'location','role':'mountain range and country','value':'Alpes suisses, Suisse','sourceUrl':'https://commons.wikimedia.org/wiki/File:Peak_of_Matterhorn.jpg'},{'kind':'media_creator','role':'photographer','value':'Olha Solodenko','sourceUrl':'https://commons.wikimedia.org/wiki/File:Peak_of_Matterhorn.jpg'}],'sources':['https://commons.wikimedia.org/wiki/File:Peak_of_Matterhorn.jpg']}}
  questions.append(matterhorn)
  credits[filename]={'filename':'Peak of Matterhorn.jpg','title':'Peak of Matterhorn in Swiss Alps','creator':'Olha Solodenko','credit':'Olha Solodenko','license':'CC BY-SA 4.0','licenseUrl':'https://creativecommons.org/licenses/by-sa/4.0/','source':'https://commons.wikimedia.org/wiki/File:Peak_of_Matterhorn.jpg','downloadedFrom':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Peak_of_Matterhorn.jpg?width=1280','localSource':'build/image-qsj-sampler/candidates/review-2026-10-28-round2/matterhorn.jpg','question':'Le Cervin (Matterhorn)','category':'Géographie — Paysages célèbres — Qui suis-je ?','visualReview':'Image depicts a single distinctive, recognizable Alps summit; pending user approval.'}
  new_review_entries.append(('gallery-'+filename.rsplit('.',1)[0],{'rating':'review','note':'New distinct Matterhorn target replacing the generic Alps panorama; please review.'}))
  changed.append({'target':'Alps panorama -> Matterhorn','image':'media/'+filename})
 # Replace the mallard photo with a male drake whose green head and yellow bill are distinctive.
 mallard=next((p for q in questions for p in q.get('presentations',[]) if p.get('id')=='image-qsj-animal-mallard-duck'),None)
 if mallard:
  filename,_=image_file('mallard-drake.jpg')
  mallard['content']['imageUrl']='media/'+filename
  q=next(q for q in questions if mallard in q.get('presentations',[]))
  q['imageFacts']={'subjectType':'animal','subjectTitle':'Mallard drake (Anas platyrhynchos)','frenchTitle':'Canard colvert mâle','facts':[{'kind':'subject_title','value':'Mallard Drake','sourceUrl':'https://commons.wikimedia.org/wiki/File:Mallard_Drake._(13962535717).jpg'},{'kind':'media_creator','role':'photographer','value':'Bernard Spragg. NZ','sourceUrl':'https://commons.wikimedia.org/wiki/File:Mallard_Drake._(13962535717).jpg'}],'sources':['https://commons.wikimedia.org/wiki/File:Mallard_Drake._(13962535717).jpg']}
  credits[filename]={'filename':'Mallard Drake. (13962535717).jpg','title':'Mallard drake','creator':'Bernard Spragg. NZ','credit':'Bernard Spragg. NZ','license':'CC0 1.0','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/','source':'https://commons.wikimedia.org/wiki/File:Mallard_Drake._(13962535717).jpg','downloadedFrom':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Mallard_Drake._(13962535717).jpg?width=1280','localSource':'build/image-qsj-sampler/candidates/review-2026-10-28-round2/mallard-drake.jpg','question':'Canard colvert','category':mallard.get('legacyCategory',''),'visualReview':'Single male mallard with distinctive green head and yellow bill; pending user approval.'}
  new_review_entries.append(('gallery-'+filename.rsplit('.',1)[0],{'rating':'review','note':'Replacement drake shows the distinctive green head and yellow bill; please review.'}))
  changed.append({'target':'female mallard -> male drake','image':'media/'+filename})
 # Replace the lower-prominence Jacinda entry with Indira Gandhi, using the official Government of India portrait.
 jac_idx=next((i for i,q in enumerate(questions) if q.get('id')=='image-qsj-politician-jacinda-ardern'),None)
 if jac_idx is not None:
  filename,_=image_file('indira-gandhi.png')
  presentation={'id':'image-qsj-politician-indira-gandhi','label':'Qui suis-je ? — image','answerMode':'BUZZER','topic':'Histoire','legacyCategory':'Histoire — Personnalités politiques — Qui suis-je ?','legacyPackageId':'image-qsj-figures-politiques','content':{'kind':'guessWho','prompt':'Qui suis-je ?','clues':[],'imageRevealMode':'PIXELATE','imageRevealSteps':6,'imageUrl':'media/'+filename,'basePoints':30,'penaltyPoints':0}}
  replacement={'id':'image-qsj-politician-indira-gandhi','legacyIds':['image-qsj-politician-indira-gandhi'],'topics':['Histoire','Personnalités politiques'],'prompt':'Quelle Première ministre indienne a dirigé le pays de 1966 à 1977, puis de 1980 à 1984 ?','answers':['Indira Gandhi','Indira Priyadarshini Gandhi','Madame Gandhi'],'content':{},'presentations':[presentation],'explanation':'Indira Gandhi fut Première ministre de l’Inde de 1966 à 1977, puis de 1980 à 1984.','legacyReviews':[],'imageFacts':{'subjectType':'political_figure','subjectTitle':'Indira Gandhi','frenchTitle':'Indira Gandhi','facts':[{'kind':'subject_title','value':'Indira Gandhi, official portrait (1983)','sourceUrl':'https://commons.wikimedia.org/wiki/File:Indira_Gandhi_official_portrait.png'},{'kind':'political_role','value':'Première ministre de l’Inde, 1966–1977 et 1980–1984','sourceUrl':'https://www.pmindia.gov.in/en/former_pm/smt-indira-gandhi/'},{'kind':'location','role':'country','value':'Inde','sourceUrl':'https://www.pmindia.gov.in/en/former_pm/smt-indira-gandhi/'}],'sources':['https://commons.wikimedia.org/wiki/File:Indira_Gandhi_official_portrait.png','https://www.pmindia.gov.in/en/former_pm/smt-indira-gandhi/']}}
  questions[jac_idx]=replacement
  credits[filename]={'filename':'Indira Gandhi official portrait.png','title':'Indira Gandhi official portrait (1983)','creator':'Prime Minister’s Office, Government of India','credit':'Prime Minister’s Office, Government of India','license':'Government Open Data License – India (GODL)','licenseUrl':'https://data.gov.in/government-open-data-license-india','source':'https://commons.wikimedia.org/wiki/File:Indira_Gandhi_official_portrait.png','downloadedFrom':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Indira_Gandhi_official_portrait.png?width=1100','localSource':'build/image-qsj-sampler/candidates/review-2026-10-28-round2/indira-gandhi.png','question':'Indira Gandhi','category':'Histoire — Personnalités politiques — Qui suis-je ?','visualReview':'Single official portrait of a globally significant Indian prime minister; pending user approval.'}
  new_review_entries.append(('gallery-'+filename.rsplit('.',1)[0],{'rating':'review','note':'Replacement for the lower-prominence politician flagged in the latest review; please review.'}))
  changed.append({'target':'Jacinda Ardern -> Indira Gandhi','image':'media/'+filename})
 # Import newest user export without losing candidate-review seeds, with the new export taking precedence.
 for key,value in new_review_entries: review_items[key]=value
 if changed and not any(r.get('id')==REV for r in bank.get('revisionHistory',[])):
  bank.setdefault('revisionHistory',[]).append({'id':REV,'note':'Applied the newest gallery feedback: replaced the generic Alps image with a distinct Matterhorn question, replaced the female mallard photo with a male drake, and substituted the lower-prominence Jacinda Ardern entry with Indira Gandhi. New images are marked Review.','updatedPresentations':len(changed),'presentationIds':['image-qsj-landscape-matterhorn','image-qsj-animal-mallard-duck','image-qsj-politician-indira-gandhi']})
 latest_doc={'schema':latest.get('schema'),'exportedAt':latest.get('exportedAt'),'items':review_items}
 QUESTIONS.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 CREDITS.write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 NEW_REVIEW.write_text(json.dumps(latest_doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'exportedAt':latest.get('exportedAt'),'inputRatings':len(latest.get('items',{})),'replacements':changed,'reviewSeedItems':len(review_items),'reviewFile':str(NEW_REVIEW)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
