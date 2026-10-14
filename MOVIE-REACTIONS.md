# Réactions vocales — pistes en langue originale

L’objectif est de remplacer les voix de synthèse plates par de véritables interprétations. Un scénario permet de trouver les mots ; il ne contient pas la piste sonore des acteurs. Cette liste est une sélection de candidats, pas une banque audio installée. Une alternative de 100 enregistrements humains est maintenant préparée dans [audio-bank](audio-bank/README.md) et intégrée à l’app. Elle contient 95 expressions de prononciation et cinq réactions anglaises de jeu jouées par Tim Rockk ; elle ne constitue pas la banque de dialogues de films envisagée. Les candidats de films ci-dessous ne sont pas des fichiers audio installés.

## Mélange proposé

Environ 70 % de français, 20 % d’anglais, 5 % d’espagnol et 5 % d’allemand. Extraits parlés généralement de 3–6 secondes (jusqu’à 8 secondes si la chute le justifie), sans chanson, ni longue musique de fond. Conserver la langue réellement prononcée, indépendamment de la nationalité du film ou de l’acteur. Le son positif/négatif précède la voix pour rendre le résultat clair, même si la phrase est ironique.

## Premiers candidats identifiés

| Réaction | Citation courte | Film / langue | Source et vérification restante |
|---|---|---|---|
| Bonne réponse | « Habile ! » | OSS 117 : Rio ne répond plus / français | [Extrait répertorié, 1 seconde](https://zonesons.com/films-d-espionnage/oss-117-rio-ne-repond-plus/339624). Écouter et vérifier le fichier original avant intégration. |
| Bonne réponse | « Eh oui ! » | OSS 117 : Rio ne répond plus / français | [Dialogue voisin du même extrait](https://zonesons.com/films-d-espionnage/oss-117-rio-ne-repond-plus/339624). Découpe et interprétation à vérifier. |
| Bonne réponse | « C’est parfait. » | La vie est un long fleuve tranquille / français | [Dialogue répertorié](https://zonesons.com/vieux-films/la-vie-est-un-long-fleuve-tranquille-1988/277304). La page contient un extrait différent et des répliques voisines ; localiser la bonne réplique, sans supposer que le MP3 correspond. |
| Bonne réponse | « Bravo, Monsieur Tintin. » | Tintin et les Oranges bleues / français | [Dialogue répertorié](https://zonesons.com/films-d-aventure/tintin-et-les-oranges-bleues/479939). Localiser la réplique, pas le rire proposé en titre. |
| Mauvaise réponse, ironique | « C’est cela, oui. » | Le Père Noël est une ordure / français | [Attribution confirmée](https://www.allocine.fr/article/fichearticle_gen_carticle=1000056880.html). Ton sarcastique ; son négatif indispensable. |
| Bonne réponse | “That’s a bingo!” | Inglourious Basterds / anglais | [Transcription](https://www.script-o-rama.com/movie_scripts/a3/inglourious-basterds-script-transcript.html). Cette phrase est en anglais, même si l’acteur est germanophone. |
| Mauvaise réponse | “You shall not pass!” | The Lord of the Rings: The Fellowship of the Ring / anglais | [Réplique du film et différence avec le texte du livre](https://www.allocine.fr/article/fichearticle_gen_carticle=1000064794.html). Utiliser l’anglais original, pas « Vous ne passerez pas ». |

L’espagnol et l’allemand n’ont pas encore de candidat film suffisamment vérifié. Pour des réactions originales enregistrées par des humains, des textes courts et accessibles conviendraient : « ¡Muy bien! », « ¡Eso no! », « Ausgezeichnet! », « Nein, leider nicht! ». Ce sont des propositions de répliques nouvelles, sans attribution à un film.

## Préparer une banque réellement utilisable

Pour chaque fichier, garder le titre, l’année, la langue entendue, la citation, la source de l’audio, le minutage et la provenance/autorisation de réutilisation. Un lien vers une citation ou un MP3 disponible ne démontre pas à lui seul une permission de redistribution. Ne pas déposer d’extraits de films dans le dépôt tant que cette provenance n’est pas établie.

Découper des fichiers sources disponibles sans traduire ni recréer la voix d’un acteur. Conserver 150–220 ms d’amorce, normaliser le volume et supprimer uniquement le silence superflu. La banque doit être variée, éviter la même voix deux fois de suite et laisser la phrase finir avant de jouer la suivante.

## Effets originaux installés

Les effets sont créés localement par `build/generate-feedback-sounds.py` : buzzer à ressort avec oscillation amortie, réussite en accord majeur brillant, échec descendant sombre, finale distincte. Ces effets ne sont pas des extraits de films.


## Révision éditoriale du 14 octobre — humour et reconnaissance

La banque installée de 100 enregistrements n’atteint pas cet objectif : 95 sont des prononciations, sans scène ni chute. Ne pas augmenter leur nombre comme substitut à des dialogues. Les 46 phrases originales de `build/answer-reactions.json` restent le cahier des charges du ton : erreurs moquées, approbations incrédules ou sarcastiques.

Critères pour la prochaine banque : conserver le contexte audible et les respirations comiques, privilégier le français, multiplier films/personnages plutôt que mots équivalents, éviter la réverbération ajoutée, écouter sur les haut-parleurs réels. Le ping indique toujours le résultat avant une phrase ironique. Les durées ci-dessous sont des cibles de montage, pas des minutages mesurés. Aucun de ces nouveaux candidats n’est encore installé.

| Résultat | Candidat / scène à auditionner | Intérêt | Source |
|---|---|---|---|
| Correct | « Bonjour, Hubert, et bravo ! » — OSS 117 : Rio ne répond plus | Reconnaissance par le personnage, félicitation pince-sans-rire ; garder l’intonation complète. | https://zonesons.com/films-d-espionnage/oss-117-rio-ne-repond-plus/339445 |
| Correct, ironique | « Il a une belle tête de vainqueur » — Le Dîner de cons | Compliment à double sens, prolonger avec la chute du même échange après audition. | https://www.bleeps.wtf/bleep/LeDinerDeCons_UneBelleTeteDeVainqueur |
| Correct, absurde | « On est fort en pomme. » — Kaamelott | Fierté disproportionnée ; garder la pause comique, pas simplement le mot « fort ». | https://kaamelott.hypnoweb.net/kaamelott/la-bibliotheque/les-citations/citations-roi-burgonde.119.3119/ |
| Correct | “Impressive… most impressive.” — L’Empire contre-attaque | Approbation intimidante immédiatement reconnaissable ; anglais original. | https://quotations.pro/people/darth-vader/quote/impressive-most-impressive |
| Correct | “That’s a bingo!” — Inglourious Basterds | Garder la réponse de l’interlocuteur si elle donne une chute et tient dans 6–8 s. | https://www.script-o-rama.com/movie_scripts/a3/inglourious-basterds-script-transcript.html |
| Incorrect, sarcastique | « C’est cela, oui. » — Le Père Noël est une ordure | Exception courte justifiée par sa signature vocale ; conserver la pause et le mépris. | https://www.allocine.fr/article/fichearticle_gen_carticle=1000056880.html |
| Incorrect, absurde | Le raisonnement qui s’emmêle sur les mille personnes — La Cité de la peur | Un petit échange avec autocorrection ratée ; choisir une chute intelligible plutôt que toute la tirade. | https://fr.wikiquote.org/wiki/La_Cit%C3%A9_de_la_peur |
| Incorrect, mordant | « Les cons, ça ose tout… » — Les Tontons flingueurs | Très reconnaissable ; plus agressif que les réactions initiales, à garder hors sélection par défaut. | https://www.allocine.fr/diaporamas/cinema/diaporama-18705664/ |
| Incorrect | “You shall not pass!” — La Communauté de l’anneau | Refus théâtral, voix originale, sans prolonger l’effet musical. | https://www.allocine.fr/article/fichearticle_gen_carticle=1000064794.html |
| Incorrect, anime | « Omae wa mō shindeiru » puis la réaction de surprise — Hokuto no Ken | Mini-échange japonais reconnaissable, plus expressif qu’un « non » ; pas une traduction française. | https://www.youtube.com/watch?v=FOtX4IyRhE8 |
| Correct, anime | Le monologue de victoire intérieure de Light — Death Note, épisode 24 | Satisfaction excessive ; retrouver l’audio japonais original, la page ci-contre ne vérifie que l’épisode et une version anglaise. | https://www.youtube.com/watch?v=91tImTdOgV4 |

Ces références identifient une scène ou une attribution. Elles n’attestent ni un fichier de qualité ni une permission de redistribution. Vérifier séparément avant de remplacer les fichiers de la banque. Ne pas générer une imitation des voix des acteurs, ni installer une version doublée comme « langue originale ».

### Écho en debug

Depuis cette révision, activer le son sur un écran debug désactive les autres écrans debug ouverts sur la même origine. Recharger les anciens onglets pour qu’ils utilisent ce mécanisme. Cela corrige la double lecture ; cela ne retire pas une réverbération déjà présente dans un enregistrement. Une audition reste nécessaire pour identifier ce second cas.

### Notes résolues

Le bouton « Correction effectuée — archiver la note » conserve une copie dans `resolvedReviews`, efface le commentaire actif et le 0 « À réviser », conserve les notes de difficulté 1–5 et refuse d’effacer une note modifiée depuis son ouverture. Les mises à jour de packages ne doivent pas résoudre aveuglément toutes les notes : uniquement celles dont la correction a été vérifiée.
