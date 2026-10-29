"""Import reviewed single-character portraits from the official Jujutsu Kaisen site."""
from __future__ import annotations
import hashlib, json, re, shutil, unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'game-library/bank/questions.json'
CREDITS=ROOT/'game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json'
CANDIDATES=ROOT/'build/image-qsj-sampler/candidates/bd-manga-official'
REVISION='2026-10-27-reviewed-jujutsu-portraits'
SOURCE='https://jujutsukaisen.jp/character/index_1st.php'
COPYRIGHT='Gege Akutami / Shueisha / Jujutsu Kaisen Production Committee'
ITEMS=[
 ('jujutsu-yuji','Yuji Itadori',['Itadori Yuji','Yūji Itadori'],'A first-year student who becomes the vessel of Ryomen Sukuna.', 'chara_detail1.png'),
 ('jujutsu-megumi','Megumi Fushiguro',['Fushiguro Megumi'],'A gifted jujutsu sorcerer who fights with shikigami.', 'chara_detail2.png'),
 ('jujutsu-nobara','Nobara Kugisaki',['Kugisaki Nobara'],'A confident first-year sorcerer who uses a hammer, nails, and a straw doll.', 'chara_detail3.png'),
 ('jujutsu-gojo','Satoru Gojo',['Gojo Satoru'],'A teacher at Tokyo Jujutsu High, widely regarded as the strongest sorcerer.', 'chara_detail4.png'),
 ('jujutsu-maki','Maki Zenin',['Maki Zen’in','Maki Zenin'],'A jujutsu student who relies on exceptional physical skill and cursed tools.', 'chara_detail6.png'),
 ('jujutsu-inumaki','Toge Inumaki',['Inumaki Toge'],'A sorcerer whose words can become a cursed technique.', 'chara_detail7.png'),
 ('jujutsu-panda','Panda',['Panda (Jujutsu Kaisen)'],'A talking, sentient cursed corpse created by Principal Yaga.', 'chara_detail8.png'),
 ('jujutsu-nanami','Kento Nanami',['Nanami Kento'],'A former salaryman and grade-one jujutsu sorcerer.', 'chara_detail9.png'),
 ('jujutsu-todo','Aoi Todo',['Todo Aoi'],'A powerful Kyoto Jujutsu High student known for his unusual questions and immense strength.', 'chara_detail13.png'),
]
def slug(s):
 s=unicodedata.normalize('NFKD',s.casefold()); s=''.join(c for c in s if not unicodedata.combining(c)); return re.sub(r'[^a-z0-9]+','-',s).strip('-')
bank=json.loads(BANK.read_text(encoding='utf8')); credits=json.loads(CREDITS.read_text(encoding='utf8'))
if any(x.get('id')==REVISION for x in bank.get('revisionHistory',[])): raise SystemExit('Jujutsu import already applied')
backup=ROOT/'review-backups'; backup.mkdir(exist_ok=True)
(backup/'questions-before-jujutsu-portraits-2026-10-27.json').write_text(BANK.read_text(encoding='utf8'),encoding='utf8')
(backup/'credits-before-jujutsu-portraits-2026-10-27.json').write_text(CREDITS.read_text(encoding='utf8'),encoding='utf8')
ids=[]; metadata_path=CANDIDATES/'next-candidate-metadata.json'; metadata=json.loads(metadata_path.read_text(encoding='utf8'))
for key,answer,aliases,fact,filename in ITEMS:
 src=CANDIDATES/(key+'.png')
 if not src.is_file(): raise FileNotFoundError(src)
 data=src.read_bytes(); digest=hashlib.sha256(data).hexdigest()[:24]+src.suffix.lower(); dest=ROOT/'game-library/bank/media'/digest
 if not dest.exists(): shutil.copyfile(src,dest)
 pid=f'image-qsj-personnages-de-manga-{slug(answer)}-official-20261027-d'
 q={'id':pid,'legacyIds':[pid],'topics':['BD et manga','Jujutsu Kaisen'],'prompt':'Qui suis-je ?','answers':list(dict.fromkeys([answer,*aliases])),'content':{},'explanation':fact,
    'imageFacts':{'subjectType':'fictional_character','subjectTitle':answer,'franchise':'Jujutsu Kaisen','facts':[{'kind':'subject_title','value':answer,'sourceUrl':SOURCE},{'kind':'series','value':'Jujutsu Kaisen','sourceUrl':SOURCE},{'kind':'media_creator','role':'official anime artwork copyright holder; no open license indicated','value':COPYRIGHT,'sourceUrl':SOURCE}],'sources':[SOURCE]},
    'presentations':[{'id':pid,'label':'Qui suis-je ? — image','answerMode':'BUZZER','topic':'BD et manga','legacyCategory':'BD et manga — Personnages de manga — Qui suis-je ?','legacyPackageId':'image-qsj-personnages-de-manga','content':{'kind':'guessWho','prompt':'Qui suis-je ?','clues':[],'imageRevealMode':'PIXELATE','imageRevealSteps':6,'imageUrl':'media/'+digest,'basePoints':30,'penaltyPoints':0}}], 'legacyReviews':[]}
 bank['questions'].append(q); ids.append(pid)
 credits[digest]={'filename':src.name,'title':'Jujutsu Kaisen official anime character design','creator':COPYRIGHT,'credit':'© Gege Akutami / Shueisha / Jujutsu Kaisen Production Committee','license':'Copyrighted official artwork; rights reserved; private local use only','licenseUrl':SOURCE,'source':SOURCE,'downloadedFrom':'https://jujutsukaisen.jp/images/'+filename,'localSource':'Official character profile; image retained unchanged','question':answer,'category':'BD et manga — Personnages de manga — Qui suis-je ?','visualReview':'Approved: one recognizable canonical character, no text and no second subject. Retained unchanged for this private local game only; do not redistribute.'}
 metadata[key]['review']='Approved and imported: one canonical character, no text or second subject; private local game only'
metadata_path.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bank.setdefault('revisionHistory',[]).append({'id':REVISION,'note':'Added nine visually reviewed single-character official Jujutsu Kaisen portraits. Copyrighted artwork is private-local-gameplay-only and must not be redistributed.','createdQuestions':len(ids),'addedPresentationsToExistingQuestions':0,'presentationIds':ids})
BANK.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf8'); CREDITS.write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'added':len(ids),'presentationIds':ids},ensure_ascii=False,indent=2))
