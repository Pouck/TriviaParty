"""Editorial replacements: avoid teaching the same event order repeatedly.

Events are in answer order; dates remain in private verification records, never
on the question cards. IDs survive so saved reviews still refer to the question.
"""
REVISIONS={}
def revise(pid,n,prompt,events,sources):
    REVISIONS[f'{pid}-{n:02}']=dict(prompt=prompt,events=events,sources=sources)

p='lib-chronologie-architecture-reperes-20261012'
revise(p,1,'Classez ces inaugurations.',[('Tour Eiffel',1889),('Opéra de Sydney',1973),('Burj Khalifa',2010)],['https://www.toureiffel.paris/fr/actualites/130-ans/1889-2019-130-ans-demerveillement','https://www.sydneyoperahouse.com/our-story/50-years-extraordinary-moments','https://www.burjkhalifa.ae/the-tower/making/'])
revise(p,2,'Classez ces ouvertures au public.',[('Louvre comme musée',1793),('Statue de la Liberté à New York',1886),('Tour CN à Toronto',1976)],['https://mini-site.louvre.fr/trimestriel/2019/Agenda_mars_mai_2019/files/assets/common/downloads/publication.pdf','https://www.nps.gov/stli/learn/statue-of-liberty-facts.htm','https://www.cntower.ca/history'])
revise(p,3,'Classez ces étapes de monuments européens.',[('Achèvement de la basilique Saint-Pierre actuelle',1626),('Installation de la cour à Versailles',1682),('Inauguration du palais Garnier',1875)],['https://www.basilicasanpietro.va/fr/faq/quand-la-basilique-saintpierre-atelle-ete-construite','https://www.chateauversailles.fr/decouvrir/histoire/grandes-dates/versailles-capitale-royaume','https://www.operadeparis.fr/info/150-ans-du-palais-garnier'])
revise(p,4,'Classez ces étapes de construction et d’ouverture.',[('Début du chantier de la Sagrada Família',1882),('Ouverture de Tower Bridge',1894),('Ouverture du Golden Gate Bridge',1937)],['https://sagradafamilia.org/en/history-of-the-temple','https://www.towerbridge.org.uk/stories/history','https://www.goldengate.org/bridge/history-research/moments-events/key-dates/'])
revise(p,5,'Classez ces inaugurations du XXe siècle.',[('Empire State Building',1931),('Centre Pompidou',1977),('Pyramide du Louvre',1989)],['https://www.esbnyc.com/about/history','https://www.centrepompidou.fr/fileadmin/user_upload/dossier-ressources-architecture-centre-pompidou-chrono_20230829.pdf','https://www.louvre.fr/decouvrir/le-palais/une-pyramide-pour-symbole'])

p='lib-chronologie-bd-premieres-20261012'
revise(p,3,'Classez les premières apparitions en BD.',[('Blake et Mortimer',1946),('Marsupilami',1952),('Boule et Bill',1959)],['https://www.dargaud.com/auteurs/edgar-p-jacobs','https://www.larousse.fr/encyclopedie/personnage/André_Franquin/120242','https://www.larousse.fr/encyclopedie/divers/Boule_et_Bill/184544'])
revise(p,4,'Classez les premières apparitions en BD.',[('Iznogoud',1962),('Achille Talon',1963),('Le Chat de Geluck',1983)],['https://iznogoud.com/naissance_vizir','https://www.dargaud.com/auteurs/greg','https://lechat.com/philippe-geluck/'])
revise(p,5,'Classez les débuts de ces séries en BD.',[('XIII',1984),('Largo Winch',1990),('Lou !',2004)],['https://www.dargaud.com/bd/xiii','https://www.dupuis.com/seriebd/largo-winch-l-integrale/4064','https://www.glenat.com/glenat-bd/lou-tome-01-9782723442756/'])

p='lib-chronologie-superheros-premieres-20261012'
revise(p,2,'Classez les débuts en bande dessinée.',[('Captain America',1941),('Hulk',1962),('Wolverine',1974)],['https://www.marvel.com/comics/guides/1284/80th_anniversary_silver_age','https://www.marvel.com/comics/guides/1305/80th-anniversary-the-70s'])
revise(p,3,'Classez les débuts de ces héros en BD.',[('Flash — Barry Allen',1956),('Green Lantern — Hal Jordan',1959),('Iron Man',1963)],['https://www.dc.com/blog/2023/06/14/flash-facts-things-you-may-not-know-about-the-scarlet-speedster','https://www.dc.com/blog/2021/09/24/finding-the-perfect-foe-how-long-did-it-take','https://www.marvel.com/comics/guides/1284/80th_anniversary_silver_age'])
revise(p,4,'Classez les débuts en bande dessinée.',[('Les Quatre Fantastiques',1961),('Spider-Man — Peter Parker',1962),('Black Panther',1966)],['https://www.marvel.com/comics/guides/1284/80th_anniversary_silver_age'])
revise(p,5,'Classez les débuts en bande dessinée.',[('Doctor Strange',1963),('Luke Cage',1972),('Deadpool',1991)],['https://www.marvel.com/amp/articles/comics/the-8-most-influential-doctor-strange-stories','https://share.marvel.com/comics/discover/433/luke-cage','https://www.marvel.com/comics/discover/1381/80th-anniversary-the-90s'])

p='lib-chronologie-ghibli-sorties-20261012'
for n,events in [(2,[('Souvenirs goutte à goutte',1991),('Porco Rosso',1992),('Je peux entendre l’océan',1993)]),
                 (3,[('Pompoko',1994),('Si tu tends l’oreille',1995),('Princesse Mononoké',1997)]),
                 (4,[('Mes voisins les Yamada',1999),('Le Voyage de Chihiro',2001),('Le Royaume des chats',2002)]),
                 (5,[('Le Château ambulant',2004),('Les Contes de Terremer',2006),('Ponyo sur la falaise',2008)])]:
    revise(p,n,'Classez les sorties originales au Japon.',events,['https://www.ghibli.jp/works/'])

p='lib-chronologie-explorateurs-reperes-20261012'
revise(p,3,'Classez ces jalons de l’exploration.',[('Premier voyage de Cartier',1534),('Départ du premier voyage de James Cook',1768),('Amundsen atteint le pôle Sud',1911)],['https://www.rmg.co.uk/collections/objects/rmgc-object-40271'])
revise(p,5,'Classez ces voyages historiques.',[('Colomb atteint les Caraïbes',1492),('Gagarine devient le premier humain dans l’espace',1961),('Armstrong fait ses premiers pas sur la Lune',1969)],['https://science.nasa.gov/resource/yuri-gagarin-first-human-in-space/','https://www.nasa.gov/missions/apollo/apollo-11/apollo-11-mission-overview/'])

revise('arts-chronologie-peintures-dans-le-temps-20261011',6,'Classez ces œuvres selon leur réalisation.',[('La Persistance de la mémoire',1931),('Nighthawks',1942),('Campbell’s Soup Cans',1962)],['https://www.moma.org/collection/works/79809/'])
revise('arts-chronologie-sculptures-reperes-20261011',5,'Classez ces sculptures selon les étapes précisées.',[('L’Oiseau dans l’espace — version du MoMA',1928),('Maman — conception de Louise Bourgeois',1999),('Cloud Gate — inauguration à Chicago',2006)],['https://www.choosechicago.com/blog/special-events/the-bean-closed/'])
revise('cinema-chronologie-reperes-20261011',6,'Classez les sorties originales de ces films.',[('E.T. the Extra-Terrestrial',1982),('Back to the Future',1985),('Titanic',1997)],['https://www.universalpicturesathome.com/movies/et-the-extra-terrestrial'])
revise('lib-chronologie-odyssee-episodes-20261012',3,'Suivez le voyage d’Ulysse, pas l’ordre des chapitres.',[('Accueil chez Éole',1),('Attaque des Lestrygons',2),('Arrivée chez Circé',3)],['https://beta.perseus.tufts.edu/urn:cts:greekLit:tlg0012.tlg002.pope1726watson1858-eng2/book:10/'])
REVISIONS['resize-20261012-jalons-1789']=dict(prompt='Classez ces événements de 1789.',events=[('Ouverture des États généraux','1789-05-05'),('Abolition des privilèges','1789-08-04'),('Déclaration des droits de l’homme et du citoyen','1789-08-26')],sources=['https://www.chateauversailles.fr/decouvrir/histoire/grandes-dates/ouverture-etats-generaux'])
