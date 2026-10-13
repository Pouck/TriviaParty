from library_common import *
TOPICS=[]
TOPICS.append(topic('cuisine-celebre','Cuisine — Plats célèbres','Cuisine',[
 'https://ich.unesco.org/en/RL/art-of-neapolitan-pizzaiuolo-00722',
 'https://ich.unesco.org/en/RL/knowledge-know-how-and-practices-pertaining-to-the-production-and-consumption-of-couscous-01602',
 'https://www.britannica.com/topic/food','https://www.bonjourquebec.com/fr-ca/decouvrir/gastronomie'],[
 mc('Quel plat italien est représenté ici ?','Une pizza',['Une paella','Un couscous','Un sushi'],'pizza'),
 mc('Quel ingrédient forme la base du guacamole ?','L’avocat',['Le concombre','Le pois chiche','La courgette']),
 mc('Quel plat québécois combine frites, fromage en grains et sauce ?','La poutine',['La tourtière','Le pâté chinois','La cipaille']),
 mc('Quel plat japonais est associé au riz vinaigré ?','Le sushi',['Le couscous','Le risotto','Le chili'],'sushi'),
 mc('Quel ingrédient est la base traditionnelle du houmous ?','Le pois chiche',['Le haricot rouge','Le maïs','La pomme de terre']),
 ],[
 buzz('Quel plat espagnol au riz cuit souvent dans une large poêle ?','La paella','paella',['Paella']),
 buzz('Quel pain français long et fin est représenté ici ?','Une baguette','baguette',['Baguette']),
 buzz('Quel dessert italien porte un nom signifiant « tire-moi vers le haut » ?','Le tiramisu',aliases=['Tiramisu']),
 buzz('Quel produit sucré est tiré de la sève des érables ?','Le sirop d’érable',aliases=['Sirop d’érable']),
 buzz('Quel plat maghrébin est associé à la semoule et à un bouillon ?','Le couscous',aliases=['Couscous']),
 ],[
 who('La poutine',['Je suis associée au Québec.','Ma sauce est souvent brune.','Je contiens du fromage en grains.','Je réunis ce fromage, la sauce et des frites.'],['Poutine']),
 who('Le sushi',['Je viens du Japon.','Je ne contiens pas toujours de poisson cru.','Mon riz est vinaigré.','Je suis servi en bouchées, parfois entourées d’algue.'],['Sushi']),
 who('La pizza',['Je suis célèbre dans la cuisine italienne.','Je suis cuite au four.','Une pâte porte ma garniture.','Tomate et mozzarella me composent souvent.'],['Pizza']),
 who('Le couscous',['Je suis un plat des cuisines du Maghreb.','Je peux accompagner viande ou légumes.','Mon élément central est constitué de petits grains.','Ces grains sont généralement faits de semoule.'],['Couscous']),
 who('Le tiramisu',['Je suis un dessert italien.','Je contiens souvent du mascarpone.','Le café imbibe mes biscuits.','On saupoudre généralement mon dessus de cacao.'],['Tiramisu']),
 ]))
TOPICS.append(topic('litterature-quebec','Littérature québécoise — Grands noms','Littérature',[
 'https://www.editionsboreal.qc.ca/actualites/7-80e-anniversaire-de-bonheur-doccasion.html',
 'https://www2.banq.qc.ca/documents/activites/trousse_mediation/du_texte_au_spectacle/BAnQ_Trousse_mediation_Pieces_1er_cycle.pdf',
 'https://www.collectionscanada.gc.ca/obj/h7/f2/01-f.pdf',
 'https://www.thecanadianencyclopedia.ca/fr/article/anne-hebert','https://www.thecanadianencyclopedia.ca/fr/article/emile-nelligan',
 'https://www.thecanadianencyclopedia.ca/fr/article/felix-leclerc'],[
 mc('Qui a écrit Les Belles-Sœurs ?','Michel Tremblay',['Robert Lepage','Wajdi Mouawad','Marcel Dubé']),
 mc('Quel roman de Gabrielle Roy se déroule à Saint-Henri, à Montréal ?','Bonheur d’occasion',['Kamouraska','Maria Chapdelaine','Agaguk'],'montreal'),
 mc('Qui a écrit Kamouraska ?','Anne Hébert',['Gabrielle Roy','Marie-Claire Blais','Nelly Arcan']),
 mc('Quel poète est associé au Vaisseau d’or ?','Émile Nelligan',['Gaston Miron','Paul Éluard','Jacques Prévert'],'ship'),
 mc('Quel écrivain a publié L’Homme rapaillé ?','Gaston Miron',['Félix Leclerc','Émile Nelligan','Alain Grandbois']),
 ],[
 buzz('Quel dramaturge québécois a créé Les Belles-Sœurs ?','Michel Tremblay'),
 buzz('Quelle romancière a écrit Bonheur d’occasion ?','Gabrielle Roy'),
 buzz('Quel poète québécois évoque un Vaisseau d’or ?','Émile Nelligan','ship',['Nelligan']),
 buzz('Quel auteur-chansonnier québécois a écrit Pieds nus dans l’aube ?','Félix Leclerc','sunrise',['Leclerc']),
 buzz('Quel roman de Louis Hémon raconte la vie d’une jeune fille au Lac-Saint-Jean ?','Maria Chapdelaine'),
 ],[
 who('Michel Tremblay',['Je suis un auteur montréalais.','Le Plateau-Mont-Royal occupe une grande place dans mon œuvre.','Mon théâtre a donné une place importante au joual.','Je suis l’auteur des Belles-Sœurs.']),
 who('Gabrielle Roy',['Je suis née à Saint-Boniface, au Manitoba.','J’ai aussi travaillé comme institutrice.','Mon premier roman décrit Saint-Henri à Montréal.','J’ai écrit Bonheur d’occasion.']),
 who('Anne Hébert',['Je suis poète et romancière.','J’ai notamment écrit Les Chambres de bois.','Les Fous de Bassan appartient à mon œuvre.','Je suis l’autrice de Kamouraska.']),
 who('Émile Nelligan',['Je suis un poète de Montréal.','J’écris surtout à la fin du XIXe siècle.','Soir d’hiver est un de mes poèmes célèbres.','On m’associe au Vaisseau d’or.']),
 who('Félix Leclerc',['Je suis écrivain, chanteur et guitariste.','Je suis associé à l’île d’Orléans.','J’ai écrit Pieds nus dans l’aube.','Mon prénom a donné son nom aux trophées de l’ADISQ.']),
 ]))
TOPICS.append(topic('histoire-mondiale-generale','Histoire mondiale — Grands repères','Histoire',[
 'https://www.britishmuseum.org/collection','https://www.bl.uk/magna-carta',
 'https://www.nasa.gov/mission/apollo-11/','https://www.un.org/en/about-us/history-of-the-un',
 'https://www.worldhistory.org/'],[
 mc('Quelle civilisation a construit les pyramides de Gizeh ?','L’Égypte antique',['La Grèce antique','L’Empire romain','L’Empire inca'],'pyramids'),
 mc('Quel souverain macédonien conquiert l’Empire perse ?','Alexandre le Grand',['Jules César','Hannibal','Charlemagne']),
 mc('Quel pays est associé à la Grande Muraille ?','La Chine',['Le Japon','L’Inde','La Corée du Sud'],'wall'),
 mc('Quel inventeur européen est célèbre pour l’imprimerie à caractères mobiles au XVe siècle ?','Gutenberg',['Galilée','Newton','Edison']),
 mc('Quel mouvement commence en France en 1789 ?','La Révolution française',['La Réforme protestante','La révolution industrielle','La Renaissance']),
 ],[
 buzz('Quel amphithéâtre antique célèbre se trouve à Rome ?','Le Colisée','colosseum',['Colisée']),
 buzz('Quel mur européen tombe en 1989 ?','Le mur de Berlin','berlin-wall',['Mur de Berlin']),
 buzz('Qui est le premier humain à marcher sur la Lune ?','Neil Armstrong',aliases=['Armstrong']),
 buzz('Quelle organisation internationale est fondée en 1945 pour favoriser la paix ?','L’ONU',aliases=['ONU','Organisation des Nations unies']),
 buzz('Quel dirigeant sud-africain reçoit la liberté en 1990 après un long emprisonnement ?','Nelson Mandela',aliases=['Mandela']),
 ],[
 who('Cléopâtre',['Je règne à la fin de l’Égypte ptolémaïque.','Alexandrie est ma capitale.','Je suis liée à Jules César puis à Marc Antoine.','Je suis la célèbre reine d’Égypte de l’Antiquité.']),
 who('Napoléon Bonaparte',['Je suis né en Corse.','Je deviens Premier consul après le 18 Brumaire.','Je suis couronné empereur en 1804.','Je suis vaincu à Waterloo.'],['Napoléon']),
 who('Gandhi',['Je suis juriste avant de devenir un dirigeant politique.','Je privilégie la résistance non violente.','Je conduis la marche du sel en Inde.','On me donne souvent le titre de Mahatma.'],['Mahatma Gandhi']),
 who('Nelson Mandela',['Je lutte contre l’apartheid.','Je passe de nombreuses années en prison.','Je deviens président de l’Afrique du Sud en 1994.','On me surnomme Madiba.']),
 who('Jeanne d’Arc',['Je viens de Domrémy.','Je participe à la guerre de Cent Ans.','Je contribue à la levée du siège d’Orléans.','Je suis la jeune héroïne appelée la Pucelle.']),
 ]))
TOPICS.append(topic('geographie-monde','Géographie mondiale — Reliefs et océans','Géographie',[
 'https://www.britannica.com/science/Pacific-Ocean','https://www.britannica.com/place/Sahara-desert-Africa',
 'https://www.britannica.com/place/Andes-Mountains','https://www.britannica.com/place/Mount-Everest',
 'https://www.nationalgeographic.org/education/'],[
 mc('Quel est le plus grand océan ?','Le Pacifique',['L’Atlantique','L’Indien','L’Arctique'],'ocean'),
 mc('Quel est le plus grand désert chaud ?','Le Sahara',['Le Gobi','Le Kalahari','L’Atacama']),
 mc('Sur quel continent se trouve l’Amazonie ?','L’Amérique du Sud',['L’Afrique','L’Asie','L’Océanie']),
 mc('Quel pays abrite ce mont Fuji ?','Le Japon',['La Chine','La Corée du Sud','Le Vietnam'],'fuji'),
 mc('Quelle chaîne longe l’ouest de l’Amérique du Sud ?','Les Andes',['Les Alpes','L’Atlas','L’Oural']),
 ],[
 buzz('Quel est le plus haut sommet terrestre au-dessus du niveau de la mer ?','L’Everest','everest',['Everest','Mont Everest']),
 buzz('Quel continent entoure le pôle Sud ?','L’Antarctique','antarctica',['Antarctique']),
 buzz('Quelle mer sépare principalement le sud de l’Europe du nord de l’Afrique ?','La Méditerranée',aliases=['Méditerranée','Mer Méditerranée']),
 buzz('Quel fleuve traverse l’Égypte ?','Le Nil',aliases=['Nil']),
 buzz('Quelle ligne imaginaire sépare les hémisphères Nord et Sud ?','L’équateur',aliases=['Équateur']),
 ],[
 who('Le Sahara',['Je couvre une grande partie du nord de l’Afrique.','Mon climat est très aride.','Je ne suis pas le plus grand désert si l’on compte les déserts polaires.','Je suis le plus grand désert chaud.'],['Sahara']),
 who('Les Andes',['Je suis une chaîne de montagnes.','Je traverse notamment le Pérou et le Chili.','Je longe l’ouest de l’Amérique du Sud.','Mon nom est celui de sa grande cordillère.'],['Andes','Cordillère des Andes']),
 who('Le Japon',['Je suis un pays insulaire d’Asie.','Honshū est ma plus grande île.','Le mont Fuji est mon sommet emblématique.','Ma capitale est Tokyo.'],['Japon']),
 who('L’Australie',['Je suis un pays de l’hémisphère Sud.','Je suis célèbre pour mes marsupiaux.','Sydney abrite mon célèbre opéra.','Ma capitale est Canberra.'],['Australie']),
 who('L’Antarctique',['Je suis un continent couvert en grande partie de glace.','Des équipes scientifiques y séjournent.','Le pôle Sud se trouve sur mon territoire.','Je suis le continent situé le plus au sud.'],['Antarctique']),
 ]))
TOPICS.append(topic('geographie-villes','Géographie mondiale — Villes et monuments','Géographie',[
 'https://www.louvre.fr/','https://www.colosseo.it/en/','https://www.sydneyoperahouse.com/',
 'https://www.tajmahal.gov.in/','https://www.britannica.com/place'],[
 mc('Dans quelle ville se trouve la tour Eiffel ?','Paris',['Lyon','Bruxelles','Genève'],'eiffel'),
 mc('Quelle ville abrite le Taj Mahal ?','Agra',['Delhi','Mumbai','Jaipur'],'taj'),
 mc('Quelle est la capitale de l’Espagne ?','Madrid',['Barcelone','Séville','Valence']),
 mc('Quelle ville est la capitale du Japon ?','Tokyo',['Kyoto','Osaka','Hiroshima']),
 mc('Quelle est la capitale du Brésil ?','Brasília',['Rio de Janeiro','São Paulo','Salvador']),
 ],[
 buzz('Dans quelle ville se trouve cet opéra célèbre ?','Sydney','sydney'),
 buzz('Quelle capitale italienne abrite le Colisée ?','Rome','colosseum'),
 buzz('Quelle est la capitale du Portugal ?','Lisbonne'),
 buzz('Quelle capitale anglaise est traversée par la Tamise ?','Londres'),
 buzz('Quelle est la capitale du Maroc ?','Rabat'),
 ],[
 who('Paris',['Je suis traversée par la Seine.','Le Louvre est l’un de mes musées.','La tour Eiffel domine mon paysage.','Je suis la capitale de la France.']),
 who('Rome',['Je suis une ville sur le Tibre.','On me surnomme la Ville éternelle.','Le Colisée est un de mes monuments.','Je suis la capitale de l’Italie.']),
 who('Londres',['Je suis traversée par la Tamise.','Buckingham Palace se trouve chez moi.','Big Ben est un de mes symboles.','Je suis la capitale du Royaume-Uni.']),
 who('Tokyo',['Je me trouve sur l’île de Honshū.','Je suis une immense métropole asiatique.','Kyoto a été une ancienne capitale de mon pays.','Je suis la capitale du Japon.']),
 who('Istanbul',['Le Bosphore traverse ma ville.','Je m’étends en Europe et en Asie.','J’ai porté le nom de Constantinople.','Je suis la grande ville turque où se trouve Sainte-Sophie.']),
 ]))
TOPICS.append(topic('explorateurs','Explorateurs célèbres','Histoire',[
 'https://www.thecanadianencyclopedia.ca/fr/article/jacques-cartier','https://www.thecanadianencyclopedia.ca/fr/article/samuel-de-champlain',
 'https://www.rmg.co.uk/stories/topics/ferdinand-magellan','https://www.britannica.com/biography/Marco-Polo',
 'https://www.britannica.com/biography/Roald-Amundsen'],[
 mc('Qui fonde Québec en 1608 ?','Samuel de Champlain',['Jacques Cartier','Jean Cabot','La Pérouse']),
 mc('Quel explorateur navigue sur le Saint-Laurent au XVIe siècle ?','Jacques Cartier',['Marco Polo','James Cook','Vasco de Gama'],'river'),
 mc('Quel voyageur vénitien est associé à la cour de Kubilai Khan ?','Marco Polo',['Ibn Battûta','Magellan','Amundsen']),
 mc('Qui atteint le pôle Sud en 1911 ?','Roald Amundsen',['Robert Scott','Ernest Shackleton','Robert Peary'],'antarctica'),
 mc('Quelle expédition réalise le premier tour du monde, terminé par Elcano ?','L’expédition de Magellan',['L’expédition de Cartier','L’expédition de Cook','L’expédition de Franklin']),
 ],[
 buzz('Quel navigateur part d’Espagne et atteint les Caraïbes en 1492 ?','Christophe Colomb',aliases=['Colomb']),
 buzz('Quel navigateur portugais atteint l’Inde par mer en contournant l’Afrique en 1498 ?','Vasco de Gama','ship',['Vasco da Gama']),
 buzz('Quel Français fonde Québec ?','Samuel de Champlain',aliases=['Champlain']),
 buzz('Quel explorateur européen longe le Saint-Laurent en 1535 ?','Jacques Cartier','river',['Cartier']),
 buzz('Quel voyageur marocain du XIVe siècle parcourt de nombreux pays ?','Ibn Battûta',aliases=['Ibn Battuta']),
 ],[
 who('Marco Polo',['Je viens de Venise.','Mon voyage me conduit vers l’Asie.','Je séjourne dans l’empire de Kubilai Khan.','Je suis le voyageur associé au Livre des merveilles.']),
 who('Jacques Cartier',['Je suis un navigateur de Saint-Malo.','Je traverse l’Atlantique au XVIe siècle.','Je remonte le Saint-Laurent.','Je suis l’explorateur français arrivé à Hochelaga en 1535.']),
 who('Samuel de Champlain',['Je cartographie des régions d’Amérique du Nord.','Je noue des alliances avec des nations autochtones.','Je participe au développement de la Nouvelle-France.','Je fonde Québec en 1608.']),
 who('Roald Amundsen',['Je suis un explorateur norvégien.','Je mène des expéditions dans les régions polaires.','Mon équipe arrive avant celle de Scott.','J’atteins le pôle Sud en décembre 1911.']),
 who('Vasco de Gama',['Je suis un navigateur portugais.','Je contourne l’Afrique par le cap de Bonne-Espérance.','Je débarque à Calicut en 1498.','J’ouvre une route maritime européenne vers l’Inde.'],['Vasco da Gama']),
 ]))
