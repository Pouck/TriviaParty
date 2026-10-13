from library_common import *
TOPICS=[]
TOPICS.append(topic('oiseaux','Oiseaux — Portraits et habitudes','Nature',[
 'https://www.allaboutbirds.org/guide/','https://nationalzoo.si.edu/animals/birds'],[
 mc('Quel oiseau est représenté ici ?','Un toucan',['Un perroquet','Un pélican','Un martin-pêcheur'],'toucan'),
 mc('Quel oiseau peut voler sur place devant une fleur ?','Le colibri',['Le cygne','L’autruche','Le corbeau']),
 mc('Quel oiseau fait une grande roue avec ses plumes ?','Le paon',['Le flamant','La grue','Le héron'],'peacock'),
 mc('Quel oiseau ne vole pas mais nage très bien en Antarctique ?','Le manchot',['L’albatros','Le macareux','La mouette']),
 mc('Quel oiseau martèle les troncs avec son bec ?','Le pic',['Le pigeon','Le canard','Le moineau']),
 ],[
 buzz('Quel oiseau africain est le plus grand oiseau vivant ?','L’autruche','ostrich',['Autruche']),
 buzz('Quel rapace nocturne est représenté ici ?','Un hibou','owl',['Hibou','Grand-duc']),
 buzz('Quelle partie du corps des oiseaux remplace les dents pour saisir la nourriture ?','Le bec',aliases=['Bec']),
 buzz('Quel oiseau domestique pond les œufs les plus courants en cuisine ?','La poule',aliases=['Poule']),
 buzz('Comment nomme-t-on le déplacement saisonnier de nombreux oiseaux ?','La migration',aliases=['Migration']),
 ],[
 who('Le colibri',['Je suis un petit oiseau des Amériques.','Mes ailes battent très rapidement.','Je me nourris souvent de nectar.','Je peux rester en vol devant une fleur.'],['Colibri','Oiseau-mouche']),
 who('Le manchot',['Mes ailes sont adaptées à la nage.','Je vis dans l’hémisphère Sud.','Je ne vole pas.','On me confond souvent avec le pingouin.'],['Manchot']),
 who('Le paon',['Je suis un oiseau au cri puissant.','Le mâle porte des plumes aux motifs en forme d’yeux.','Il déploie sa traîne pour séduire.','Je suis l’oiseau qui fait la roue.'],['Paon']),
 who('Le pic',['Je cherche souvent des insectes dans le bois.','Je grimpe sur les troncs.','Mon bec frappe les arbres.','Mon nom français commence comme celui d’un outil pointu.'],['Pic','Pivert']),
 who('L’autruche',['Je viens d’Afrique.','Je cours très vite sur deux grandes pattes.','Je ponds les plus gros œufs des oiseaux vivants.','Je suis le plus grand oiseau, mais je ne vole pas.'],['Autruche']),
 ]))
TOPICS.append(topic('insectes','Insectes — Petites bêtes','Nature',[
 'https://naturalhistory.si.edu/education/teaching-resources/life-science/butterflies-and-beyond',
 'https://www.si.edu/spotlight/buginfo','https://www.britannica.com/animal/insect'],[
 mc('Combien de pattes possède normalement un insecte adulte ?','Six',['Quatre','Huit','Dix']),
 mc('Quel insecte est représenté ici ?','Une coccinelle',['Une luciole','Un scarabée rhinocéros','Une punaise'],'ladybird'),
 mc('Quelle est la larve du papillon ?','La chenille',['Le têtard','Le ver de terre','L’asticot']),
 mc('Quel insecte est connu pour produire du miel ?','L’abeille',['La guêpe','Le moustique','La cigale'],'bee'),
 mc('Lequel de ces animaux n’est pas un insecte ?','L’araignée',['La fourmi','La libellule','Le criquet']),
 ],[
 buzz('Quel insecte bâtit souvent une fourmilière ?','La fourmi','ant',['Fourmi']),
 buzz('Quel insecte adulte est représenté avec quatre grandes ailes ?','Un papillon','butterfly',['Papillon']),
 buzz('Quel insecte est célèbre pour son chant en été ?','La cigale',aliases=['Cigale']),
 buzz('Quel insecte ressemble à une brindille ?','Le phasme',aliases=['Phasme']),
 buzz('Quel insecte produit de la lumière, comme une petite lanterne ?','La luciole',aliases=['Luciole']),
 ],[
 who('La coccinelle',['Je suis un petit coléoptère.','Je mange souvent des pucerons.','Mes ailes visibles sont souvent rouges à points noirs.','On m’appelle parfois la bête à bon Dieu.'],['Coccinelle']),
 who('L’abeille',['Je visite les fleurs.','Je participe à la pollinisation.','Certaines de mes espèces vivent dans des ruches.','L’abeille domestique produit du miel.'],['Abeille']),
 who('La mante religieuse',['Je suis un insecte prédateur.','J’attends souvent immobile ma proie.','Mes pattes avant sont repliées devant moi.','Ma posture me donne un nom lié à la prière.'],['Mante religieuse']),
 who('Le phasme',['Je mise sur le camouflage.','Je peux être confondu avec une partie de plante.','Mon corps est souvent long et fin.','Je suis l’insecte qui ressemble à une brindille.'],['Phasme']),
 who('La libellule',['Je suis souvent observée près de l’eau.','Ma larve vit dans l’eau.','Je possède de grands yeux et deux paires d’ailes.','Je suis la chasseuse volante au long abdomen.'],['Libellule']),
 ]))
TOPICS.append(topic('animaux-terrestres','Animaux terrestres — Mammifères','Nature',[
 'https://nationalzoo.si.edu/animals','https://animals.sandiegozoo.org/animals',
 'https://australian.museum/learn/animals/mammals/platypus/'],[
 mc('Quel animal porte ces rayures noires et blanches ?','Le zèbre',['La girafe','L’okapi','L’antilope'],'zebra'),
 mc('Quel mammifère porte généralement son petit dans une poche ?','Le kangourou',['Le renard','Le lapin','Le panda']),
 mc('Quel animal est représenté ici ?','Une girafe',['Un chameau','Un lama','Un cerf'],'giraffe'),
 mc('Quel mammifère pond des œufs ?','L’ornithorynque',['Le castor','La loutre','Le raton laveur']),
 mc('Quelle nourriture est particulièrement associée au panda géant ?','Le bambou',['Le poisson','Les glands','Les fourmis']),
 ],[
 buzz('Quel grand félin mâle porte souvent une crinière ?','Le lion','lion',['Lion']),
 buzz('Quel animal construit des barrages avec des branches ?','Le castor','beaver',['Castor']),
 buzz('Combien de bosses a généralement le dromadaire ?','Une',aliases=['1']),
 buzz('Quel grand mammifère a une trompe ?','L’éléphant',aliases=['Éléphant']),
 buzz('Quel animal arctique est aussi appelé ours blanc ?','L’ours polaire',aliases=['Ours polaire']),
 ],[
 who('L’éléphant',['Je suis un grand mammifère terrestre.','Mes oreilles et mes défenses sont célèbres.','Je peux saisir des objets avec mon nez allongé.','Ce nez s’appelle une trompe.'],['Éléphant']),
 who('Le kangourou',['Je suis associé à l’Australie.','Je me déplace souvent en bondissant.','Ma queue m’aide à garder l’équilibre.','Mon petit grandit dans une poche.'],['Kangourou']),
 who('L’ornithorynque',['Je vis en Australie.','Je suis un mammifère qui pond des œufs.','Mes pattes sont palmées.','Mon bec ressemble à celui d’un canard.'],['Ornithorynque']),
 who('Le panda géant',['Je vis à l’état sauvage en Chine.','Mon pelage est noir et blanc.','Je mange surtout du bambou.','Je suis le célèbre ours associé à ce régime.'],['Panda','Panda géant']),
 who('Le castor',['Je suis un rongeur semi-aquatique.','Ma queue est large et aplatie.','Je coupe des arbres avec mes incisives.','Je construis des barrages.'],['Castor']),
 ]))
TOPICS.append(topic('animaux-marins','Animaux marins — Sous l’eau','Nature',[
 'https://www.fisheries.noaa.gov/whales','https://www.fisheries.noaa.gov/dolphins-porpoises',
 'https://ocean.si.edu/ocean-life','https://www.montereybayaquarium.org/animals'],[
 mc('Quel animal marin possède huit bras ?','La pieuvre',['Le calmar','La méduse','La seiche'],'octopus'),
 mc('Quel est le plus grand animal vivant ?','La baleine bleue',['Le requin-baleine','L’orque','Le cachalot']),
 mc('À quel groupe appartient le dauphin ?','Aux mammifères',['Aux poissons','Aux reptiles','Aux amphibiens']),
 mc('Quel petit poisson est représenté ici ?','Un hippocampe',['Un poisson-clown','Un poisson-lune','Une anguille'],'seahorse'),
 mc('Quel organe permet à la plupart des poissons de respirer dans l’eau ?','Les branchies',['Les poumons','Les antennes','Les nageoires']),
 ],[
 buzz('Quel mammifère marin est représenté ici ?','Un dauphin','dolphin',['Dauphin']),
 buzz('Quel reptile marin possède une carapace ?','La tortue marine','turtle',['Tortue','Tortue marine']),
 buzz('Quel animal marin forme un polype et peut bâtir des récifs ?','Le corail',aliases=['Corail']),
 buzz('Quel grand cétacé noir et blanc est aussi appelé épaulard ?','L’orque',aliases=['Orque','Épaulard']),
 buzz('Quel poisson cartilagineux est connu pour son aileron dorsal ?','Le requin',aliases=['Requin']),
 ],[
 who('La pieuvre',['Je suis un mollusque.','Je peux changer rapidement d’apparence.','Je peux projeter de l’encre.','Je possède huit bras à ventouses.'],['Pieuvre','Poulpe']),
 who('La baleine bleue',['Je suis un mammifère des océans.','Je me nourris surtout de krill.','Je respire à la surface.','Je suis le plus grand animal vivant.'],['Baleine bleue']),
 who('L’hippocampe',['Je suis un poisson.','Le mâle porte les œufs dans une poche.','Ma queue s’enroule autour de supports.','Ma tête ressemble à celle d’un cheval.'],['Hippocampe']),
 who('La tortue marine',['Je suis un reptile.','Je respire de l’air mais nage dans l’océan.','Les femelles pondent sur les plages.','Je porte une carapace et des pattes en nageoires.'],['Tortue marine','Tortue']),
 who('Le poisson-clown',['Je suis un petit poisson des récifs.','Je vis souvent près d’anémones.','Mon corps peut être orange à bandes blanches.','Nemo appartient à mon groupe.'],['Poisson-clown']),
 ]))
