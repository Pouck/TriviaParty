# Réponses écrites et lecture confirmée

55 forfaits écrits et 68 forfaits oraux coexistent dans le catalogue. Les titres distinguent les versions écrites. Les identifiants et les notes sont conservés.

## Chronologies

Les joueurs lisent la question sur le téléviseur puis touchent **PRÊT**. Le délai de 45 secondes commence automatiquement quand toutes les équipes connectées sont prêtes. L’hôte peut utiliser **DÉMARRER SANS ATTENDRE**.

## Qui suis-je ?

Chaque indice commence par une lecture libre. L’hôte démarre ensuite le sablier de 20 secondes. Les joueurs ne confirment pas leur lecture dans ce format.

## Réponses écrites

Le joueur saisit sa réponse et touche **ENVOYER** ou appuie sur Entrée. Le buzzer disparaît. Quand toutes les réponses sont reçues ou que le temps expire, l’hôte valide les textes privés un à un avec **Accepter** et **Refuser**. Le score dépend du moment de l’envoi, sans double attribution.

Les questions écrites issues du buzzer donnent 30 secondes et 15 → 10 → 5 points. Les Qui suis-je écrits donnent 20 secondes par indice et une pénalité de 5 points par mauvaise réponse. Si aucune réponse n’est acceptée, l’indice suivant apparaît et l’hôte démarre son chronomètre. Sinon, la solution apparaît après la dernière validation.

Le téléviseur montre le nom de l’équipe en cours de validation, jamais son texte privé. Après la dernière validation, l’hôte retrouve le contrôle pour avancer. Les mises à jour sont envoyées dans l’ordre pour éviter de rester sur une ancienne validation.

## Choix multiples

Un seul sablier de 15 secondes : la récompense descend de 15 à 0, d’un point par seconde. Le téléviseur affiche les points.

## Sources

La banque JSON utilise `answerMode: "WRITTEN"` et des questions `textAnswer` ou `guessWho`. Voir [les forfaits écrits](WRITTEN-PACKAGES.json) et [le catalogue](current/README.md).

Après une mise à jour, recharger les pages TV et joueur de débogage. Cliquer **Activer le son** sur la page TV.
