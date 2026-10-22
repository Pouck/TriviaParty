# Banque cinéma privée : 100 extraits préparés

La sélection comporte **50 réactions positives et 50 négatives**, comprenant 90 répliques de 30 œuvres et 10 réactions humaines courtes : 88 extraits en français, 10 en anglais et 2 en japonais. L’expansion du 15 octobre 2026 ajoute 16 extraits sans modifier les 72 fichiers précédents ni leurs annotations. Deux répliques James Bond approuvées ont ensuite été intégrées : « Perfect. Cheers. » et « Well done. Congratulations. ». La sélection classique complète est approuvée ; 19 autres lignes attendent encore leur audio (voir `CLASSIC-REACTIONS.md`). Certaines additions sont des versions françaises de films ou séries étrangers ; les voix ne sont ni synthétisées ni imitées.

- Écouter et filtrer : `../build/movie-audition/index.html`.
- Sélection, sources et découpes : `movie-reactions-selection.json`.
- Manifeste, durées et empreintes : `movie-preview.json`.
- Annoter : `REACTIONS-A-ANNOTER.md`. Les 16 ajouts sont « à vérifier » et restent exclus du filtre tout public jusqu’à votre décision.
- Préparer : `python build/prepare-movie-audition.py`.
- Vérifier dans Chrome : `node build/check-movie-audition.cjs`.
- Installer : `python build/install-movie-audition.py --serial SERIAL`, puis relancer l’application. La préparation seule ne change pas la banque du téléphone.

Les médias restent dans `build/movie-audition/` ; ils ne sont ni publiés dans GitHub ni incorporés à l’APK. Aucun droit de redistribution n’est affirmé. Après installation, la lecture utilise le stockage privé du téléphone.

Les réactions courtes (« bravo », « génial », « super », « exact », « faux », « raté », « dommage », « erreur », « non », « presque ») sont mêlées au tirage des répliques. Leurs enregistrements, licences et crédits sont conservés sans modification ; les crédits sont aussi affichés sur la page d’écoute.

Le tirage épuise les clips d’un résultat avant de répéter et privilégie une autre voix et une autre œuvre. Le volume est normalisé et une amorce de 220 ms protège le début des mots. Les nouveaux extraits ont été décodés et confrontés aux légendes sources par reconnaissance vocale locale ; une écoute humaine reste à faire, notamment pour les dialogues bruités ou les échanges à plusieurs voix.

## Banque de secours incluse dans l’APK

50 bonnes réponses et 50 mauvaises réponses. Répartition : 70 français, 20 anglais, 5 espagnol, 5 allemand. 57 personnes et 60 expressions distinctes par langue/résultat.

Ouvrir **index.html** pour écouter les fichiers, filtrer et lancer une sélection de dix extraits. Les enregistrements sont réellement parlés par des personnes ; 95 sont des expressions de prononciation et 5 sont des réactions anglaises jouées par Tim Rockk. Ils ne constituent pas une banque de dialogues de films. Une grande partie des expressions reste neutre : écouter avant de considérer leur intonation comme une performance comique ou cinématographique.

Chaque fichier a une source, un crédit, une licence et un hash dans **reactions.json**. Les fichiers dérivés gardent leur licence d’origine, récapitulée dans **ATTRIBUTION.md**. La banque comporte des licences CC BY-SA 4.0, CC BY 4.0 et CC0. La banque de films privée est documentée séparément dans **MOVIE-REACTIONS.md** ; elle ne remplace pas ces fichiers licenciés dans l’APK.

Le traitement conserve la langue et la voix originales : conversion mono PCM 44,1 kHz, normalisation de volume, suppression du silence initial superflu et ajout de 220 ms d’amorce. Il n’y a ni synthèse, ni traduction, ni imitation d’acteur.

La sélection dans l’app utilise un sac de tirage par résultat : tous les fichiers d’un résultat passent avant de recommencer. Elle préfère une autre voix disponible et évite les six formulations récemment entendues. Une phrase peut exister dans plusieurs voix ; 100 fichiers ne signifie pas 100 textes différents.

Préparation : `python build/collect-human-reactions.py`, puis `python build/prepare-human-reactions.py`. Vérification et archive portable : `python build/validate-human-reactions.py`. Activation : `python build/activate-human-reactions.py`, puis compilation et tests Android. Respecter les limites du service source ; le collecteur emploie des dérivés audio compressés officiels et conserve un cache local.
