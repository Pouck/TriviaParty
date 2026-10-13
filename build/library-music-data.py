from library_common import *
TOPICS=[]
TOPICS.append(topic('chanson-francophone','Chanson francophone — Classiques','Musique',[
 'https://www.fondationbrel.be/biographie-brel/','https://www.radiofrance.fr/franceinfo/podcasts/c-est-une-chanson-qui-nous-ressemble/edith-piaf-et-le-baiser-de-la-vie-en-rose-8083733',
 'https://www.britannica.com/biography/Georges-Brassens','https://www.britannica.com/biography/Charles-Aznavour'],[
 mc('Quelle chanteuse est associée à La Vie en rose ?','Édith Piaf',['Barbara','Dalida','Juliette Gréco'],'rose'),
 mc('Qui chante Amsterdam et Ne me quitte pas ?','Jacques Brel',['Charles Trenet','Serge Gainsbourg','Charles Aznavour']),
 mc('Quel chanteur a écrit Les Copains d’abord ?','Georges Brassens',['Jacques Dutronc','Alain Souchon','Michel Sardou']),
 mc('Quel instrument est associé à Yvette Horner ?','L’accordéon',['La harpe','Le saxophone','La contrebasse'],'accordion'),
 mc('Qui chante La Bohème ?','Charles Aznavour',['Charles Trenet','Claude François','Gilbert Bécaud']),
 ],[
 buzz('Quel chanteur français est surnommé le Fou chantant ?','Charles Trenet'),
 buzz('Quel instrument accompagne souvent Georges Brassens ?','La guitare','guitar',['Guitare']),
 buzz('Quelle chanteuse est surnommée la Môme ?','Édith Piaf'),
 buzz('Quel chanteur a créé La Mer ?','Charles Trenet','sea'),
 buzz('Quel chanteur de rock français est surnommé Johnny ?','Johnny Hallyday',aliases=['Hallyday']),
 ],[
 who('Édith Piaf',['Je suis une figure de la chanson française.','Non, je ne regrette rien est un de mes succès.','Je suis surnommée la Môme.','On m’associe à La Vie en rose.']),
 who('Jacques Brel',['Je suis un chanteur belge francophone.','Je suis célèbre pour ma présence intense sur scène.','Je chante Amsterdam.','J’ai écrit Ne me quitte pas.']),
 who('Georges Brassens',['Je chante souvent avec une guitare.','Mes textes jouent avec la poésie et l’ironie.','Je suis lié à la ville de Sète.','Je suis l’auteur des Copains d’abord.']),
 who('Charles Aznavour',['Mes racines familiales sont arméniennes.','Je chante notamment Emmenez-moi.','Hier encore fait partie de mes succès.','Je suis l’interprète de La Bohème.']),
 who('Barbara',['Je suis une autrice-compositrice-interprète française.','Mon surnom évoque une dame en noir.','Nantes appartient à mon répertoire.','Je chante L’Aigle noir.']),
 ]))
TOPICS.append(topic('musique-quebec','Musique — Artistes du Québec','Musique',[
 'https://www.celinedion.com/','https://www.leonardcohen.com/track/hallelujah',
 'https://www.adisq.com/galas-et-prix/','https://www.thecanadianencyclopedia.ca/fr/article/felix-leclerc',
 'https://www.thecanadianencyclopedia.ca/fr/article/gilles-vigneault'],[
 mc('Qui a écrit Gens du pays ?','Gilles Vigneault',['Félix Leclerc','Robert Charlebois','Claude Dubois'],'maple-leaf'),
 mc('Quel instrument accompagne souvent Félix Leclerc ?','La guitare',['La trompette','Le violon','La batterie'],'guitar'),
 mc('Quel artiste montréalais a écrit Hallelujah ?','Leonard Cohen',['Bryan Adams','Neil Young','Gordon Lightfoot']),
 mc('Quel groupe québécois est associé à la musique traditionnelle ?','La Bottine Souriante',['Simple Plan','Voivod','Les Trois Accords']),
 mc('Quel chanteur interprète Lindberg avec Louise Forestier ?','Robert Charlebois',['Jean-Pierre Ferland','Michel Rivard','Daniel Bélanger']),
 ],[
 buzz('Quelle chanteuse québécoise interprète My Heart Will Go On ?','Céline Dion','ship'),
 buzz('Quels trophées récompensent les artistes au gala de l’ADISQ ?','Les Félix',aliases=['Félix']),
 buzz('Quel groupe québécois a notamment enregistré La Manifestation ?','Les Cowboys Fringants','cowboy-hat'),
 buzz('Qui est l’auteur-interprète de Mon pays ?','Gilles Vigneault'),
 buzz('Quel groupe de Serge Fiori a enregistré Pour un instant ?','Harmonium'),
 ],[
 who('Céline Dion',['Je viens de Charlemagne, au Québec.','Je chante en français et en anglais.','Je remporte l’Eurovision pour la Suisse en 1988.','J’interprète My Heart Will Go On pour Titanic.']),
 who('Félix Leclerc',['Je suis écrivain et chansonnier.','Je m’accompagne souvent à la guitare.','Je suis associé à l’île d’Orléans.','Les trophées de l’ADISQ portent mon prénom.']),
 who('Gilles Vigneault',['Je viens de Natashquan.','La langue française et le Québec occupent mon œuvre.','Je chante Mon pays.','J’ai écrit Gens du pays.']),
 who('Leonard Cohen',['Je suis né à Montréal.','Je suis aussi poète et romancier.','Suzanne fait partie de mes chansons.','J’ai écrit Hallelujah.']),
 who('Robert Charlebois',['Je suis un artiste québécois aux spectacles énergiques.','J’allie chanson et rock.','Je chante Lindberg avec Louise Forestier.','J’interprète Je reviendrai à Montréal.']),
 ]))
TOPICS.append(topic('pop-rock','Pop et rock — Grands noms','Musique',[
 'https://www.thebeatles.com/','https://www.queenonline.com/freddie_mercury',
 'https://www.michaeljackson.com/albums/thriller/','https://www.bobmarley.com/',
 'https://www.graceland.com/elvis-biography'],[
 mc('Quel groupe a enregistré Abbey Road ?','Les Beatles',['Les Rolling Stones','Queen','The Who'],'crosswalk'),
 mc('Qui est le chanteur de Queen associé à Bohemian Rhapsody ?','Freddie Mercury',['David Bowie','Mick Jagger','Bono']),
 mc('Quel artiste est associé à l’album Thriller ?','Michael Jackson',['Prince','Stevie Wonder','Elton John']),
 mc('Quel style musical est associé à Bob Marley ?','Le reggae',['Le metal','Le tango','Le flamenco'],'guitar'),
 mc('Quel chanteur est surnommé le King du rock ’n’ roll ?','Elvis Presley',['Chuck Berry','Little Richard','Buddy Holly']),
 ],[
 buzz('Quel groupe comprend John, Paul, George et Ringo ?','Les Beatles',aliases=['Beatles']),
 buzz('Quel artiste est célèbre pour sa danse appelée moonwalk ?','Michael Jackson','moon'),
 buzz('Quel chanteur britannique est aussi un pianiste connu pour Rocket Man ?','Elton John','piano'),
 buzz('Quel chanteur est la voix principale des Rolling Stones ?','Mick Jagger'),
 buzz('Quel chanteur jamaïcain est associé à No Woman, No Cry ?','Bob Marley'),
 ],[
 who('Freddie Mercury',['Je suis né sous le nom Farrokh Bulsara.','J’ai une voix très reconnaissable.','J’ai écrit Bohemian Rhapsody.','Je suis le chanteur emblématique de Queen.']),
 who('Michael Jackson',['J’ai commencé avec mes frères.','Ma danse moonwalk est célèbre.','Billie Jean est un de mes succès.','Je suis le chanteur de Thriller.']),
 who('Elvis Presley',['Graceland est ma célèbre demeure.','Je mêle notamment rock, country et gospel.','Je suis associé à Memphis.','On me surnomme le King.']),
 who('Bob Marley',['Je suis un artiste jamaïcain.','Les Wailers m’accompagnent.','Le reggae a porté ma musique dans le monde.','Je chante notamment Three Little Birds.']),
 who('Les Beatles',['Nous sommes un groupe de Liverpool.','Nos quatre membres sont devenus mondialement connus.','Nous avons enregistré Abbey Road.','Nous sommes John, Paul, George et Ringo.'],['Beatles']),
 ]))
TOPICS.append(topic('jazz-blues','Jazz, blues et soul — Repères','Musique',[
 'https://www.milesdavis.com/music/releases','https://www.louisarmstronghouse.org/',
 'https://www.ellafitzgerald.com/','https://www.britannica.com/art/jazz','https://www.britannica.com/art/blues-music'],[
 mc('Quel instrument joue Louis Armstrong ?','La trompette',['Le violon','La harpe','L’accordéon'],'trumpet'),
 mc('Qui est associé à l’album Kind of Blue ?','Miles Davis',['Duke Ellington','Louis Armstrong','Charlie Parker']),
 mc('Quel genre accorde une grande place à l’improvisation ?','Le jazz',['Le plain-chant','La comptine','La marche militaire']),
 mc('Quel instrument est représenté ici ?','Un saxophone',['Une clarinette','Un hautbois','Un basson'],'saxophone'),
 mc('Quelle chanteuse est connue comme la First Lady of Song ?','Ella Fitzgerald',['Édith Piaf','Madonna','Nina Hagen']),
 ],[
 buzz('Quel trompettiste à la voix grave chante What a Wonderful World ?','Louis Armstrong','trumpet'),
 buzz('Quel pianiste et chef d’orchestre de jazz est surnommé Duke ?','Duke Ellington'),
 buzz('Quel guitariste de blues donnait à ses guitares le nom Lucille ?','B. B. King','guitar',['BB King']),
 buzz('Quelle chanteuse de soul est surnommée la Queen of Soul ?','Aretha Franklin'),
 buzz('Comment appelle-t-on le chant de jazz utilisant des syllabes improvisées ?','Le scat',aliases=['Scat']),
 ],[
 who('Louis Armstrong',['Je viens de La Nouvelle-Orléans.','Je suis chanteur et trompettiste.','Ma voix est grave et rocailleuse.','Je chante What a Wonderful World.']),
 who('Ella Fitzgerald',['Je suis une grande chanteuse de jazz.','Je suis célèbre pour le scat.','J’ai enregistré avec Louis Armstrong.','On me surnomme la First Lady of Song.']),
 who('Miles Davis',['Je suis un musicien américain de jazz.','Mon instrument principal est la trompette.','J’ai exploré plusieurs styles, dont le jazz électrique.','Mon album Kind of Blue est célèbre.']),
 who('Duke Ellington',['Je suis pianiste et compositeur.','Je dirige un grand orchestre de jazz.','Mon surnom évoque un titre de noblesse.','Je suis le Duke du jazz.']),
 who('B. B. King',['Je suis un grand artiste du blues.','Je joue de la guitare électrique.','Je donne à mes guitares le nom Lucille.','Mes initiales sont B. B.'],['BB King']),
 ]))
TOPICS.append(topic('classique','Musique classique — Compositeurs et œuvres','Musique',[
 'https://mozarteum.at/en/mozart-museums/mozarts-residence','https://www.beethoven.de/',
 'https://www.britannica.com/biography/Antonio-Vivaldi','https://www.britannica.com/biography/Frederic-Chopin',
 'https://www.britannica.com/biography/Pyotr-Ilyich-Tchaikovsky'],[
 mc('Qui a composé Les Quatre Saisons ?','Antonio Vivaldi',['Mozart','Bach','Beethoven'],'four-seasons'),
 mc('Qui a composé La Flûte enchantée ?','Mozart',['Chopin','Debussy','Ravel']),
 mc('Quel instrument est particulièrement associé à Chopin ?','Le piano',['Le tuba','La batterie','La trompette'],'piano'),
 mc('Quel compositeur a écrit le Boléro ?','Maurice Ravel',['Claude Debussy','Camille Saint-Saëns','Hector Berlioz']),
 mc('Dans quelle symphonie de Beethoven trouve-t-on l’Ode à la joie ?','La Neuvième',['La Troisième','La Cinquième','La Sixième']),
 ],[
 buzz('Qui a composé Le Lac des cygnes ?','Tchaïkovski','swan',['Piotr Ilitch Tchaïkovski']),
 buzz('Quel compositeur devient presque sourd tout en continuant de créer ?','Ludwig van Beethoven',aliases=['Beethoven']),
 buzz('Quel compositeur français a écrit Clair de lune ?','Claude Debussy','moon',['Debussy']),
 buzz('Quelle famille d’instruments comprend le violon et le violoncelle ?','Les cordes',aliases=['Cordes','Instruments à cordes']),
 buzz('Quel compositeur allemand est associé aux Concertos brandebourgeois ?','Jean-Sébastien Bach',aliases=['Bach','Johann Sebastian Bach']),
 ],[
 who('Mozart',['Je suis né à Salzbourg.','Je compose dès mon enfance.','J’ai écrit Les Noces de Figaro.','Je suis le compositeur de La Flûte enchantée.'],['Wolfgang Amadeus Mozart']),
 who('Beethoven',['Je suis né à Bonn.','Ma surdité progresse pendant ma carrière.','La Cinquième et la Neuvième sont mes symphonies célèbres.','J’ai mis l’Ode à la joie en musique.'],['Ludwig van Beethoven']),
 who('Vivaldi',['Je suis un compositeur italien.','On me surnomme le Prêtre roux.','Je suis violoniste.','J’ai composé Les Quatre Saisons.'],['Antonio Vivaldi']),
 who('Chopin',['Je suis un compositeur d’origine polonaise.','Je passe une partie de ma vie à Paris.','Mes nocturnes et polonaises sont célèbres.','Mon œuvre est surtout associée au piano.'],['Frédéric Chopin']),
 who('Tchaïkovski',['Je suis un compositeur russe.','Casse-Noisette est un de mes ballets.','La Belle au bois dormant est un autre de mes ballets.','J’ai composé Le Lac des cygnes.']),
 ]))
TOPICS.append(topic('instruments','Musique — Instruments','Musique',[
 'https://www.carnegiehall.org/Education/Programs/Link-Up/Activities-for-Families',
 'https://www.metmuseum.org/art/collection/search?department=18'],[
 mc('Quel instrument est représenté ici ?','Un violon',['Une mandoline','Une guitare','Une harpe'],'violin'),
 mc('Quel instrument possède habituellement 88 touches ?','Le piano',['L’accordéon','L’orgue portatif','Le clavecin']),
 mc('Quel instrument est représenté ici ?','Une harpe',['Un violoncelle','Une contrebasse','Un luth'],'harp'),
 mc('Quel instrument utilise une coulisse pour modifier la hauteur des notes ?','Le trombone',['La trompette','Le cor','Le tuba']),
 mc('Quel instrument appartient à la famille des bois malgré son corps généralement métallique ?','La flûte traversière',['Le trombone','Le cor','La trompette']),
 ],[
 buzz('Quel instrument à soufflet est représenté ici ?','Un accordéon','accordion',['Accordéon']),
 buzz('Quel instrument à cordes pincées est représenté ici ?','Une guitare','guitar',['Guitare']),
 buzz('Comment appelle-t-on la baguette courbe qui frotte les cordes d’un violon ?','Un archet',aliases=['Archet']),
 buzz('Quel ensemble de percussions comprend souvent grosse caisse et cymbales ?','Une batterie',aliases=['Batterie']),
 buzz('Quel petit instrument se joue en soufflant dans plusieurs trous côte à côte ?','Un harmonica',aliases=['Harmonica']),
 ],[
 who('Le piano',['Je suis un instrument à clavier.','Des marteaux frappent mes cordes.','J’ai généralement des touches noires et blanches.','Un modèle courant possède 88 touches.'],['Piano']),
 who('Le violon',['Je suis un instrument à cordes.','On me tient entre l’épaule et le menton.','On me joue souvent avec un archet.','Je suis plus petit que le violoncelle.'],['Violon']),
 who('La guitare',['Je suis un instrument à cordes pincées.','Mes modèles acoustiques ont souvent une caisse creuse.','J’ai généralement six cordes.','Je suis très présente dans le rock et la chanson.'],['Guitare']),
 who('L’accordéon',['Je suis un instrument à vent.','Je porte des touches ou des boutons.','Mon soufflet s’ouvre et se ferme.','Je suis associé au bal musette.'],['Accordéon']),
 who('La harpe',['Je suis un instrument à cordes pincées.','Mon cadre est souvent triangulaire.','Je possède de nombreuses cordes de tailles différentes.','Je suis souvent représentée avec les anges.'],['Harpe']),
 ]))
TOPICS.append(topic('musique-ecran','Musique — Films et comédies musicales','Musique',[
 'https://www.starwars.com/news/john-williams-birthday','https://www.celinedion.com/',
 'https://www.ghibli.jp/works/','https://www.andrewlloydwebber.com/','https://www.disney.com/'],[
 mc('Qui a composé la musique de Star Wars ?','John Williams',['Hans Zimmer','Ennio Morricone','Danny Elfman'],'space'),
 mc('Qui chante My Heart Will Go On pour Titanic ?','Céline Dion',['Whitney Houston','Mariah Carey','Madonna']),
 mc('Quel compositeur est souvent associé aux films de Miyazaki ?','Joe Hisaishi',['Ryuichi Sakamoto','John Barry','Alan Menken']),
 mc('Quelle comédie musicale met en scène un fantôme à l’Opéra de Paris ?','The Phantom of the Opera',['Cats','Chicago','Mamma Mia!'],'mask'),
 mc('Quel groupe fournit les chansons de Mamma Mia! ?','ABBA',['Queen','The Beatles','Bee Gees']),
 ],[
 buzz('Quelle comédie musicale de Disney met en scène Simba sur scène ?','Le Roi lion','lion',['The Lion King']),
 buzz('Quel compositeur italien est associé aux westerns de Sergio Leone ?','Ennio Morricone',aliases=['Morricone']),
 buzz('Quel film de Disney comprend la chanson Let It Go, ou Libérée, délivrée ?','La Reine des neiges','snowman',['Frozen']),
 buzz('Quel compositeur a écrit Cats et The Phantom of the Opera ?','Andrew Lloyd Webber'),
 buzz('Quel est le titre original de La Mélodie du bonheur ?','The Sound of Music',aliases=['Sound of Music']),
 ],[
 who('John Williams',['Je suis un compositeur américain.','J’ai souvent travaillé avec Steven Spielberg.','J’ai composé les thèmes d’Indiana Jones et de Harry Potter.','La musique de Star Wars est aussi mon œuvre.']),
 who('Joe Hisaishi',['Je suis un compositeur japonais.','J’écris souvent pour le cinéma d’animation.','Je collabore régulièrement avec Hayao Miyazaki.','J’ai composé la musique de Mon voisin Totoro.']),
 who('Ennio Morricone',['Je suis un compositeur italien.','Ma musique de cinéma utilise parfois des sons inattendus.','Sergio Leone est un de mes collaborateurs célèbres.','J’ai composé pour Le Bon, la Brute et le Truand.']),
 who('Mamma Mia!',['Je suis une comédie musicale.','Mon histoire mêle mariage et recherche d’un père.','Dancing Queen figure dans mon répertoire.','Mes chansons viennent du groupe ABBA.']),
 who('Cats',['Je suis une comédie musicale d’Andrew Lloyd Webber.','Mes personnages s’inspirent de poèmes de T. S. Eliot.','Memory est ma chanson la plus célèbre.','Mon titre anglais désigne des chats.']),
 ]))
