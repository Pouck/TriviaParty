# Forfaits originaux

Les cinq ensembles originaux ont été convertis en ZIP indépendants. Le nouvel APK les installe automatiquement une seule fois dans le même stockage que les forfaits importés. Ils peuvent ensuite être mis à jour ou supprimés depuis le menu ⋮. Une suppression reste effective après le redémarrage de l’application.

- `original-gaming-history.zip` : Histoire du jeu vidéo.
- `original-pop-culture.zip` : Culture populaire.
- `original-science-tech.zip` : Sciences et technologie.
- `original-video-game-maps.zip` : Cartes de jeux vidéo.
- `original-world-geography.zip` : Géographie mondiale.

Révision du 12 octobre 2026 : les 25 identifiants sont conservés, mais les questions sont désormais en français, plus courtes, et les formulations ambiguës ont été corrigées. Les questions sans carte ont été remplacées. Chaque forfait comporte deux questions illustrées et trois textuelles. Réglages : 15 secondes, 15 / 10 / 5 points et 10 secondes pour répondre au buzzer. Les chronologies bénéficient d’au moins 45 secondes dans l’application. Sélectionnez plusieurs ensembles pour les combiner.

Pour corriger un forfait : modifier les JSON dans `sources/<identifiant>/`, puis créer un ZIP contenant directement `game.json` et `question-bank/`. Garder le même `id` dans `game.json`, puis choisir **Mettre à jour** dans le menu du forfait. Les copies des ZIP permettent aussi de réimporter un ensemble supprimé.

Les JSON dans `app/src/main/assets/question-bank/` sont les sources historiques conservées pour régénérer les archives ; ils ne sont plus chargés comme ensembles permanents. Les anciens manifests dans `app/src/main/assets/game-packages/` restent des références historiques, sans être chargés au démarrage.
