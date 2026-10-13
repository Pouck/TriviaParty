"""Original French questions; museum references and image keys are retained."""
SOURCES={
 'joconde':'https://www.louvre.fr/en/explore/the-palace/from-the-mona-lisa-to-the-wedding-feast-at-cana',
 'naissance':'https://www.uffizi.it/opere/nascita-di-venere',
 'menines':'https://www.museodelprado.es/en/easy-to-read/las-meninas-diego-velazquez/c43f1c8d-e6c9-a8c2-44dc-0c9be2e10177',
 'perle':'https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring',
 'ronde':'https://www.rijksmuseum.nl/en/stories/10-things/story/10-things-about-rembrandt-s-night-watch',
 'impression':'https://www.marmottan.fr/notice/4014/',
 'nuit':'https://www.moma.org/collection/works/79802',
 'vague':'https://www.metmuseum.org/art/collection/search/39799',
 'david':'https://www.galleriaaccademiafirenze.it/fr/opere/david-michelangelo/',
 'venus':'https://collections.louvre.fr/en/ark:/53355/cl010277627',
 'victoire':'https://www.louvre.fr/en/support-the-louvre/become-a-patron/the-campaigns/the-winged-victory-of-samothrace-0',
 'penseur':'https://www.musee-rodin.fr/en/musee/collections/oeuvres/penseur-meudon',
 'cene':'https://cenacolovinciano.org/en/museum/the-works/the-last-supper-leonardo-da-vinci-1452-1519/',
 'gothic':'https://www.artic.edu/artworks/6565/american-gothic',
 'liberte':'https://collections.louvre.fr/en/ark:/53355/cl010065872',
 'radeau':'https://www.louvre.fr/en/explore/visitor-trails/the-louvre-s-masterpieces/romanticism-topicality-sensuality',
 'baiser':'https://www.belvedere.at/en/permanent-collection',
 'cri':'https://www.nasjonalmuseet.no/en/collection/object/NG.M.00939',
 'olympia':'https://www.musee-orsay.fr/fr/oeuvres/olympia-712',
 'galette':'https://www.musee-orsay.fr/en/artworks/bal-du-moulin-de-la-galette-497',
 'discobole':'https://www.britishmuseum.org/collection/object/G_1805-0703-43',
 'laocoon':'https://www.museivaticani.va/content/museivaticani/en/collezioni/musei/museo-pio-clementino/Cortile-Ottagono/laocoonte.html',
 'pieta':'https://www.vatican.va/news_services/or/or_quo/115q01.pdf',
 'danseuse':'https://www.nga.gov/artworks/110292-little-dancer-aged-fourteen',
 'sistine':'https://www.museivaticani.va/content/museivaticani/en/collezioni/musei/cappella-sistina/storia-cappella-sistina.html',
 'nympheas':'https://www.musee-orangerie.fr/sites/default/files/2024-08/Dossier_Pedagogique_Nympheas_2024.pdf',
 'guernica':'https://guernica.museoreinasofia.es/agente/pablo-picasso-5322',
 'memoire':'https://www.moma.org/collection/works/79018',
 'tournesols':'https://www.nationalgallery.org.uk/paintings/vincent-van-gogh-sunflowers',
 'arnolfini':'https://www.nationalgallery.org.uk/paintings/catalogues/campbell-1998/the-arnolfini-portrait',
 'nighthawks':'https://archive.artic.edu/hopper/nighthawks/',
 'maman':'https://www.guggenheim-bilbao.eus/fr/la-collection/oeuvres/maman',
 'statue':'https://www.nps.gov/stli/learn/statue-of-liberty-facts.htm',
 'donatello':'https://bargellomusei.it/en/visit-itineraries/donatello-e-lalba-del-rinascimento/',
 'bernini':'https://galleriaborghese.cultura.gov.it/en/archivio-schede/apollo-and-dafne/',
 'bourg':'https://www.musee-rodin.fr/musee/collections/oeuvres/monument-bourgeois-de-calais',
 'baiser-rodin':'https://www.musee-rodin.fr/musee/collections/oeuvres/baiser',
 'oiseau':'https://press.moma.org/wp-content/uploads/2018/10/brancusi_object_labels_for_press_final.pdf',
 'moai':'https://www.britishmuseum.org/about-us/british-museum-story/contested-objects-collection/moai',
}
def c(prompt,options,index,source,image=None,note=''):
 return dict(prompt=prompt,options=options,index=index,sources=[source],image=image,note=note)
def b(prompt,answers,source,image=None,note=''):
 return dict(prompt=prompt,answers=answers,sources=[source],image=image,note=note)
def g(answers,clues,source,note=''):
 return dict(answers=answers,clues=clues,sources=[source],note=note)
CHOICE=[
 ('peintures-classiques','Peintures classiques',[
  c('Qui a peint ce portrait ?', ['Léonard de Vinci','Raphaël','Sandro Botticelli','Le Caravage'],0,'joconde','joconde'),
  c('Où Michel-Ange a-t-il peint La Création d’Adam ?', ['La chapelle Sixtine','Le palais des Doges','Le Panthéon','La cathédrale de Florence'],0,'sistine'),
  c('Quel est le titre de cette œuvre de Botticelli ?', ['Le Printemps','La Naissance de Vénus','L’Annonciation','La Vierge à la grenade'],1,'naissance','naissance'),
  c('Dans La Cène de Léonard de Vinci, combien d’apôtres entourent Jésus ?', ['10','11','12','13'],2,'cene'),
  c('Quelle princesse est au centre des Ménines ?', ['Marguerite-Thérèse','Marie-Antoinette','Élisabeth Ire','Isabelle de Castille'],0,'menines','menines'),
  c('Quel peintre a réalisé Les Époux Arnolfini ?', ['Jan van Eyck','Pieter Bruegel l’Ancien','Albrecht Dürer','Jérôme Bosch'],0,'arnolfini'),
  c('Quel est le titre de ce tableau de Vermeer ?', ['La Laitière','La Jeune Fille à la perle','La Dentellière','La Femme à la balance'],1,'perle','perle'),
  c('Dans La Naissance de Vénus, la déesse se tient sur quel objet ?', ['Une coquille','Une amphore','Un char','Un trône'],0,'naissance'),
 ]),
 ('couleurs-mouvements','Couleurs et mouvements',[
  c('Quel peintre est l’auteur de La Ronde de nuit ?', ['Rembrandt','Johannes Vermeer','Frans Hals','Peter Paul Rubens'],0,'ronde','ronde'),
  c('Quel musée parisien présente les Nymphéas dans deux salles ovales ?', ['Le musée de l’Orangerie','Le musée Rodin','Le musée du quai Branly','Le musée Carnavalet'],0,'nympheas'),
  c('Le titre de ce tableau de Monet a donné son nom à quel mouvement ?', ['Le cubisme','L’impressionnisme','Le surréalisme','Le fauvisme'],1,'impression','impression'),
  c('Quelle palette domine Guernica de Picasso ?', ['Noir, blanc et gris','Rouge, jaune et bleu','Vert et violet','Rose et or'],0,'guernica'),
  c('Quel musée conserve cette Nuit étoilée de 1889 ?', ['Le MoMA à New York','Le Louvre à Paris','Le Prado à Madrid','Les Offices à Florence'],0,'nuit','nuit', 'La Nuit étoilée de Saint-Rémy, pas La Nuit étoilée sur le Rhône.'),
  c('Dans La Persistance de la mémoire de Dalí, quels objets semblent fondre ?', ['Des montres','Des clés','Des bouteilles','Des livres'],0,'memoire'),
  c('Quel artiste japonais a créé cette célèbre estampe ?', ['Hokusai','Hiroshige','Utamaro','Sesshū'],0,'vague','vague','La Grande Vague est une estampe sur bois, pas une peinture à l’huile.'),
  c('Quel peintre est célèbre pour ses tableaux de Tournesols en vase ?', ['Vincent van Gogh','Paul Cézanne','Georges Seurat','Henri Rousseau'],0,'tournesols'),
 ]),
 ('sculptures-iconiques','Sculptures iconiques',[
  c('Qui a sculpté ce David en marbre ?', ['Michel-Ange','Donatello','Le Bernin','Auguste Rodin'],0,'david','david'),
  c('Quel animal est représenté par Maman, la sculpture monumentale de Louise Bourgeois ?', ['Une araignée','Une pieuvre','Une fourmi','Une libellule'],0,'maman'),
  c('Dans quel musée se trouve la Vénus de Milo ?', ['Le Louvre','Le British Museum','Le Prado','Le Rijksmuseum'],0,'venus','venus'),
  c('Quel métal forme l’enveloppe extérieure de la statue de la Liberté ?', ['Le cuivre','L’argent','L’aluminium','Le zinc'],0,'statue'),
  c('Quelle divinité grecque est représentée par la Victoire de Samothrace ?', ['Niké','Athéna','Artémis','Héra'],0,'victoire','victoire'),
  c('Dans le groupe Apollon et Daphné du Bernin, en quel végétal Daphné se transforme-t-elle ?', ['Un laurier','Un olivier','Un chêne','Un cyprès'],0,'bernini'),
  c('Qui est l’auteur de cette sculpture appelée Le Penseur ?', ['Auguste Rodin','Camille Claudel','Antoine Bourdelle','Aristide Maillol'],0,'penseur','penseur'),
  c('En quel matériau est le David de Donatello coiffé d’un chapeau ?', ['Bronze','Marbre','Bois','Terre cuite'],0,'donatello',note='Le chapeau distingue le David en bronze du David en marbre du même artiste.'),
 ]),
]
BUZZER=[
 ('tableaux-celebres','Tableaux célèbres',[
  b('Quel est le nom de cette peinture murale de Léonard de Vinci ?', ['La Cène','The Last Supper','L’Ultima Cena'], 'cene','cene'),
  b('Quel peintre néerlandais a peint La Jeune Fille à la perle ?', ['Johannes Vermeer','Vermeer'], 'perle'),
  b('Quel artiste américain a peint American Gothic ?', ['Grant Wood','Wood'], 'gothic','gothic'),
  b('Quelles fleurs composent les célèbres bouquets jaunes de Van Gogh ?', ['Des tournesols','Tournesols'], 'tournesols'),
  b('Quel est le titre de ce tableau d’Eugène Delacroix ?', ['La Liberté guidant le peuple','Liberté guidant le peuple'], 'liberte','liberte'),
  b('Quel peintre espagnol est l’auteur des Ménines ?', ['Diego Velázquez','Velázquez','Velazquez'], 'menines'),
  b('Qui a peint Le Radeau de la Méduse ?', ['Théodore Géricault','Géricault','Gericault'], 'radeau','radeau'),
  b('Quel tableau de Picasso évoque une ville basque bombardée en 1937 ?', ['Guernica'], 'guernica'),
 ]),
 ('regards-scenes','Regards et scènes',[
  b('Qui a peint ce Baiser aux couleurs dorées ?', ['Gustav Klimt','Klimt'], 'baiser','baiser'),
  b('Quel port français Monet représente-t-il dans Impression, soleil levant ?', ['Le Havre','Havre'], 'impression'),
  b('Quel est le titre de cette œuvre d’Edvard Munch ?', ['Le Cri','The Scream'], 'cri','cri','Image de la version peinte de 1893 ; Munch en a réalisé plusieurs versions.'),
  b('Qui a peint Nighthawks, la scène d’un café de nuit ?', ['Edward Hopper','Hopper'], 'nighthawks'),
  b('Qui a peint Olympia ?', ['Édouard Manet','Manet'], 'olympia','olympia'),
  b('Quelle montagne japonaise apparaît au loin dans La Grande Vague de Hokusai ?', ['Le mont Fuji','Fuji','Fujiyama'], 'vague'),
  b('Qui a peint le Bal du moulin de la Galette ?', ['Auguste Renoir','Pierre-Auguste Renoir','Renoir'], 'galette','galette'),
  b('Quel artiste a peint La Nuit étoilée de Saint-Rémy en 1889 ?', ['Vincent van Gogh','Van Gogh'], 'nuit'),
 ]),
 ('marbre-bronze','Marbre et bronze',[
  b('Comment s’appelle cette statue de lanceur de disque ?', ['Le Discobole','Discobole','Discobolus'], 'discobole','discobole','Une copie du modèle antique attribué à Myron ; on ne demande pas l’auteur de la copie.'),
  b('Qui a sculpté Le Baiser, le célèbre couple enlacé ?', ['Auguste Rodin','Rodin'], 'baiser-rodin'),
  b('Quel personnage troyen est représenté ici avec ses deux fils et des serpents ?', ['Laocoon','Laocoön'], 'laocoon','laocoon'),
  b('Dans quelle ville italienne se trouve le David original de Michel-Ange ?', ['Florence','Firenze'], 'david'),
  b('Comment s’appelle cette sculpture de Michel-Ange ?', ['La Pietà','Pietà','Pieta'], 'pieta','pieta'),
  b('De quelle île du Pacifique les moaï sont-ils originaires ?', ['Rapa Nui','L’île de Pâques','Île de Pâques','Easter Island'], 'moai'),
  b('Quel artiste a créé La Petite Danseuse de quatorze ans ?', ['Edgar Degas','Degas'], 'danseuse','danseuse','Des bronzes posthumes existent ; la question porte sur le créateur du modèle.'),
  b('Quel pays a offert la statue de la Liberté aux États-Unis ?', ['La France','France'], 'statue'),
 ]),
]
GUESS=[
 ('peintures-mysteres','Peintures mystères',[
  g(['Guernica'], ['J’ai été peint pour le pavillon espagnol de l’Exposition de Paris de 1937.','Je réunis un cheval, un taureau et une mère portant son enfant.','Mes noirs, blancs et gris évoquent la guerre.','Picasso m’a donné le nom d’une ville basque bombardée.'], 'guernica'),
  g(['La Persistance de la mémoire','The Persistence of Memory'], ['Je suis une petite toile surréaliste achevée en 1931.','Des fourmis se rassemblent sur un objet posé dans mon paysage.','Plusieurs de mes montres deviennent molles et se déforment.','Je suis le célèbre tableau de Salvador Dalí aux montres molles.'], 'memoire'),
  g(['Les Nymphéas de Monet','Les Nymphéas','Nymphéas'], ['J’ai été offert à la France pour célébrer la paix après la Grande Guerre.','Mes panneaux entourent deux salles ovales.','Je représente l’eau et les plantes du jardin de Giverny.','Je suis l’ensemble de Monet au musée de l’Orangerie.'], 'nympheas','On demande l’ensemble de l’Orangerie, pas une toile précise de la série.'),
  g(['Les Époux Arnolfini','Le Portrait des Arnolfini','The Arnolfini Portrait'], ['Une inscription affirme que mon peintre était présent en 1434.','Mon miroir convexe révèle d’autres personnages.','Je montre un couple debout et un petit chien.','Je suis le portrait du couple Arnolfini par Jan van Eyck.'], 'arnolfini','L’identité exacte du couple et l’interprétation comme mariage ne sont pas affirmées.'),
  g(['Nighthawks','Les Noctambules'], ['Je suis une toile américaine achevée en 1942.','La rue qui m’entoure paraît déserte et obscure.','Trois clients et un serveur sont visibles derrière la grande vitre d’un café éclairé.','Je suis la célèbre scène nocturne de café peinte par Edward Hopper.'], 'nighthawks'),
 ]),
 ('sculptures-mysteres','Sculptures mystères',[
  g(['La Statue de la Liberté','La Liberté éclairant le monde','Statue of Liberty'], ['Ma peau de cuivre recouvre une structure métallique.','Cadeau de la France aux États-Unis, je suis inaugurée en 1886.','Je porte une couronne à rayons et une torche levée.','Je suis la statue de Bartholdi dans le port de New York.'], 'statue'),
  g(['Les Bourgeois de Calais','Le Monument des Bourgeois de Calais'], ['J’évoque un siège pendant la guerre de Cent Ans.','Je rassemble six hommes aux expressions graves.','Mes personnages portent une corde au cou ou les clés de leur ville.','Rodin m’a créé pour les habitants qui se sont livrés pour sauver Calais.'], 'bourg'),
  g(['L’Oiseau dans l’espace','Bird in Space','Oiseau dans l’espace'], ['Je fais partie d’une série de sculptures de Constantin Brancusi.','Ma forme abandonne les détails anatomiques au profit d’une ligne élancée.','Je suggère l’élan du vol sans montrer de plumes ni d’ailes déployées.','Je suis l’oiseau de Brancusi dont le titre évoque l’espace.'], 'oiseau','Plusieurs versions et matériaux existent ; on demande le titre de la série.'),
  g(['Les moaï','Moaï','Moai'], ['Nous représentons des ancêtres et pouvons être placés sur des plateformes cérémonielles.','Nos silhouettes de pierre possèdent de grandes têtes aux traits allongés.','Nous sommes associés au peuple rapanui et à son île du Pacifique.','Nous sommes les statues monumentales de l’île de Pâques.'], 'moai'),
  g(['Le David en bronze de Donatello','David de Donatello','David'], ['Je suis une œuvre de la Renaissance conservée au musée du Bargello.','Je porte un chapeau et des bottes, tout en étant presque nu.','La tête de Goliath repose à mes pieds ; mon matériau est le bronze.','Je suis le David en bronze sculpté par Donatello.'], 'donatello','Le dernier indice précise l’artiste : distinguer de Michel-Ange et de Verrocchio.'),
 ]),
]
def t(theme,works,sources,note=''):
 return dict(theme=theme,works=works,sources=sources,note=note)
CHRONOLOGY=[
 ('peintures-dans-le-temps','Peintures dans le temps',[
  t('Classez ces peintures selon leur réalisation',[('Les Époux Arnolfini',1434),('La Naissance de Vénus',1485),('Les Ménines',1656)],['arnolfini','naissance','menines'],'La Naissance de Vénus est datée vers 1485.'),
  t('Classez ces peintures selon leur réalisation',[('La Ronde de nuit',1642),('La Jeune Fille à la perle',1665),('Impression, soleil levant',1872)],['ronde','perle','impression']),
  t('Classez ces tableaux du XIXe siècle',[('Le Radeau de la Méduse',1819),('La Liberté guidant le peuple',1830),('Olympia',1863)],['radeau','liberte','olympia'],'Radeau : 1818–1819 ; Liberté : 1830 ; Olympia : réalisation en 1863, pas exposition de 1865.'),
  t('Classez ces tableaux de la fin du XIXe siècle',[('Bal du moulin de la Galette',1876),('La Nuit étoilée',1889),('Le Cri — version peinte de 1893',1893)],['galette','nuit','cri'],'La Nuit étoilée de Saint-Rémy ; première version peinte du Cri.'),
  t('Classez ces tableaux du début du XXe siècle',[('Le Baiser de Klimt',1909),('American Gothic',1930),('Guernica',1937)],['baiser','gothic','guernica'],'Le Baiser : 1908–1909 (certaines notices donnent vers 1907–1909), sans incidence sur l’ordre.'),
  t('Classez ces scènes peintes selon leur réalisation',[('Impression, soleil levant',1872),('La Persistance de la mémoire',1931),('Nighthawks',1942)],['impression','memoire','nighthawks']),
 ]),
 ('sculptures-reperes','Sculptures et repères',[
  t('Classez ces œuvres selon leur création',[('Vénus de Milo',-150),('David de Michel-Ange',1504),('Le Penseur — conception du modèle',1880)],['venus','david','penseur'],'Vénus : vers 150–125 av. J.-C. ; David : 1501–1504 ; Penseur : conception en 1880, pas fonte d’un bronze.'),
  t('Classez ces modèles de Rodin selon leur conception',[('Le Penseur',1880),('Le Baiser',1882),('Les Bourgeois de Calais',1889)],['penseur','baiser-rodin','bourg'],'Dates des modèles : 1880, vers 1882, 1884–1889 ; pas les dates des tirages ou installations.'),
  t('Classez ces présentations publiques',[('Dévoilement du David de Michel-Ange',1504),('Inauguration de la statue de la Liberté',1886),('Installation des Bourgeois de Calais à Calais',1895)],['david','statue','bourg']),
  t('Classez ces découvertes archéologiques',[('Découverte du groupe du Laocoon',1506),('Découverte de la Vénus de Milo',1820),('Découverte de la Victoire de Samothrace',1863)],['laocoon','venus','victoire'],'Il s’agit des découvertes modernes, pas de la création des œuvres antiques.'),
  t('Classez ces sculptures modernes selon les repères précisés',[('Inauguration de la statue de la Liberté',1886),('L’Oiseau dans l’espace — version du MoMA de 1928',1928),('Maman — conception de Louise Bourgeois',1999)],['statue','oiseau','maman'],'Maman : conception en 1999 ; certains exemplaires ont été fondus en 2001.'),
  t('Classez ces œuvres de Michel-Ange selon leur achèvement',[('Pietà de Saint-Pierre',1499),('David de Florence',1504),('Plafond de la chapelle Sixtine',1512)],['pieta','david','sistine'],'Pietà vaticane, pas les Pietà tardives ; plafond de 1508–1512, pas Le Jugement dernier.'),
 ]),
]
