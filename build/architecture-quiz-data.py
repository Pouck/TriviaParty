"""French architectural landmark questions, with primary verification sources."""
SOURCES={
 'colosseum':'https://colosseo.it/en/area/the-colosseum/',
 'pantheon':'https://direzionemuseiroma.cultura.gov.it/pantheon/',
 'pisa':'https://www.opapisa.it/en/square-of-miracles/tower/',
 'chenonceau':'https://www.chenonceau.com/chateau-renaissance/pieces/',
 'alhambra':'https://whc.unesco.org/en/list/314/',
 'chartres':'https://whc.unesco.org/en/list/81/',
 'taj':'https://whc.unesco.org/en/list/252/',
 'petra':'https://whc.unesco.org/en/list/326/',
 'angkor':'https://whc.unesco.org/en/list/668/',
 'borobudur':'https://whc.unesco.org/en/list/592/',
 'forbidden':'https://whc.unesco.org/en/list/439/',
 'abusimbel':'https://whc.unesco.org/en/list/88/',
 'sydney':'https://www.sydneyoperahouse.com/our-story/jorn-utzon',
 'cn':'https://www.cntower.ca/history',
 'guggenheim':'https://www.guggenheim.org/articles/checklist/your-guide-to-the-guggenheims-secret-language',
 'pompidou':'https://www.centrepompidou.fr/en/centre-pompidou-is-transforming-itself/an-iconic-architecture',
 'fallingwater':'https://fallingwater.org/history/the-kaufmanns-fallingwater/designing-fallingwater/',
 'brasilia':'https://whc.unesco.org/en/list/445/',
 'eiffel':'https://www.toureiffel.paris/en/the-monument/history',
 'bigben':'https://www.parliament.uk/about/living-heritage/building/palace/architecture/palacestructure/towers-of-parliament/',
 'arc':'https://www.paris-arc-de-triomphe.fr/decouvrir/histoire-de-l-arc-de-triomphe',
 'mont':'https://whc.unesco.org/en/list/80/',
 'versailles':'https://whc.unesco.org/en/list/83/',
 'sagrada':'https://sagradafamilia.org/en/history-of-the-temple',
 'machu':'https://whc.unesco.org/en/list/274/',
 'giza':'https://whc.unesco.org/en/list/86/',
 'wall':'https://whc.unesco.org/en/list/438/',
 'liberty':'https://www.nps.gov/articles/000/statue-of-liberty-national-monument-world-heritage-site.htm',
 'moai':'https://whc.unesco.org/en/list/715/',
 'parthenon':'https://whc.unesco.org/en/list/404/',
 'burj':'https://www.burjkhalifa.ae/en/assets/FACT-SHEET.pdf',
 'buckingham':'https://www.rct.uk/visit/buckingham-palace',
 'goldengate':'https://www.goldengate.org/faq/',
 'marina':'https://www.marinabaysands.com/guides/exceptional-experiences/marina-bay-sands-architecture.html',
 'habitat':'https://www.safdiearchitects.com/projects/habitat-67',
 'chrysler':'https://chryslerbuilding.com/amenities/',
 'notredame':'https://www.notredamedeparis.fr/en/understand/architecture/',
 'hagia':'https://whc.unesco.org/en/list/356/',
 'chambord':'https://www.chambord.org/fr/histoire/le-chateau/architecture/',
}
def mc(prompt,options,index,site,image=None,note=''):
 return dict(prompt=prompt,options=options,index=index,site=site,image=image,note=note)
def buzz(prompt,answers,site,image=None,note=''):
 return dict(prompt=prompt,answers=answers,site=site,image=image,note=note)
def guess(answers,clues,site):return dict(answers=answers,clues=clues,site=site)

CHOICE=[
('europe','Monuments d’Europe',[
 mc('Quelle était la fonction de cet édifice romain ?', ['Spectacles et combats','Réunions du Sénat','Stockage de céréales','Bains publics'],0,'colosseum','colosseum','Le Colisée est un amphithéâtre, pas un théâtre semi-circulaire.'),
 mc('Quel élément caractéristique perce le sommet de la coupole du Panthéon de Rome ?', ['Une flèche','Un oculus circulaire','Une cheminée','Un clocher'],1,'pantheon'),
 mc('À quoi servait cette tour ?', ['Un phare','Un observatoire','Un clocher','Une tour de défense'],2,'pisa','pisa'),
 mc('Quelle rivière la galerie du château de Chenonceau enjambe-t-elle ?', ['La Loire','Le Cher','L’Indre','La Vienne'],1,'chenonceau'),
 mc('Dans quelle ville espagnole est ce site ?', ['Séville','Cordoue','Grenade','Tolède'],2,'alhambra','alhambra'),
 mc('La cathédrale de Chartres est un chef-d’œuvre de quel style architectural ?', ['Roman','Gothique','Baroque','Néoclassique'],1,'chartres'),
]),
('asie-orient','Asie et Proche-Orient',[
 mc('Qui a commandé ce mausolée ?', ['Akbar','Shah Jahan','Aurangzeb','Babur'],1,'taj','taj'),
 mc('Quel peuple a fait de Pétra sa capitale et y a sculpté des façades dans la roche ?', ['Les Hittites','Les Nabatéens','Les Phéniciens','Les Perses achéménides'],1,'petra'),
 mc('Dans quel pays est ce temple ?', ['Thaïlande','Laos','Cambodge','Myanmar'],2,'angkor','angkor'),
 mc('À quelle tradition religieuse le temple de Borobudur, sur l’île de Java, appartient-il ?', ['Le bouddhisme','Le shintoïsme','Le taoïsme','Le zoroastrisme'],0,'borobudur'),
 mc('Quelles dynasties ont habité ce palais ?', ['Han et Tang','Song et Yuan','Ming et Qing','Qin et Han'],2,'forbidden','forbidden'),
 mc('Pourquoi les temples d’Abou Simbel ont-ils été déplacés dans les années 1960 ?', ['Pour les protéger de la montée des eaux liée au barrage d’Assouan','Pour les rapprocher du Caire','Pour dégager une voie ferrée','Pour éviter des coulées de lave'],0,'abusimbel'),
]),
('moderne','Architecture moderne',[
 mc('Qui a conçu cet opéra ?', ['Alvar Aalto','Jørn Utzon','Le Corbusier','Eero Saarinen'],1,'sydney','sydney'),
 mc('Dans quelle ville canadienne se trouve la tour CN ?', ['Montréal','Vancouver','Toronto','Calgary'],2,'cn'),
 mc('Qui a conçu ce musée new-yorkais ?', ['Frank Gehry','Frank Lloyd Wright','Mies van der Rohe','I. M. Pei'],1,'guggenheim','guggenheim','Le Guggenheim de New York est de Wright ; celui de Bilbao est de Gehry.'),
 mc('Quelle particularité architecturale distingue le Centre Pompidou, à Paris ?', ['Ses réseaux techniques et circulations visibles à l’extérieur','Une structure entièrement en bois','Des façades sans aucune fenêtre','Une coupole médiévale'],0,'pompidou'),
 mc('Où est la maison par rapport à la cascade ?', ['Au-dessus','Sous l’eau','De l’autre côté d’un lac','Dans une grotte'],0,'fallingwater','fallingwater'),
 mc('Quel architecte a conçu plusieurs grands bâtiments publics de Brasília, dont le Congrès national ?', ['Oscar Niemeyer','Antoni Gaudí','Renzo Piano','Norman Foster'],0,'brasilia',note='Lúcio Costa est l’urbaniste du plan ; Oscar Niemeyer est l’architecte des bâtiments cités.'),
])]

BUZZER=[
('europe','Reconnaissance — Europe',[
 buzz('Quel monument voyez-vous ?', ['La tour Eiffel','Tour Eiffel'], 'eiffel','eiffel'),
 buzz('Quel site français est célèbre pour son abbaye perchée sur un îlot rocheux au milieu d’une baie ?', ['Le Mont-Saint-Michel','Mont-Saint-Michel'],'mont'),
 buzz('Quel nom courant désigne cette célèbre tour de l’horloge londonienne ?', ['Big Ben','La tour Elizabeth','Elizabeth Tower'], 'bigben','bigben','Big Ben est précisément la grande cloche ; ce nom désigne aussi couramment la tour Elizabeth.'),
 buzz('Quel roi, surnommé le Roi-Soleil, a fait de Versailles le siège de sa cour ?', ['Louis XIV','Louis 14'], 'versailles'),
 buzz('Quel monument parisien voyez-vous ?', ['L’Arc de triomphe','Arc de triomphe','L’Arc de triomphe de l’Étoile'],'arc','arc'),
 buzz('Dans quelle ville espagnole se trouve la Sagrada Família ?', ['Barcelone','Barcelona'],'sagrada'),
]),
('monde','Reconnaissance — Sites historiques',[
 buzz('Dans quel pays se trouve le site photographié, Machu Picchu ?', ['Le Pérou','Pérou'],'machu','machu'),
 buzz('Dans quel pays se trouve la grande pyramide de Khéops ?', ['L’Égypte','Égypte','Egypte'],'giza'),
 buzz('Dans quel pays se trouve cette célèbre muraille ?', ['La Chine','Chine'],'wall','wall'),
 buzz('Quel pays a offert la statue de la Liberté aux États-Unis ?', ['La France','France'],'liberty'),
 buzz('Sur quelle île se trouvent ces statues appelées moaï ?', ['L’île de Pâques','Île de Pâques','Rapa Nui'],'moai','moai'),
 buzz('Quelle ville grecque est dominée par l’Acropole et le Parthénon ?', ['Athènes','Athenes'],'parthenon'),
]),
('moderne','Reconnaissance — Icônes modernes',[
 buzz('Quel est le nom de ce gratte-ciel de Dubaï ?', ['Burj Khalifa','Le Burj Khalifa'],'burj','burj'),
 buzz('Dans quelle ville se trouve le palais de Buckingham ?', ['Londres','London'],'buckingham'),
 buzz('Quelle ville américaine se trouve à l’extrémité sud de ce pont ?', ['San Francisco'],'goldengate','goldengate'),
 buzz('Dans quelle cité-État se trouve Marina Bay Sands, avec ses trois tours reliées par une terrasse ?', ['Singapour','Singapore'],'marina'),
 buzz('Quel ensemble résidentiel montréalais, construit pour l’Expo 67, voyez-vous ?', ['Habitat 67','Habitat67'],'habitat','habitat'),
 buzz('À quel style architectural associe-t-on le Chrysler Building de New York ?', ['L’Art déco','Art déco','Art deco'],'chrysler'),
])]

GUESS=[
('antiquite','Merveilles antiques',[
 guess(['Le Colisée','Colisée','L’amphithéâtre Flavien'],[
 'Mon chantier commence sous Vespasien, puis Titus m’inaugure en 80 de notre ère.',
 'Mon plan elliptique entoure une arène et des gradins.',
 'Des gladiateurs et des animaux ont participé aux spectacles que j’accueillais.',
 'Je suis le célèbre amphithéâtre antique de Rome.'
 ],'colosseum'),
 guess(['Le Parthénon','Parthénon'],[
 'Je suis construit au Ve siècle avant notre ère, à l’époque de Périclès.',
 'Mes colonnes appartiennent principalement à l’ordre dorique.',
 'J’étais consacré à Athéna et j’abritais une statue réalisée par Phidias.',
 'Je suis le grand temple qui domine l’Acropole d’Athènes.'
 ],'parthenon'),
 guess(['La grande pyramide de Khéops','La pyramide de Khéops','Khéops','La grande pyramide de Gizeh'],[
 'Je suis un monument funéraire de la IVe dynastie égyptienne.',
 'Je suis la seule merveille de l’Antiquité encore largement conservée.',
 'Deux autres grandes pyramides se dressent à mes côtés.',
 'Je suis la plus imposante des trois pyramides du plateau de Gizeh.'
 ],'giza'),
]),
('sacre','Édifices sacrés',[
 guess(['Notre-Dame de Paris','La cathédrale Notre-Dame de Paris'],[
 'Mes arcs-boutants soutiennent un édifice gothique commencé au XIIe siècle.',
 'Trois grandes roses de vitraux font partie de mes trésors.',
 'Victor Hugo m’a rendue célèbre dans un roman peuplé de Quasimodo et d’Esmeralda.',
 'Je suis la grande cathédrale de l’île de la Cité, à Paris.'
 ],'notredame'),
 guess(['Sainte-Sophie','Hagia Sophia','Ayasofya','La basilique Sainte-Sophie'],[
 'L’empereur Justinien me fait reconstruire au VIe siècle.',
 'Ma vaste coupole est un symbole de l’architecture byzantine.',
 'Au fil de mon histoire, j’ai servi d’église, de mosquée et de musée.',
 'Mon nom signifie « Sagesse divine » ; je me trouve à Istanbul.'
 ],'hagia'),
 guess(['La Sagrada Família','Sagrada Família','Sagrada Familia'],[
 'Mon chantier débute en 1882 ; Antoni Gaudí en reprend la direction l’année suivante.',
 'Mes colonnes ramifiées évoquent une forêt de pierre.',
 'Mes façades racontent notamment la Nativité et la Passion du Christ.',
 'Je suis la basilique emblématique de Gaudí, à Barcelone.'
 ],'sagrada'),
]),
('palais','Palais et châteaux',[
 guess(['Le château de Versailles','Versailles','Le palais de Versailles'],[
 'À l’origine, je suis un pavillon de chasse de Louis XIII.',
 'Mes jardins sont étroitement associés au travail d’André Le Nôtre.',
 'Ma galerie des Glaces est l’une de mes salles les plus célèbres.',
 'Je suis le palais près de Paris où Louis XIV installe sa cour.'
 ],'versailles'),
 guess(['Le château de Chambord','Chambord'],[
 'François Ier lance mon chantier en 1519.',
 'Ma silhouette de la Renaissance rassemble tours, cheminées et terrasses.',
 'Mon escalier à double révolution permet d’emprunter deux parcours distincts.',
 'Je suis le célèbre château de François Ier, près de Blois.'
 ],'chambord'),
 guess(['L’Alhambra','Alhambra'],[
 'Mes palais conservent un remarquable héritage de la dynastie nasride.',
 'Mes décors associent calligraphie, motifs géométriques et stucs sculptés.',
 'Ma cour des Lions comporte une célèbre fontaine portée par douze lions.',
 'Je suis l’ensemble palatial fortifié qui domine Grenade, en Espagne.'
 ],'alhambra'),
]),
('civilisations','Sites de grandes civilisations',[
 guess(['Pétra','Petra','La cité de Pétra'],[
 'Un système de canalisations et de citernes permettait d’utiliser l’eau dans mon environnement aride.',
 'Je fus un important centre caravanier des Nabatéens.',
 'Le défilé du Siq conduit à ma façade appelée le Trésor.',
 'Je suis la célèbre cité aux façades taillées dans la roche rose, en Jordanie.'
 ],'petra'),
 guess(['Le Taj Mahal','Taj Mahal'],[
 'Je suis un mausolée moghol élevé au XVIIe siècle.',
 'Mon ensemble associe un jardin symétrique, du marbre blanc et des incrustations de pierres.',
 'Shah Jahan me fait construire en mémoire de Mumtaz Mahal.',
 'Je suis le célèbre monument de marbre blanc situé à Agra, en Inde.'
 ],'taj'),
 guess(['Angkor Vat','Angkor Wat','Le temple d’Angkor Vat'],[
 'Je suis construit au XIIe siècle sous le roi Suryavarman II.',
 'À l’origine consacré à Vishnou, je deviens ensuite un lieu de culte bouddhiste.',
 'Mes tours figurent sur le drapeau national du pays où je me trouve.',
 'Je suis le célèbre temple khmer près de Siem Reap, au Cambodge.'
 ],'angkor'),
]),
('modernes','Icônes de l’époque moderne',[
 guess(['La tour Eiffel','Tour Eiffel'],[
 'Mes pièces de fer puddlé sont assemblées à l’aide de rivets.',
 'Je suis construite pour l’Exposition universelle de 1889.',
 'Je me dresse au Champ-de-Mars et porte le nom de l’entrepreneur qui m’a réalisée.',
 'Je suis la célèbre tour métallique devenue un symbole de Paris.'
 ],'eiffel'),
 guess(['L’opéra de Sydney','Opéra de Sydney','Sydney Opera House'],[
 'Le projet de mon architecte danois remporte un concours international en 1957.',
 'Je suis construit à Bennelong Point, au bord d’un port australien.',
 'Mes grandes coques blanches abritent des salles de spectacle.',
 'Mes toitures évoquent des voiles sur le port de Sydney, en Australie.'
 ],'sydney'),
 guess(['Fallingwater','La Maison sur la cascade','Maison sur la cascade','La maison Kaufmann'],[
 'Je suis une résidence de week-end commandée par la famille Kaufmann en Pennsylvanie.',
 'Mes terrasses en porte-à-faux s’avancent au-dessus d’un ruisseau.',
 'Frank Lloyd Wright m’intègre directement à une cascade.',
 'Mon nom anglais évoque l’eau qui tombe sous mes terrasses.'
 ],'fallingwater'),
])]
