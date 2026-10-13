"""Standalone chronological sets; numeric keys define exact public milestones."""
from library_common import timeline
TOPICS=[]
def add(slug,title,subject,sources,entries):
 assert len(entries)==5
 TOPICS.append(dict(slug=slug,title=title,subject=subject,sources=sources,qcm=[],buzzer=[],qsj=[],chronologie=entries))
add('bd-premieres','BD — Premières apparitions','BD et manga',[
 'https://www.tintin.com/en/albums','https://www.dupuis.com/univers/FR/spirou.html',
 'https://www.luckyluke.com/','https://www.parcasterix.fr/nos-conseils/personnages-village-asterix',
 'https://www.dupuis.com/'],[
 timeline('Classez les premières apparitions',[('Tintin',1929),('Spirou',1938),('Astérix',1959)]),
 timeline('Classez les premières apparitions',[('Lucky Luke',1946),('Gaston Lagaffe',1957),('Les Schtroumpfs',1958)]),
 timeline('Classez les premières apparitions',[('Spirou',1938),('Lucky Luke',1946),('Gaston Lagaffe',1957)]),
 timeline('Classez les premières apparitions',[('Tintin',1929),('Les Schtroumpfs',1958),('Astérix',1959)]),
 timeline('Classez les premières apparitions',[('Tintin',1929),('Lucky Luke',1946),('Astérix',1959)]),
])
add('superheros-premieres','DC et Marvel — Premières apparitions','Super-héros',[
 'https://www.dc.com/characters/superman','https://www.dc.com/characters/batman','https://www.dc.com/characters/wonder-woman',
 'https://www.marvel.com/comics/guides/1284/80th_anniversary_silver_age',
 'https://share.marvel.com/comics/discover/1305/80th-anniversary-the-70s'],[
 timeline('Classez les débuts en bande dessinée',[('Superman',1938),('Batman',1939),('Wonder Woman',1941)]),
 timeline('Classez les débuts en bande dessinée',[('Captain America',1941),('Spider-Man — Peter Parker',1962),('Iron Man',1963)]),
 timeline('Classez les débuts en bande dessinée',[('Iron Man',1963),('Black Panther',1966),('Wolverine',1974)]),
 timeline('Classez les débuts en bande dessinée',[('Superman',1938),('Spider-Man — Peter Parker',1962),('Wolverine',1974)]),
 timeline('Classez les débuts en bande dessinée',[('Batman',1939),('Iron Man',1963),('Black Panther',1966)]),
])
add('disney-sorties','Disney — Sorties des films animés','Cinéma',[
 'https://d23.com/list-of-disney-films/','https://disneyanimation.com/films/'],[
 timeline('Classez les sorties originales des dessins animés',[('Blanche-Neige et les Sept Nains',1937),('Dumbo',1941),('Bambi',1942)]),
 timeline('Classez les sorties originales des dessins animés',[('Cendrillon',1950),('La Belle au bois dormant',1959),('Le Livre de la jungle',1967)]),
 timeline('Classez les sorties originales des dessins animés',[('La Petite Sirène',1989),('La Belle et la Bête',1991),('Aladdin',1992)]),
 timeline('Classez les sorties originales des dessins animés',[('Le Roi lion',1994),('Mulan',1998),('Lilo et Stitch',2002)]),
 timeline('Classez les sorties originales des dessins animés',[('La Princesse et la Grenouille',2009),('La Reine des neiges',2013),('Vaiana',2016)]),
])
add('ghibli-sorties','Studio Ghibli — Sorties japonaises','Cinéma',[
 'https://www.ghibli.jp/works/'],[
 timeline('Classez les sorties au Japon',[('Le Château dans le ciel',1986),('Mon voisin Totoro',1988),('Kiki la petite sorcière',1989)]),
 timeline('Classez les sorties au Japon',[('Porco Rosso',1992),('Princesse Mononoké',1997),('Le Voyage de Chihiro',2001)]),
 timeline('Classez les sorties au Japon',[('Le Château ambulant',2004),('Ponyo sur la falaise',2008),('Le Vent se lève',2013)]),
 timeline('Classez les sorties au Japon',[('Mon voisin Totoro',1988),('Le Voyage de Chihiro',2001),('Le Garçon et le Héron',2023)]),
 timeline('Classez les sorties au Japon',[('Princesse Mononoké',1997),('Ponyo sur la falaise',2008),('Le Conte de la princesse Kaguya',2013)]),
])
add('musique-reperes','Musique — Œuvres dans le temps','Musique',[
 'https://www.beethoven.de/','https://mozarteum.at/','https://www.thebeatles.com/abbey-road',
 'https://www.michaeljackson.com/albums/thriller/','https://www.queenonline.com/music',
 'https://www.britannica.com/'],[
 timeline('Classez les compositeurs selon leur naissance',[('Jean-Sébastien Bach',1685),('Mozart',1756),('Beethoven',1770)]),
 timeline('Classez les créations publiques de ces œuvres',[('La Flûte enchantée',1791),('Neuvième Symphonie de Beethoven',1824),('Le Lac des cygnes',1877)]),
 timeline('Classez les sorties des albums',[('Abbey Road — The Beatles',1969),('A Night at the Opera — Queen',1975),('Thriller — Michael Jackson',1982)]),
 timeline('Classez les compositeurs selon leur naissance',[('Vivaldi',1678),('Chopin',1810),('Tchaïkovski',1840)]),
 timeline('Classez ces repères musicaux',[('Création de La Flûte enchantée',1791),('Sortie d’Abbey Road',1969),('Sortie de Thriller',1982)]),
])
add('romans-publications','Littérature — Premières publications','Littérature',[
 'https://www.gutenberg.org/','https://catalogue.bnf.fr/','https://www.loc.gov/'],[
 timeline('Classez les premières publications en volume',[('Pride and Prejudice',1813),('Frankenstein',1818),('Jane Eyre',1847)]),
 timeline('Classez les premières publications en volume',[('Notre-Dame de Paris',1831),('Madame Bovary',1857),('Les Misérables',1862)]),
 timeline('Classez les premières publications en volume',[('Moby-Dick',1851),('The Great Gatsby',1925),('To Kill a Mockingbird',1960)]),
 timeline('Classez les premières publications en volume',[('Alice’s Adventures in Wonderland',1865),('Dracula',1897),('Animal Farm',1945)]),
 timeline('Classez les premières publications',[('Candide',1759),('Le Petit Prince',1943),('Fahrenheit 451',1953)]),
])
add('explorateurs-reperes','Explorateurs — Voyages et expéditions','Histoire',[
 'https://www.rmg.co.uk/stories/topics/ferdinand-magellan',
 'https://www.thecanadianencyclopedia.ca/fr/article/jacques-cartier',
 'https://www.thecanadianencyclopedia.ca/fr/article/samuel-de-champlain',
 'https://www.britannica.com/biography/Roald-Amundsen'],[
 timeline('Classez ces étapes de navigation européenne',[('Colomb atteint les Caraïbes',1492),('Vasco de Gama atteint l’Inde',1498),('L’expédition de Magellan-Elcano achève le tour du monde',1522)]),
 timeline('Classez ces repères en Amérique du Nord',[('Cabot atteint les côtes de l’Atlantique Nord',1497),('Premier voyage de Cartier',1534),('Champlain fonde Québec',1608)]),
 timeline('Classez ces repères',[('Premier voyage de Cartier',1534),('Champlain fonde Québec',1608),('Amundsen atteint le pôle Sud',1911)]),
 timeline('Classez les étapes de la première circumnavigation',[('Départ de l’expédition de Magellan',1519),('Mort de Magellan aux Philippines',1521),('Retour d’Elcano en Espagne',1522)]),
 timeline('Classez ces voyages',[('Colomb atteint les Caraïbes',1492),('Cartier atteint Hochelaga',1535),('Amundsen atteint le pôle Sud',1911)]),
])
add('odyssee-episodes','L’Odyssée — Ordre des épisodes','Mythologie',[
 'https://www.gutenberg.org/ebooks/1727','https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0136'],[
 timeline('Suivez le voyage d’Ulysse, pas l’ordre des chapitres',[('Fin de la guerre de Troie',1),('Rencontre du Cyclope',2),('Retour à Ithaque',3)]),
 timeline('Suivez le voyage d’Ulysse, pas l’ordre des chapitres',[('Rencontre du Cyclope',1),('Séjour chez Circé',2),('Passage devant les Sirènes',3)]),
 timeline('Suivez le voyage d’Ulysse, pas l’ordre des chapitres',[('Séjour chez Circé',1),('Passage devant les Sirènes',2),('Séjour chez Calypso',3)]),
 timeline('Classez les événements du retour',[('Arrivée à Ithaque',1),('Épreuve de l’arc et combat contre les prétendants',2),('Pénélope reconnaît Ulysse grâce au secret du lit',3)]),
 timeline('Suivez le voyage d’Ulysse, pas l’ordre des chapitres',[('Séjour chez Calypso',1),('Accueil chez les Phéaciens',2),('Arrivée à Ithaque',3)]),
])
add('nature-cycles','Nature — Cycles de vie','Nature',[
 'https://naturalhistory.si.edu/education/teaching-resources/life-science/butterflies-and-beyond',
 'https://www.allaboutbirds.org/guide/','https://www.britannica.com/science/metamorphosis'],[
 timeline('Classez ces étapes de vie du papillon',[('Œuf',1),('Chenille',2),('Papillon adulte',3)]),
 timeline('Classez ces étapes de vie de la grenouille',[('Œuf',1),('Têtard',2),('Grenouille adulte',3)]),
 timeline('Classez ces étapes de vie d’un oiseau',[('Ponte de l’œuf',1),('Éclosion',2),('Premier envol',3)]),
 timeline('Classez ces étapes chez un mammifère',[('Gestation',1),('Naissance',2),('Sevrage',3)]),
 timeline('Classez ces étapes d’une abeille',[('Œuf',1),('Larve',2),('Abeille adulte',3)]),
])
add('architecture-reperes','Architecture — Monuments dans le temps','Architecture',[
 'https://www.toureiffel.paris/en/the-monument/history','https://www.sydneyoperahouse.com/our-story',
 'https://www.burjkhalifa.ae/','https://www.nps.gov/stli/learn/statue-of-liberty-facts.htm',
 'https://www.chateauversailles.fr/','https://www.louvre.fr/'],[
 timeline('Classez les ouvertures et inaugurations',[('Tour Eiffel',1889),('Opéra de Sydney',1973),('Burj Khalifa',2010)]),
 timeline('Classez ces inaugurations',[('Statue de la Liberté à New York',1886),('Tour Eiffel',1889),('Opéra de Sydney',1973)]),
 timeline('Classez ces repères',[('Ouverture du Louvre comme musée',1793),('Inauguration de la tour Eiffel',1889),('Ouverture du Burj Khalifa',2010)]),
 timeline('Classez ces repères',[('Installation de la cour de Louis XIV à Versailles',1682),('Ouverture du Louvre comme musée',1793),('Ouverture de l’Opéra de Sydney',1973)]),
 timeline('Classez ces inaugurations',[('Statue de la Liberté à New York',1886),('Opéra de Sydney',1973),('Burj Khalifa',2010)]),
])
