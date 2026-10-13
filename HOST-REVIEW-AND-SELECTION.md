# Commentaires et sélection des forfaits

Le téléviseur joue désormais une réaction parlée aléatoire à chaque nouveau résultat, avec une banque de 46 enregistrements et cinq voix (français, anglais, allemand et russe). La même réaction n’est pas tirée deux fois de suite. Une coche verte ou une croix rouge apparaît pendant 2,2 secondes au-dessus du panneau de question, sans déplacer son contenu. Un son de buzzer accompagne la prise de parole acceptée ; les appuis suivants pendant cette prise de parole ne rejouent pas le son. Se reconnecter au téléviseur ne rejoue pas les anciens résultats ou buzzers. Les voix sont embarquées dans l’application : aucun service de synthèse n’est nécessaire pendant la partie.

Dans l’écran TV de débogage, cliquer **Activer le son** après l’ouverture ou le rechargement. La voix dit « Le son est activé ! », puis le bouton disparaît. Ce clic autorise le navigateur à lire les sons automatiquement. Si la lecture est bloquée ou échoue, le bouton réapparaît. Les sons passent par la même adresse que la page de débogage, y compris lors d’un transfert USB sur `localhost`. Le téléphone hôte n’émet plus le petit bip qui pouvait être confondu avec le son du téléviseur.

Chaque réaction vocale est précédée d’un court son positif ou négatif, lu en entier avant la voix. Une fanfare distincte marque l’arrivée au classement final ; elle ne se répète ni pendant les mises à jour du classement ni lors d’une connexion tardive.

Pour les choix multiples (y compris les choix A/B/C/D sur une carte), la carte d’équipe sur le téléviseur devient verte ou rouge dès la sélection définitive. Une équipe sans réponse reste bleue. Les points sont attribués à la révélation comme auparavant et les couleurs sont effacées à la question suivante.

Le catalogue courant se trouve dans `game-library/current`. Tous les forfaits contiennent désormais **5 à 7 questions** et l’importation refuse les autres tailles. Les anciens exports de `package-examples` servent d’archives de rédaction. Les regroupements et divisions conservent les identifiants des questions, donc leurs notes. Les forfaits de diagnostic restent exclus des tirages ordinaires.

## Commenter une question

Pendant une partie, **NOTE** ouvre une fenêtre privée pour la question courante. Saisissez un commentaire, choisissez éventuellement une difficulté de **1 (facile) à 5 (difficile)**, puis **Enregistrer**. **0 — À réviser** est un signalement distinct, pas une difficulté. Toucher une note déjà sélectionnée la retire. La fenêtre n’est pas diffusée au téléviseur et ne met pas automatiquement le chrono en pause ; utilisez PAUSE si nécessaire.

Dans la sélection des forfaits, **Questions à revoir** affiche les notes enregistrées et permet de les modifier. **Exporter commentaires et statistiques** crée un fichier JSON à l’emplacement choisi. Les données sont enregistrées dans `files/host-review.json` sur le téléphone hôte, indépendamment des ZIP. Une mise à jour conservant les identifiants des questions conserve leurs commentaires.

## Sélection

Dans **Questions à revoir**, le filtre **À réviser** affiche uniquement les questions enregistrées avec la note 0. Les notes de difficulté 1–5 restent séparées de ce signalement. Les commentaires et signalements sont conservés lors d’une mise à jour des forfaits.

La page ouvre sur le tirage aléatoire. Le sélecteur en haut permet de changer de parcours ; seuls les contrôles du parcours choisi apparaissent. Les sujets sont regroupés sur plusieurs colonnes, selon la largeur de l’écran. Les forfaits tirés peuvent être affichés ou masqués avec « Voir les forfaits ». L’importation, la gestion, la revue des questions, l’exportation et la réinitialisation sont dans le menu **Outils**.

- **Choix manuel** : sélectionner les forfaits comme auparavant.
- **Tous les forfaits** : sélectionner toute la bibliothèque disponible, sauf tests et démonstrations.
- **Nombre aléatoire** : saisir le nombre souhaité, puis **TIRER LES FORFAITS**. Un autre tirage permet de renouveler la proposition avant de commencer.
- **Par sujets** : choisir plusieurs sujets, puis **TIRER LES FORFAITS**. Un forfait est choisi pour chaque sujet ; l’algorithme varie les formats parmi les possibilités disponibles.

Les tirages privilégient les forfaits les moins joués, puis la diversité des sujets et formats, puis les dernières utilisations les plus anciennes. Les égalités sont départagées aléatoirement. L’ordre de jeu mélange ensuite sujets et formats. Une bibliothèque ou un choix restreint peut limiter l’équilibre possible.

Les forfaits dont l’identifiant ou le nom contient le mot TEST, TESTS, DÉMO ou DÉMONSTRATION sont exclus de toutes les sélections automatiques. Ils restent accessibles en choix manuel. L’ancienne option « Connecter l’arbitre privé » a été retirée.

Le compteur d’un forfait augmente lorsque sa première question est effectivement jouée. Une simple sélection ou un tirage ne compte pas. Chaque forfait compte une seule fois par partie, même après reconnexion de l’hôte. **Réinitialiser les statistiques** efface les compteurs et dates d’utilisation sans effacer les commentaires. Ces statistiques concernent ce téléphone hôte.

## Vote des joueurs

Choisir **Vote des joueurs**, puis le nombre de catégories (5 par défaut) et le nombre de forfaits par catégorie (1 par défaut). Ici, une catégorie de vote correspond à un sujet de la bibliothèque : Musique, Nature, Histoire, etc. Seuls les sujets disposant du nombre demandé de forfaits sont proposés. Le nombre de catégories est limité au nombre de sujets disponibles.

**Ouvrir le salon** permet aux joueurs de rejoindre avant le vote ; le QR apparaît sur la TV. Quand les équipes sont prêtes, l’hôte appuie sur **OUVRIR LE VOTE**. Chaque équipe peut sélectionner jusqu’au nombre de places disponibles et confirmer son vote. Elle peut le modifier tant que le vote reste ouvert. Une équipe compte une fois par sujet ; les votes sont liés à son identité et conservés après reconnexion.

L’hôte ferme le vote. Les sujets au-dessus du seuil sont retenus. Si une égalité à la dernière place dépasse le nombre demandé, seuls les sujets concernés sont revotés pour les places restantes. En cas de nouvelle égalité, l’hôte choisit exactement le nombre restant de sujets. Les abstentions sont autorisées et peuvent produire une égalité à zéro vote.

Les forfaits des sujets gagnants sont ensuite tirés avec priorité aux moins joués et diversité des formats. La partie garde les équipes connectées, leurs identités et le même salon. L’hôte peut alors commencer. Les tests et démonstrations restent exclus.

## Révision solo

Choisir **Révision solo**, sélectionner les forfaits à revoir et commencer. La question et les choix s’affichent sur le téléphone hôte, sans autre joueur ni chrono. Une réponse QCM révèle immédiatement la solution ; les chronologies utilisent les cartes à déplacer. Pour les réponses orales, révéler la solution puis indiquer si sa réponse était correcte. Les indices de « Qui suis-je ? » sont révélés manuellement.

Après révélation, la difficulté et le commentaire sont disponibles sous la réponse. Ils sont enregistrés en passant à la question suivante ou en fermant, ou avec **Enregistrer maintenant**. La révision ne modifie pas les compteurs d’utilisation des forfaits. Les notes utilisent les mêmes identifiants et le même fichier que NOTE et Questions à revoir.

## Sons

Deux signaux originaux courts accompagnent les jugements de réponse : positif et négatif. Pour les réponses simultanées, un son positif indique qu’au moins une réponse est correcte ; sinon un son négatif accompagne les réponses incorrectes soumises. Les jugements oraux produisent leur propre signal. Les ticks et les reconnexions ne rejouent pas un ancien son.

Les sons passent par le téléviseur lorsque Cast est connecté, sinon par le téléphone hôte ; la révision solo utilise le téléphone. Le volume dépend du volume multimédia de l’appareil. Un navigateur de prévisualisation peut demander une interaction préalable avant d’autoriser le son.

## Correction d’image

La question sur le cheval de Lucky Luke utilise l’illustration réelle de Jolly Jumper provenant de la page personnages de Dargaud, créditée dans le ZIP. L’image conserve les droits de ses ayants droit. Les autres illustrations symboliques restent des indices de contexte, plutôt que des représentations exactes d’objets de fiction ; elles peuvent être signalées avec NOTE pour une révision ciblée.

Validation : tests Android et navigateur, vote avec égalité sur le Pixel, révision solo contrôlée sur le Pixel ; les trois écrans de vote tiennent à 1920 × 1080 avec 17 sujets.

Les nouveaux enregistrements ont une amorce silencieuse de 220 ms pour éviter de couper le premier mot. Les réactions sont mises en file et ne sont plus interrompues par le passage à la question suivante. Voir [Réponses écrites et lecture confirmée](game-library/WRITTEN-AND-READY.md).
