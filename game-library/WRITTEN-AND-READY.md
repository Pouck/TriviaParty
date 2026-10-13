# Réponses écrites et lecture confirmée

55 forfaits écrits et 68 forfaits oraux coexistent dans le catalogue. Les titres distinguent les versions écrites. Les identifiants et les notes sont conservés.

## Chronologies

Les joueurs lisent la question sur le téléviseur puis touchent **PRÊT**. Le délai de 45 secondes commence automatiquement quand toutes les équipes connectées sont prêtes. L’hôte peut utiliser **DÉMARRER SANS ATTENDRE**.

## Qui suis-je ?

Le sablier de 20 secondes démarre automatiquement avec chaque indice, y compris après une mauvaise réponse écrite. Seules les chronologies ont une phase de lecture avant de démarrer.

## Réponses écrites

Le joueur saisit sa réponse et touche **ENVOYER** ou appuie sur Entrée. Le buzzer disparaît. Quand toutes les réponses sont reçues ou que le temps expire, l’hôte valide les textes privés un à un avec **Accepter** et **Refuser**. Le score dépend du moment de l’envoi, sans double attribution.

Les questions écrites issues du buzzer donnent 30 secondes et 15 → 10 → 5 points. Les Qui suis-je écrits donnent 20 secondes par indice et une pénalité de 5 points par mauvaise réponse. Si aucune réponse n’est acceptée, l’indice suivant apparaît et son chronomètre démarre automatiquement. Sinon, la solution apparaît après la dernière validation.

Le téléviseur montre le nom de l’équipe et son texte soumis pendant sa validation. Les autres réponses et la réponse attendue restent cachées. Après chaque validation, le nom et le texte restent sur le téléviseur avec le résultat. L’hôte touche **CONTINUER** pour passer au joueur suivant ou finir les validations. Les mises à jour sont envoyées dans l’ordre pour éviter de rester sur une ancienne validation.

## Choix multiples

Un seul sablier de 15 secondes : la récompense descend de 15 à 0, d’un point par seconde. Le téléviseur affiche les points.

## Sources

La banque JSON utilise `answerMode: "WRITTEN"` et des questions `textAnswer` ou `guessWho`. Voir [les forfaits écrits](WRITTEN-PACKAGES.json) et [le catalogue](current/README.md).

Après une mise à jour, recharger les pages TV et joueur de débogage. Cliquer **Activer le son** sur la page TV.

Pendant une prise de parole au buzzer, la question et son image sont masquées complètement. Elles retrouvent leur place lorsque le jeu reprend.
