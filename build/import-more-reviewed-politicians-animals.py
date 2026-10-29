"""Import the visually screened Commons politician portraits and exotic-animal photos."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'game-library/bank'; QUESTIONS=BANK/'questions.json'; CREDITS=BANK/'IMAGE-QSJ-MEDIA-CREDITS.json'
META=ROOT/'build/image-qsj-sampler/candidates/politicians-animals-more/candidate-metadata.json'
REV='image-qsj-politician-animal-expansion-2026-10-27'
# Jacinda Ardern's fetched portrait has prominent campaign signage. Meerkats and
# emperor penguins are group shots. These are deliberately not imported.
POLITICIANS={
 'mao-zedong':('Mao Zedong','Mao Zedong','Chairman of the Chinese Communist Party'),
 'ho-chi-minh':('Ho Chi Minh','Hô Chi Minh','Vietnamese revolutionary and president'),
 'simon-bolivar':('Simón Bolívar','Simón Bolívar','South American independence leader'),
 'eva-peron':('Eva Perón','Eva Perón','Argentine political leader'),
 'mustafa-kemal-ataturk':('Mustafa Kemal Atatürk','Mustafa Kemal Atatürk','Founder and first president of Turkey'),
 'deng-xiaoping':('Deng Xiaoping','Deng Xiaoping','Chinese political leader'),
 'fidel-castro':('Fidel Castro','Fidel Castro','Cuban political leader'),
 'emmanuel-macron':('Emmanuel Macron','Emmanuel Macron','President of France'),
 'volodymyr-zelenskyy':('Volodymyr Zelenskyy','Volodymyr Zelenskyy','President of Ukraine'),
 'benazir-bhutto':('Benazir Bhutto','Benazir Bhutto','Prime minister of Pakistan'),
}
ANIMALS={
 'fennec-fox':('Fennec fox','Fennec','Small desert fox'),
 'red-panda':('Red panda','Panda roux','Mammal native to the eastern Himalayas and southwestern China'),
 'quokka':('Quokka','Quokka','Small marsupial native to Western Australia'),
 'axolotl':('Axolotl','Axolotl','Aquatic salamander native to Mexico'),
 'narwhal':('Narwhal','Narval','Arctic whale known for its long tusk'),
 'malayan-tapir':('Malayan tapir','Tapir malais','Tapir native to Southeast Asia'),
 'three-toed-sloth':('Three-toed sloth','Paresseux à trois doigts','Slow-moving mammal native to Central and South America'),
 'ring-tailed-lemur':('Ring-tailed lemur','Lémur catta','Lemur native to Madagascar'),
 'capybara':('Capybara','Capybara','Largest living rodent'),
 'komodo-dragon':('Komodo dragon','Dragon de Komodo','Largest living lizard'),
 'chameleon':('Chameleon','Caméléon','Color-changing lizard'),
 'whale-shark':('Whale shark','Requin-baleine','Largest living fish'),
 'platypus':('Platypus','Ornithorynque','Egg-laying mammal native to Australia'),
 'secretarybird':('Secretarybird','Messager sagittaire','Large African bird of prey'),
 'shoebill':('Shoebill','Bec-en-sabot du Nil','Large African wading bird'),
 'fossa':('Fossa','Fossa','Carnivorous mammal native to Madagascar'),
 'aye-aye':('Aye-aye','Aye-aye','Nocturnal lemur native to Madagascar'),
}
def main():
 bank=json.loads(QUESTIONS.read_text(encoding='utf-8'));credits=json.loads(CREDITS.read_text(encoding='utf-8'))
 if any(x.get('id')==REV for x in bank.get('revisionHistory',[])):
  print('Revision already applied.');return
 meta=json.loads(META.read_text(encoding='utf-8')); known={a.casefold() for q in bank['questions'] for a in q.get('answers',[])}
 imported=[]; excluded=[]
 groups=[('politician',POLITICIANS),('animal',ANIMALS)]
 for kind,rows in groups:
  for key,(original,french,detail) in rows.items():
   m=meta.get(key,{})
   if not m.get('candidate') or not m.get('source') or not m.get('license'):
    excluded.append({'key':key,'reason':m.get('status','missing reviewed candidate')});continue
   src=ROOT/m['candidate']; blob=src.read_bytes(); ext=src.suffix.lower()
   fn=hashlib.sha256(blob).hexdigest()[:24]+ext;(BANK/'media'/fn).write_bytes(blob)
   title='Histoire — Personnalités politiques — Qui suis-je ?' if kind=='politician' else 'Nature — Animaux — Qui suis-je ?'
   topic='Histoire' if kind=='politician' else 'Nature'; pid=f'image-qsj-{kind}-{key}'
   answers=[original]+([french] if french.casefold()!=original.casefold() else [])
   facts={'subjectType':'political_figure' if kind=='politician' else 'animal','subjectTitle':original,'frenchTitle':french,
          'facts':[{'kind':'subject_title','value':original,'sourceUrl':m['source']}],'sources':[m['source']]}
   presentation={'id':pid,'label':'Qui suis-je ? — image','answerMode':'BUZZER','topic':topic,'legacyCategory':title,
      'legacyPackageId':'image-qsj-figures-politiques' if kind=='politician' else 'image-qsj-animaux',
      'content':{'kind':'guessWho','prompt':'Qui suis-je ?','clues':[],'imageRevealMode':'BLUR','imageRevealSteps':6,
                 'imageUrl':'media/'+fn,'basePoints':30,'penaltyPoints':0}}
   existing=next((q for q in bank['questions'] if any(a.casefold() in {x.casefold() for x in q.get('answers',[])} for a in answers)),None)
   if existing:
    existing['presentations'].append(presentation)
    if pid not in existing['legacyIds']:existing['legacyIds'].append(pid)
    if not existing.get('imageFacts'):existing['imageFacts']=facts
    if not existing.get('explanation'):existing['explanation']=f'{original} — {detail}.\n\nNom français : {french}.'
    q=existing
   else:
    if original.casefold() in known:raise ValueError('Unexpected duplicate answer '+original)
    explanation=f'{original} — {detail}.'
    if french.casefold()!=original.casefold():explanation+='\n\nNom français : '+french+'.'
    q={'id':pid,'legacyIds':[pid],'topics':[topic],'prompt':'Qui suis-je ?','answers':answers,'content':{},
       'presentations':[presentation],'explanation':explanation,'legacyReviews':[],'imageFacts':facts}
    bank['questions'].append(q)
   known.update(a.casefold() for a in answers)
   credits[fn]={'filename':m.get('commonsFile','').removeprefix('File:'),'title':original,'creator':m.get('creator',''),
      'credit':m.get('credit',''),'license':m['license'],'licenseUrl':m.get('licenseUrl',''),'source':m['source'],
      'downloadedFrom':m.get('downloadedFrom',m['source']),'localSource':m['candidate'],'question':original,'category':title,
      'visualReview':'Approved after contact-sheet inspection: one clear individual portrait or animal, no answer-bearing text.'}
   imported.append({'kind':kind,'title':original,'presentationId':pid})
 bank.setdefault('revisionHistory',[]).append({'id':REV,'note':'Added reviewed single-subject portraits for ten global political figures and seventeen exotic animals. Campaign-text and group-animal candidates were excluded.','addedPresentations':[x['presentationId'] for x in imported]})
 QUESTIONS.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');CREDITS.write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'imported':imported,'excluded':excluded},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
