# Architecture — onze forfaits

51 questions en français : 18 QCM, 18 buzzer et 15 Qui suis-je ?. Les trois QCM et les trois buzzer alternent une question avec photo et une question textuelle (3 + 3 par forfait). Les 18 photographies sont intégrées aux ZIP et ne nécessitent pas Internet pendant la partie.

## Réglages

- QCM et buzzer : 15 secondes ; 15 → 10 → 5 points ; pas de pénalité ordinaire.
- Qui suis-je ? : quatre indices textuels du plus difficile au plus facile, un nouvel indice toutes les 20 secondes ; 80 secondes au total ; 20 → 15 → 10 → 5 points. Erreur : −5 points, nouvelle tentative au prochain indice.
- Réponse après buzzer : 10 secondes. QCM en un clic, avec les positions A–D mélangées et équilibrées.
- Les photos ne sont affichées que sur le téléviseur, selon le fonctionnement actuel de l’application.

## Forfaits

| Forfait | Questions | Photos | Archive |
|---|---:|---:|---|
| Architecture — Monuments d’Europe — QCM | 6 | 3 | [architecture-qcm-europe-20261011.zip](architecture-qcm-europe-20261011.zip) |
| Architecture — Asie et Proche-Orient — QCM | 6 | 3 | [architecture-qcm-asie-orient-20261011.zip](architecture-qcm-asie-orient-20261011.zip) |
| Architecture — Architecture moderne — QCM | 6 | 3 | [architecture-qcm-moderne-20261011.zip](architecture-qcm-moderne-20261011.zip) |
| Architecture — Reconnaissance — Europe — Buzzer | 6 | 3 | [architecture-buzzer-europe-20261011.zip](architecture-buzzer-europe-20261011.zip) |
| Architecture — Reconnaissance — Sites historiques — Buzzer | 6 | 3 | [architecture-buzzer-monde-20261011.zip](architecture-buzzer-monde-20261011.zip) |
| Architecture — Reconnaissance — Icônes modernes — Buzzer | 6 | 3 | [architecture-buzzer-moderne-20261011.zip](architecture-buzzer-moderne-20261011.zip) |
| Architecture — Merveilles antiques — Qui suis-je ? | 3 | 0 | [architecture-qsj-antiquite-20261011.zip](architecture-qsj-antiquite-20261011.zip) |
| Architecture — Édifices sacrés — Qui suis-je ? | 3 | 0 | [architecture-qsj-sacre-20261011.zip](architecture-qsj-sacre-20261011.zip) |
| Architecture — Palais et châteaux — Qui suis-je ? | 3 | 0 | [architecture-qsj-palais-20261011.zip](architecture-qsj-palais-20261011.zip) |
| Architecture — Sites de grandes civilisations — Qui suis-je ? | 3 | 0 | [architecture-qsj-civilisations-20261011.zip](architecture-qsj-civilisations-20261011.zip) |
| Architecture — Icônes de l’époque moderne — Qui suis-je ? | 3 | 0 | [architecture-qsj-modernes-20261011.zip](architecture-qsj-modernes-20261011.zip) |

## Contenu et sources

[Questions, indices et corrigé](QUESTIONS-ET-REPONSES.csv) · [Vérification](VERIFICATION.md) · [Crédits photo](PHOTOS.md).

Tous les JSON et les images sont accessibles sous `sources/<identifiant>/`. Les fichiers `PHOTOS.json` et `VERIFICATION.json` dans ces dossiers sont des documents de référence et ne sont pas inclus dans les ZIP importables.

Données : `build/architecture-quiz-data.py`. Régénérer : `python build/build-architecture-packages.py`. Télécharger les photos manquantes : `python build/download-architecture-images.py`. Les photos existantes sont mises en cache.

## Images progressives

Le format actuel révèle progressivement les indices textuels, mais son unique champ image affiche immédiatement la photo complète. Ces cinq forfaits Qui suis-je ? restent donc sans image. Une future variante « image mystère » pourrait révéler des portions d’une photo à chaque baisse de points ; elle nécessiterait une modification de l’application et du récepteur TV.
