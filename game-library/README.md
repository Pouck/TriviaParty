# Bibliothèque de jeu

Le catalogue importable actuel est dans [current](current/README.md). **Tous les forfaits contiennent de 5 à 7 questions**, y compris les six forfaits de diagnostic, exclus des tirages automatiques. Chaque forfait utilise un seul format de réponse.

- ZIP prêts à importer : `current/*.zip`.
- Sources JSON et images : `current/sources/<ID>/`.
- Inventaire des questions : [QUESTIONS-ET-REPONSES.csv](current/QUESTIONS-ET-REPONSES.csv).
- Regroupements et scissions : [CHANGEMENTS.csv](current/CHANGEMENTS.csv).
- Génération : `python build/build-playable-library.py`.
- Mise à jour directe du Pixel : `python build/install-tablet-packages.py --serial <identifiant adb>`.

L’installation applique la table de migration : les anciens petits/grands forfaits remplacés sont conservés en sauvegardes cachées sur le téléphone. Les identifiants de questions, leurs notes et leurs commentaires sont préservés. L’historique d’utilisation des nouvelles parties issues d’une scission hérite du forfait d’origine, lorsque celui-ci a déjà été joué.

Les dossiers de `package-examples` conservent les anciennes données d’auteur et les exports historiques. Ils servent à reconstruire les sources, mais leurs ZIP ne constituent plus la bibliothèque à installer.
