from library_common import *
TOPICS=[]
TOPICS.append(topic('litterature-france','Littérature française — Romans et personnages','Littérature',[
 'https://gallica.bnf.fr/essentiels/','https://www.bnf.fr/fr'],[
 mc('Qui a écrit Les Misérables ?','Victor Hugo',['Alexandre Dumas','Émile Zola','Gustave Flaubert']),
 mc('Quel roman de Verne voyage sous la mer ?','Vingt mille lieues sous les mers',['Germinal','Candide','Madame Bovary'],'sea'),
 mc('Qui est l’auteur de Candide ?','Voltaire',['Rousseau','Diderot','Montesquieu']),
 mc('Quel personnage est le sonneur de Notre-Dame ?','Quasimodo',['Javert','d’Artagnan','Rastignac'],'notre-dame'),
 mc('Qui a écrit Germinal ?','Émile Zola',['Stendhal','Maupassant','Proust']),
 ],[
 buzz('Quel ancien forçat est le héros des Misérables ?','Jean Valjean'),
 buzz('Quel auteur raconte les aventures du capitaine Nemo ?','Jules Verne','submarine'),
 buzz('Quel héros de Dumas arrive de Gascogne pour devenir mousquetaire ?','d’Artagnan'),
 buzz('Quel prince de Saint-Exupéry vient de l’astéroïde B-612 ?','Le Petit Prince','space'),
 buzz('Quel personnage de Dumas est aussi Edmond Dantès ?','Le Comte de Monte-Cristo',aliases=['Comte de Monte-Cristo']),
 ],[
 who('Les Misérables',['Je décris notamment la misère au XIXe siècle.','Javert poursuit mon personnage principal.','Cosette et Jean Valjean appartiennent à mon récit.','Je suis le grand roman de Victor Hugo sur cet ancien forçat.']),
 who('Le Petit Prince',['Mon narrateur est un aviateur.','Un enfant lui demande de dessiner un mouton.','Une rose et un renard marquent mon histoire.','Je suis le conte de Saint-Exupéry au petit héros venu d’un astéroïde.']),
 who('Madame Bovary',['Je suis un roman de Flaubert.','Mon héroïne vit en Normandie.','Elle s’ennuie auprès de son mari médecin.','Je porte le nom d’Emma et de son mari Charles Bovary.']),
 who('Le Comte de Monte-Cristo',['Je suis un roman d’Alexandre Dumas.','Mon héros est emprisonné au château d’If.','Il trouve un trésor et prépare sa vengeance.','Il s’appelle Edmond Dantès.']),
 who('Candide',['Je suis un conte philosophique.','Pangloss enseigne l’optimisme à mon héros.','Je me moque de l’idée du meilleur des mondes.','Voltaire est mon auteur.']),
 ]))
TOPICS.append(topic('litterature-anglaise','Littérature anglophone — Classiques','Littérature',[
 'https://www.bl.uk/','https://www.gutenberg.org/ebooks/84','https://www.gutenberg.org/ebooks/1342',
 'https://www.gutenberg.org/ebooks/11'],[
 mc('Qui a écrit Pride and Prejudice ?','Jane Austen',['Charlotte Brontë','Virginia Woolf','Mary Shelley']),
 mc('Quel auteur a créé Sherlock Holmes ?','Arthur Conan Doyle',['Agatha Christie','Charles Dickens','Oscar Wilde'],'magnifier'),
 mc('Dans quel roman trouve-t-on le capitaine Crochet ?','Peter Pan',['Alice’s Adventures in Wonderland','Jane Eyre','Dracula']),
 mc('Quel auteur a écrit Animal Farm ?','George Orwell',['Aldous Huxley','William Golding','H. G. Wells'],'pig'),
 mc('Qui a écrit Frankenstein ?','Mary Shelley',['Bram Stoker','Emily Brontë','George Eliot']),
 ],[
 buzz('Quel prince de Shakespeare est le fils du roi du Danemark assassiné ?','Hamlet'),
 buzz('Quelle héroïne de Lewis Carroll suit un lapin blanc ?','Alice','rabbit'),
 buzz('Quel détective habite au 221B Baker Street ?','Sherlock Holmes'),
 buzz('Quel avare de Dickens change après la visite de fantômes ?','Ebenezer Scrooge','ghost',['Scrooge']),
 buzz('Quel vampire est au centre du roman de Bram Stoker ?','Dracula'),
 ],[
 who('Frankenstein',['Je suis un roman publié en 1818.','Un savant y crée un être vivant.','Le nom du savant est souvent donné par erreur à la créature.','Mary Shelley est mon autrice.']),
 who('Pride and Prejudice',['Je suis un roman de Jane Austen.','Mon héroïne a quatre sœurs.','Mr Darcy occupe une place centrale dans mon intrigue.','Je raconte l’histoire d’Elizabeth Bennet.'],['Orgueil et Préjugés']),
 who('Animal Farm',['Je suis une fable politique de 1945.','Des animaux renversent leur fermier.','Des cochons prennent ensuite le pouvoir.','Je suis la ferme de George Orwell.'],['La Ferme des animaux']),
 who('Dracula',['Je suis un roman gothique de Bram Stoker.','Jonathan Harker y visite un château.','Mon personnage célèbre vient de Transylvanie.','Il est un comte vampire.']),
 who('Alice’s Adventures in Wonderland',['Je suis un récit de Lewis Carroll.','Une petite fille tombe dans un terrier.','Un chapelier et un chat étrange apparaissent.','Je suis le voyage d’Alice au pays des merveilles.'],['Alice au pays des merveilles']),
 ]))
TOPICS.append(topic('litterature-americaine','Littérature américaine — Classiques','Littérature',[
 'https://www.loc.gov/','https://www.gutenberg.org/ebooks/2701','https://www.gutenberg.org/ebooks/64317',
 'https://www.pulitzer.org/winners/harper-lee'],[
 mc('Qui a écrit The Great Gatsby ?','F. Scott Fitzgerald',['Ernest Hemingway','John Steinbeck','Mark Twain']),
 mc('Quel animal Ahab poursuit-il dans Moby-Dick ?','Une baleine',['Un requin','Une pieuvre','Un dauphin'],'whale'),
 mc('Qui a écrit The Grapes of Wrath ?','John Steinbeck',['William Faulkner','Herman Melville','Nathaniel Hawthorne']),
 mc('Dans Fahrenheit 451, que brûlent les pompiers ?','Des livres',['Des bateaux','Des récoltes','Des tableaux'],'book'),
 mc('Quelle autrice a écrit Beloved ?','Toni Morrison',['Harper Lee','Sylvia Plath','Louisa May Alcott']),
 ],[
 buzz('Quel avocat défend Tom Robinson dans To Kill a Mockingbird ?','Atticus Finch'),
 buzz('Quel auteur américain a créé Tom Sawyer ?','Mark Twain'),
 buzz('Quel roman de Melville suit la chasse à une baleine blanche ?','Moby-Dick','whale'),
 buzz('Quel roman de Thoreau porte le nom d’un étang ?','Walden','lake'),
 buzz('Quel auteur a écrit The Old Man and the Sea ?','Ernest Hemingway'),
 ],[
 who('Moby-Dick',['Je suis un roman d’Herman Melville.','Ishmael raconte mon histoire.','Le capitaine Ahab commande le Pequod.','Une baleine blanche est au centre de sa chasse.']),
 who('The Great Gatsby',['Je suis un roman de Fitzgerald.','Nick Carraway est mon narrateur.','Daisy Buchanan est aimée par mon héros.','Il donne de grandes fêtes à Long Island.'],['Gatsby le Magnifique']),
 who('To Kill a Mockingbird',['Je suis un roman de Harper Lee.','Scout raconte une enfance en Alabama.','Son père défend Tom Robinson.','Cet avocat s’appelle Atticus Finch.'],['Ne tirez pas sur l’oiseau moqueur']),
 who('Fahrenheit 451',['Je suis un roman de Ray Bradbury.','Mon héros s’appelle Montag.','Les livres sont interdits dans mon monde.','Mes pompiers les brûlent.']),
 who('The Old Man and the Sea',['Je suis un récit d’Hemingway.','Mon héros est un vieux pêcheur cubain.','Il lutte contre un grand marlin.','Mon titre réunit le vieil homme et la mer.'],['Le Vieil Homme et la Mer']),
 ]))
TOPICS.append(topic('jeux-video','Jeux vidéo — Grands univers','Jeux vidéo',[
 'https://www.nintendo.com/us/','https://www.minecraft.net/','https://www.pokemon.com/',
 'https://www.sonicthehedgehog.com/','https://www.pacman.com/'],[
 mc('Quel héros de Nintendo est un plombier à casquette rouge ?','Mario',['Link','Kirby','Samus']),
 mc('Quel jeu construit son monde avec des blocs ?','Minecraft',['Tetris','Pac-Man','Portal'],'blocks'),
 mc('Quel personnage est un hérisson bleu ?','Sonic',['Pikachu','Yoshi','Donkey Kong'],'hedgehog'),
 mc('Quel héros contrôle-t-on souvent dans The Legend of Zelda ?','Link',['Zelda','Ganondorf','Bowser']),
 mc('Quel jeu fait tomber des pièces de quatre carrés ?','Tetris',['Mario Kart','Minecraft','Pokémon']),
 ],[
 buzz('Quel personnage jaune de Pokémon est associé à l’électricité ?','Pikachu','lightning'),
 buzz('Quel jeu d’arcade suit un personnage jaune dans un labyrinthe ?','Pac-Man','maze',['Pacman']),
 buzz('Quel frère de Mario porte du vert ?','Luigi'),
 buzz('Quelle princesse donne son nom à une série d’aventures de Nintendo ?','Zelda'),
 buzz('Quel jeu de course réunit Mario et ses amis sur des karts ?','Mario Kart'),
 ],[
 who('Mario',['Je suis un héros de Nintendo.','Luigi est mon frère.','Je sauve souvent la princesse Peach.','Je suis le plombier à la casquette rouge.']),
 who('Sonic',['Je suis un héros de Sega.','Je cours à grande vitesse.','Je ramasse souvent des anneaux.','Je suis un hérisson bleu.']),
 who('Pikachu',['Je suis un Pokémon.','Mes joues peuvent produire de l’électricité.','Je suis un compagnon de Sacha dans le dessin animé.','Je suis jaune, avec une queue en forme d’éclair.']),
 who('Minecraft',['Je suis un jeu de construction et d’exploration.','Les joueurs fabriquent des outils et des abris.','Les creepers peuplent mon monde.','Mes paysages sont faits de blocs.']),
 who('Pac-Man',['Je suis un héros de jeu d’arcade.','Je mange des pastilles.','Des fantômes me poursuivent dans un labyrinthe.','Je suis un disque jaune à grande bouche.']),
 ]))
TOPICS.append(topic('science-generale','Sciences — Découvertes accessibles','Sciences',[
 'https://science.nasa.gov/solar-system/','https://www.nasa.gov/','https://www.nobelprize.org/',
 'https://www.si.edu/spotlight/buginfo'],[
 mc('Quelle planète est surnommée la planète rouge ?','Mars',['Vénus','Jupiter','Mercure'],'mars'),
 mc('Quel phénomène attire les objets vers la Terre ?','La gravité',['Le magnétisme','La friction','La photosynthèse']),
 mc('Quel astre est au centre du Système solaire ?','Le Soleil',['La Lune','Jupiter','La Terre'],'sunrise'),
 mc('Quelle unité sert à mesurer la température en usage courant au Québec ?','Le degré Celsius',['Le kilogramme','Le litre','Le volt']),
 mc('Quel appareil agrandit l’image de très petits objets ?','Le microscope',['Le télescope','Le périscope','Le stéthoscope']),
 ],[
 buzz('Quel satellite naturel tourne autour de la Terre ?','La Lune','moon',['Lune']),
 buzz('Quel métal un aimant attire-t-il facilement : le fer ou l’or ?','Le fer','magnet',['Fer']),
 buzz('Quel gaz de l’air est indispensable à notre respiration ?','L’oxygène',aliases=['Oxygène']),
 buzz('Comment appelle-t-on le passage de l’eau liquide en vapeur ?','L’évaporation',aliases=['Évaporation']),
 buzz('Qui est associé à la théorie de la relativité ?','Albert Einstein',aliases=['Einstein']),
 ],[
 who('La Lune',['Je ne produis pas ma propre lumière visible.','Mes phases changent au fil des semaines.','Apollo 11 a atteint ma surface.','Je suis le satellite naturel de la Terre.'],['Lune']),
 who('Un aimant',['Je crée un champ autour de moi.','Je possède deux pôles.','J’attire notamment le fer.','On m’utilise parfois pour tenir un papier sur un réfrigérateur.'],['Aimant']),
 who('Mars',['Je suis une planète du Système solaire.','Je possède Phobos et Déimos comme lunes.','Des robots explorent ma surface.','On me surnomme la planète rouge.']),
 who('Un microscope',['Je suis un appareil scientifique.','Je permets d’observer ce qui est très petit.','On m’utilise pour étudier des cellules.','Mes lentilles agrandissent l’image d’un échantillon.'],['Microscope']),
 who('Albert Einstein',['Je suis un physicien.','Mon visage aux cheveux blancs est célèbre.','E = mc² est associé à mon travail.','J’ai développé la relativité.'],['Einstein']),
 ]))
TOPICS.append(topic('inventions-canada','Inventions canadiennes — Créateurs et objets','Sciences',[
 'https://nrc.canada.ca/en/research-development/research-collaboration/research-centres/history-canadian-innovation',
 'https://www.thecanadianencyclopedia.ca/en/article/inventions-and-innovations',
 'https://www.nobelprize.org/prizes/medicine/1923/summary/'],[
 mc('Quel sport James Naismith invente-t-il en 1891 ?','Le basketball',['Le volleyball','Le football','Le baseball'],'basketball'),
 mc('Quelle hormone traite le diabète grâce aux travaux de l’équipe de Toronto ?','L’insuline',['L’adrénaline','La mélatonine','La thyroxine']),
 mc('Quel créateur québécois est associé aux véhicules qui circulent sur la neige ?','Joseph-Armand Bombardier',['Alexander Graham Bell','Arthur Sicard','George Klein'],'snowmobile'),
 mc('Quel système de cinéma à écran géant est développé au Canada ?','IMAX',['Technicolor','Dolby','CinemaScope']),
 mc('Quel robot canadien a équipé les navettes spatiales ?','Le Canadarm',['Sojourner','Curiosity','Voyager']),
 ],[
 buzz('Quel appareil Arthur Sicard développe-t-il pour enlever la neige ?','La souffleuse à neige','snow',['Souffleuse']),
 buzz('Quel jeu de questions est créé par les Canadiens Chris Haney et Scott Abbott ?','Trivial Pursuit'),
 buzz('Quel téléphone intelligent est développé par Research In Motion à Waterloo ?','Le BlackBerry',aliases=['BlackBerry']),
 buzz('Quel sport utilise les paniers de Naismith ?','Le basketball','basketball',['Basket','Basketball']),
 buzz('Quel est le nom du bras robotisé canadien de la navette spatiale ?','Le Canadarm',aliases=['Canadarm']),
 ],[
 who('James Naismith',['Je suis né au Canada.','J’enseigne l’éducation physique aux États-Unis.','J’utilise deux paniers de pêches pour créer un jeu.','J’invente le basketball.']),
 who('Joseph-Armand Bombardier',['Je viens de Valcourt.','Je développe des véhicules adaptés à l’hiver.','Mes véhicules peuvent transporter des gens sur la neige.','Mon nom est celui d’une célèbre entreprise québécoise.'],['Bombardier']),
 who('L’insuline',['Je suis une hormone.','Je joue un rôle dans la régulation du sucre sanguin.','L’équipe de Banting travaille à mon usage médical à Toronto.','Je suis essentielle au traitement de nombreux diabétiques.'],['Insuline']),
 who('Le Canadarm',['Je suis un appareil robotisé.','Je travaille dans l’espace.','J’ai été installé sur les navettes de la NASA.','Mon nom anglais rappelle le Canada et un bras.'],['Canadarm']),
 who('IMAX',['Je suis un système de cinéma.','Des Canadiens ont participé à mon développement.','Je suis associé à une très grande image.','Je suis célèbre pour mes écrans géants et immersifs.']),
 ]))
TOPICS.append(topic('histoire-france-generale','Histoire de France — Figures et repères','Histoire',[
 'https://www.chateauversailles.fr/','https://www.britannica.com/place/France/History',
 'https://www.louvre.fr/'],[
 mc('Quel roi de France est surnommé le Roi-Soleil ?','Louis XIV',['Louis XVI','Henri IV','François Ier'],'sunrise'),
 mc('Quelle héroïne contribue à libérer Orléans en 1429 ?','Jeanne d’Arc',['Aliénor d’Aquitaine','Catherine de Médicis','Olympe de Gouges']),
 mc('Quel château est associé au règne de Louis XIV ?','Versailles',['Chambord','Chenonceau','Vincennes'],'versailles'),
 mc('Quel roi accueille Léonard de Vinci en France ?','François Ier',['Louis XIII','Henri III','Charles X']),
 mc('Quelle prison-forteresse est prise le 14 juillet 1789 ?','La Bastille',['Le Louvre','La Conciergerie','Le château d’If']),
 ],[
 buzz('Quelle reine est l’épouse de Louis XVI ?','Marie-Antoinette'),
 buzz('Quel empereur français est vaincu à Waterloo ?','Napoléon Bonaparte','battle',['Napoléon']),
 buzz('Quel édit de 1598 accorde une tolérance religieuse aux protestants ?','L’édit de Nantes',aliases=['Édit de Nantes']),
 buzz('Quel palais royal près de Paris est associé au Roi-Soleil ?','Versailles','versailles'),
 buzz('Quel chef de la France libre prononce l’appel du 18 juin 1940 ?','Charles de Gaulle',aliases=['De Gaulle']),
 ],[
 who('Louis XIV',['Mon règne dure plus de soixante-dix ans.','Je fais de Versailles le centre de ma cour.','Je suis associé à la monarchie absolue.','On me surnomme le Roi-Soleil.']),
 who('Jeanne d’Arc',['Je viens de Domrémy.','Je participe à la guerre de Cent Ans.','J’aide les forces françaises à Orléans.','On m’appelle la Pucelle d’Orléans.']),
 who('François Ier',['Je règne pendant la Renaissance.','Marignan marque le début de mon règne.','J’accueille Léonard de Vinci en France.','Mon prénom est François et je suis le premier de ce nom.']),
 who('Marie-Antoinette',['Je suis née dans la dynastie des Habsbourg.','Je deviens reine de France.','La Révolution met fin à ma vie.','Je suis l’épouse de Louis XVI.']),
 who('Charles de Gaulle',['Je dirige la France libre pendant la guerre.','Je prononce l’appel du 18 juin 1940.','Je deviens président sous la Ve République.','On m’appelle souvent le Général.']),
 ]))
TOPICS.append(topic('histoire-etats-unis','Histoire des États-Unis — Grands repères','Histoire',[
 'https://www.archives.gov/founding-docs','https://www.nps.gov/people/abraham-lincoln.htm',
 'https://www.nasa.gov/mission/apollo-11/','https://www.si.edu/'],[
 mc('Qui est le premier président des États-Unis ?','George Washington',['Thomas Jefferson','John Adams','Abraham Lincoln']),
 mc('Quelle statue est offerte par la France aux États-Unis ?','La Statue de la Liberté',['Le David','Le Penseur','Le Discobole'],'liberty-statue'),
 mc('En quelle année la Déclaration d’indépendance est-elle adoptée ?','1776',['1492','1789','1812']),
 mc('Quel président est associé à l’abolition de l’esclavage pendant la guerre de Sécession ?','Abraham Lincoln',['George Washington','Theodore Roosevelt','John Kennedy']),
 mc('Quelle mission américaine permet le premier pas humain sur la Lune ?','Apollo 11',['Apollo 8','Gemini 4','Mercury 7'],'moon'),
 ],[
 buzz('Quel président américain est assassiné à Dallas en 1963 ?','John F. Kennedy',aliases=['Kennedy','JFK']),
 buzz('Quel monument national sculpté représente quatre présidents dans une montagne ?','Le mont Rushmore','rushmore',['Mount Rushmore','Rushmore']),
 buzz('Quelle crise économique suit le krach de 1929 ?','La Grande Dépression',aliases=['Grande Dépression']),
 buzz('Quel astronaute américain marche le premier sur la Lune ?','Neil Armstrong','moon',['Armstrong']),
 buzz('Quel militant américain est associé au discours I Have a Dream ?','Martin Luther King Jr.',aliases=['Martin Luther King']),
 ],[
 who('George Washington',['Je dirige les forces américaines pendant la guerre d’indépendance.','Mon nom est celui de la capitale fédérale.','J’apparais sur le billet américain d’un dollar.','Je suis le premier président des États-Unis.']),
 who('Abraham Lincoln',['Je suis président pendant la guerre de Sécession.','Je prononce le discours de Gettysburg.','Je suis assassiné au théâtre Ford.','Je suis associé à l’émancipation des esclaves.']),
 who('Martin Luther King Jr.',['Je suis pasteur et militant.','Je défends les droits civiques par la non-violence.','Je prononce un discours à Washington en 1963.','Ce discours est connu comme I Have a Dream.'],['Martin Luther King']),
 who('Rosa Parks',['Je suis une figure des droits civiques.','Mon geste a lieu à Montgomery, en Alabama.','Je refuse de céder ma place dans un bus.','Mon prénom est Rosa.']),
 who('Neil Armstrong',['Je suis pilote puis astronaute.','Buzz Aldrin et Michael Collins sont mes coéquipiers.','Je commande Apollo 11.','Je suis le premier humain à marcher sur la Lune.']),
 ]))
