from library_common import *
TOPICS=[]
TOPICS.append(topic('logique','Logique — Défis rapides','Logique et énigmes',[
 'https://www.mathsisfun.com/','https://www.britannica.com/science/logic',
 'Créations originales ; solutions démontrées dans VERIFICATION.json.'],[
 mc('Comptez de deux en deux : 2, 4, 6, 8… Quel nombre suit ?','10',['9','12','16'],'sequence'),
 mc('Tous les chats de ce jeu sont bleus. Mina est un chat. Quelle couleur a Mina ?','Bleue',['Rouge','Verte','Impossible à savoir']),
 mc('Combien de pommes voyez-vous en tout ?','5',['3','4','6'],'five-apples'),
 mc('Lina est devant Hugo, qui est devant Zoé. Qui est en dernier ?','Zoé',['Lina','Hugo','Impossible à savoir']),
 mc('Une boîte contient 4 billes rouges et 1 bleue. Combien de billes contient-elle ?','5',['4','6','3']),
 ],[
 buzz('Quel nombre manque : 5, 10, 15, __, 25, en comptant de cinq en cinq ?','20','fives'),
 buzz('Un grand-père mange avec son fils et son petit-fils. Combien de personnes sont à table ?','Trois',aliases=['3']),
 buzz('Vous doublez la personne en deuxième place d’une course. Quelle place prenez-vous ?','La deuxième',aliases=['Deuxième','2','Seconde']),
 buzz('Combien de carrés sont dessinés ici ?','Quatre','four-squares',['4']),
 buzz('Marie a 3 pommes et en donne 1. Combien lui en reste-t-il ?','Deux',aliases=['2']),
 ],[
 who('Le zéro',['Je suis un nombre entier.','M’ajouter à un nombre ne le change pas.','Je représente l’absence de quantité.','Mon chiffre s’écrit 0.'],['Zéro','0']),
 who('Un triangle',['Je suis une figure plane.','La somme de mes angles vaut 180 degrés en géométrie ordinaire.','J’ai trois côtés.','Mon nom commence par « tri ».'],['Triangle']),
 who('Un nombre pair',['Je suis un nombre entier.','Je peux être partagé en deux groupes égaux sans reste.','2, 4 et 6 sont des exemples de moi.','Je suis divisible par deux.'],['Nombre pair','Pair']),
 who('Un carré',['Je suis un quadrilatère.','Tous mes angles sont droits.','Mes quatre côtés ont la même longueur.','Je ressemble à une case de damier.'],['Carré']),
 who('La moitié',['Je suis une part d’un tout.','Deux parts comme moi reconstituent le tout.','Je correspond à 50 %.','Je suis ce qu’on obtient en divisant par deux.'],['Moitié','Une moitié']),
 ]))
TOPICS.append(topic('devinettes','Devinettes — Objets familiers','Logique et énigmes',[
 'Créations originales ; réponses rendues uniques par le dernier indice.',
 'https://www.britannica.com/art/riddle'],[
 mc('Je garde des dents dans vos cheveux, sans vous mordre. Qui suis-je ?','Un peigne',['Une fourchette','Une fermeture éclair','Une scie']),
 mc('Je donne l’heure avec des aiguilles, sans piquer. Qui suis-je ?','Une horloge',['Une boussole','Un thermomètre','Une balance'],'clock'),
 mc('J’ai des pages et une couverture, sans être un lit. Qui suis-je ?','Un livre',['Une valise','Un tapis','Un oreiller']),
 mc('J’ouvre une serrure sans avoir de main. Qui suis-je ?','Une clé',['Une pièce','Un clou','Une cuillère'],'key'),
 mc('Je sèche votre corps et deviens humide. Qui suis-je ?','Une serviette',['Un savon','Un miroir','Une éponge sèche']),
 ],[
 buzz('Que peut-on casser en ne tenant pas sa parole ?','Une promesse',aliases=['Promesse']),
 buzz('Je protège de la pluie et m’ouvre au-dessus de votre tête. Qui suis-je ?','Un parapluie','umbrella',['Parapluie']),
 buzz('J’ai un goulot et contiens des boissons. Qui suis-je ?','Une bouteille',aliases=['Bouteille']),
 buzz('Je porte votre reflet et suis accroché au mur. Qui suis-je ?','Un miroir','mirror',['Miroir']),
 buzz('Je suis la partie d’une chaussure qui touche le sol. Qui suis-je ?','La semelle',aliases=['Semelle']),
 ],[
 who('Une bougie',['Je peux décorer une fête.','Je diminue quand on m’utilise.','Une mèche me traverse.','Ma cire fond près de ma flamme.'],['Bougie']),
 who('Un miroir',['Je vous montre sans parler.','Je reproduis vos mouvements.','Je suis souvent dans une salle de bains.','Vous y regardez votre reflet.'],['Miroir']),
 who('Un parapluie',['Je suis utile par mauvais temps.','Je peux être plié pour le transport.','Je m’ouvre au-dessus de votre tête.','Je vous protège de la pluie.'],['Parapluie']),
 who('Un livre',['Je peux raconter une histoire.','Vous me parcourez sans marcher.','Je possède des pages.','Ma couverture protège mon texte.'],['Livre']),
 who('Un peigne',['Je suis un petit objet de toilette.','Je porte des dents sans manger.','Je passe entre les mèches.','Je démêle vos cheveux.'],['Peigne']),
 ]))
