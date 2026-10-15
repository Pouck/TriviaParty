# Choix du buzzer

Ouvrir [buzzer-sampler.html](buzzer-sampler.html) pour écouter dix sons originaux. Le numéro 1 est le buzzer actuel. Un seul extrait joue à la fois ; le bouton Arrêter interrompt la lecture. Les fichiers sont inclus dans le projet et dans l’application.

Sur cet ordinateur : `node build/serve-buzzer-sampler.cjs`, puis http://127.0.0.1:18082/ . Quand une partie est préparée sur le téléphone, la même page est disponible à `/tv/buzzer-sampler` sur son serveur local (port 8080 ; via le transfert USB : http://127.0.0.1:18080/tv/buzzer-sampler).

L’écoute ne modifie pas encore le buzzer utilisé en partie. Indiquer le numéro choisi pour le remplacer. Régénération : `python build/prepare-buzzer-sampler.py`. Les dix signaux sont créés mathématiquement ; aucun extrait de film n’est utilisé.

## Réduction du délai

Le téléphone du joueur envoie le buzz au contact du doigt (pointerdown), tout en conservant le clic pour le clavier et les technologies d’assistance. Un seul envoi est autorisé jusqu’à la réponse du serveur. Le serveur décide du joueur retenu.

Le téléviseur précharge et décode le buzzer avant une pression, puis utilise Web Audio en mémoire, avec le mode de latence interactive. Si cette API n’est pas disponible ou si le préchargement échoue, la lecture audio habituelle reste disponible. Le bouton Activer le son déverrouille aussi le contexte Web Audio du navigateur.

Vérification : `node build/check-buzzer-sampler.cjs` valide le décodage des dix sons, une attaque de moins de 10 ms, la lecture exclusive, la mise en page téléphone et le déclenchement depuis le tampon décodé. Cela mesure le démarrage logiciel, pas le délai du réseau ni la sortie audio physique du téléviseur.
