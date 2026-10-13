# Mise à jour — Retours de partie

## Arbitrage privé, même avec une recopie d’écran

1. Pendant la sélection des forfaits, appuyer sur **CONNECTER L’ARBITRE PRIVÉ**.
2. Avec un second téléphone, une tablette ou un ordinateur connecté au même Wi-Fi, ouvrir le lien privé ou scanner le QR. Aucune installation n’est nécessaire.
3. Fermer le dialogue contenant le QR, puis commencer la diffusion de l’écran de l’hôte.
4. Lors d’une question orale, la page privée affiche la réponse attendue. Quand une équipe buzze, ses boutons **Bonne réponse** et **Mauvaise réponse** s’activent.

Cette page doit rester sur le second appareil, hors diffusion. Le lien privé ne doit pas être partagé aux joueurs. Le téléviseur et les pages des joueurs ne reçoivent pas la réponse avant sa révélation.

## Chronologies

Les chronologies grecque et romaine utilisent désormais quatre choix A–D. Les anciennes archives à cartes sont aussi converties au lancement de la question par le nouvel APK.

Chaque question chronologique commence par une phase de lecture libre. Le téléviseur affiche les événements, les joueurs attendent et le chrono ne tourne pas. **DÉMARRER LE CHRONO** lance le temps de réponse et affiche les choix sur les téléphones. Les autres types de question démarrent comme avant.

## Qui suis-je ?

- Chaque indice dure **20 secondes** : une question à quatre indices peut durer **80 secondes**.
- Le barème reste **20 → 15 → 10 → 5 points** pour les forfaits à quatre indices.
- Une mauvaise réponse ou un délai de réponse dépassé coûte **5 points** dans ces forfaits. L’équipe ne peut pas rebuzzer sur le même indice, mais revient dès le prochain.
- Le temps de réponse orale après le buzzer reste de **10 secondes**, et la progression des indices s’arrête pendant cette réponse.
- Le rythme de 20 secondes et la pénalité calculée par indice s’appliquent aussi aux archives précédemment importées. Les ZIP révisés rendent ces réglages explicites.

## Interface

- Forfaits regroupés en rubriques repliables ; recherche sans distinction d’accents ou de majuscules.
- Liste de scores défilante et noms d’équipes pouvant occuper plusieurs lignes.
- Boutons de démarrage, navigation, pause et validation plus compacts.
- Pause synchronisée avec le serveur et remise à zéro à chaque nouvelle question.
- Chrono remonté dans l’en-tête, police des indices réduite, lignes d’attente superflues retirées et paragraphes resserrés.
- Le curseur de mise prépare un montant sans l’envoyer. **VERROUILLER LA MISE** confirme définitivement ce montant, y compris zéro. Sans confirmation au départ de la question : aucune mise.

## Installation et forfaits

Installer `app/build/outputs/apk/debug/app-debug.apk`. Les forfaits existants restent utilisables avec les nouvelles règles. Les archives révisées de Grèce et Rome sont sous `package-examples/histoire-antique-2026-10-10/` ; les forfaits à indices révisés et leur catalogue sont sous `package-examples/culture-2026-10-10/`.

Pour remplacer un forfait déjà importé, choisir **Mettre à jour** dans son menu. Les identifiants des archives sont conservés.

Les fichiers du récepteur autonome dans `cast-receiver/` ont également été actualisés. Un récepteur Google Cast hébergé séparément doit être redéployé pour recevoir les changements de police et d’indication de lecture.
# Mise à jour du 11 octobre

## Écrans distincts après activation de Google Cast

Le Pixel affiche maintenant un tableau de commandes privé : réponses attendues, validation, pause, révélation, progression et mises. Une colonne d’équipes classées par score reste visible ; toucher une équipe ouvre la correction de son score. La colonne défile et met en évidence l’équipe à la parole.

Le téléviseur affiche le contenu public, le QR de connexion dans le salon, le lien joueur, le classement latéral et le nom de l’équipe au buzzer. Les sabliers graphiques se vident avec le temps ; le sablier de réponse remplace celui de la question pendant une réponse orale. La lecture avant le départ du chrono ne fait pas couler le sable.

Après installation, préparer une partie sur le Pixel puis utiliser **TV** pour reconnecter le Vizio et charger les nouveaux fichiers. Les packages ne sont pas modifiés par cette mise à jour. Validation : 65 tests Android et 27 tests navigateur, décodage du QR et aperçu 1080p de 36 questions à quatre indices.

Les classements affichent désormais toutes les équipes, du score le plus élevé au plus faible, avec défilement et rangs ex æquo. Le classement reste accessible à la fin de la partie. Les textes des questions et choix sont plus petits pour laisser davantage de place sur le téléviseur.

Installation directe par USB : `python build/install-tablet-packages.py --serial R52WB0GQRBW`. Le script installe ou actualise les 59 forfaits locaux sans sélectionner de ZIP dans Android. Il nécessite la tablette connectée et autorisée pour le débogage USB, ainsi que la version debug de TriviaParty. Il ferme la partie en cours, préserve les autres forfaits et garde les versions remplacées dans des sauvegardes masquées. Cette méthode est préparée et les archives ont été vérifiées ; son installation sur la tablette reste à vérifier lors de la prochaine connexion USB.

