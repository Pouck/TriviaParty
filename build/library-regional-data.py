from library_common import *
TOPICS=[]
TOPICS.append(topic('legendes-france','Légendes de France — Régions et créatures','Contes et légendes',[
 'https://ich.unesco.org/en/RL/processional-giants-and-dragons-in-belgium-and-france-00153',
 'https://gallica.bnf.fr/','https://www.britannica.com/topic/Melusine',
 'https://www.britannica.com/topic/Beast-of-Gevaudan'],[
 mc('Quelle créature légendaire est associée à Tarascon ?','La Tarasque',['Le Minotaure','Le Kraken','Le Sphinx'],'dragon'),
 mc('Quelle région est associée à la ville engloutie d’Ys ?','La Bretagne',['La Provence','L’Alsace','La Bourgogne']),
 mc('Quelle fée est souvent représentée moitié femme, moitié serpent ?','Mélusine',['Cendrillon','Blanche-Neige','Aurore']),
 mc('Quel type de créature est généralement un korrigan breton ?','Un petit être féerique',['Un géant de pierre','Un oiseau marin','Un serpent de mer'],'fairy'),
 mc('Quelle forêt bretonne est associée aux légendes arthuriennes ?','Brocéliande',['Fontainebleau','Les Landes','Rambouillet']),
 ],[
 buzz('Quelle créature légendaire donne son nom aux fêtes de Tarascon ?','La Tarasque','dragon',['Tarasque']),
 buzz('Quelle ville légendaire bretonne est engloutie sous la mer ?','Ys','sea'),
 buzz('Quelle fée légendaire est associée à la famille de Lusignan ?','Mélusine'),
 buzz('Quelle bête terrorise le Gévaudan au XVIIIe siècle ?','La Bête du Gévaudan',aliases=['Bête du Gévaudan']),
 buzz('Quel nom désigne de petits êtres féeriques des traditions bretonnes ?','Les korrigans',aliases=['Korrigans','Korrigan']),
 ],[
 who('La Tarasque',['Je suis un monstre d’une légende provençale.','Sainte Marthe est associée à mon histoire.','Des fêtes me font défiler à Tarascon.','Mon nom rappelle celui de cette ville.'],['Tarasque']),
 who('Mélusine',['Je suis une fée de récits médiévaux.','Je suis associée à Lusignan.','Un interdit protège mon intimité.','Je peux apparaître moitié femme, moitié serpent.']),
 who('Ys',['Je suis une ville de légende bretonne.','Le roi Gradlon est lié à mon histoire.','Dahut apparaît dans plusieurs versions du récit.','Je suis la cité engloutie sous la mer.']),
 who('Un korrigan',['Je suis un être du folklore breton.','Je suis souvent petit et facétieux.','On m’associe aux lieux et aux nuits mystérieuses.','Mon nom commence par « korri ».'],['Korrigan','Les korrigans']),
 who('La Bête du Gévaudan',['Mon histoire se déroule au XVIIIe siècle.','Des attaques frappent une région de France.','Mon identité exacte reste discutée.','Mon nom est celui de la bête associée au Gévaudan.'],['Bête du Gévaudan']),
 ]))
TOPICS.append(topic('cuisine-saveurs','Cuisine — Saveurs et desserts du monde','Cuisine',[
 'https://www.britannica.com/topic/food','https://ich.unesco.org/en/lists',
 'https://www.britannica.com/topic/chocolate','https://www.britannica.com/topic/taco'],[
 mc('Quel fruit sec forme la base habituelle de la pâte de massepain ?','L’amande',['La noix de coco','La noisette','La noix de cajou']),
 mc('Quel ingrédient donne son nom à la vanille ?','Les gousses d’une orchidée',['Une écorce de chêne','Une racine de rose','Un grain de café']),
 mc('Quelle viennoiserie en forme de croissant est représentée ?','Un croissant',['Un éclair','Un macaron','Un millefeuille'],'croissant'),
 mc('Quel plat mexicain se sert dans une tortilla garnie ?','Un taco',['Un sushi','Une crêpe Suzette','Un ravioli'],'taco'),
 mc('Quelle épice est tirée d’une fleur de crocus ?','Le safran',['Le poivre','Le gingembre','La cannelle']),
 ],[
 buzz('Quelle fève sert à fabriquer le chocolat ?','La fève de cacao','cacao',['Cacao']),
 buzz('Quel dessert français est une fine crêpe garnie ou roulée ?','Une crêpe',aliases=['Crêpe']),
 buzz('Quel dessert italien au café est représenté ici ?','Le tiramisu','tiramisu',['Tiramisu']),
 buzz('Quel petit gâteau français assemble deux coques avec une garniture ?','Le macaron',aliases=['Macaron']),
 buzz('Quel dessert japonais est à base de riz gluant pilé ?','Le mochi',aliases=['Mochi']),
 ],[
 who('Le chocolat',['Je suis un aliment sucré ou amer.','Je peux être noir, au lait ou blanc.','Le cacao est essentiel aux versions noires et au lait.','Je me vends souvent en tablettes.'],['Chocolat']),
 who('Le croissant',['Je suis une viennoiserie.','Ma pâte est généralement feuilletée.','Je suis souvent mangé au petit-déjeuner.','Ma forme rappelle une lune partielle.'],['Croissant']),
 who('Le taco',['Je suis un plat mexicain.','Je peux contenir viande, légumes et salsa.','Ma garniture repose sur une tortilla.','Mon nom compte quatre lettres et commence par T.'],['Taco']),
 who('Le macaron',['Je suis un petit gâteau.','Mes coques sont souvent colorées.','Elles sont réunies par une garniture.','Ma version parisienne compte deux coques à base d’amande.'],['Macaron']),
 who('Le mochi',['Je suis un aliment japonais.','Ma texture est souple et collante.','Je peux entourer une garniture sucrée.','Je suis fait de riz gluant pilé.'],['Mochi']),
 ]))
