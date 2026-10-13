# Exports historiques et données d’auteur

La bibliothèque actuelle, réorganisée en forfaits de **5 à 7 questions**, se trouve dans [game-library/current](../game-library/current/README.md).

Les archives de ce dossier sont conservées comme entrées des scripts d’auteur et références historiques. Certaines comportent des nombres de questions devenus obsolètes. Pour importer ou mettre à jour un forfait dans l’application, utilisez les ZIP du catalogue actuel, pas ces anciens exports.

Après une modification des données d’auteur : exécuter le générateur concerné, puis `python build/build-playable-library.py` pour reconstituer le catalogue actuel. Les sources finales modifiables et les images figurent sous `game-library/current/sources/<ID>/`.
