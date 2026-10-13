# Vérification des forfaits de géographie — 10 octobre 2026

**Mise à jour :** les cinq forfaits de cartes proposent désormais des cibles aléatoires. Voir [CARTES-ALEATOIRES.md](CARTES-ALEATOIRES.md) et `VARIANTES-CARTES.csv` pour les règles actuelles et toutes les variantes. Le texte ci-dessous documente la vérification initiale. Ottawa a également été corrigé dans `geographie-capitales-v2.zip` ; voir `OTTAWA-V2.md`.

Six forfaits importables, 26 images et 26 questions : une question par image. Les originaux sont conservés ; les copies incluses dans les ZIP portent des noms compatibles avec l’importateur.

## Règles appliquées

- Cartes : choix multiples simultanés, réponses exactement **A, B, C, D** ; une seule bonne lettre.
- États-Unis : les repères désignent des **États**, et non des pays ; les questions utilisent donc « État ».
- Capitales : rébus, buzzer et réponse orale, validée par l’hôte. Les noms attendus proviennent des fichiers.
- Chaque question : **15 secondes de recherche**, réparties en trois intervalles de 5 secondes : **15 points de 0 à moins de 5 s, 10 points de 5 à moins de 10 s, 5 points de 10 à moins de 15 s**. Aucune pénalité de points après une mauvaise réponse.
- Capitales : **10 secondes pour répondre après le buzzer**. Le temps de recherche et la valeur en points sont gelés au buzzer ; une erreur ou un dépassement reprend le temps de recherche restant. Ces 10 secondes peuvent donc porter la durée réelle de la question au-delà de 15 secondes.

## Corrections orthographiques

| Fichier source | Réponse retenue | Correction |
|---|---|---|
| `abbis abéba.png` | **Addis-Abeba** | « abbis » doit devenir « Addis » ; orthographe française harmonisée. La variante « Addis Abeba » est aussi acceptée. |
| `saint marin.png` | **Saint-Marin** | Majuscules et trait d’union. |
| `port-au-prince.png` | **Port-au-Prince** | Majuscules harmonisées. |
| Autres capitales | Bangkok, Kaboul, Lima, Luxembourg, Ottawa, Paris | Orthographe correcte ; capitalisation harmonisée. |

Références : [Éthiopie — France Diplomatie](https://www.diplomatie.gouv.fr/fr/information-par-pays/ethiopie/presentation-de-l-ethiopie), [Saint-Marin — France Diplomatie](https://www.diplomatie.gouv.fr/fr/information-par-pays/saint-marin/presentation-de-saint-marin).

## Erreurs, omissions et ambiguïtés relevées

1. **Afrique — les quatre images : frontière Soudan / Soudan du Sud absente.** Elles représentent cette zone comme un seul territoire. Les questions sélectionnées portent sur d’autres pays : Angola, Niger, Gabon et Zambie. Pour une carte pédagogique actuelle, rétablir cette séparation. Référence : [carte des États et capitales — France Diplomatie, juin 2026](https://www.diplomatie.gouv.fr/files/files/le-ministere/archives-et-traites/S%E2%80%99orienter%20dans%20les%20fonds%20et%20collections/carte-monde_etats_et_capitales_a3_2026-06.pdf).
2. **`12-amerique-sud.png`, D : Guyane française.** Ce repère désigne un territoire français, pas un pays indépendant. Le pays choisi pour la question est le **Suriname, C**. B correspond au **Guyana**, distinct de la Guyane française. Référence : [Guyane — Insee](https://www.insee.fr/fr/metadonnees/geographie/region/03-guyane).
3. **`06-asie.png`, C : flèche insuffisamment précise.** Son extrémité est près de la côte et de plusieurs petits territoires du Levant ; elle n’a pas le point de localisation net des autres petites zones. Aucun nom n’a été fixé pour C dans le corrigé d’audit. La question porte sur l’**Iran, A**, clairement repéré. Ajouter un point placé à l’intérieur du territoire voulu.
4. **`europe-tchequie-slovaquie-croatie-slovenie.png`, D : repère à préciser.** La lettre se trouve dans la zone autrichienne et sa flèche aboutit près de la frontière ; le nom du fichier suggère la Slovénie. La question porte sur la **Croatie, C**. Placer le point à l’intérieur de la Slovénie pour éviter une lecture « Autriche ».
5. **`europe-microetats-abcd.png` : localisations schématiques.** Les micro-États sont des points, sans contours ; A et C apparaissent très près du littoral dans l’encart italien. B est une position approximative dans les Pyrénées. La question porte sur **Monaco, D**. Des agrandissements locaux plus précis seraient préférables si ces autres lettres deviennent les bonnes réponses.
6. **Ottawa — rébus phonétiquement approximatif.** L’image se lit « eau + tas + voie », soit approximativement « o-ta-vwa », alors que le nom visé est Ottawa. Le nom du fichier a été conservé comme réponse demandée. Suggestion : remplacer la voie ferrée par une **oie** (« eau + tas + oie »), plus proche de « o-ta-wa ».
7. **Port-au-Prince — plusieurs princes.** Le rébus montre un port avec plusieurs princes : « port aux princes » est une lecture possible. Le contexte « capitale » permet normalement de retrouver Port-au-Prince ; un seul prince réduirait l’ambiguïté.
8. **Luxembourg — indice large.** L’image évoque « luxe + bourg », mais peut aussi être décrite comme une ville riche. Le contexte « capitale » est nécessaire. Aucune erreur d’orthographe dans la réponse.
9. **Lettres minuscules sur certaines cartes, majuscules sur les téléphones.** Les réponses A–D correspondent aux repères a–d de même lettre. Pour harmoniser les images, convertir ultérieurement tous les repères en majuscules.

Les frontières des illustrations sont schématiques : ce contrôle vérifie les pays sélectionnés et signale les problèmes visibles, sans certifier l’exactitude de chaque frontière ou de chaque territoire non sélectionné. **Aucune des 26 images n’a été omise.** Les zones ambiguës ne sont pas utilisées comme bonnes réponses. Les rébus signalés restent inclus conformément aux noms de fichiers fournis.

## Suggestions

- Essayer les rébus sur le téléviseur avec quelques joueurs : 15 secondes peuvent être courtes pour les indices phonétiques les moins directs.
- Pour varier les parties sans ajouter d’images, créer ultérieurement des variantes ciblant d’autres lettres, après correction des repères ambigus.
- Ne pas mélanger l’ordre des choix A–D sans mettre à jour l’index de la bonne réponse.
- Conserver `QUESTIONS-ET-REPONSES.csv` pour l’hôte : il contient les réponses, les correspondances de lettres et les noms de fichiers originaux.

## Importation

Copier les six ZIP sur le téléphone hôte, puis choisir **IMPORTER UN FORFAIT (.ZIP)** pour chaque fichier. Importer les ZIP individuels ; les dossiers `sources/` servent à la révision des JSON. Chaque ZIP contient `game.json`, `question-bank/` et `images/` à sa racine.

## Inventaire

| Forfait | Questions | ZIP | Taille (Mo) |
|---|---:|---|---:|
| Géographie - Afrique | 4 | `geographie-afrique.zip` | 3.23 |
| Géographie - Asie | 4 | `geographie-asie.zip` | 6.28 |
| Géographie - Amérique du Sud | 2 | `geographie-amerique-du-sud.zip` | 2.37 |
| Géographie - États-Unis | 3 | `geographie-etats-unis.zip` | 4.18 |
| Géographie - Europe | 4 | `geographie-europe.zip` | 5.79 |
| Géographie - Capitales | 9 | `geographie-capitales.zip` | 12.96 |
