# Bibliothèque actuelle — 5 à 7 questions par forfait

248 forfaits ; 1303 questions ; chaque forfait contient **5, 6 ou 7 questions**. Les six forfaits de diagnostic ont cinq questions chacun et restent exclus des tirages automatiques.

55 forfaits à réponses écrites coexistent avec les versions orales. Les choix multiples utilisent 15 points, puis −1 point par seconde dans un seul sablier. Les joueurs confirment la lecture avant chaque indice de Qui suis-je.

Cette bibliothèque remplace les anciennes archives courtes ou longues de `package-examples`. Utiliser les ZIP de ce dossier pour importer ou mettre à jour. Les anciennes archives sont conservées comme sources et références historiques ; elles ne représentent plus le catalogue proposé sur le Pixel.

## Réorganisation

- Architecture : cinq forfaits de trois indices regroupés en trois forfaits de cinq, sans ajouter ni supprimer de question.
- Arts et cinéma : les séries de huit deviennent des séries de six ; les questions restantes forment quatre nouveaux forfaits de six.
- Canada et QCM littéraires : les onze forfaits de dix sont scindés en deux forfaits de cinq.
- Géographie : regroupement des cartes régionales en 5/6/6 ; eaux et paysages en deux séries de six ; capitales en deux séries de sept ; fleuves en deux séries de six.
- Antiquité, mythologie et littérature : regroupement par tradition et format, avec neuf nouveaux portraits accessibles ; les versions d’un même personnage sont réparties entre les forfaits.
- Histoire : regroupement des QCM mondiaux en trois séries de sept ; États-Unis en six/sept ; compléments courts pour Renaissance, Révolution et chronologie américaine.
- Les ensembles originaux deviennent homogènes : les chronologies de jeux rejoignent les repères BD ; les QCM restent dans deux ensembles distincts de six et sept.
- Diagnostic : six forfaits homogènes de cinq exemples, toujours exclus des sélections automatiques ; les compléments de test sont des copies identifiées de questions existantes.

20 nouvelles questions courtes complètent les pools qui ne pouvaient pas être répartis proprement ; 20 copies supplémentaires servent uniquement aux diagnostics. Les 1263 anciens identifiants de questions sont tous conservés. Les notes restent liées aux questions, même lorsque leur forfait ou leur titre change. Les images et leurs clés sont déplacées avec les questions. Les rébus incomplets de l’exemple Charades ont été remplacés par une charade textuelle complète, puis quatre charades accessibles ont été ajoutées.

## Sources modifiables et inventaire

[Questions et réponses](QUESTIONS-ET-REPONSES.csv) · [Répartition des anciennes séries](CHANGEMENTS.csv) · [Catalogue](CATALOGUE.json) · [Migration](MIGRATION.json).

Les JSON et images prêts à éditer sont dans `sources/<ID>/`. Les références propres à chaque question sont dans `VERIFICATION.json`. Les ajouts sont rédigés dans `build/library-size-supplements.py`. Reconstituer le catalogue : `python build/build-playable-library.py`. Ce script utilise les exports historiques comme entrées ; une correction durable doit aussi être reportée dans les données d’auteur correspondantes.

## Forfaits

| Sujet | Forfait | Questions | Archive |
|---|---|---:|---|
| Architecture | Architecture — Reconnaissance — Europe — Réponses écrites | 6 | [architecture-buzzer-europe-20261011.zip](architecture-buzzer-europe-20261011.zip) |
| Architecture | Architecture — Reconnaissance — Icônes modernes — Buzzer | 6 | [architecture-buzzer-moderne-20261011.zip](architecture-buzzer-moderne-20261011.zip) |
| Architecture | Architecture — Reconnaissance — Sites historiques — Buzzer | 6 | [architecture-buzzer-monde-20261011.zip](architecture-buzzer-monde-20261011.zip) |
| Architecture | Architecture — Asie et Proche-Orient — QCM | 6 | [architecture-qcm-asie-orient-20261011.zip](architecture-qcm-asie-orient-20261011.zip) |
| Architecture | Architecture — Monuments d’Europe — QCM | 6 | [architecture-qcm-europe-20261011.zip](architecture-qcm-europe-20261011.zip) |
| Architecture | Architecture — Architecture moderne — QCM | 6 | [architecture-qcm-moderne-20261011.zip](architecture-qcm-moderne-20261011.zip) |
| Architecture | Architecture — Merveilles historiques — Qui suis-je ? | 5 | [architecture-qsj-antiquite-20261011.zip](architecture-qsj-antiquite-20261011.zip) |
| Architecture | Architecture — Monuments emblématiques — Qui suis-je ? | 5 | [architecture-qsj-modernes-20261011.zip](architecture-qsj-modernes-20261011.zip) |
| Architecture | Architecture — Palais et lieux d’exception — Qui suis-je ? écrit | 5 | [architecture-qsj-palais-20261011.zip](architecture-qsj-palais-20261011.zip) |
| Arts | Arts — Marbre et bronze — Réponses écrites | 6 | [arts-buzzer-marbre-bronze-20261011.zip](arts-buzzer-marbre-bronze-20261011.zip) |
| Arts | Arts — Regards et scènes — Buzzer | 6 | [arts-buzzer-regards-scenes-20261011.zip](arts-buzzer-regards-scenes-20261011.zip) |
| Arts | Arts — Œuvres et artistes — Réponses écrites | 6 | [arts-buzzer-selection-variee-20261012.zip](arts-buzzer-selection-variee-20261012.zip) |
| Arts | Arts — Tableaux célèbres — Buzzer | 6 | [arts-buzzer-tableaux-celebres-20261011.zip](arts-buzzer-tableaux-celebres-20261011.zip) |
| Arts | Arts — Peintures dans le temps — Chronologie | 6 | [arts-chronologie-peintures-dans-le-temps-20261011.zip](arts-chronologie-peintures-dans-le-temps-20261011.zip) |
| Arts | Arts — Sculptures et repères — Chronologie | 6 | [arts-chronologie-sculptures-reperes-20261011.zip](arts-chronologie-sculptures-reperes-20261011.zip) |
| Arts | Arts — Couleurs et mouvements — QCM | 6 | [arts-qcm-couleurs-mouvements-20261011.zip](arts-qcm-couleurs-mouvements-20261011.zip) |
| Arts | Arts — Peintures classiques — QCM | 6 | [arts-qcm-peintures-classiques-20261011.zip](arts-qcm-peintures-classiques-20261011.zip) |
| Arts | Arts — Sculptures iconiques — QCM | 6 | [arts-qcm-sculptures-iconiques-20261011.zip](arts-qcm-sculptures-iconiques-20261011.zip) |
| Arts | Arts — Œuvres et artistes — QCM | 6 | [arts-qcm-selection-variee-20261012.zip](arts-qcm-selection-variee-20261012.zip) |
| Arts | Arts — Peintures mystères — Qui suis-je ? écrit | 5 | [arts-qsj-peintures-mysteres-20261011.zip](arts-qsj-peintures-mysteres-20261011.zip) |
| Arts | Arts — Sculptures mystères — Qui suis-je ? | 5 | [arts-qsj-sculptures-mysteres-20261011.zip](arts-qsj-sculptures-mysteres-20261011.zip) |
| Histoire | Canada — Culture et institutions — Réponses écrites — 1 | 5 | [canada-buzzer-culture-20261011.zip](canada-buzzer-culture-20261011.zip) |
| Histoire | Canada — Culture et institutions — Buzzer — 2 | 5 | [canada-buzzer-culture-20261011-part-2.zip](canada-buzzer-culture-20261011-part-2.zip) |
| Histoire | Canada — Premières et repères historiques — Buzzer — 1 | 5 | [canada-buzzer-premieres-20261011.zip](canada-buzzer-premieres-20261011.zip) |
| Histoire | Canada — Premières et repères historiques — Buzzer — 2 | 5 | [canada-buzzer-premieres-20261011-part-2.zip](canada-buzzer-premieres-20261011-part-2.zip) |
| Géographie | Canada — Géographie et symboles — Buzzer — 1 | 5 | [canada-buzzer-symboles-20261011.zip](canada-buzzer-symboles-20261011.zip) |
| Géographie | Canada — Géographie et symboles — Buzzer — 2 | 5 | [canada-buzzer-symboles-20261011-part-2.zip](canada-buzzer-symboles-20261011-part-2.zip) |
| Géographie | Géographie du Canada — Sites et plans d’eau — Réponses écrites | 5 | [canada-geo-buzzer-sites-20261011.zip](canada-geo-buzzer-sites-20261011.zip) |
| Géographie | Géographie du Canada — Villes et provinces | 5 | [canada-geo-buzzer-villes-20261011.zip](canada-geo-buzzer-villes-20261011.zip) |
| Géographie | Géographie du Canada — Eaux, îles et climat | 6 | [canada-geo-qcm-eaux-climat-20261011.zip](canada-geo-qcm-eaux-climat-20261011.zip) |
| Géographie | Géographie du Canada — Géographie politique et humaine | 6 | [canada-geo-qcm-humaine-20261011.zip](canada-geo-qcm-humaine-20261011.zip) |
| Géographie | Géographie du Canada — Relief et extrêmes | 6 | [canada-geo-qcm-relief-20261011.zip](canada-geo-qcm-relief-20261011.zip) |
| Sciences | Inventions canadiennes — Médecine et percées vitales | 6 | [canada-inventions-medical-20261011.zip](canada-inventions-medical-20261011.zip) |
| Sciences | Inventions canadiennes — Sports, culture et vie quotidienne | 6 | [canada-inventions-quotidien-20261011.zip](canada-inventions-quotidien-20261011.zip) |
| Sciences | Inventions canadiennes — Transport, technologie et communication | 6 | [canada-inventions-technologie-20261011.zip](canada-inventions-technologie-20261011.zip) |
| Histoire | Canada — Époque coloniale et évolution constitutionnelle — QCM — 1 | 5 | [canada-qcm-colonial-20261011.zip](canada-qcm-colonial-20261011.zip) |
| Histoire | Canada — Époque coloniale et évolution constitutionnelle — QCM — 2 | 5 | [canada-qcm-colonial-20261011-part-2.zip](canada-qcm-colonial-20261011-part-2.zip) |
| Histoire | Canada — Guerres et relations internationales — QCM — 1 | 5 | [canada-qcm-international-20261011.zip](canada-qcm-international-20261011.zip) |
| Histoire | Canada — Guerres et relations internationales — QCM — 2 | 5 | [canada-qcm-international-20261011-part-2.zip](canada-qcm-international-20261011-part-2.zip) |
| Histoire | Canada — Jalons sociaux et politiques modernes — QCM — 1 | 5 | [canada-qcm-moderne-20261011.zip](canada-qcm-moderne-20261011.zip) |
| Histoire | Canada — Jalons sociaux et politiques modernes — QCM — 2 | 5 | [canada-qcm-moderne-20261011-part-2.zip](canada-qcm-moderne-20261011-part-2.zip) |
| Histoire | Qui suis-je ? écrit — Canada — Bâtisseurs et premières époques | 5 | [canada-qsj-batisseurs-20261011.zip](canada-qsj-batisseurs-20261011.zip) |
| Histoire | Qui suis-je ? écrit — Canada — Figures du XXe siècle | 5 | [canada-qsj-icones-20261011.zip](canada-qsj-icones-20261011.zip) |
| Logique et énigmes | Logique et énigmes — Charades — Buzzer | 5 | [charades.zip](charades.zip) |
| Cinéma | Cinéma — France et Québec — Rapide — Buzzer | 6 | [cinema-buzzer-france-quebec-20261011.zip](cinema-buzzer-france-quebec-20261011.zip) |
| Cinéma | Cinéma — Personnages et grands univers — Buzzer | 6 | [cinema-buzzer-selection-variee-20261012.zip](cinema-buzzer-selection-variee-20261012.zip) |
| Cinéma | Cinéma — Titres et héros — Rapide — Réponses écrites | 6 | [cinema-buzzer-titres-heros-20261011.zip](cinema-buzzer-titres-heros-20261011.zip) |
| Cinéma | Cinéma — Univers et animation — Rapide — Réponses écrites | 6 | [cinema-buzzer-univers-20261011.zip](cinema-buzzer-univers-20261011.zip) |
| Cinéma | Cinéma — Sorties de films — Repères — Chronologie | 6 | [cinema-chronologie-reperes-20261011.zip](cinema-chronologie-reperes-20261011.zip) |
| Cinéma | Cinéma — Sorties de films — Sagas et studios — Chronologie | 6 | [cinema-chronologie-sagas-20261011.zip](cinema-chronologie-sagas-20261011.zip) |
| Cinéma | Cinéma — Réalisateurs, musique et animation — QCM | 6 | [cinema-qcm-coulisses-20261011.zip](cinema-qcm-coulisses-20261011.zip) |
| Cinéma | Cinéma — Films et personnages — QCM | 6 | [cinema-qcm-films-personnages-20261011.zip](cinema-qcm-films-personnages-20261011.zip) |
| Cinéma | Cinéma — Récompenses et classiques — QCM | 6 | [cinema-qcm-prix-classiques-20261011.zip](cinema-qcm-prix-classiques-20261011.zip) |
| Cinéma | Cinéma — Personnages et grands univers — QCM | 6 | [cinema-qcm-selection-variee-20261012.zip](cinema-qcm-selection-variee-20261012.zip) |
| Cinéma | Cinéma — Cinéastes et personnages — Qui suis-je ? écrit | 5 | [cinema-qsj-figures-20261011.zip](cinema-qsj-figures-20261011.zip) |
| Cinéma | Cinéma — Films à découvrir — Qui suis-je ? écrit | 5 | [cinema-qsj-films-20261011.zip](cinema-qsj-films-20261011.zip) |
| Littérature | Littérature américaine — Œuvres : choix multiples — 1 | 5 | [culture-qcm-americaine-oeuvres-20261010.zip](culture-qcm-americaine-oeuvres-20261010.zip) |
| Littérature | Littérature américaine — Œuvres : choix multiples — 2 | 5 | [culture-qcm-americaine-oeuvres-20261010-part-2.zip](culture-qcm-americaine-oeuvres-20261010-part-2.zip) |
| Littérature | Littérature britannique et irlandaise — Œuvres : choix multiples — 1 | 5 | [culture-qcm-anglophone-oeuvres-20261010.zip](culture-qcm-anglophone-oeuvres-20261010.zip) |
| Littérature | Littérature britannique et irlandaise — Œuvres : choix multiples — 2 | 5 | [culture-qcm-anglophone-oeuvres-20261010-part-2.zip](culture-qcm-anglophone-oeuvres-20261010-part-2.zip) |
| Littérature | Littérature britannique et irlandaise — Personnages : choix multiples — 1 | 5 | [culture-qcm-anglophone-personnages-20261010.zip](culture-qcm-anglophone-personnages-20261010.zip) |
| Littérature | Littérature britannique et irlandaise — Personnages : choix multiples — 2 | 5 | [culture-qcm-anglophone-personnages-20261010-part-2.zip](culture-qcm-anglophone-personnages-20261010-part-2.zip) |
| Littérature | Littérature française — Œuvres : choix multiples — 1 | 5 | [culture-qcm-francaise-oeuvres-20261010.zip](culture-qcm-francaise-oeuvres-20261010.zip) |
| Littérature | Littérature française — Œuvres : choix multiples — 2 | 5 | [culture-qcm-francaise-oeuvres-20261010-part-2.zip](culture-qcm-francaise-oeuvres-20261010-part-2.zip) |
| Littérature | Littérature française — Personnages : choix multiples — 1 | 5 | [culture-qcm-francaise-personnages-20261010.zip](culture-qcm-francaise-personnages-20261010.zip) |
| Littérature | Littérature française — Personnages : choix multiples — 2 | 5 | [culture-qcm-francaise-personnages-20261010-part-2.zip](culture-qcm-francaise-personnages-20261010-part-2.zip) |
| Histoire | Qui suis-je ? écrit — Grèce antique — Figures et lieux | 5 | [culture-qsj-grece-figures-et-lieux-20261010.zip](culture-qsj-grece-figures-et-lieux-20261010.zip) |
| Histoire | Qui suis-je ? — Grèce antique — Grandes figures | 5 | [culture-qsj-grece-grandes-figures-20261010.zip](culture-qsj-grece-grandes-figures-20261010.zip) |
| Littérature | Littérature américaine — Œuvres et personnages — Qui suis-je ? écrit — 1 | 5 | [culture-qsj-litterature-americaine-oeuvres-20261010.zip](culture-qsj-litterature-americaine-oeuvres-20261010.zip) |
| Littérature | Littérature américaine — Œuvres et personnages — Qui suis-je ? — 2 | 5 | [culture-qsj-litterature-americaine-personnages-20261010.zip](culture-qsj-litterature-americaine-personnages-20261010.zip) |
| Littérature | Littérature britannique et irlandaise — Œuvres et personnages — Qui suis-je ? — 1 | 5 | [culture-qsj-litterature-anglophone-oeuvres-20261010.zip](culture-qsj-litterature-anglophone-oeuvres-20261010.zip) |
| Littérature | Littérature britannique et irlandaise — Œuvres et personnages — Qui suis-je ? — 2 | 5 | [culture-qsj-litterature-anglophone-personnages-20261010.zip](culture-qsj-litterature-anglophone-personnages-20261010.zip) |
| Littérature | Littérature française — Œuvres et personnages — Qui suis-je ? — 1 | 5 | [culture-qsj-litterature-francaise-oeuvres-20261010.zip](culture-qsj-litterature-francaise-oeuvres-20261010.zip) |
| Littérature | Littérature française — Œuvres et personnages — Qui suis-je ? écrit — 2 | 5 | [culture-qsj-litterature-francaise-personnages-20261010.zip](culture-qsj-litterature-francaise-personnages-20261010.zip) |
| Mythologie | Mythologie grecque — Dieux et mortels — Qui suis-je ? écrit | 5 | [culture-qsj-mythologie-grecque-dieux-et-mortels-20261010.zip](culture-qsj-mythologie-grecque-dieux-et-mortels-20261010.zip) |
| Mythologie | Mythologie grecque — Héros et objets — Qui suis-je ? écrit | 5 | [culture-qsj-mythologie-grecque-monstres-et-objets-20261010.zip](culture-qsj-mythologie-grecque-monstres-et-objets-20261010.zip) |
| Mythologie | Mythologie romaine — Dieux et héros — Qui suis-je ? | 5 | [culture-qsj-mythologie-romaine-divinites-20261010.zip](culture-qsj-mythologie-romaine-divinites-20261010.zip) |
| Mythologie | Mythologie romaine — Dieux et fondations — Qui suis-je ? | 5 | [culture-qsj-mythologie-romaine-fondations-20261010.zip](culture-qsj-mythologie-romaine-fondations-20261010.zip) |
| Histoire | Qui suis-je ? — Rome antique — Monuments et pouvoirs | 5 | [culture-qsj-rome-monuments-et-crises-20261010.zip](culture-qsj-rome-monuments-et-crises-20261010.zip) |
| Histoire | Qui suis-je ? écrit — Rome antique — République et Empire | 5 | [culture-qsj-rome-personnages-20261010.zip](culture-qsj-rome-personnages-20261010.zip) |
| Géographie | Géographie — Cartes du monde — 1 | 6 | [geographie-afrique-20261010.zip](geographie-afrique-20261010.zip) |
| Géographie | Géographie — Cartes des Amériques | 5 | [geographie-amerique-du-sud-20261010.zip](geographie-amerique-du-sud-20261010.zip) |
| Géographie | Géographie — Cartes du monde — 2 | 6 | [geographie-asie-20261010.zip](geographie-asie-20261010.zip) |
| Géographie | Géographie - Capitales — Réponses écrites | 7 | [geographie-capitales-20261010-v2.zip](geographie-capitales-20261010-v2.zip) |
| Géographie | Géographie - Chaînes de montagnes | 6 | [geographie-chaines-de-montagnes-20261010.zip](geographie-chaines-de-montagnes-20261010.zip) |
| Nature | Géographie — Paysages et milieux naturels — QCM | 6 | [geographie-deserts-et-paysages-arides-20261010.zip](geographie-deserts-et-paysages-arides-20261010.zip) |
| Géographie | Géographie — Fleuves et rivières — 1 | 6 | [geographie-fleuves-et-rivieres-20261010.zip](geographie-fleuves-et-rivieres-20261010.zip) |
| Géographie | Géographie — Fleuves et rivières — 2 | 6 | [geographie-fleuves-et-rivieres-20261010-part-2.zip](geographie-fleuves-et-rivieres-20261010-part-2.zip) |
| Géographie | Géographie — Îles et eaux du monde — QCM | 6 | [geographie-iles-et-archipels-20261010.zip](geographie-iles-et-archipels-20261010.zip) |
| Géographie | Géographie - Sommets et volcans | 6 | [geographie-sommets-et-volcans-20261010.zip](geographie-sommets-et-volcans-20261010.zip) |
| Histoire | Histoire du Canada - Chronologie facile | 5 | [histoire-canada-chronologie-facile-20261010.zip](histoire-canada-chronologie-facile-20261010.zip) |
| Histoire | Histoire du Canada - Chronologie moins facile | 5 | [histoire-canada-chronologie-moins-facile-20261010.zip](histoire-canada-chronologie-moins-facile-20261010.zip) |
| Histoire | Histoire - Chronologie de la Grèce antique | 5 | [histoire-chronologie-grece-antique-20261010.zip](histoire-chronologie-grece-antique-20261010.zip) |
| Histoire | Histoire - Chronologie de la Rome antique | 5 | [histoire-chronologie-rome-antique-20261010.zip](histoire-chronologie-rome-antique-20261010.zip) |
| Histoire | Histoire des États-Unis — Chronologie | 5 | [histoire-etats-unis-chronologie-20261010.zip](histoire-etats-unis-chronologie-20261010.zip) |
| Histoire | Histoire des États-Unis — Figures et institutions — QCM | 6 | [histoire-etats-unis-politique-et-grandes-figures-20261010.zip](histoire-etats-unis-politique-et-grandes-figures-20261010.zip) |
| Histoire | Histoire des États-Unis — Société et repères — QCM | 7 | [histoire-etats-unis-societe-crises-et-culture-20261010.zip](histoire-etats-unis-societe-crises-et-culture-20261010.zip) |
| Histoire | Histoire de France — Moyen Âge — Repères | 6 | [histoire-france-moyen-age-reperes-20261010.zip](histoire-france-moyen-age-reperes-20261010.zip) |
| Histoire | Histoire de France — Moyen Âge — Vie quotidienne | 6 | [histoire-france-moyen-age-vie-quotidienne-20261010.zip](histoire-france-moyen-age-vie-quotidienne-20261010.zip) |
| Histoire | Histoire de France — Renaissance — Chronologie | 5 | [histoire-france-renaissance-chronologie-20261010.zip](histoire-france-renaissance-chronologie-20261010.zip) |
| Histoire | Histoire de France — Renaissance — Lettres et savoirs | 5 | [histoire-france-renaissance-lettres-et-savoirs-20261010.zip](histoire-france-renaissance-lettres-et-savoirs-20261010.zip) |
| Histoire | Histoire de France — Renaissance — Rois et arts | 5 | [histoire-france-renaissance-rois-et-arts-20261010.zip](histoire-france-renaissance-rois-et-arts-20261010.zip) |
| Histoire | Histoire mondiale — Transformations et explorations — Chronologie — 1 | 6 | [histoire-mondiale-chronologie-1-20261010.zip](histoire-mondiale-chronologie-1-20261010.zip) |
| Histoire | Histoire mondiale — Transformations et explorations — Chronologie — 2 | 7 | [histoire-mondiale-chronologie-2-20261010.zip](histoire-mondiale-chronologie-2-20261010.zip) |
| Histoire | Histoire mondiale — Grands repères — QCM — 1 | 7 | [histoire-mondiale-xixe-empires-et-industrie-20261010.zip](histoire-mondiale-xixe-empires-et-industrie-20261010.zip) |
| Histoire | Histoire mondiale — Grands repères — QCM — 2 | 7 | [histoire-mondiale-xixe-revoltes-et-unifications-20261010.zip](histoire-mondiale-xixe-revoltes-et-unifications-20261010.zip) |
| Histoire | Histoire mondiale — Grands repères — QCM — 3 | 7 | [histoire-mondiale-xxe-conflits-et-transformations-20261010.zip](histoire-mondiale-xxe-conflits-et-transformations-20261010.zip) |
| Nature | Animaux marins — Sous l’eau — Buzzer | 5 | [lib-buzzer-animaux-marins-20261012.zip](lib-buzzer-animaux-marins-20261012.zip) |
| Nature | Animaux terrestres — Mammifères — Buzzer | 5 | [lib-buzzer-animaux-terrestres-20261012.zip](lib-buzzer-animaux-terrestres-20261012.zip) |
| BD et manga | BD française et belge — Buzzer | 5 | [lib-buzzer-bd-franco-belge-20261012.zip](lib-buzzer-bd-franco-belge-20261012.zip) |
| Musique | Chanson francophone — Classiques — Buzzer | 5 | [lib-buzzer-chanson-francophone-20261012.zip](lib-buzzer-chanson-francophone-20261012.zip) |
| Musique | Musique classique — Compositeurs et œuvres — Réponses écrites | 5 | [lib-buzzer-classique-20261012.zip](lib-buzzer-classique-20261012.zip) |
| Contes et légendes | Contes et légendes d’Angleterre — Buzzer | 5 | [lib-buzzer-contes-anglais-20261012.zip](lib-buzzer-contes-anglais-20261012.zip) |
| Contes et légendes | Contes et légendes de France — Buzzer | 5 | [lib-buzzer-contes-francais-20261012.zip](lib-buzzer-contes-francais-20261012.zip) |
| Cuisine | Cuisine — Plats célèbres — Réponses écrites | 5 | [lib-buzzer-cuisine-celebre-20261012.zip](lib-buzzer-cuisine-celebre-20261012.zip) |
| Cuisine | Cuisine — Saveurs et desserts du monde — Buzzer | 5 | [lib-buzzer-cuisine-saveurs-20261012.zip](lib-buzzer-cuisine-saveurs-20261012.zip) |
| Super-héros | DC — Héros et univers — Buzzer | 5 | [lib-buzzer-dc-20261012.zip](lib-buzzer-dc-20261012.zip) |
| Logique et énigmes | Devinettes — Objets familiers — Buzzer | 5 | [lib-buzzer-devinettes-20261012.zip](lib-buzzer-devinettes-20261012.zip) |
| Cinéma | Disney — Animation — Réponses écrites | 5 | [lib-buzzer-disney-20261012.zip](lib-buzzer-disney-20261012.zip) |
| Histoire | Histoire — Explorateurs célèbres — Réponses écrites | 5 | [lib-buzzer-explorateurs-20261012.zip](lib-buzzer-explorateurs-20261012.zip) |
| Géographie | Géographie mondiale — Reliefs et océans — Réponses écrites | 5 | [lib-buzzer-geographie-monde-20261012.zip](lib-buzzer-geographie-monde-20261012.zip) |
| Géographie | Géographie mondiale — Villes et monuments — Buzzer | 7 | [lib-buzzer-geographie-villes-20261012.zip](lib-buzzer-geographie-villes-20261012.zip) |
| Cinéma | Cinéma — Studio Ghibli — Films animés — Buzzer | 5 | [lib-buzzer-ghibli-20261012.zip](lib-buzzer-ghibli-20261012.zip) |
| Histoire | Histoire des États-Unis — Grands repères — Réponses écrites | 5 | [lib-buzzer-histoire-etats-unis-20261012.zip](lib-buzzer-histoire-etats-unis-20261012.zip) |
| Histoire | Histoire de France — Figures et repères — Réponses écrites | 5 | [lib-buzzer-histoire-france-generale-20261012.zip](lib-buzzer-histoire-france-generale-20261012.zip) |
| Histoire | Histoire mondiale — Grands repères — Buzzer | 5 | [lib-buzzer-histoire-mondiale-generale-20261012.zip](lib-buzzer-histoire-mondiale-generale-20261012.zip) |
| Nature | Insectes — Petites bêtes — Réponses écrites | 5 | [lib-buzzer-insectes-20261012.zip](lib-buzzer-insectes-20261012.zip) |
| Musique | Musique — Instruments — Buzzer | 5 | [lib-buzzer-instruments-20261012.zip](lib-buzzer-instruments-20261012.zip) |
| Sciences | Inventions canadiennes — Créateurs et objets — Réponses écrites | 5 | [lib-buzzer-inventions-canada-20261012.zip](lib-buzzer-inventions-canada-20261012.zip) |
| Musique | Jazz, blues et soul — Repères — Réponses écrites | 5 | [lib-buzzer-jazz-blues-20261012.zip](lib-buzzer-jazz-blues-20261012.zip) |
| Jeux vidéo | Jeux vidéo — Grands univers — Buzzer | 5 | [lib-buzzer-jeux-video-20261012.zip](lib-buzzer-jeux-video-20261012.zip) |
| Contes et légendes | Légendes de France — Régions et créatures — Réponses écrites | 5 | [lib-buzzer-legendes-france-20261012.zip](lib-buzzer-legendes-france-20261012.zip) |
| Littérature | Littérature américaine — Classiques — Réponses écrites | 5 | [lib-buzzer-litterature-americaine-20261012.zip](lib-buzzer-litterature-americaine-20261012.zip) |
| Littérature | Littérature anglophone — Classiques — Buzzer | 5 | [lib-buzzer-litterature-anglaise-20261012.zip](lib-buzzer-litterature-anglaise-20261012.zip) |
| Littérature | Littérature française — Romans et personnages — Buzzer | 5 | [lib-buzzer-litterature-france-20261012.zip](lib-buzzer-litterature-france-20261012.zip) |
| Littérature | Littérature québécoise — Grands noms — Réponses écrites | 5 | [lib-buzzer-litterature-quebec-20261012.zip](lib-buzzer-litterature-quebec-20261012.zip) |
| Logique et énigmes | Logique — Défis rapides — Réponses écrites | 5 | [lib-buzzer-logique-20261012.zip](lib-buzzer-logique-20261012.zip) |
| BD et manga | Manga — Grands classiques — Réponses écrites | 5 | [lib-buzzer-manga-20261012.zip](lib-buzzer-manga-20261012.zip) |
| Super-héros | Marvel — Héros et univers — Réponses écrites | 5 | [lib-buzzer-marvel-20261012.zip](lib-buzzer-marvel-20261012.zip) |
| Musique | Musique — Films et comédies musicales — Buzzer | 5 | [lib-buzzer-musique-ecran-20261012.zip](lib-buzzer-musique-ecran-20261012.zip) |
| Musique | Musique — Artistes du Québec — Réponses écrites | 5 | [lib-buzzer-musique-quebec-20261012.zip](lib-buzzer-musique-quebec-20261012.zip) |
| Mythologie | Mythologie grecque — Dieux et héros — Buzzer | 5 | [lib-buzzer-mythologie-grecque-20261012.zip](lib-buzzer-mythologie-grecque-20261012.zip) |
| Mythologie | Mythologie romaine — Dieux et récits — Buzzer | 5 | [lib-buzzer-mythologie-romaine-20261012.zip](lib-buzzer-mythologie-romaine-20261012.zip) |
| Mythologie | Mythologie — L’Odyssée — Le voyage d’Ulysse — Réponses écrites | 5 | [lib-buzzer-odyssee-20261012.zip](lib-buzzer-odyssee-20261012.zip) |
| Nature | Oiseaux — Portraits et habitudes — Réponses écrites | 5 | [lib-buzzer-oiseaux-20261012.zip](lib-buzzer-oiseaux-20261012.zip) |
| Musique | Musique — Pop et rock — Grands noms — Buzzer | 5 | [lib-buzzer-pop-rock-20261012.zip](lib-buzzer-pop-rock-20261012.zip) |
| Contes et légendes | Contes et légendes — Récits autochtones — Traditions nommées — Buzzer | 5 | [lib-buzzer-recits-autochtones-20261012.zip](lib-buzzer-recits-autochtones-20261012.zip) |
| Sciences | Sciences — Découvertes accessibles — Buzzer | 5 | [lib-buzzer-science-generale-20261012.zip](lib-buzzer-science-generale-20261012.zip) |
| Contes et légendes | Le cycle de la Table ronde — Réponses écrites | 5 | [lib-buzzer-table-ronde-20261012.zip](lib-buzzer-table-ronde-20261012.zip) |
| Architecture | Architecture — Monuments dans le temps — Chronologie | 5 | [lib-chronologie-architecture-reperes-20261012.zip](lib-chronologie-architecture-reperes-20261012.zip) |
| Culture populaire | Culture populaire — Jeux et BD — Chronologie | 7 | [lib-chronologie-bd-premieres-20261012.zip](lib-chronologie-bd-premieres-20261012.zip) |
| Cinéma | Disney — Sorties des films animés — Chronologie | 5 | [lib-chronologie-disney-sorties-20261012.zip](lib-chronologie-disney-sorties-20261012.zip) |
| Cinéma | Cinéma — Studio Ghibli — Sorties japonaises — Chronologie | 5 | [lib-chronologie-ghibli-sorties-20261012.zip](lib-chronologie-ghibli-sorties-20261012.zip) |
| Musique | Musique — Œuvres dans le temps — Chronologie | 5 | [lib-chronologie-musique-reperes-20261012.zip](lib-chronologie-musique-reperes-20261012.zip) |
| Nature | Nature — Cycles de vie — Chronologie | 5 | [lib-chronologie-nature-cycles-20261012.zip](lib-chronologie-nature-cycles-20261012.zip) |
| Mythologie | Mythologie — L’Odyssée — Ordre des épisodes — Chronologie | 5 | [lib-chronologie-odyssee-episodes-20261012.zip](lib-chronologie-odyssee-episodes-20261012.zip) |
| Littérature | Littérature — Premières publications — Chronologie | 5 | [lib-chronologie-romans-publications-20261012.zip](lib-chronologie-romans-publications-20261012.zip) |
| Super-héros | DC et Marvel — Premières apparitions — Chronologie | 5 | [lib-chronologie-superheros-premieres-20261012.zip](lib-chronologie-superheros-premieres-20261012.zip) |
| Nature | Animaux marins — Sous l’eau — QCM | 5 | [lib-qcm-animaux-marins-20261012.zip](lib-qcm-animaux-marins-20261012.zip) |
| Nature | Animaux terrestres — Mammifères — QCM | 5 | [lib-qcm-animaux-terrestres-20261012.zip](lib-qcm-animaux-terrestres-20261012.zip) |
| BD et manga | BD française et belge — QCM | 5 | [lib-qcm-bd-franco-belge-20261012.zip](lib-qcm-bd-franco-belge-20261012.zip) |
| Musique | Chanson francophone — Classiques — QCM | 5 | [lib-qcm-chanson-francophone-20261012.zip](lib-qcm-chanson-francophone-20261012.zip) |
| Musique | Musique classique — Compositeurs et œuvres — QCM | 5 | [lib-qcm-classique-20261012.zip](lib-qcm-classique-20261012.zip) |
| Contes et légendes | Contes et légendes d’Angleterre — QCM | 5 | [lib-qcm-contes-anglais-20261012.zip](lib-qcm-contes-anglais-20261012.zip) |
| Contes et légendes | Contes et légendes de France — QCM | 5 | [lib-qcm-contes-francais-20261012.zip](lib-qcm-contes-francais-20261012.zip) |
| Cuisine | Cuisine — Plats célèbres — QCM | 5 | [lib-qcm-cuisine-celebre-20261012.zip](lib-qcm-cuisine-celebre-20261012.zip) |
| Cuisine | Cuisine — Saveurs et desserts du monde — QCM | 5 | [lib-qcm-cuisine-saveurs-20261012.zip](lib-qcm-cuisine-saveurs-20261012.zip) |
| Super-héros | DC — Héros et univers — QCM | 5 | [lib-qcm-dc-20261012.zip](lib-qcm-dc-20261012.zip) |
| Logique et énigmes | Devinettes — Objets familiers — QCM | 5 | [lib-qcm-devinettes-20261012.zip](lib-qcm-devinettes-20261012.zip) |
| Cinéma | Disney — Animation — QCM | 5 | [lib-qcm-disney-20261012.zip](lib-qcm-disney-20261012.zip) |
| Histoire | Histoire — Explorateurs célèbres — QCM | 5 | [lib-qcm-explorateurs-20261012.zip](lib-qcm-explorateurs-20261012.zip) |
| Géographie | Géographie mondiale — Reliefs et océans — QCM | 5 | [lib-qcm-geographie-monde-20261012.zip](lib-qcm-geographie-monde-20261012.zip) |
| Géographie | Géographie mondiale — Villes et monuments — QCM | 5 | [lib-qcm-geographie-villes-20261012.zip](lib-qcm-geographie-villes-20261012.zip) |
| Cinéma | Cinéma — Studio Ghibli — Films animés — QCM | 5 | [lib-qcm-ghibli-20261012.zip](lib-qcm-ghibli-20261012.zip) |
| Histoire | Histoire de France — Figures et repères — QCM | 5 | [lib-qcm-histoire-france-generale-20261012.zip](lib-qcm-histoire-france-generale-20261012.zip) |
| Nature | Insectes — Petites bêtes — QCM | 5 | [lib-qcm-insectes-20261012.zip](lib-qcm-insectes-20261012.zip) |
| Musique | Musique — Instruments — QCM | 5 | [lib-qcm-instruments-20261012.zip](lib-qcm-instruments-20261012.zip) |
| Sciences | Inventions canadiennes — Créateurs et objets — QCM | 5 | [lib-qcm-inventions-canada-20261012.zip](lib-qcm-inventions-canada-20261012.zip) |
| Musique | Jazz, blues et soul — Repères — QCM | 5 | [lib-qcm-jazz-blues-20261012.zip](lib-qcm-jazz-blues-20261012.zip) |
| Contes et légendes | Légendes de France — Régions et créatures — QCM | 5 | [lib-qcm-legendes-france-20261012.zip](lib-qcm-legendes-france-20261012.zip) |
| Littérature | Littérature américaine — Classiques — QCM | 5 | [lib-qcm-litterature-americaine-20261012.zip](lib-qcm-litterature-americaine-20261012.zip) |
| Littérature | Littérature anglophone — Classiques — QCM | 5 | [lib-qcm-litterature-anglaise-20261012.zip](lib-qcm-litterature-anglaise-20261012.zip) |
| Littérature | Littérature française — Romans et personnages — QCM | 5 | [lib-qcm-litterature-france-20261012.zip](lib-qcm-litterature-france-20261012.zip) |
| Littérature | Littérature québécoise — Grands noms — QCM | 5 | [lib-qcm-litterature-quebec-20261012.zip](lib-qcm-litterature-quebec-20261012.zip) |
| Logique et énigmes | Logique — Défis rapides — QCM | 5 | [lib-qcm-logique-20261012.zip](lib-qcm-logique-20261012.zip) |
| BD et manga | Manga — Grands classiques — QCM | 5 | [lib-qcm-manga-20261012.zip](lib-qcm-manga-20261012.zip) |
| Super-héros | Marvel — Héros et univers — QCM | 5 | [lib-qcm-marvel-20261012.zip](lib-qcm-marvel-20261012.zip) |
| Musique | Musique — Films et comédies musicales — QCM | 5 | [lib-qcm-musique-ecran-20261012.zip](lib-qcm-musique-ecran-20261012.zip) |
| Musique | Musique — Artistes du Québec — QCM | 5 | [lib-qcm-musique-quebec-20261012.zip](lib-qcm-musique-quebec-20261012.zip) |
| Mythologie | Mythologie grecque — Dieux et héros — QCM | 5 | [lib-qcm-mythologie-grecque-20261012.zip](lib-qcm-mythologie-grecque-20261012.zip) |
| Mythologie | Mythologie romaine — Dieux et récits — QCM | 5 | [lib-qcm-mythologie-romaine-20261012.zip](lib-qcm-mythologie-romaine-20261012.zip) |
| Mythologie | Mythologie — L’Odyssée — Le voyage d’Ulysse — QCM | 5 | [lib-qcm-odyssee-20261012.zip](lib-qcm-odyssee-20261012.zip) |
| Nature | Oiseaux — Portraits et habitudes — QCM | 5 | [lib-qcm-oiseaux-20261012.zip](lib-qcm-oiseaux-20261012.zip) |
| Musique | Musique — Pop et rock — Grands noms — QCM | 5 | [lib-qcm-pop-rock-20261012.zip](lib-qcm-pop-rock-20261012.zip) |
| Contes et légendes | Contes et légendes — Récits autochtones — Traditions nommées — QCM | 5 | [lib-qcm-recits-autochtones-20261012.zip](lib-qcm-recits-autochtones-20261012.zip) |
| Sciences | Sciences — Découvertes accessibles — QCM | 5 | [lib-qcm-science-generale-20261012.zip](lib-qcm-science-generale-20261012.zip) |
| Contes et légendes | Le cycle de la Table ronde — QCM | 5 | [lib-qcm-table-ronde-20261012.zip](lib-qcm-table-ronde-20261012.zip) |
| Nature | Animaux marins — Sous l’eau — Qui suis-je ? | 5 | [lib-qsj-animaux-marins-20261012.zip](lib-qsj-animaux-marins-20261012.zip) |
| Nature | Animaux terrestres — Mammifères — Qui suis-je ? | 5 | [lib-qsj-animaux-terrestres-20261012.zip](lib-qsj-animaux-terrestres-20261012.zip) |
| BD et manga | BD française et belge — Qui suis-je ? | 5 | [lib-qsj-bd-franco-belge-20261012.zip](lib-qsj-bd-franco-belge-20261012.zip) |
| Musique | Chanson francophone — Classiques — Qui suis-je ? écrit | 5 | [lib-qsj-chanson-francophone-20261012.zip](lib-qsj-chanson-francophone-20261012.zip) |
| Musique | Musique classique — Compositeurs et œuvres — Qui suis-je ? | 5 | [lib-qsj-classique-20261012.zip](lib-qsj-classique-20261012.zip) |
| Contes et légendes | Contes et légendes d’Angleterre — Qui suis-je ? | 5 | [lib-qsj-contes-anglais-20261012.zip](lib-qsj-contes-anglais-20261012.zip) |
| Contes et légendes | Contes et légendes de France — Qui suis-je ? | 5 | [lib-qsj-contes-francais-20261012.zip](lib-qsj-contes-francais-20261012.zip) |
| Cuisine | Cuisine — Plats célèbres — Qui suis-je ? | 5 | [lib-qsj-cuisine-celebre-20261012.zip](lib-qsj-cuisine-celebre-20261012.zip) |
| Cuisine | Cuisine — Saveurs et desserts du monde — Qui suis-je ? écrit | 5 | [lib-qsj-cuisine-saveurs-20261012.zip](lib-qsj-cuisine-saveurs-20261012.zip) |
| Super-héros | DC — Héros et univers — Qui suis-je ? | 5 | [lib-qsj-dc-20261012.zip](lib-qsj-dc-20261012.zip) |
| Logique et énigmes | Devinettes — Objets familiers — Qui suis-je ? | 5 | [lib-qsj-devinettes-20261012.zip](lib-qsj-devinettes-20261012.zip) |
| Cinéma | Disney — Animation — Qui suis-je ? | 5 | [lib-qsj-disney-20261012.zip](lib-qsj-disney-20261012.zip) |
| Histoire | Histoire — Explorateurs célèbres — Qui suis-je ? | 5 | [lib-qsj-explorateurs-20261012.zip](lib-qsj-explorateurs-20261012.zip) |
| Géographie | Géographie mondiale — Reliefs et océans — Qui suis-je ? écrit | 5 | [lib-qsj-geographie-monde-20261012.zip](lib-qsj-geographie-monde-20261012.zip) |
| Géographie | Géographie mondiale — Villes et monuments — Qui suis-je ? | 5 | [lib-qsj-geographie-villes-20261012.zip](lib-qsj-geographie-villes-20261012.zip) |
| Cinéma | Cinéma — Studio Ghibli — Films animés — Qui suis-je ? | 5 | [lib-qsj-ghibli-20261012.zip](lib-qsj-ghibli-20261012.zip) |
| Histoire | Histoire des États-Unis — Grands repères — Qui suis-je ? | 5 | [lib-qsj-histoire-etats-unis-20261012.zip](lib-qsj-histoire-etats-unis-20261012.zip) |
| Histoire | Histoire de France — Figures et repères — Qui suis-je ? | 5 | [lib-qsj-histoire-france-generale-20261012.zip](lib-qsj-histoire-france-generale-20261012.zip) |
| Histoire | Histoire mondiale — Grands repères — Qui suis-je ? écrit | 5 | [lib-qsj-histoire-mondiale-generale-20261012.zip](lib-qsj-histoire-mondiale-generale-20261012.zip) |
| Nature | Insectes — Petites bêtes — Qui suis-je ? écrit | 5 | [lib-qsj-insectes-20261012.zip](lib-qsj-insectes-20261012.zip) |
| Musique | Musique — Instruments — Qui suis-je ? | 5 | [lib-qsj-instruments-20261012.zip](lib-qsj-instruments-20261012.zip) |
| Sciences | Inventions canadiennes — Créateurs et objets — Qui suis-je ? écrit | 5 | [lib-qsj-inventions-canada-20261012.zip](lib-qsj-inventions-canada-20261012.zip) |
| Musique | Jazz, blues et soul — Repères — Qui suis-je ? | 5 | [lib-qsj-jazz-blues-20261012.zip](lib-qsj-jazz-blues-20261012.zip) |
| Jeux vidéo | Jeux vidéo — Grands univers — Qui suis-je ? | 5 | [lib-qsj-jeux-video-20261012.zip](lib-qsj-jeux-video-20261012.zip) |
| Contes et légendes | Légendes de France — Régions et créatures — Qui suis-je ? écrit | 5 | [lib-qsj-legendes-france-20261012.zip](lib-qsj-legendes-france-20261012.zip) |
| Littérature | Littérature québécoise — Grands noms — Qui suis-je ? écrit | 5 | [lib-qsj-litterature-quebec-20261012.zip](lib-qsj-litterature-quebec-20261012.zip) |
| Logique et énigmes | Logique — Défis rapides — Qui suis-je ? écrit | 5 | [lib-qsj-logique-20261012.zip](lib-qsj-logique-20261012.zip) |
| BD et manga | Manga — Grands classiques — Qui suis-je ? écrit | 5 | [lib-qsj-manga-20261012.zip](lib-qsj-manga-20261012.zip) |
| Super-héros | Marvel — Héros et univers — Qui suis-je ? écrit | 5 | [lib-qsj-marvel-20261012.zip](lib-qsj-marvel-20261012.zip) |
| Musique | Musique — Films et comédies musicales — Qui suis-je ? | 5 | [lib-qsj-musique-ecran-20261012.zip](lib-qsj-musique-ecran-20261012.zip) |
| Musique | Musique — Artistes du Québec — Qui suis-je ? écrit | 5 | [lib-qsj-musique-quebec-20261012.zip](lib-qsj-musique-quebec-20261012.zip) |
| Mythologie | Mythologie — L’Odyssée — Le voyage d’Ulysse — Qui suis-je ? | 5 | [lib-qsj-odyssee-20261012.zip](lib-qsj-odyssee-20261012.zip) |
| Nature | Oiseaux — Portraits et habitudes — Qui suis-je ? écrit | 5 | [lib-qsj-oiseaux-20261012.zip](lib-qsj-oiseaux-20261012.zip) |
| Musique | Musique — Pop et rock — Grands noms — Qui suis-je ? écrit | 5 | [lib-qsj-pop-rock-20261012.zip](lib-qsj-pop-rock-20261012.zip) |
| Contes et légendes | Contes et légendes — Récits autochtones — Traditions nommées — Qui suis-je ? | 5 | [lib-qsj-recits-autochtones-20261012.zip](lib-qsj-recits-autochtones-20261012.zip) |
| Sciences | Sciences — Découvertes accessibles — Qui suis-je ? | 5 | [lib-qsj-science-generale-20261012.zip](lib-qsj-science-generale-20261012.zip) |
| Contes et légendes | Le cycle de la Table ronde — Qui suis-je ? écrit | 5 | [lib-qsj-table-ronde-20261012.zip](lib-qsj-table-ronde-20261012.zip) |
| Jeux vidéo | Histoire du jeu vidéo | 5 | [original-gaming-history.zip](original-gaming-history.zip) |
| Culture populaire | Culture populaire — QCM | 6 | [original-pop-culture.zip](original-pop-culture.zip) |
| Sciences | Sciences et technologie | 5 | [original-science-tech.zip](original-science-tech.zip) |
| Jeux vidéo | Jeux vidéo — Univers et personnages — QCM | 7 | [original-video-game-maps.zip](original-video-game-maps.zip) |
| Géographie | Géographie mondiale | 5 | [original-world-geography.zip](original-world-geography.zip) |
| Histoire | Révolution française — Chronologie | 5 | [revolution-francaise-chronologie-20261010.zip](revolution-francaise-chronologie-20261010.zip) |
| Histoire | Révolution française — Culture et mobilisation | 5 | [revolution-francaise-culture-et-mobilisation-20261010.zip](revolution-francaise-culture-et-mobilisation-20261010.zip) |
| Histoire | Révolution française — Politique et personnages | 5 | [revolution-francaise-politique-et-personnages-20261010.zip](revolution-francaise-politique-et-personnages-20261010.zip) |
| Tests | TEST — Buzzer | 5 | [test-buzzer-20261012.zip](test-buzzer-20261012.zip) |
| Tests | TEST — Cartes | 5 | [test-carte-20261012.zip](test-carte-20261012.zip) |
| Tests | TEST — Chronologie | 5 | [test-chronologie-20261012.zip](test-chronologie-20261012.zip) |
| Tests | TEST — Qui suis-je ? | 5 | [test-indices-20261012.zip](test-indices-20261012.zip) |
| Tests | TEST — QCM et images | 5 | [test-qcm-20261012.zip](test-qcm-20261012.zip) |
| Tests | TEST — Rapidité | 5 | [test-rapidite-20261012.zip](test-rapidite-20261012.zip) |
