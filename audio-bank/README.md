# Banque active : essai cinéma privé de 60 extraits

Le Pixel utilise maintenant **30 réactions positives et 30 négatives**, tirées de 22 films, séries et sketches : 50 en français, 8 en anglais, 2 en japonais. Les voix et langues originales sont conservées. Le passage burgonde dont la légende était incertaine a été remplacé par une réplique de Kaamelott sur la magie.

- Écouter et filtrer : `build/movie-audition/index.html`, ou `/tv/audio-credits` pendant une partie.
- Sélection éditoriale et découpes : `movie-reactions-selection.json`.
- Manifeste des fichiers préparés, sources, crédits et empreintes : `movie-preview.json`.
- Préparer : `python build/prepare-movie-audition.py` (outils audio et reconnaissance locale dans `build/`).
- Vérifier dans Chrome : `node build/check-movie-audition.cjs`.
- Installer : `python build/install-movie-audition.py --serial SERIAL` ; retirer le manifeste privé avec `--remove` puis relancer l’app pour revenir à la banque de secours.

Les fichiers audio de films restent dans `build/movie-audition/` et dans le stockage privé du Pixel. Ils ne sont ni publiés dans GitHub ni incorporés à l’APK. Aucun droit de redistribution n’est affirmé. Une fois installés, ils se lisent depuis le téléphone sans utiliser les fichiers du PC.

Le tirage épuise les 30 clips d’un résultat avant de répéter et privilégie une autre voix et une autre œuvre quand des alternatives restent disponibles. Les silences superflus sont retirés, le volume est normalisé et une amorce de 220 ms protège le début des mots ; aucune réverbération n’est ajoutée. Les coupes ont lieu avant l’ajout de cette amorce pour préserver la fin des phrases.

## Banque de secours incluse dans l’APK

50 bonnes réponses et 50 mauvaises réponses. Répartition : 70 français, 20 anglais, 5 espagnol, 5 allemand. 57 personnes et 60 expressions distinctes par langue/résultat.

Ouvrir **index.html** pour écouter les fichiers, filtrer et lancer une sélection de dix extraits. Les enregistrements sont réellement parlés par des personnes ; 95 sont des expressions de prononciation et 5 sont des réactions anglaises jouées par Tim Rockk. Ils ne constituent pas une banque de dialogues de films. Une grande partie des expressions reste neutre : écouter avant de considérer leur intonation comme une performance comique ou cinématographique.

Chaque fichier a une source, un crédit, une licence et un hash dans **reactions.json**. Les fichiers dérivés gardent leur licence d’origine, récapitulée dans **ATTRIBUTION.md**. La banque comporte des licences CC BY-SA 4.0, CC BY 4.0 et CC0. La banque de films privée est documentée séparément dans **MOVIE-REACTIONS.md** ; elle ne remplace pas ces fichiers licenciés dans l’APK.

Le traitement conserve la langue et la voix originales : conversion mono PCM 44,1 kHz, normalisation de volume, suppression du silence initial superflu et ajout de 220 ms d’amorce. Il n’y a ni synthèse, ni traduction, ni imitation d’acteur.

La sélection dans l’app utilise un sac de tirage par résultat : tous les fichiers d’un résultat passent avant de recommencer. Elle préfère une autre voix disponible et évite les six formulations récemment entendues. Une phrase peut exister dans plusieurs voix ; 100 fichiers ne signifie pas 100 textes différents.

Préparation : `python build/collect-human-reactions.py`, puis `python build/prepare-human-reactions.py`. Vérification et archive portable : `python build/validate-human-reactions.py`. Activation : `python build/activate-human-reactions.py`, puis compilation et tests Android. Respecter les limites du service source ; le collecteur emploie des dérivés audio compressés officiels et conserve un cache local.
