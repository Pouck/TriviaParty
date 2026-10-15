# Choix du buzzer

Ouvrir [buzzer-sampler.html](buzzer-sampler.html) pour écouter vingt sons originaux. Le numéro 1 est le buzzer actuel. Un seul extrait joue à la fois ; le bouton Arrêter interrompt la lecture. Les fichiers sont inclus dans le projet et dans l’application.

Sur cet ordinateur : `node build/serve-buzzer-sampler.cjs`, puis http://127.0.0.1:18082/ . Quand une partie est préparée sur le téléphone, la même page est disponible à `/tv/buzzer-sampler` sur son serveur local (port 8080 ; via le transfert USB : http://127.0.0.1:18080/tv/buzzer-sampler).

L’écoute ne modifie pas encore le buzzer utilisé en partie. Indiquer le numéro choisi pour le remplacer. Régénération : `python build/prepare-buzzer-sampler.py`. Les quarante signaux sont créés mathématiquement ; aucun extrait de film n’est utilisé.

## Réduction du délai

Le téléphone du joueur envoie le buzz au contact du doigt (pointerdown), tout en conservant le clic pour le clavier et les technologies d’assistance. Un seul envoi est autorisé jusqu’à la réponse du serveur. Le serveur décide du joueur retenu.

Le téléviseur précharge et décode le buzzer avant une pression, puis utilise Web Audio en mémoire, avec le mode de latence interactive. Si cette API n’est pas disponible ou si le préchargement échoue, la lecture audio habituelle reste disponible. Le bouton Activer le son déverrouille aussi le contexte Web Audio du navigateur.

Vérification : `node build/check-buzzer-sampler.cjs` valide le décodage des quarante sons, une attaque de moins de 10 ms, la lecture exclusive, la mise en page téléphone et le déclenchement depuis le tampon décodé. Cela mesure le démarrage logiciel, pas le délai du réseau ni la sortie audio physique du téléviseur.


## Sons de bonne réponse

[success-sampler.html](success-sampler.html) propose vingt effets de réussite : cloches, carillons, marimba, fanfares et bonus arcade. Le numéro 1 reproduit `good-ping.wav`, le son actuellement joué avant une réaction vocale. Aucun de ces effets n’utilise d’extrait de film. La sélection définitive reste à faire après écoute.

Sur cet ordinateur : http://127.0.0.1:18082/success-sampler.html . Sur le serveur du téléphone : `/tv/success-sampler` ou `/tv/success-sampler.html`.

## Cue immédiat du moniteur de débogage

Lorsqu’un buzz est accepté, le serveur envoie un petit message public `buzzer` contenant uniquement la version, la salle et l’identifiant du son. Cet envoi passe indépendamment de la file des états complets. La page de débogage le joue sans reconstruire l’écran et ne rejoue pas le même buzz lorsque l’état complet arrive ensuite, même si un ancien état s’intercale. Le test réseau maintient volontairement la file des états bloquée pour vérifier ce chemin.

Cette amélioration concerne le moniteur de débogage. Le délai audio du téléviseur réel n’a pas été mesuré. Le buzzer du joueur attend toujours la décision du serveur pour déterminer qui a la parole ; les autres pressions ne sont pas conservées dans une file d’attente.
