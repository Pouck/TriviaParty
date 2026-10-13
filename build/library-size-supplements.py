"""Short, accessible additions required to turn four/nine-question pools into five/ten."""
import random

ADDITIONS={}
def add(key,kind,**fields):
    q=dict(id='resize-20261012-'+key,kind=kind,category='',basePoints=20 if kind=='guessWho' else 15,
           penaltyPoints=5 if kind=='guessWho' else 0,**fields)
    ADDITIONS[key]=q
def who(key,answer,clues,sources,aliases=()):
    add(key,'guessWho',prompt='Qui suis-je ?',clues=clues,acceptableAnswers=[answer,*aliases],sources=sources)
def mc(key,prompt,answer,distractors,sources):
    add(key,'multipleChoice',prompt=prompt,options=[f'{letter} — {text}' for letter,text in zip('ABCD',[answer,*distractors])],correctOptionIndex=0,sources=sources)
def chrono(key,prompt,events,sources):
    correct=[text for text,date in sorted(events,key=lambda e:e[1])]
    display=correct.copy();random.Random(key).shuffle(display)
    if display==correct:display=display[1:]+display[:1]
    items=[dict(id=f'item-{i}',text=text) for i,text in enumerate(display)]
    add(key,'ordering',prompt=prompt,items=items,correctOrderIds=[next(i['id'] for i in items if i['text']==text) for text in correct],sources=sources,
        verification=' → '.join(f'{text} ({date})' for text,date in sorted(events,key=lambda e:e[1])))

who('socrate','Socrate',[
 'Je fais réfléchir mes interlocuteurs en leur posant des questions.',
 'Je n’ai laissé aucun écrit de ma main.',
 'Je suis condamné à Athènes en 399 avant notre ère.',
 'Platon raconte mes dialogues ; je meurs après avoir bu la ciguë.'
],['https://plato.stanford.edu/entries/socrates/'])
who('aristote','Aristote',[
 'Mes recherches portent sur de nombreux domaines du savoir.',
 'Je fonde une école appelée le Lycée à Athènes.',
 'J’ai étudié dans l’Académie de Platon.',
 'J’ai été le précepteur d’Alexandre le Grand.'
],['https://plato.stanford.edu/entries/aristotle/'])
who('cesar','Jules César',[
 'Je forme une alliance politique avec Pompée et Crassus.',
 'Je franchis le Rubicon avec mon armée.',
 'Je suis assassiné lors des ides de mars.',
 'Je suis le général romain qui bat Vercingétorix à Alésia.'
],['https://www.perseus.tufts.edu/hopper/','https://www.metmuseum.org/art/collection/search/330161'],['César'])
who('auguste','Auguste',[
 'Mon règne ouvre une longue période de paix romaine.',
 'Je suis l’héritier adoptif de Jules César.',
 'Je remporte la bataille d’Actium contre Marc Antoine.',
 'Je suis le premier empereur romain.'
],['https://www.metmuseum.org/ko/essays/augustan-rule-27-b-c-14-a-d','https://resources.metmuseum.org/resources/metpublications/pdf/Pergamon_and_the_Hellenistic_Kingdoms_of_the_Ancient_World.pdf'])
who('hugo','Victor Hugo',[
 'Une partie de mon exil se déroule sur l’île de Guernesey.',
 'Je suis poète, dramaturge et romancier français du XIXe siècle.',
 'J’écris Notre-Dame de Paris.',
 'Je suis l’auteur des Misérables.'
],['https://www.bnf.fr/fr/mediatheque/victor-hugo-guernesey-1855-1870-creations-et-combats','https://gallica.bnf.fr/selections/fr/html/litteratures/victor-hugo'])
who('hamlet','Hamlet',[
 'Le fantôme de mon père me confie un terrible secret.',
 'Mon oncle Claudius occupe désormais le trône.',
 'Je cherche à venger mon père assassiné.',
 'Je suis le prince de Danemark créé par Shakespeare.'
],['https://www.folger.edu/explore/shakespeares-works/hamlet/'])
who('huck-finn','Huckleberry Finn',[
 'Je fuis un père violent dans l’Amérique du XIXe siècle.',
 'Je descends le Mississippi sur un radeau avec Jim.',
 'Mark Twain raconte mes aventures.',
 'Je suis le jeune ami de Tom Sawyer, souvent surnommé Huck.'
],['https://www.gutenberg.org/files/76/76-h/76-h'],['Huck Finn'])
who('athena','Athéna',[
 'La chouette est l’un de mes symboles.',
 'Selon le mythe, je nais de la tête de Zeus.',
 'Je protège la cité d’Athènes.',
 'Je suis la déesse grecque de la sagesse.'
],['https://www.metmuseum.org/essays/greek-gods-and-religious-practices'],['Athena'])
who('neptune','Neptune',[
 'Mes tempêtes menacent les marins.',
 'On me représente avec un trident.',
 'Mon équivalent grec est Poséidon.',
 'Je suis le dieu romain des mers.'
],['https://www.perseus.tufts.edu/hopper/','https://www.britishmuseum.org/collection'])
mc('marignan','Quelle bataille François Ier remporte-t-il en 1515 ?','Marignan',['Azincourt','Crécy','Poitiers'],
 ['https://www.musee-armee.fr/au-programme/expositions/detail/chevaliers-et-bombardes-d-azincourt-a-marignan-1415-1515.html'])
mc('pleiade','Quel groupe de poètes réunit notamment Ronsard et Du Bellay ?','La Pléiade',['Les Encyclopédistes','Le Parnasse','L’Oulipo'],
 ['https://gallica.bnf.fr/selections/fr/html/litteratures/les-classiques-de-la-litterature-la-pleiade'])
chrono('rois-renaissance','Classez ces accessions au trône de France',[
 ('François Ier devient roi',1515),('Henri II devient roi',1547),('Henri IV devient roi',1589)
],['https://collections-ressources.chateaudefontainebleau.fr/document/francois-ier-roi-de-france/5f6b540ffde2e4199866ce4e','https://www.chateauversailles.fr/decouvrir/histoire/grandes-dates/courtisans'])
mc('louis-xvi','Quel roi de France est exécuté en 1793 ?','Louis XVI',['Louis XIV','Louis XV','Charles X'],
 ['https://www.assemblee-nationale.fr/dyn/histoire-et-patrimoine/revolution-francaise/proces-et-execution-de-louis-xvi'])
mc('guillotine','Quel instrument d’exécution devient un symbole de la Révolution française ?','La guillotine',['Le gibet','La roue','La chaise électrique'],
 ['https://www.assemblee-nationale.fr/dyn/histoire-et-patrimoine/revolution-francaise/proces-et-execution-de-louis-xvi'])
chrono('jalons-1789','Classez ces jalons de 1789',[
 ('Serment du Jeu de paume',17890620),('Abolition des privilèges',17890804),('Adoption de la Déclaration des droits de l’homme et du citoyen',17890826)
],['https://www.assemblee-nationale.fr/dyn/histoire-et-patrimoine/revolution-francaise/assemblee-nationale-constituante'],)
ADDITIONS['jalons-1789']['verification']='20 juin 1789 → nuit du 4 août 1789 → 26 août 1789'
chrono('usa-xxe','Classez ces événements américains du XXe siècle',[
 ('Premier vol motorisé des frères Wright',1903),('Krach de Wall Street',1929),('Premiers pas humains sur la Lune',1969)
],['https://airandspace.si.edu/collection-objects/1903-wright-flyer/nasm_A19610048000','https://www.federalreservehistory.org/essays/stock-market-crash-of-1929','https://www.nasa.gov/history/apollo-11-mission-overview/'])

CHARADE_REPLACEMENT=dict(prompt='Mon premier est la carte la plus forte. Mon deuxième est « en ». Mon troisième est une fille ayant les mêmes parents que moi. Mon tout monte et descend dans un immeuble.',
    acceptableAnswers=['Ascenseur','Un ascenseur'],verification='as + en + sœur = ascenseur ; ancien rébus remplacé par une charade textuelle complète.')
for key,prompt,answer,note in [
 ('chapeau','Mon premier miaule. Mon second recouvre le corps. Mon tout se porte sur la tête.','Chapeau','chat + peau'),
 ('radeau','Mon premier est un petit rongeur. Mon second est la partie arrière du corps. Mon tout flotte sur l’eau.','Radeau','rat + dos'),
 ('pinceau','Mon premier se mange en tartines. Mon second sert à porter de l’eau. Mon tout sert à peindre.','Pinceau','pain + seau'),
 ('cartable','Mon premier est un véhicule qui transporte des passagers. Mon second est un meuble sur lequel on mange. Mon tout transporte les affaires d’école.','Cartable','car + table')
]:
    add(key,'textAnswer',prompt=prompt,acceptableAnswers=[answer],allowFuzzyMatch=False,sources=[],verification=note)
