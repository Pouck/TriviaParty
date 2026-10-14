# Réactions vocales — pistes en langue originale

L’objectif est de remplacer les voix de synthèse plates par de véritables interprétations. Un scénario permet de trouver les mots ; il ne contient pas la piste sonore des acteurs. Cette liste est une sélection de candidats, pas une banque audio installée. Les enregistrements actuels restent en place.

## Mélange proposé

Environ 70 % de français, 20 % d’anglais, 5 % d’espagnol et 5 % d’allemand. Extraits parlés de 1–3 secondes, sans chanson, ni longue musique de fond. Conserver la langue réellement prononcée, indépendamment de la nationalité du film ou de l’acteur. Le son positif/négatif précède la voix pour rendre le résultat clair, même si la phrase est ironique.

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
