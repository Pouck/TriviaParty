# Affichage de l’hôte et questions à mettre en ordre

- Images : environ deux tiers de la largeur disponible, et toute la hauteur de l’écran intérieur dès le bord supérieur, avec proportions conservées. Le numéro de question et les contrôles restent dans le tiers droit ; aucune bande de titre ne réduit la hauteur de la carte.
- Questions sans image : titre aligné avec JOINDRE / SCORE / FIN, choix multiples en grille de deux colonnes. Les événements des questions à mettre en ordre sont affichés dans leur liste initiale fixe.
- Choix redondants : les permutations des chronologies à choix multiples ne sont pas répétées lorsque les événements figurent déjà dans la question. Les simples lettres A/B/C/D des cartes ne sont pas répétées non plus. Les options restent disponibles sur les téléphones ; les choix comportant des noms ou d’autres informations restent visibles aux spectateurs.
- Buzzer : nom de l’équipe ayant la parole mis en évidence au-dessus de la question, avec compte à rebours de réponse. Les boutons de jugement restent visibles.
- Mises : équipes en deux colonnes ; les commandes restent au bas de l’écran. Une longue liste peut défiler dans sa propre zone.
- Révélation : réponse et classement dans deux panneaux séparés. Le classement des trois premiers et des ex æquo reste visible pendant la lecture de la réponse ; seule sa propre liste peut défiler s’il y a beaucoup d’ex æquo.
- Les boutons JOINDRE / SCORE / FIN mesurent 30 dp de hauteur avec des libellés de 10 sp. Les titres réservent 180 dp à droite pour éviter le chevauchement. Les réponses révélées utilisent 20 sp sur l’hôte. En chronologie, le texte introductif est réduit au sujet, sans répéter les événements ; les réponses des questions à mettre en ordre sont présentées en liste numérotée.
- Téléviseur : image agrandie, choix visibles, événements fixes et classement à lignes compactes. `cast-receiver/` et les ressources TV de l’APK sont synchronisés. Un récepteur Cast hébergé séparément doit être mis à jour avec ces fichiers pour profiter de cette mise en page ; le téléviseur local `/tv` utilise immédiatement les ressources du nouvel APK.

## Téléphones et mise en ordre

Les cartes se déplacent en glissant la poignée ↕ vers le haut ou le bas. Des flèches ↑ / ↓ offrent le même résultat sans glissement. **ENVOYER L’ORDRE** verrouille l’ordre final ; le déplacement seul transmet un brouillon privé et ne termine pas la réponse. La reconnexion peut restaurer le brouillon déjà reçu par l’hôte. Aucun buzzer n’apparaît pour ce format.

Le protocole transmet uniquement les identifiants et les textes des événements au joueur. Il n’envoie ni le texte de la question, ni la chronologie correcte. Les brouillons des autres équipes restent privés. Le barème de mise en ordre existant exige la chronologie complète correcte.

Les forfaits grecs et romains révisés sont dans `package-examples/histoire-antique-2026-10-10/`. Leurs IDs sont inchangés pour permettre une mise à jour. Les forfaits canadiens gardent le format à choix multiples.
