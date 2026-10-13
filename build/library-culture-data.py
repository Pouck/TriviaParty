from library_common import *
TOPICS=[]
TOPICS.append(topic('bd-franco-belge','BD française et belge','BD et manga',[
 'https://www.tintin.com/fr/characters','https://www.parcasterix.fr/nos-conseils/personnages-village-asterix',
 'https://www.luckyluke.com/','https://www.smurf.com/','https://www.dupuis.com/'],[
 mc('Quel reporter voyage jusqu’à la Lune ?','Tintin',['Spirou','Gaston','Lucky Luke'],'moon'),
 mc('Qui prépare la potion magique d’Astérix ?','Panoramix',['Assurancetourix','Abraracourcix','Cétautomatix']),
 mc('Quel cow-boy tire plus vite que son ombre ?','Lucky Luke',['Blueberry','Red Ryder','Boule']),
 mc('Quel petit peuple bleu vit dans des maisons-champignons ?','Les Schtroumpfs',['Les Minipouss','Les Snorky','Les Barbapapa'],'mushroom'),
 mc('Quel héros maladroit travaille dans les bureaux du journal Spirou ?','Gaston Lagaffe',['Marsupilami','Fantasio','Johan']),
 ],[
 buzz('Comment s’appelle le chien de Tintin ?','Milou'),
 buzz('Quel ami d’Astérix porte des menhirs ?','Obélix','stone'),
 buzz('Quel cheval accompagne Lucky Luke ?','Jolly Jumper','bd-character-03'),
 buzz('Quel animal à longue queue est créé par Franquin ?','Le Marsupilami',aliases=['Marsupilami']),
 buzz('Quel est le nom du capitaine ami de Tintin ?','Haddock',aliases=['Capitaine Haddock']),
 ],[
 who('Astérix',['Je vis dans un village qui résiste à Rome.','Mon meilleur ami porte des menhirs.','Une potion me donne une force extraordinaire.','Je suis le petit guerrier gaulois au casque ailé.']),
 who('Le professeur Tournesol',['Mes inventions créent parfois des problèmes.','Je vis avec les amis de Tintin à Moulinsart.','Ma surdité provoque des malentendus.','Je suis le professeur au chapeau vert et au pendule.'],['Tournesol']),
 who('Gargamel',['Je vis avec un chat.','Je tente sans cesse de capturer un petit peuple.','Mes ennemis sont les Schtroumpfs.','Je suis le sorcier accompagné d’Azraël.']),
 who('Spirou',['Mes aventures paraissent dans un journal portant mon nom.','Un écureuil appelé Spip m’accompagne.','Fantasio est mon grand ami.','Je suis le héros en costume rouge de groom.']),
 who('Les Dalton',['Nous sommes quatre frères hors-la-loi.','Nos tailles forment un escalier.','Joe est le plus petit et Averell le plus grand.','Nous affrontons souvent Lucky Luke.']),
 ]))
TOPICS.append(topic('dc','DC — Héros et univers','Super-héros',[
 'https://www.dc.com/characters/batman','https://www.dc.com/characters/superman','https://www.dc.com/characters/wonder-woman',
 'https://www.dc.com/characters/the-flash','https://www.dc.com/characters/aquaman'],[
 mc('Quel animal inspire l’identité de Batman ?','La chauve-souris',['Le corbeau','Le loup','Le hibou'],'bat'),
 mc('Quel est le nom civil de Superman ?','Clark Kent',['Bruce Wayne','Barry Allen','Peter Parker']),
 mc('Quelle héroïne est une princesse des Amazones ?','Wonder Woman',['Supergirl','Catwoman','Harley Quinn']),
 mc('Quel héros de DC est associé à la vitesse et à l’éclair ?','Flash',['Aquaman','Cyborg','Green Arrow'],'lightning'),
 mc('Dans quelle ville Batman combat-il le crime ?','Gotham City',['Metropolis','Central City','Star City']),
 ],[
 buzz('Quelle planète est le monde natal de Superman ?','Krypton'),
 buzz('Quel héros règne sur Atlantis dans l’univers DC ?','Aquaman','sea'),
 buzz('Quel milliardaire est Batman ?','Bruce Wayne'),
 buzz('Quel adversaire de Batman porte souvent un maquillage de clown ?','Le Joker',aliases=['Joker']),
 buzz('Quelle héroïne utilise un lasso de vérité ?','Wonder Woman','rope'),
 ],[
 who('Superman',['J’ai été envoyé sur Terre alors que j’étais bébé.','Je travaille comme journaliste.','La kryptonite affaiblit mes pouvoirs.','Je suis Clark Kent, le héros à la cape rouge.']),
 who('Batman',['Je n’ai pas de super-pouvoirs.','Alfred m’aide dans ma double vie.','Je protège Gotham depuis la Batcave.','Je suis Bruce Wayne, le Chevalier noir.']),
 who('Wonder Woman',['Je viens de Themyscira.','Je suis une guerrière amazone.','Mes bracelets et mon lasso sont célèbres.','Je suis Diana, membre de la Ligue des justiciers.']),
 who('Green Lantern',['Je fais partie d’un corps de protecteurs de l’espace.','Mon pouvoir dépend de ma volonté.','Mon anneau crée des formes de lumière verte.','Mon nom signifie « lanterne verte ».'],['La Lanterne verte']),
 who('Aquaman',['Mes aventures se déroulent souvent sous l’eau.','Je peux communiquer avec des créatures marines.','Je porte un trident et règne sur Atlantis.','Je suis Arthur Curry, le héros aquatique de DC.']),
 ]))
TOPICS.append(topic('marvel','Marvel — Héros et univers','Super-héros',[
 'https://www.marvel.com/characters/spider-man-peter-parker','https://www.marvel.com/characters/iron-man-tony-stark',
 'https://www.marvel.com/characters/thor-thor-odinson','https://www.marvel.com/characters/black-panther-t-challa',
 'https://www.marvel.com/characters/captain-america-steve-rogers'],[
 mc('Quel héros de Marvel utilise un bouclier ?','Captain America',['Iron Man','Hawkeye','Doctor Strange'],'shield'),
 mc('Quelle est l’identité de Spider-Man, le héros créé en 1962 ?','Peter Parker',['Bruce Banner','Steve Rogers','Matt Murdock']),
 mc('Quel héros devient vert lorsqu’il se transforme ?','Hulk',['Thor','Loki','Vision']),
 mc('Quel dieu de Marvel manie Mjöllnir ?','Thor',['Odin','Loki','Heimdall'],'hammer'),
 mc('Quel royaume africain fictif est celui de Black Panther ?','Le Wakanda',['Latveria','Sokovia','Genosha']),
 ],[
 buzz('Quel milliardaire construit l’armure d’Iron Man ?','Tony Stark'),
 buzz('Quel héros utilise des toiles et est aussi Peter Parker ?','Spider-Man','web',['Spiderman','L’Homme-araignée']),
 buzz('Quel héros mutant porte des griffes et le nom Logan ?','Wolverine'),
 buzz('Quel héros de Marvel est le dieu du tonnerre ?','Thor','lightning'),
 buzz('Quel groupe comprend Star-Lord, Gamora, Rocket et Groot ?','Les Gardiens de la Galaxie',aliases=['Gardiens de la Galaxie']),
 ],[
 who('Iron Man',['Je suis un inventeur et un homme d’affaires.','Mon assistant informatique m’aide à combattre.','Mon armure vole et porte de nombreuses armes.','Je suis Tony Stark, l’homme de fer.']),
 who('Black Panther',['Je dirige un royaume riche en vibranium.','Mon costume évoque un grand félin.','Mon nom civil est T’Challa.','Je suis le héros protecteur du Wakanda.']),
 who('Hulk',['Une exposition aux rayons gamma change ma vie.','Dans ma vie humaine, je suis un scientifique.','La colère déclenche ma transformation.','Je suis le géant vert associé à Bruce Banner.']),
 who('Doctor Strange',['J’exerçais la chirurgie avant de perdre l’usage précis de mes mains.','Je découvre ensuite les arts mystiques.','Je porte une cape de lévitation.','Je suis le célèbre sorcier de Marvel.'],['Docteur Strange']),
 who('Groot',['Je voyage avec les Gardiens de la Galaxie.','Rocket est mon compagnon.','Mon corps ressemble à un arbre.','Je ne dis habituellement que « Je s’appelle Groot ».']),
 ]))
TOPICS.append(topic('manga','Manga — Grands classiques','BD et manga',[
 'https://www.viz.com/naruto','https://www.viz.com/one-piece','https://www.viz.com/dragon-ball',
 'https://www.viz.com/death-note','https://www.viz.com/sailor-moon'],[
 mc('Quel héros de manga adore les ramen ?','Naruto',['Light Yagami','Edward Elric','Luffy'],'ramen'),
 mc('Quel pirate porte un chapeau de paille ?','Monkey D. Luffy',['Roronoa Zoro','Shanks','Sanji']),
 mc('Qui a créé Dragon Ball ?','Akira Toriyama',['Eiichirō Oda','Masashi Kishimoto','Osamu Tezuka']),
 mc('Combien de boules faut-il réunir pour appeler Shenron dans Dragon Ball ?','Sept',['Trois','Cinq','Neuf'],'seven-balls'),
 mc('Quel carnet est au centre des aventures de Light Yagami ?','Le Death Note',['Le Livre de la jungle','Le Grimoire de Clow','Le One Piece']),
 ],[
 buzz('Quel est le titre du manga de pirates de Luffy ?','One Piece','ship'),
 buzz('Quel héros de Dragon Ball est aussi appelé Kakarot ?','Son Goku',aliases=['Goku']),
 buzz('Quelle héroïne de manga est associée à la Lune et aux guerrières Sailor ?','Sailor Moon','moon'),
 buzz('Quel ninja blond rêve de devenir Hokage ?','Naruto Uzumaki',aliases=['Naruto']),
 buzz('Quel héros robot d’Osamu Tezuka est connu en français sous le nom Astro ?','Astro Boy',aliases=['Astro','Astro le petit robot']),
 ],[
 who('Naruto',['Je grandis dans le village de Konoha.','J’ai un démon-renard scellé en moi.','Je rêve de devenir Hokage.','Je suis le ninja blond qui adore les ramen.']),
 who('Monkey D. Luffy',['Je rassemble un équipage de pirates.','Un fruit du démon a rendu mon corps élastique.','Je cherche le trésor One Piece.','Je suis le capitaine au chapeau de paille.'],['Luffy']),
 who('Son Goku',['Je suis un Saiyan élevé sur Terre.','Je m’entraîne pour affronter des adversaires puissants.','Le Kamehameha est ma technique célèbre.','Je suis le héros principal de Dragon Ball.'],['Goku']),
 who('Sailor Moon',['Dans ma vie quotidienne, je suis Usagi Tsukino.','Luna, une chatte parlante, m’accompagne.','Je combats avec les guerrières Sailor.','Je suis la guerrière associée à la Lune.']),
 who('Light Yagami',['Je suis un lycéen très doué.','Un dieu de la mort nommé Ryuk me suit.','J’écris des noms dans un carnet qui tue.','Je suis le personnage appelé Kira dans Death Note.'],['Light','Kira']),
 ]))
TOPICS.append(topic('disney','Disney — Animation','Cinéma',[
 'https://movies.disney.com/the-lion-king','https://movies.disney.com/aladdin','https://movies.disney.com/frozen',
 'https://movies.disney.com/moana','https://movies.disney.com/beauty-and-the-beast'],[
 mc('Quel héros de Disney est un jeune lion ?','Simba',['Bambi','Dumbo','Baloo'],'lion'),
 mc('Dans La Belle et la Bête, quel objet perd ses pétales ?','Une rose',['Une tulipe','Un lotus','Une marguerite']),
 mc('Quel objet volant aide Aladdin ?','Un tapis',['Un balai','Un bateau','Un nuage']),
 mc('Quel conte de Disney transforme une citrouille en carrosse ?','Cendrillon',['La Petite Sirène','Mulan','Pocahontas'],'pumpkin'),
 mc('Quel animal est Dumbo ?','Un éléphant',['Un rhinocéros','Un hippopotame','Un zèbre']),
 ],[
 buzz('Quelle princesse perd une pantoufle de verre ?','Cendrillon'),
 buzz('Quel personnage de La Reine des neiges est un bonhomme de neige ?','Olaf','snowman'),
 buzz('Quel petit garçon de bois souhaite devenir un vrai garçon ?','Pinocchio'),
 buzz('Quel phacochère accompagne Timon dans Le Roi lion ?','Pumbaa','warthog'),
 buzz('Quelle navigatrice de Disney voyage avec Maui ?','Vaiana',aliases=['Moana']),
 ],[
 who('Elsa',['Je cache un pouvoir que je maîtrise mal.','Ma sœur s’appelle Anna.','Je peux créer de la glace et de la neige.','Je suis la reine d’Arendelle dans La Reine des neiges.']),
 who('Ariel',['Je collectionne les objets du monde des humains.','Mon père est le roi Triton.','Je rêve de vivre sur terre avec le prince Éric.','Je suis La Petite Sirène de Disney.']),
 who('Mulan',['Je prends la place de mon père dans l’armée.','Je me déguise pour pouvoir combattre.','Le petit dragon Mushu m’accompagne.','Je suis l’héroïne chinoise d’un film Disney.']),
 who('Belle',['J’aime lire et rêve d’une autre vie.','Je suis retenue dans un château enchanté.','Lumière et Big Ben m’accueillent.','Je suis l’héroïne de La Belle et la Bête.']),
 who('Stitch',['Je suis une expérience extraterrestre.','Mon numéro est 626.','Une petite fille d’Hawaï m’adopte.','Je suis le compagnon bleu de Lilo.']),
 ]))
TOPICS.append(topic('ghibli','Studio Ghibli — Films animés','Cinéma',[
 'https://www.ghibli.jp/works/','https://gkids.com/films/my-neighbor-totoro/',
 'https://gkids.com/films/spirited-away/','https://gkids.com/films/kikis-delivery-service/'],[
 mc('Qui a réalisé Mon voisin Totoro ?','Hayao Miyazaki',['Isao Takahata','Satoshi Kon','Mamoru Hosoda']),
 mc('Quel véhicule magique apparaît dans Mon voisin Totoro ?','Un chat-bus',['Un chien-train','Un renard-avion','Un lapin-bateau'],'bus'),
 mc('Dans Ponyo, quel animal marin est d’abord la petite héroïne ?','Un poisson',['Une pieuvre','Une méduse','Une tortue']),
 mc('Quel film suit une jeune sorcière qui livre des colis ?','Kiki la petite sorcière',['Le Château ambulant','Porco Rosso','Le Vent se lève'],'broom'),
 mc('Dans Le Voyage de Chihiro, les parents deviennent quels animaux ?','Des cochons',['Des loups','Des chats','Des singes']),
 ],[
 buzz('Comment s’appelle le grand esprit de la forêt ami de Mei et Satsuki ?','Totoro','forest'),
 buzz('Quelle petite sorcière est accompagnée du chat noir Jiji ?','Kiki'),
 buzz('Quel film de Miyazaki suit un pilote au visage de cochon ?','Porco Rosso','plane'),
 buzz('Comment s’appelle le garçon dragon dans Le Voyage de Chihiro ?','Haku'),
 buzz('Quel château de Ghibli se déplace sur des pattes ?','Le Château ambulant',aliases=['Howl’s Moving Castle']),
 ],[
 who('Chihiro',['Je traverse un lieu étrange avec mes parents.','Je dois travailler dans un établissement de bains.','Yubaba me retire une partie de mon nom.','Je suis la petite fille aidée par Haku.']),
 who('Totoro',['Je vis près de grands arbres.','Deux sœurs découvrent mon existence.','Je rencontre les enfants à un arrêt de bus sous la pluie.','Je suis le grand voisin gris du film de Miyazaki.']),
 who('Kiki',['Je quitte ma famille pour apprendre à vivre seule.','Jiji est mon chat noir.','Je livre des colis en volant.','Je suis la petite sorcière sur son balai.']),
 who('Ponyo',['Je viens du monde marin.','Je rencontre un garçon appelé Sôsuke.','Je veux devenir une petite fille.','Je suis l’héroïne poisson du film de Miyazaki.']),
 who('Sophie',['Je travaille dans une boutique de chapeaux.','Une sorcière me transforme en vieille femme.','Je rencontre Calcifer et le magicien Hauru.','Je suis l’héroïne du Château ambulant.']),
 ]))
