# Qui suis-je ? — Indices progressifs

Importer `qui-suis-je-demo.zip` depuis la sélection des forfaits, après installation de la nouvelle version de l’application. Ce forfait de démonstration contient une question sur un objet, avec trois indices.

| Temps de jeu | Récompense | Affichage hôte / TV |
|---|---|---|
| 0 à moins de 20 s | 15 points | Premier indice |
| 20 à moins de 40 s | 10 points | Premier et deuxième indices |
| 40 à moins de 60 s | 5 points | Trois indices |
| 15 s | Fin de question | Réponse et classement |

Les indices déjà révélés restent visibles. Le buzzer fige le temps de jeu, les indices et le palier de points ; le temps de réponse du forfait prend le relais (10 secondes ici). L’hôte juge la réponse orale. Une réponse correcte rapporte la récompense du palier où l’équipe a buzzé. Une mauvaise réponse ou l’expiration du temps de réponse bloque cette équipe pour la question ; les autres peuvent buzzer et la progression reprend. Une pause manuelle fige également les indices. Les mises de début de catégorie fonctionnent comme pour les autres questions.

Les téléphones montrent uniquement le score et le buzzer : ni les indices, ni les réponses acceptées ne sont envoyés aux joueurs web. La TV reçoit uniquement les indices déjà révélés. Lorsque la réponse est révélée, les indices sont retirés pour laisser la place à la réponse et au classement.

## Créer un forfait

Les JSON dans `sources/` donnent un exemple complet. Copier ce dossier, modifier les identifiants et le nom de catégorie, puis zipper son contenu : `game.json` doit être à la racine de l’archive, avec `question-bank/` à côté. Ne pas inclure ce README dans le ZIP.

- `kind` : `guessWho`.
- `prompt` : titre facultatif, par défaut `Qui suis-je ?`.
- `clues` : textes non vides dans l’ordre souhaité, du plus difficile au plus explicite.
- `acceptableAnswers` : au moins une réponse non vide, utilisée pour l’affichage de la solution ; le jugement reste manuel.
- `answerMode` de la catégorie : `BUZZER`.
- `questionTypes` : `["Qui suis-je ?"]`.
- Prévoir exactement `maxFlips + 1` indices par question : un au départ, puis un par changement de palier. L’import refuse les indices manquants, supplémentaires ou vides.
- Pour « Qui suis-je ? », utiliser `secondsPerFlip: 20`. La nouvelle application applique aussi les 20 secondes aux anciens forfaits. `pointsDecayPerFlip` définit la baisse de points ; durée totale : `(maxFlips + 1) × 20` secondes.
- `answerTimeSeconds` définit le temps de réponse orale, séparé du temps des indices.

Le format `textAnswer` existant reste compatible et n’affiche pas d’indices progressifs. Une catégorie doit contenir uniquement des questions du même type. Un forfait peut réunir plusieurs catégories de types différents.

Pour des devinettes avec des indices longs, augmenter la durée des paliers plutôt que de surcharger chaque indice. Aucune mise à jour des forfaits existants n’est nécessaire. Le récepteur TV local est livré dans l’APK ; un récepteur Google Cast hébergé séparément doit utiliser les fichiers actuels de `cast-receiver/` pour préserver les retours à la ligne.

Pour valider sans dévoiler la réponse sur un écran recopié : ouvrir « CONNECTER L’ARBITRE PRIVÉ » pendant la préparation, scanner le QR sur un autre appareil, fermer ce dialogue puis commencer la diffusion. La page privée affiche la réponse et les boutons de validation.
