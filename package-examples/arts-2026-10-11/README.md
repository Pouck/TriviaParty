# Peintures et sculptures célèbres — dix forfaits

70 questions en français : trois QCM de huit questions, trois séries buzzer de huit questions, deux Qui suis-je ? de cinq questions et deux chronologies de six questions. Les six séries QCM/buzzer alternent quatre questions illustrées et quatre questions textuelles. Les 24 images sont intégrées aux archives pour jouer hors ligne. Niveau accessible à intermédiaire.

## Réglages

- QCM et buzzer : 15 secondes ; 15 → 10 → 5 points. Réponse après buzzer : 10 secondes.
- Qui suis-je ? : quatre indices de 20 secondes (80 secondes au total) ; 20 → 15 → 10 → 5 points ; erreur : −5 points, nouvelle tentative au prochain indice. Pas d’image immédiatement révélatrice.
- Chronologies : trois cartes à glisser, puis « Envoyer l’ordre ». Les ZIP restent compatibles avec la conversion automatique de l’application. Lecture libre avant le départ du chronomètre par l’hôte, puis 30 secondes ; 15 → 10 → 5 points, par tranches de 10 secondes. Le téléviseur réordonne les trois éléments à la révélation.
- Bonnes réponses réparties également entre A–D pour les QCM de huit questions ; une ou deux par position dans les chronologies.
- Sujet déclaré « Arts » pour le regroupement et l’ordre équilibré des catégories.

| Forfait | Questions | Images | Archive |
|---|---:|---:|---|
| Arts — Peintures classiques — QCM | 8 | 4 | [arts-qcm-peintures-classiques-20261011.zip](arts-qcm-peintures-classiques-20261011.zip) |
| Arts — Couleurs et mouvements — QCM | 8 | 4 | [arts-qcm-couleurs-mouvements-20261011.zip](arts-qcm-couleurs-mouvements-20261011.zip) |
| Arts — Sculptures iconiques — QCM | 8 | 4 | [arts-qcm-sculptures-iconiques-20261011.zip](arts-qcm-sculptures-iconiques-20261011.zip) |
| Arts — Tableaux célèbres — Buzzer | 8 | 4 | [arts-buzzer-tableaux-celebres-20261011.zip](arts-buzzer-tableaux-celebres-20261011.zip) |
| Arts — Regards et scènes — Buzzer | 8 | 4 | [arts-buzzer-regards-scenes-20261011.zip](arts-buzzer-regards-scenes-20261011.zip) |
| Arts — Marbre et bronze — Buzzer | 8 | 4 | [arts-buzzer-marbre-bronze-20261011.zip](arts-buzzer-marbre-bronze-20261011.zip) |
| Arts — Peintures mystères — Qui suis-je ? | 5 | 0 | [arts-qsj-peintures-mysteres-20261011.zip](arts-qsj-peintures-mysteres-20261011.zip) |
| Arts — Sculptures mystères — Qui suis-je ? | 5 | 0 | [arts-qsj-sculptures-mysteres-20261011.zip](arts-qsj-sculptures-mysteres-20261011.zip) |
| Arts — Peintures dans le temps — Chronologie | 6 | 0 | [arts-chronologie-peintures-dans-le-temps-20261011.zip](arts-chronologie-peintures-dans-le-temps-20261011.zip) |
| Arts — Sculptures et repères — Chronologie | 6 | 0 | [arts-chronologie-sculptures-reperes-20261011.zip](arts-chronologie-sculptures-reperes-20261011.zip) |

[Questions, indices et corrigé](QUESTIONS-ET-REPONSES.csv) · [Sources et vérification](VERIFICATION.md) · [Crédits des images](PHOTOS.md).

Les sources modifiables sont dans `sources/<identifiant>/game.json`, `question-bank/<identifiant>.json` et `images/`. Données : `build/art-quiz-data.py`. Régénération : `python build/build-art-packages.py`. Images manquantes : `python build/download-art-images.py`.

Certaines œuvres reviennent dans plusieurs formats avec une question différente. Jouer d’abord les Qui suis-je ? peut préserver la difficulté de leurs indices. La Grande Vague est explicitement présentée comme une estampe ; les moaï et la statue de la Liberté élargissent le thème à la sculpture monumentale.
