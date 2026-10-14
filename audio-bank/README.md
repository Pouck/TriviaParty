# Banque de 100 réactions humaines

50 bonnes réponses et 50 mauvaises réponses. Répartition : 70 français, 20 anglais, 5 espagnol, 5 allemand. 57 personnes et 60 expressions distinctes par langue/résultat.

Ouvrir **index.html** pour écouter les fichiers, filtrer et lancer une sélection de dix extraits. Les enregistrements sont réellement parlés par des personnes ; 95 sont des expressions de prononciation et 5 sont des réactions anglaises jouées par Tim Rockk. Ils ne constituent pas une banque de dialogues de films. Une grande partie des expressions reste neutre : écouter avant de considérer leur intonation comme une performance comique ou cinématographique.

Chaque fichier a une source, un crédit, une licence et un hash dans **reactions.json**. Les fichiers dérivés gardent leur licence d’origine, récapitulée dans **ATTRIBUTION.md**. La banque comporte des licences CC BY-SA 4.0, CC BY 4.0 et CC0. Les dialogues commerciaux recherchés restent des candidats textuels dans **MOVIE-REACTIONS.md**, avec permission de réutilisation à établir.

Le traitement conserve la langue et la voix originales : conversion mono PCM 44,1 kHz, normalisation de volume, suppression du silence initial superflu et ajout de 220 ms d’amorce. Il n’y a ni synthèse, ni traduction, ni imitation d’acteur.

La sélection dans l’app utilise un sac de tirage par résultat : tous les fichiers d’un résultat passent avant de recommencer. Elle préfère une autre voix disponible et évite les six formulations récemment entendues. Une phrase peut exister dans plusieurs voix ; 100 fichiers ne signifie pas 100 textes différents.

Préparation : `python build/collect-human-reactions.py`, puis `python build/prepare-human-reactions.py`. Vérification et archive portable : `python build/validate-human-reactions.py`. Activation : `python build/activate-human-reactions.py`, puis compilation et tests Android. Respecter les limites du service source ; le collecteur emploie des dérivés audio compressés officiels et conserve un cache local.
