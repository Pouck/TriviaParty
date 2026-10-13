"""French cinema quizzes. Sources are verification references, not copied questions."""
SOURCES={
 'gandalf':'https://www.mckellen.com/cinema/lotr/',
 'titanic':'https://www.bfi.org.uk/film/aa4a1930-21de-51ce-9700-6acaf2d59437/titanic',
 'blade':'https://www.bfi.org.uk/features/where-begin-with-ridley-scott',
 'inception':'https://www.nolanfans.com/library/pdf/inception-screenplay.pdf',
 'dune':'https://www.dunemovie.com/',
 'gladiator':'https://www.paramountpictures.com/movies/gladiator',
 'godfather':'https://www.paramountpictures.com/movies/the-godfather',
 'haine':'https://www.bfi.org.uk/features/la-haine-project-surrealism',
 'williams':'https://www.starwars.com/news/john-williams-birthday',
 'parasite':'https://www.festival-cannes.com/en/f/gisaengchung/',
 'amelie':'https://www.sonyclassics.com/film/amelie/',
 'leone':'https://www.bfi.org.uk/lists/10-great-films-set-desert',
 'chihiro':'https://gkids.com/films/spirited-away/',
 'walle':'https://www.pixar.com/wall-e',
 'nightmare':'https://d23.com/25-years-of-making-nightmares/',
 'toystory':'https://www.pixar.com/our-story',
 'oscar2020':'https://www.oscars.org/oscars/ceremonies/2020',
 'oscar1998':'https://www.oscars.org/oscars/ceremonies/1998',
 'oscar2002':'https://www.oscars.org/oscars/ceremonies/2002',
 'cannes1994':'https://www.festival-cannes.com/en/f/pulp-fiction/',
 'disney-list':'https://d23.com/list-of-disney-films/',
 'furiosa':'https://www.bfi.org.uk/lists/10-great-dangerous-journey-films',
 'kubrick':'https://www.bfi.org.uk/film/cefccdb2-b558-5623-9c17-72b4be7bd4c1/2001-a-space-odyssey',
 'oscar2004':'https://www.oscars.org/oscars/ceremonies/2004',
 'hogwarts':'https://www.harrypotter.com/fact-file/locations/hogwarts',
 'woody':'https://www.pixar.com/toy-story',
 'frodo':'https://www.bfi.org.uk/film/83919a25-6bb5-5866-bef4-3249172e8b9a/the-lord-of-the-rings-the-two-towers',
 'et':'https://amblin.com/movie/e-t-the-extra-terrestrial/',
 'gollum':'https://www.bfi.org.uk/film/83919a25-6bb5-5866-bef4-3249172e8b9a/the-lord-of-the-rings-the-two-towers',
 'ironman':'https://www.marvel.com/comics/guides/1723/tony-stark-iron-man',
 'zootopia':'https://movies.disney.com/zootopia',
 'batman':'https://www.dc.com/characters/batman',
 'thor':'https://www.marvel.com/comics/guides/181/who_has_wielded_thors_hammer',
 'superman':'https://www.dc.com/characters/superman',
 'lightsaber':'https://www.starwars.com/databank/lightsaber',
 'avatar':'https://www.avatar.com/pandorapedia/',
 'frozen':'https://movies.disney.com/frozen',
 'nemo':'https://www.pixar.com/finding-nemo',
 'simba':'https://movies.disney.com/the-lion-king',
 'vadrouille':'https://www.cinematheque.fr/film/50401.html',
 'choristes':'https://www.unifrance.org/film/24171/les-choristes',
 'cleopatre':'https://www.pathefilms.com/fr/films/asterix-et-obelix-mission-cleopatre/',
 'intouchables':'https://medias.unifrance.org/medias/97/17/69985/presse/intouchables-dossier-de-presse-anglais.pdf',
 'visiteurs':'https://www.gaumont.com/en/node/2612',
 'boncop':'https://www.cinematheque.qc.ca/en/cinema/bon-cop-bad-cop/',
 'lazhar':'https://www.musicboxfilms.com/film/monsieur-lazhar/',
 'future':'https://www.backtothefuture.com/movies/backtothefuture1/',
 'jaws':'https://amblin.com/movie/jaws/',
 'matrix':'https://www.bfi.org.uk/features/matrix-wachowskis-keanu-reeves',
 'pirates':'https://d23.com/a-to-z/pirates-of-the-caribbean-the-curse-of-the-black-pearl-film/',
 'spielberg':'https://amblin.com/steven-spielberg/',
 'chaplin':'https://www.charliechaplin.com/en/biography/articles/21-Chaplin-s-Life',
 'hitchcock':'https://www.bfi.org.uk/features/set-alfred-hitchcock',
 'indy':'https://www.lucasfilm.com/productions/indiana-jones-and-the-last-crusade/',
 'bond':'https://www.007.com/the-films/',
 'jurassic':'https://amblin.com/movie/jurassic-park/',
 'raiders':'https://www.lucasfilm.com/productions/raiders-of-the-lost-ark/',
 'indy-history':'https://www.lucasfilm.com/who-we-are/our-story/',
 'starwars-history':'https://www.starwars.com/news/star-wars-movies-and-series-guide',
 'musicals':'https://catalog.afi.com/Catalog/moviedetails/50652',
 'soundmusic':'https://www.bfi.org.uk/lists/best-musical-every-year',
 'grease':'https://catalog.afi.com/Catalog/moviedetails/55211',
 'superman1978':'https://www.bfi.org.uk/sight-and-sound/greatest-films-all-time/all-voters/ben-stoddart',
 'batman1989':'https://www.bfi.org.uk/film/43a149e2-78d7-53e5-bed2-a26c8dca3e2d/batman-begins',
 'spiderman2002':'https://www.sonypictures.com/movies/spiderman',
 'bond-history':'https://www.007.com/page/57/?cat=missions&id=drno',
 'potter-films':'https://www.harrypotter.com/discover/films',
 'potter2005':'https://www.bfi.org.uk/film/ff6fde32-6103-533b-96d5-214a6820eeb8/harry-potter-and-the-goblet-of-fire',
 'potter2011':'https://www.bfi.org.uk/film/b20515b2-b16c-5b81-8aed-6c39e514e889/harry-potter-and-the-deathly-hallows-part-2',
 'lotr-films':'https://www.bfi.org.uk/lists/remembering-ian-holm-10-essential-films',
}
def mc(prompt,options,index,source,note=''):
 return dict(prompt=prompt,options=options,index=index,sources=[source],note=note)
def buzz(prompt,answers,source,note=''):
 return dict(prompt=prompt,answers=answers,sources=[source],note=note)
def guess(answers,clues,source,note=''):
 return dict(answers=answers,clues=clues,sources=[source],note=note)
def chrono(theme,films,sources):
 return dict(theme=theme,films=films,sources=sources,note='Premières sorties originales en salles ; pas les rééditions, remakes ni la chronologie interne du récit.')

CHOICE=[
('films-personnages','Films et personnages',[
 mc('Qui incarne Gandalf dans la trilogie du Seigneur des anneaux réalisée par Peter Jackson ?', ['Ian McKellen','Christopher Lee','Michael Gambon','Richard Harris'],0,'gandalf'),
 mc('Qui réalise Titanic, sorti en 1997 ?', ['Steven Spielberg','James Cameron','Ridley Scott','Robert Zemeckis'],1,'titanic'),
 mc('Dans quelle ville se déroule principalement Blade Runner, le film de 1982 ?', ['New York','Tokyo','Los Angeles','Chicago'],2,'blade'),
 mc('Quel objet Cobb fait-il tourner dans la dernière scène d’Inception ?', ['Une pièce de monnaie','Une toupie','Un dé','Une bague'],1,'inception','La question porte sur l’objet visible, sans imposer une interprétation de la fin ni de son propriétaire initial.'),
 mc('Quel écrivain est l’auteur du roman Dune, adapté au cinéma ?', ['Isaac Asimov','Arthur C. Clarke','Frank Herbert','Philip K. Dick'],2,'dune'),
 mc('Dans Gladiator (2000), quelle civilisation domine le monde de Maximus ?', ['La Grèce antique','L’Empire romain','L’Égypte pharaonique','L’Empire perse'],1,'gladiator'),
 mc('Quel nom porte la famille au centre de The Godfather (Le Parrain) ?', ['Corleone','Soprano','Barzini','Tattaglia'],0,'godfather'),
 mc('Quels sont les trois amis au centre de La Haine ?', ['Vinz, Saïd et Hubert','Vinz, Nino et Driss','Hubert, Philippe et Saïd','Nino, Driss et Philippe'],0,'haine'),
]),
('coulisses','Réalisateurs, musique et animation',[
 mc('Qui compose le célèbre thème principal du premier Star Wars, sorti en 1977 ?', ['Hans Zimmer','John Williams','Ennio Morricone','Howard Shore'],1,'williams'),
 mc('Qui réalise Parasite, Palme d’or en 2019 ?', ['Park Chan-wook','Bong Joon-ho','Kim Ki-duk','Lee Chang-dong'],1,'parasite'),
 mc('Qui réalise Le Fabuleux Destin d’Amélie Poulain ?', ['Luc Besson','Michel Gondry','Jean-Pierre Jeunet','Jacques Audiard'],2,'amelie'),
 mc('Qui réalise Le Bon, la Brute et le Truand ?', ['Sergio Leone','John Ford','Clint Eastwood','Sam Peckinpah'],0,'leone'),
 mc('Quel cinéaste réalise Le Voyage de Chihiro ?', ['Isao Takahata','Hayao Miyazaki','Satoshi Kon','Mamoru Hosoda'],1,'chihiro'),
 mc('Quel studio produit WALL-E ?', ['DreamWorks Animation','Pixar','Studio Ghibli','Aardman'],1,'walle'),
 mc('Quel film utilise principalement l’animation image par image de marionnettes ?', ['L’Étrange Noël de monsieur Jack','Toy Story','Finding Nemo','Zootopia'],0,'nightmare','Henry Selick réalise ce film ; Tim Burton en est notamment le créateur et producteur.'),
 mc('Quel long métrage de 1995 est le premier entièrement animé par ordinateur ?', ['A Bug’s Life','Toy Story','Shrek','Monsters, Inc.'],1,'toystory'),
]),
('prix-classiques','Récompenses et classiques',[
 mc('Quel film devient, en 2020, le premier film principalement non anglophone à remporter l’Oscar du meilleur film ?', ['Roma','Parasite','La vita è bella','Crouching Tiger, Hidden Dragon'],1,'oscar2020','Cérémonie de 2020 ; Parasite est un film de 2019.'),
 mc('Parmi ces films, lequel remporte onze Oscars lors de la cérémonie de 1998 ?', ['Titanic','Avatar','Jurassic Park','Terminator 2: Judgment Day'],0,'oscar1998'),
 mc('Quel film reçoit le premier Oscar du meilleur long métrage d’animation, remis en 2002 ?', ['Monsters, Inc.','Toy Story 2','Shrek','The Lion King'],2,'oscar2002'),
 mc('Quel film de Quentin Tarantino remporte la Palme d’or en 1994 ?', ['Reservoir Dogs','Pulp Fiction','Jackie Brown','Kill Bill: Volume 1'],1,'cannes1994'),
 mc('Quel est le premier long métrage d’animation des studios Disney ?', ['Pinocchio','Fantasia','Snow White and the Seven Dwarfs','Dumbo'],2,'disney-list','Premier long métrage d’animation Disney, pas premier long métrage d’animation de l’histoire du cinéma.'),
 mc('Qui incarne Furiosa dans Mad Max: Fury Road (2015) ?', ['Charlize Theron','Anya Taylor-Joy','Emily Blunt','Cate Blanchett'],0,'furiosa','Le film de 2015 est précisé pour éviter la confusion avec Furiosa (2024).'),
 mc('Qui réalise 2001: A Space Odyssey ?', ['Stanley Kubrick','Ridley Scott','George Lucas','Steven Spielberg'],0,'kubrick'),
 mc('Quel film québécois remporte l’Oscar du meilleur film en langue étrangère en 2004 ?', ['Les Invasions barbares','Monsieur Lazhar','Incendies','Le Déclin de l’empire américain'],0,'oscar2004'),
])]

BUZZER=[
('titres-heros','Titres et héros — Rapide',[
 buzz('Dans quel film de 1997 Jack et Rose tombent-ils amoureux à bord d’un paquebot ?', ['Titanic'],'titanic'),
 buzz('Comment s’appelle l’école de sorcellerie où Harry Potter étudie ?', ['Poudlard','Hogwarts'],'hogwarts'),
 buzz('Comment s’appelle le jouet cow-boy dans Toy Story ?', ['Woody'],'woody'),
 buzz('Quel hobbit, incarné par Elijah Wood, doit détruire l’Anneau dans les films du Seigneur des anneaux ?', ['Frodon','Frodon Sacquet','Frodo','Frodo Baggins'],'frodo'),
 buzz('Quel extraterrestre de cinéma se lie d’amitié avec un garçon nommé Elliott ?', ['E.T.','ET','E.T. l’extraterrestre'],'et'),
 buzz('Quel personnage du Seigneur des anneaux est interprété en capture de mouvement par Andy Serkis ?', ['Gollum'],'gollum'),
 buzz('Quel superhéros se cache derrière l’identité de Tony Stark ?', ['Iron Man','Ironman'],'ironman'),
 buzz('Quel film d’animation réunit la policière lapine Judy Hopps et le renard Nick Wilde ?', ['Zootopia','Zootopie','Zootropolis'],'zootopia'),
]),
('univers','Univers et animation — Rapide',[
 buzz('Dans quelle ville fictive Batman combat-il le crime ?', ['Gotham','Gotham City'],'batman'),
 buzz('Comment s’appelle le marteau de Thor dans les films Marvel ?', ['Mjolnir','Mjølnir'],'thor'),
 buzz('De quelle planète Superman est-il originaire ?', ['Krypton'],'superman'),
 buzz('Quelle arme lumineuse les Jedi utilisent-ils dans Star Wars ?', ['Un sabre laser','Le sabre laser','Sabre laser','Lightsaber'],'lightsaber'),
 buzz('Sur quel monde vivent les Na’vi dans Avatar ?', ['Pandora'],'avatar','Pandora est une lune ; le mot « planète » a été évité.'),
 buzz('Comment s’appelle la sœur d’Anna qui possède des pouvoirs de glace dans Frozen (La Reine des neiges) ?', ['Elsa'],'frozen'),
 buzz('Quel type de poisson est Nemo ?', ['Un poisson-clown','Poisson-clown','Poisson clown'],'nemo'),
 buzz('Quel lion est le fils de Mufasa dans The Lion King (Le Roi lion) ?', ['Simba'],'simba'),
]),
('france-quebec','France et Québec — Rapide',[
 buzz('Qui incarne le chef d’orchestre Stanislas Lefort dans La Grande Vadrouille ?', ['Louis de Funès','Louis de Funes','De Funès'],'vadrouille'),
 buzz('Dans Les Choristes, quelle activité musicale Clément Mathieu fait-il pratiquer aux élèves ?', ['Le chant choral','Le chant','Une chorale','Un chœur'],'choristes'),
 buzz('Quelle reine d’Égypte confie la construction d’un palais à Numérobis dans le film d’Alain Chabat ?', ['Cléopâtre','Cleopatre'],'cleopatre'),
 buzz('Dans quelle ville se déroule principalement Le Fabuleux Destin d’Amélie Poulain ?', ['Paris'],'amelie'),
 buzz('Qui joue Philippe, l’homme tétraplégique, dans le film français Intouchables ?', ['François Cluzet','Francois Cluzet','Cluzet'],'intouchables'),
 buzz('Quel acteur incarne Godefroy de Montmirail dans Les Visiteurs ?', ['Jean Reno','Reno'],'visiteurs'),
 buzz('Dans Bon Cop, Bad Cop, de quelles deux provinces viennent les policiers principaux ?', ['Le Québec et l’Ontario','Québec et Ontario','Ontario et Québec'],'boncop'),
 buzz('De quel pays Bachir Lazhar est-il originaire dans Monsieur Lazhar ?', ['L’Algérie','Algérie','Algerie'],'lazhar'),
])]

GUESS=[
('films','Films à découvrir',[
 guess(['Back to the Future','Retour vers le futur'],[
 'Mon histoire met en péril l’existence d’un adolescent lorsqu’il rencontre ses parents encore jeunes.',
 'Une horloge frappée par la foudre joue un rôle décisif dans mon dénouement.',
 'Doc Brown transforme une DeLorean en machine à voyager dans le temps.',
 'Marty McFly est envoyé de 1985 à 1955 dans ce film de Robert Zemeckis.'
 ],'future'),
 guess(['Jaws','Les Dents de la mer','Les Dents de mer'],[
 'Mon intrigue oppose la sécurité des habitants aux intérêts touristiques d’une station balnéaire.',
 'Un policier, un biologiste marin et un pêcheur partent ensemble en mer.',
 'La communauté d’Amity est terrorisée par un grand requin blanc.',
 'Je suis le film de Steven Spielberg, sorti en 1975, qui a fait craindre les baignades en mer.'
 ],'jaws'),
 guess(['The Matrix','Matrix','La Matrice'],[
 'Mon héros découvre que sa vie quotidienne masque une réalité fabriquée par des machines.',
 'Morpheus lui propose de choisir entre une pilule rouge et une pilule bleue.',
 'Keanu Reeves incarne Neo, qui affronte notamment l’agent Smith.',
 'Je suis le film de science-fiction des Wachowski, sorti en 1999, consacré à une simulation informatique.'
 ],'matrix'),
 guess(['Le Fabuleux Destin d’Amélie Poulain','Amélie','Amélie Poulain','Amelie'],[
 'Mon héroïne décide d’améliorer discrètement la vie des gens qu’elle observe.',
 'Elle croise notamment un collectionneur de photos nommé Nino Quincampoix.',
 'Audrey Tautou y joue une serveuse du quartier de Montmartre.',
 'Je suis le film de Jean-Pierre Jeunet dont l’héroïne parisienne porte le prénom Amélie.'
 ],'amelie'),
 guess(['Pirates of the Caribbean: The Curse of the Black Pearl','Pirates des Caraïbes : La Malédiction du Black Pearl','La Malédiction du Black Pearl','Pirates des Caraïbes 1'],[
 'Une malédiction transforme certains de mes personnages en squelettes sous la lumière de la lune.',
 'Will Turner cherche à sauver Elizabeth Swann, enlevée à Port Royal.',
 'Le capitaine Barbossa a pris le navire d’un pirate excentrique incarné par Johnny Depp.',
 'Je suis le premier Pirates des Caraïbes, sorti en 2003, avec Jack Sparrow et le Black Pearl.'
 ],'pirates'),
]),
('figures','Cinéastes et personnages',[
 guess(['Steven Spielberg','Spielberg'],[
 'Je réalise Duel, un suspense où un automobiliste est poursuivi par un camion.',
 'Mon film Schindler’s List me vaut l’Oscar de la réalisation.',
 'Je mets en scène E.T. et les dinosaures de Jurassic Park.',
 'Je suis le réalisateur de Jaws et de plusieurs aventures d’Indiana Jones.'
 ],'spielberg'),
 guess(['Charlie Chaplin','Charles Chaplin','Chaplin'],[
 'Né à Londres en 1889, je suis acteur, réalisateur et compositeur.',
 'Dans Modern Times, je confronte mon personnage à une chaîne de montage.',
 'Une petite moustache, une canne et un chapeau melon font partie de mon image.',
 'Je suis l’acteur et cinéaste qui a créé le personnage de Charlot.'
 ],'chaplin','On demande l’artiste, pas seulement le nom de son personnage Charlot.'),
 guess(['Alfred Hitchcock','Hitchcock'],[
 'J’aime faire de brèves apparitions dans mes propres films.',
 'Rope expérimente un récit donnant l’impression de longs plans ininterrompus.',
 'Je dirige James Stewart dans Rear Window et Vertigo.',
 'Surnommé le maître du suspense, je réalise Psycho et The Birds.'
 ],'hitchcock'),
 guess(['Indiana Jones','Indy','Henry Jones Junior','Henry Jones Jr.'],[
 'Mon père, professeur, est incarné par Sean Connery dans l’une de mes aventures.',
 'Je recherche notamment l’Arche d’alliance et le Saint Graal.',
 'Mon fouet et mon chapeau accompagnent mes expéditions ; je redoute les serpents.',
 'Je suis l’archéologue aventurier incarné pendant des décennies par Harrison Ford.'
 ],'indy'),
 guess(['James Bond','Bond','007'],[
 'Mes aventures cinématographiques commencent avec Dr. No, en 1962.',
 'M dirige mes missions et Q me fournit des équipements spéciaux.',
 'Sean Connery, Roger Moore et Daniel Craig font partie des acteurs qui m’ont incarné.',
 'Je suis l’agent secret britannique connu sous le numéro 007.'
 ],'bond'),
])]

CHRONOLOGY=[
('reperes','Sorties de films — Repères',[
 chrono('Grands succès de Spielberg', [('Jaws',1975),('Raiders of the Lost Ark',1981),('Jurassic Park',1993)], ['jaws','raiders','jurassic']),
 chrono('Animation Disney — versions originales', [('Snow White and the Seven Dwarfs',1937),('Cinderella',1950),('The Lion King',1994)], ['disney-list']),
 chrono('Science-fiction', [('2001: A Space Odyssey',1968),('Star Wars: A New Hope',1977),('The Matrix',1999)], ['kubrick','starwars-history','matrix']),
 chrono('Comédies musicales', [('Singin’ in the Rain',1952),('The Sound of Music',1965),('Grease',1978)], ['musicals','soundmusic','grease']),
 chrono('Superhéros — versions avec ces acteurs', [('Superman (Christopher Reeve)',1978),('Batman (Michael Keaton)',1989),('Spider-Man (Tobey Maguire)',2002)], ['superman1978','batman1989','spiderman2002']),
 chrono('Aventure et grands spectacles', [('Back to the Future',1985),('Jurassic Park',1993),('Titanic',1997)], ['future','jurassic','titanic']),
]),
('sagas','Sorties de films — Sagas et studios',[
 chrono('Indiana Jones', [('Raiders of the Lost Ark',1981),('Indiana Jones and the Temple of Doom',1984),('Indiana Jones and the Last Crusade',1989)], ['indy-history']),
 chrono('James Bond — époque Daniel Craig', [('Casino Royale',2006),('Skyfall',2012),('Spectre',2015)], ['bond-history']),
 chrono('Pixar', [('Toy Story',1995),('Finding Nemo',2003),('Inside Out',2015)], ['disney-list','toystory']),
 chrono('Harry Potter', [('Harry Potter à l’école des sorciers',2001),('Harry Potter et la Coupe de feu',2005),('Harry Potter et les Reliques de la Mort — Partie 2',2011)], ['potter-films','potter2005','potter2011']),
 chrono('Le Seigneur des anneaux', [('La Communauté de l’anneau',2001),('Les Deux Tours',2002),('Le Retour du roi',2003)], ['lotr-films','frodo']),
 chrono('Star Wars — trilogie originale', [('A New Hope',1977),('The Empire Strikes Back',1980),('Return of the Jedi',1983)], ['starwars-history']),
])]
