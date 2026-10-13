from library_common import *
TOPICS=[]
TOPICS.append(topic('mythologie-grecque','Mythologie grecque — Dieux et héros','Mythologie',[
 'https://www.metmuseum.org/essays/greek-gods-and-religious-practices',
 'https://www.theoi.com/','https://www.perseus.tufts.edu/hopper/'],[
 mc('Quel dieu grec manie la foudre ?','Zeus',['Hadès','Hermès','Apollon'],'lightning'),
 mc('Quelle déesse est associée à la sagesse ?','Athéna',['Aphrodite','Artémis','Déméter']),
 mc('Quel héros accomplit douze travaux ?','Héraclès',['Persée','Thésée','Jason']),
 mc('Quel cheval mythique possède des ailes ?','Pégase',['Cerbère','Chiron','Arion'],'winged-horse'),
 mc('Quel dieu grec règne sur les mers ?','Poséidon',['Dionysos','Héphaïstos','Arès']),
 ],[
 buzz('Quel monstre a des serpents pour cheveux ?','Méduse','snakes'),
 buzz('Quel héros vainc le Minotaure ?','Thésée'),
 buzz('Comment s’appelle le chien à trois têtes des Enfers ?','Cerbère'),
 buzz('Quel oiseau mythique renaît de ses cendres ?','Le phénix','phoenix',['Phénix']),
 buzz('Quel héros mène les Argonautes à la recherche de la Toison d’or ?','Jason'),
 ],[
 who('Hermès',['Je protège voyageurs et messagers.','Je porte souvent un caducée.','Mes sandales sont ailées.','Je suis le messager des dieux grecs.']),
 who('Artémis',['Je suis la sœur jumelle d’Apollon.','Les animaux sauvages m’accompagnent.','Mon arc me sert à chasser.','Je suis la déesse grecque de la chasse.']),
 who('Dionysos',['Je suis lié au théâtre et aux fêtes.','Des satyres et des ménades m’accompagnent.','La vigne est mon symbole.','Je suis le dieu grec du vin.']),
 who('Persée',['J’utilise des objets magiques pour une mission dangereuse.','J’évite de regarder mon ennemie directement.','Je sauve aussi Andromède.','Je suis le héros qui décapite Méduse.']),
 who('Achille',['Je combats pendant la guerre de Troie.','Patrocle est mon compagnon.','Mon nom évoque un point faible du corps.','Je suis le héros célèbre pour son talon.']),
 ]))
TOPICS.append(topic('mythologie-romaine','Mythologie romaine — Dieux et récits','Mythologie',[
 'https://www.metmuseum.org/essays/roman-religion','https://www.perseus.tufts.edu/hopper/',
 'https://www.britishmuseum.org/collection'],[
 mc('Quel dieu romain correspond à Zeus ?','Jupiter',['Mars','Mercure','Neptune'],'lightning'),
 mc('Quelle déesse romaine correspond à Aphrodite ?','Vénus',['Minerve','Junon','Diane']),
 mc('Quel dieu romain est associé à la guerre ?','Mars',['Bacchus','Vulcain','Janus']),
 mc('Quel animal nourrit Romulus et Rémus dans la légende ?','Une louve',['Une chèvre','Une ourse','Une biche'],'wolf'),
 mc('Quel dieu romain est représenté avec deux visages ?','Janus',['Saturne','Pluton','Apollon']),
 ],[
 buzz('Quel dieu romain règne sur les mers ?','Neptune','sea'),
 buzz('Quel dieu romain correspond à Hermès ?','Mercure'),
 buzz('Quelle déesse romaine protège le foyer ?','Vesta','fire'),
 buzz('Quel héros troyen est au centre de L’Énéide ?','Énée'),
 buzz('Quelle déesse romaine correspond à Athéna ?','Minerve'),
 ],[
 who('Junon',['Je protège notamment le mariage.','Mon équivalente grecque est Héra.','Jupiter est mon époux.','Je suis la reine des dieux romains.']),
 who('Vulcain',['Je travaille auprès des flammes.','Mon équivalent grec est Héphaïstos.','Je suis associé à la forge.','Je suis le dieu romain du feu et des forgerons.']),
 who('Diane',['Je suis associée à la nature sauvage.','Mon équivalente grecque est Artémis.','Je porte souvent un arc.','Je suis la déesse romaine de la chasse.']),
 who('Bacchus',['Mes fêtes sont célèbres dans le monde romain.','Mon équivalent grec est Dionysos.','Je suis lié à la vigne.','Je suis le dieu romain du vin.']),
 who('Romulus',['Je grandis avec mon frère jumeau.','Une louve nous nourrit dans la légende.','Mon frère s’appelle Rémus.','Je suis le fondateur légendaire de Rome.']),
 ]))
TOPICS.append(topic('contes-francais','Contes et légendes de France','Contes et légendes',[
 'https://gallica.bnf.fr/essentiels/perrault/contes','https://www.bnf.fr/fr/agenda/le-bleu-de-la-barbe-les-ressorts-du-conte-dramatique-de-perrault',
 'https://www.bnf.fr/fr/charles-perrault'],[
 mc('Chez Perrault, quel objet permet au Petit Poucet de voyager vite ?','Les bottes de sept lieues',['Un tapis volant','Une baguette','Un anneau']),
 mc('Quel conte de Perrault met en scène une pantoufle de verre ?','Cendrillon',['Peau d’âne','Les Fées','Riquet à la houppe'],'slipper'),
 mc('Quel personnage interdit d’ouvrir une pièce de son château ?','Barbe bleue',['Le Chat botté','Le Petit Poucet','Riquet à la houppe']),
 mc('Dans Le Chat botté, en quel animal l’ogre se change-t-il avant d’être mangé ?','Une souris',['Un lion','Un lapin','Un serpent'],'mouse'),
 mc('Qui a publié les célèbres contes français de 1697 ?','Charles Perrault',['Victor Hugo','Jules Verne','Molière']),
 ],[
 buzz('Qui porte un panier à sa grand-mère dans un conte de Perrault ?','Le Petit Chaperon rouge'),
 buzz('Quel animal trompe le Petit Chaperon rouge chez Perrault ?','Le loup','wolf'),
 buzz('Quel personnage transforme une citrouille en carrosse pour Cendrillon ?','La fée marraine','pumpkin',['Sa marraine','La marraine']),
 buzz('Qui laisse des cailloux pour retrouver son chemin chez Perrault ?','Le Petit Poucet'),
 buzz('Quel conte français met en scène une princesse cachée sous une peau d’animal ?','Peau d’âne'),
 ],[
 who('Le Chat botté',['Je suis l’héritage d’un fils de meunier.','Je fais passer mon maître pour un marquis.','Je piège un ogre capable de se transformer.','Je suis le chat qui porte des bottes.']),
 who('La Belle au bois dormant',['Une fée me condamne lors de ma naissance.','Je me pique à un fuseau.','Je dors pendant cent ans.','Mon nom évoque une belle endormie dans un bois.']),
 who('Barbe bleue',['Je suis un riche personnage inquiétant.','Je remets à mon épouse une clé interdite.','Une chambre révèle le sort de mes anciennes femmes.','Je suis l’homme à la barbe d’une couleur inhabituelle.']),
 who('Cendrillon',['Je vis avec une famille qui me traite mal.','Ma marraine m’aide à aller au bal.','Je dois partir avant minuit.','Je perds une pantoufle de verre chez Perrault.']),
 who('Le Petit Poucet',['Je suis le plus jeune de sept frères.','Je guide ma fratrie grâce à des cailloux.','J’échappe à un ogre et prends ses bottes.','Je suis le petit héros de Perrault nommé comme un doigt.']),
 ]))
TOPICS.append(topic('contes-anglais','Contes et légendes d’Angleterre','Contes et légendes',[
 'https://www.gutenberg.org/ebooks/7439','https://www.gutenberg.org/ebooks/14241',
 'https://www.bl.uk/stories/blogs/posts/king-arthur-fable-fact-and-fiction'],[
 mc('Dans Jack et le Haricot magique, que troque Jack contre des haricots ?','Une vache',['Un cheval','Un mouton','Un chien'],'cow'),
 mc('Quelle maison résiste au loup dans Les Trois Petits Cochons ?','La maison de briques',['La maison de paille','La maison de bois','La tente']),
 mc('Quel héros légendaire est associé à la forêt de Sherwood ?','Robin des Bois',['Peter Pan','Oliver Twist','Sherlock Holmes'],'forest'),
 mc('Quel objet est trop grand pour Boucle d’or dans la maison des ours ?','Un des lits',['La clé de la maison','Une baguette','Une botte']),
 mc('Quel personnage de comptine anglaise tombe d’un mur ?','Humpty Dumpty',['Jack Frost','Tom Thumb','Old King Cole']),
 ],[
 buzz('Combien de cochons construisent chacun une maison dans le conte ?','Trois','three-houses',['3']),
 buzz('Comment s’appelle la fille qui entre chez les trois ours ?','Boucle d’or',aliases=['Goldilocks']),
 buzz('Quel héros grimpe vers un géant grâce à une plante magique ?','Jack','beanstalk'),
 buzz('Quel compagnon géant de Robin des Bois porte le nom Petit Jean ?','Petit Jean',aliases=['Little John']),
 buzz('Quel héros minuscule du folklore anglais est appelé Tom Pouce ?','Tom Pouce',aliases=['Tom Thumb']),
 ],[
 who('Robin des Bois',['Mon histoire se déroule en Angleterre médiévale.','Le shérif de Nottingham est mon adversaire.','Je suis un archer associé à Sherwood.','Je suis le hors-la-loi qui aide les pauvres.']),
 who('Boucle d’or',['Je découvre un repas et des meubles sans permission.','Je préfère ce qui n’est ni trop grand ni trop petit.','Les propriétaires de la maison sont trois ours.','Mon nom évoque ma chevelure blonde.']),
 who('Jack',['Je reçois des graines en échange d’un animal.','Une plante géante pousse pendant la nuit.','Je rencontre un géant dans le ciel.','Je suis le héros du Haricot magique.']),
 who('Humpty Dumpty',['Je suis un personnage d’une comptine anglaise.','Je m’assieds en hauteur avant de tomber.','Les hommes du roi ne peuvent me réparer.','Je suis souvent représenté comme un œuf.']),
 who('Les Trois Petits Cochons',['Nous sommes trois frères dans un conte.','Nous construisons des abris de matériaux différents.','Un loup essaie de souffler nos maisons.','Notre maison de briques résiste.']),
 ]))
TOPICS.append(topic('table-ronde','Le cycle de la Table ronde','Contes et légendes',[
 'https://www.bl.uk/stories/blogs/posts/king-arthur-fable-fact-and-fiction',
 'https://www.gutenberg.org/ebooks/1251','https://www.gutenberg.org/ebooks/1252'],[
 mc('Qui est le roi de la Table ronde ?','Arthur',['Charlemagne','Richard Cœur de Lion','Henri VIII']),
 mc('Quelle forme a la table des chevaliers d’Arthur ?','Ronde',['Carrée','Triangulaire','Rectangulaire'],'round-table'),
 mc('Quel enchanteur conseille Arthur ?','Merlin',['Gandalf','Dumbledore','Prospero']),
 mc('Quel objet sacré les chevaliers recherchent-ils ?','Le Graal',['La Toison d’or','Le trident','La boîte de Pandore'],'cup'),
 mc('Quel chevalier est célèbre pour son amour de Guenièvre ?','Lancelot',['Galahad','Gauvain','Perceval']),
 ],[
 buzz('Quel est le nom de la célèbre épée d’Arthur ?','Excalibur','sword'),
 buzz('Comment s’appelle l’épouse du roi Arthur ?','Guenièvre',aliases=['Guinevere']),
 buzz('Quel château est associé à la cour d’Arthur ?','Camelot','castle'),
 buzz('Quel fils de Lancelot est associé à l’accomplissement de la quête du Graal ?','Galahad',aliases=['Galaad']),
 buzz('Quel chevalier est le héros du Conte du Graal de Chrétien de Troyes ?','Perceval',aliases=['Percival']),
 ],[
 who('Merlin',['Je connais des secrets et des prophéties.','J’aide à préparer le règne d’un jeune souverain.','Je conseille Arthur.','Je suis l’enchanteur de la légende arthurienne.']),
 who('Lancelot',['Je suis un chevalier de la Table ronde.','Mon fils est Galahad.','J’aime la reine Guenièvre.','Mon surnom est « du Lac ».']),
 who('Le Graal',['Je suis au centre d’une quête spirituelle.','Plusieurs chevaliers tentent de me retrouver.','Je suis souvent représenté comme une coupe sacrée.','Je suis l’objet recherché par les chevaliers de la Table ronde.']),
 who('Arthur',['Je rassemble de célèbres chevaliers.','Ma cour est associée à Camelot.','Guenièvre est mon épouse.','Je suis le roi de la Table ronde.']),
 who('Excalibur',['Je suis un objet lié à la royauté légendaire.','La Dame du Lac m’est associée dans plusieurs versions.','Arthur me porte au combat.','Je suis son épée célèbre.']),
 ]))
TOPICS.append(topic('odyssee','L’Odyssée — Le voyage d’Ulysse','Mythologie',[
 'https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0136',
 'https://www.gutenberg.org/ebooks/1727'],[
 mc('Sur quelle île Ulysse veut-il rentrer ?','Ithaque',['Crète','Lesbos','Rhodes'],'island'),
 mc('Quel dieu poursuit Ulysse de sa colère ?','Poséidon',['Apollon','Héphaïstos','Dionysos']),
 mc('Quel prénom Ulysse donne-t-il au Cyclope pour le tromper ?','Personne',['Achille','Paris','Nestor']),
 mc('Comment Ulysse écoute-t-il les Sirènes sans les rejoindre ?','Attaché au mât',['Caché sous un mouton','Dans un coffre','Endormi'],'ship'),
 mc('Quelle déesse aide souvent Ulysse ?','Athéna',['Héra','Aphrodite','Artémis']),
 ],[
 buzz('Qui attend Ulysse à Ithaque ?','Pénélope'),
 buzz('Quel monstre de L’Odyssée possède un seul œil ?','Le Cyclope','one-eye',['Polyphème','Cyclope']),
 buzz('Comment s’appelle le fils d’Ulysse ?','Télémaque'),
 buzz('Quelle magicienne transforme des compagnons d’Ulysse en cochons ?','Circé','pig'),
 buzz('Quel poète est traditionnellement associé à L’Odyssée ?','Homère'),
 ],[
 who('Ulysse',['Je reviens de la guerre de Troie.','Mon voyage de retour dure dix ans.','J’utilise la ruse contre un Cyclope.','Je suis le roi d’Ithaque et l’époux de Pénélope.'],['Odysseus']),
 who('Pénélope',['Des prétendants veulent m’épouser.','Je défais la nuit ce que je tisse le jour.','Télémaque est mon fils.','Je suis l’épouse qui attend Ulysse.']),
 who('Polyphème',['Je vis dans une grotte avec mes troupeaux.','Poséidon est mon père.','Un voyageur me dit s’appeler Personne.','Je suis le Cyclope aveuglé par Ulysse.']),
 who('Circé',['Je vis sur l’île d’Ééa.','Je possède des pouvoirs magiques.','Je transforme des marins en cochons.','Je suis la magicienne rencontrée par Ulysse.']),
 who('Les Sirènes',['Nous apparaissons dans le voyage d’Ulysse.','Notre chant attire les marins.','Les compagnons d’Ulysse se bouchent les oreilles.','Ulysse est attaché au mât pour nous écouter.']),
 ]))
