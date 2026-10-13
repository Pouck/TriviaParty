# Forfaits — Antiquité, mythologie et littérature

19 forfaits indépendants : 36 questions à indices et 50 questions à choix multiples. Tous sont en français.

## Importation

Importer chaque ZIP souhaité depuis l’application ; plusieurs forfaits peuvent être sélectionnés pour une partie. Ne pas importer les CSV ou les dossiers de sources. Les forfaits à indices nécessitent la version de l’application prenant en charge « Qui suis-je ? ».

## Réglages

- Qui suis-je ? : quatre indices, révélés à 0, 20, 40 et 60 secondes ; 80 secondes au total ; 20 → 15 → 10 → 5 points. Buzzer oral, avec 10 secondes pour répondre après le buzzer ; validation sur le panneau privé d’un second appareil.
- Choix multiples : 15 secondes ; 15 → 10 → 5 points ; réponses simultanées en un clic.
- Qui suis-je ? : −5 points par mauvaise réponse ou délai dépassé ; retour au prochain indice. QCM : aucune pénalité ordinaire. Les mises éventuelles suivent les règles de l’application.
- Les réponses A–D sont mélangées dans chaque archive : deux ou trois bonnes réponses par position sur dix questions. Le mélange ne change pas automatiquement à chaque partie.

## Archives

| Forfait | Questions | Format |
| --- | ---: | --- |
| [Qui suis-je ? — Grèce antique — Figures et lieux](culture-qsj-grece-figures-et-lieux.zip) | 4 | Indices + buzzer |
| [Qui suis-je ? — Grèce antique — Grandes figures](culture-qsj-grece-grandes-figures.zip) | 4 | Indices + buzzer |
| [Qui suis-je ? — Rome antique — République et Empire](culture-qsj-rome-personnages.zip) | 4 | Indices + buzzer |
| [Qui suis-je ? — Rome antique — Monuments et crises](culture-qsj-rome-monuments-et-crises.zip) | 4 | Indices + buzzer |
| [Qui suis-je ? — Mythologie grecque — Dieux et mortels](culture-qsj-mythologie-grecque-dieux-et-mortels.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Mythologie grecque — Monstres et objets](culture-qsj-mythologie-grecque-monstres-et-objets.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Mythologie romaine — Divinités](culture-qsj-mythologie-romaine-divinites.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Mythologie romaine — Héros et fondations](culture-qsj-mythologie-romaine-fondations.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Littérature française — Œuvres](culture-qsj-litterature-francaise-oeuvres.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Littérature française — Personnages](culture-qsj-litterature-francaise-personnages.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Littérature britannique et irlandaise — Œuvres](culture-qsj-litterature-anglophone-oeuvres.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Littérature britannique et irlandaise — Personnages](culture-qsj-litterature-anglophone-personnages.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Littérature américaine — Œuvres](culture-qsj-litterature-americaine-oeuvres.zip) | 2 | Indices + buzzer |
| [Qui suis-je ? — Littérature américaine — Personnages](culture-qsj-litterature-americaine-personnages.zip) | 2 | Indices + buzzer |
| [Littérature française — Œuvres : choix multiples](culture-qcm-francaise-oeuvres.zip) | 10 | Choix multiples |
| [Littérature française — Personnages : choix multiples](culture-qcm-francaise-personnages.zip) | 10 | Choix multiples |
| [Littérature britannique et irlandaise — Œuvres : choix multiples](culture-qcm-anglophone-oeuvres.zip) | 10 | Choix multiples |
| [Littérature britannique et irlandaise — Personnages : choix multiples](culture-qcm-anglophone-personnages.zip) | 10 | Choix multiples |
| [Littérature américaine — Œuvres : choix multiples](culture-qcm-americaine-oeuvres.zip) | 10 | Choix multiples |

## Révision et mises à jour

Voir [les vérifications, corrections et recoupements](VERIFICATION.md), [le corrigé des indices](QUI-SUIS-JE-ET-CORRIGE.csv) et [le corrigé des choix multiples](CHOIX-MULTIPLES-ET-CORRIGE.csv).

Les sources JSON sont sous `sources/`. Pour mettre à jour un forfait, conserver son identifiant et reconstruire son ZIP avec `game.json` et `question-bank/` à la racine. Pour régénérer les archives, modifier les données dans `build/culture_guess_who_data.py` ou `build/culture_multiple_choice_data.py`, puis exécuter `python build/build-culture-packages.py`.
