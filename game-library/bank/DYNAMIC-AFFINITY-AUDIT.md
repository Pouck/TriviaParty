# Dynamic affinity audit

Generated from `questions.json` by `build/audit-question-bank-affinities.py`.
Exact normalized answer matches are title collisions only. They do not establish shared subject identity or authorize a merge.

## Bank totals

- Canonical entries: 1580
- Ordering presentations: 124
- Distinct normalized ordering item labels: 357
- Item labels colliding with another entry's accepted answer text: 88 (97 item occurrences)
- Potential target question entries pending subject-identity resolution: 101
- Ordering source pools: 23

## Existing ordering pools

Combination counts are mathematical upper bounds from item counts and authored set size. They assume all items in a pool share a valid comparator; that assumption must be verified before generating a package.

| Legacy pool | Existing sets | Unique items | Items per set | Potential sets at typical size |
|---|---:|---:|---:|---:|
| arts-chronologie-peintures-dans-le-temps-20261011 | 6 | 18 | 3–3 | C(18, 3) = 816 |
| arts-chronologie-sculptures-reperes-20261011 | 6 | 18 | 3–3 | C(18, 3) = 816 |
| cinema-chronologie-reperes-20261011 | 6 | 18 | 3–3 | C(18, 3) = 816 |
| cinema-chronologie-sagas-20261011 | 6 | 18 | 3–3 | C(18, 3) = 816 |
| histoire-canada-chronologie-facile-20261010 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| histoire-canada-chronologie-moins-facile-20261010 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| histoire-chronologie-grece-antique-20261010 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| histoire-chronologie-rome-antique-20261010 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| histoire-etats-unis-chronologie-20261010 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| histoire-france-renaissance-chronologie-20261010 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| histoire-mondiale-chronologie-1-20261010 | 6 | 18 | 3–3 | C(18, 3) = 816 |
| histoire-mondiale-chronologie-2-20261010 | 7 | 21 | 3–3 | C(21, 3) = 1,330 |
| lib-chronologie-architecture-reperes-20261012 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| lib-chronologie-bd-premieres-20261012 | 7 | 22 | 3–4 | C(22, 3) = 1,540 |
| lib-chronologie-disney-sorties-20261012 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| lib-chronologie-ghibli-sorties-20261012 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| lib-chronologie-musique-reperes-20261012 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| lib-chronologie-nature-cycles-20261012 | 5 | 13 | 3–3 | C(13, 3) = 286 |
| lib-chronologie-odyssee-episodes-20261012 | 5 | 13 | 3–3 | C(13, 3) = 286 |
| lib-chronologie-romans-publications-20261012 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| lib-chronologie-superheros-premieres-20261012 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| revolution-francaise-chronologie-20261010 | 5 | 15 | 3–3 | C(15, 3) = 455 |
| test-chronologie-20261012 | 5 | 15 | 3–3 | C(15, 3) = 455 |

## Item labels that match existing entries

A title can identify distinct subjects. For example, `La Naissance de Vénus` is used for separate paintings by Botticelli, Bouguereau, and Cabanel. Use the subject facts and relationships below to resolve each row; never merge based on this table alone.

| Ordering item | Candidate entry IDs and tags |
|---|---|
| Achille Talon | `image-qsj-bd-request-achille-talon-solo` (BD et manga) |
| Aladdin | `image-qsj-personnages-disney-aladdin-disney-character` (Personnages Disney) |
| Alice’s Adventures in Wonderland | `lib-qsj-litterature-anglaise-20261012-05` (Littérature) |
| American Gothic | `image-qsj-arts-gothic` (Arts) |
| Animal Farm | `culture-qsj-litterature-anglophone-oeuvres-20261010-02` (Littérature) |
| Astérix | `lib-qsj-bd-franco-belge-20261012-01` (BD et manga) |
| Back to the Future | `cinema-qsj-films-20261011-01` (Cinéma) |
| Bal du moulin de la Galette | `image-qsj-arts-galette` (Arts) |
| Batman | `lib-qsj-dc-20261012-02` (Super-héros, Héros DC) |
| Beethoven | `lib-buzzer-classique-20261012-02` (Musique) |
| Black Panther | `lib-qsj-marvel-20261012-02` (Super-héros, Héros Marvel) |
| Boule et Bill | `image-qsj-bd-request-boule-et-bill` (BD et manga) |
| Burj Khalifa | `architecture-buzzer-moderne-20261011-01` (Architecture) |
| Candide | `culture-qcm-francaise-oeuvres-20261010-08` (Littérature) |
| Captain America | `lib-qcm-marvel-20261012-01` (Super-héros, Héros Marvel) |
| Cartier | `lib-buzzer-explorateurs-20261012-04` (Histoire) |
| Cendrillon | `lib-buzzer-disney-20261012-01` (Cinéma, Contes et légendes, Personnages Disney) |
| Champlain | `canada-qsj-batisseurs-20261011-03` (Histoire) |
| Chopin | `lib-qsj-classique-20261012-04` (Musique) |
| Deadpool | `image-qsj-heros-marvel-deadpool` (Héros Marvel) |
| Deux | `lib-buzzer-logique-20261012-05` (Logique et énigmes) |
| Doctor Strange | `lib-qsj-marvel-20261012-04` (Super-héros, Héros Marvel) |
| Dracula | `lib-qsj-litterature-anglaise-20261012-04` (Littérature) |
| Empire State Building | `image-qsj-building-022` (Architecture) |
| Fahrenheit 451 | `lib-qsj-litterature-americaine-20261012-04` (Littérature) |
| Frankenstein | `culture-qsj-litterature-anglophone-oeuvres-20261010-01` (Littérature) |
| Gaston Lagaffe | `lib-qcm-bd-franco-belge-20261012-05` (BD et manga) |
| Guernica | `arts-buzzer-tableaux-celebres-20261011-08` (Arts) |
| Hulk | `lib-qcm-marvel-20261012-03` (Super-héros, Héros Marvel) |
| Impression, soleil levant | `image-qsj-arts-impression` (Arts) |
| Iron Man | `cinema-buzzer-titres-heros-20261011-07` (Cinéma, Culture populaire, Super-héros, Héros Marvel) |
| Iznogoud | `image-qsj-bd-request-iznogoud` (BD et manga) |
| Jaws | `cinema-qsj-films-20261011-02` (Cinéma) |
| Jean-Sébastien Bach | `lib-buzzer-classique-20261012-05` (Musique) |
| Kiki la petite sorcière | `lib-qcm-ghibli-20261012-04` (Cinéma) |
| La Belle au bois dormant | `lib-qsj-contes-francais-20261012-02` (Contes et légendes) |
| La Jeune Fille à la perle | `arts-qcm-peintures-classiques-20261011-07` (Arts); `image-qsj-painting-rank-012` (Arts) |
| La Liberté guidant le peuple | `arts-buzzer-tableaux-celebres-20261011-05` (Arts); `image-qsj-painting-rank-021` (Arts) |
| La Naissance de Vénus | `arts-qcm-peintures-classiques-20261011-03` (Arts); `image-qsj-painting-rank-014` (Arts); `image-qsj-painting-rank-076` (Arts); `image-qsj-painting-rank-099` (Arts) |
| La Nuit étoilée | `image-qsj-arts-nuit` (Arts) |
| La Persistance de la mémoire | `arts-qsj-peintures-mysteres-20261011-02` (Arts) |
| La Petite Sirène | `image-qsj-little-mermaid-statue` (Arts) |
| La Reine des neiges | `lib-buzzer-musique-ecran-20261012-03` (Musique) |
| La Ronde de nuit | `image-qsj-arts-ronde` (Arts); `image-qsj-painting-rank-027` (Arts) |
| Largo Winch | `image-qsj-bd-request-largo-winch` (BD et manga) |
| Le Baiser | `image-qsj-arts-baiser` (Arts); `image-qsj-painting-rank-011` (Arts) |
| Le Château ambulant | `lib-buzzer-ghibli-20261012-05` (Cinéma) |
| Le Penseur | `image-qsj-arts-penseur` (Arts) |
| Le Petit Prince | `culture-qsj-litterature-francaise-oeuvres-20261010-02` (Littérature) |
| Le Radeau de la Méduse | `image-qsj-arts-radeau` (Arts); `image-qsj-painting-rank-025` (Arts) |
| Le Roi lion | `lib-buzzer-musique-ecran-20261012-01` (Musique) |
| Les Bourgeois de Calais | `arts-qsj-sculptures-mysteres-20261011-02` (Arts); `image-qsj-sculpture-065` (Arts) |
| Les Époux Arnolfini | `arts-qsj-peintures-mysteres-20261011-04` (Arts); `image-qsj-painting-028` (Arts) |
| Les Ménines | `image-qsj-arts-menines` (Arts) |
| Les Misérables | `cv-bb7744e0c8af2c8fb78d` (Littérature) |
| Les Schtroumpfs | `lib-qcm-bd-franco-belge-20261012-04` (BD et manga) |
| Lucky Luke | `lib-qcm-bd-franco-belge-20261012-03` (BD et manga) |
| Madame Bovary | `lib-qsj-litterature-france-20261012-03` (Littérature) |
| Marie-Antoinette | `lib-buzzer-histoire-france-generale-20261012-01` (Histoire) |
| Marsupilami | `lib-buzzer-bd-franco-belge-20261012-04` (BD et manga) |
| Moby-Dick | `culture-qsj-litterature-americaine-oeuvres-20261010-01` (Littérature) |
| Mozart | `lib-qcm-classique-20261012-02` (Musique) |
| Mulan | `lib-qsj-disney-20261012-03` (Cinéma, Personnages Disney) |
| Nighthawks | `arts-qsj-peintures-mysteres-20261011-05` (Arts) |
| Notre-Dame de Paris | `architecture-qsj-sacre-20261011-01` (Architecture); `culture-qcm-francaise-oeuvres-20261010-01` (Littérature) |
| Olympia | `image-qsj-arts-olympia` (Arts) |
| Opéra de Sydney | `architecture-qsj-modernes-20261011-02` (Architecture) |
| Porco Rosso | `lib-buzzer-ghibli-20261012-03` (Cinéma) |
| Pride and Prejudice | `cv-772851924e95e4ef0d4c` (Littérature) |
| Snow White and the Seven Dwarfs | `cinema-qcm-prix-classiques-20261011-05` (Cinéma) |
| Spirou | `lib-qsj-bd-franco-belge-20261012-04` (BD et manga) |
| Superman | `lib-qsj-dc-20261012-01` (Super-héros, Héros DC) |
| Tchaïkovski | `lib-buzzer-classique-20261012-01` (Musique) |
| The Great Gatsby | `culture-qsj-litterature-americaine-oeuvres-20261010-02` (Littérature) |
| The Lion King | `lib-buzzer-musique-ecran-20261012-01` (Musique) |
| The Matrix | `cinema-qsj-films-20261011-03` (Cinéma) |
| The Sound of Music | `lib-buzzer-musique-ecran-20261012-05` (Musique) |
| Tintin | `lib-qcm-bd-franco-belge-20261012-01` (BD et manga) |
| Titanic | `cinema-buzzer-titres-heros-20261011-01` (Cinéma); `cinema-qcm-prix-classiques-20261011-02` (Cinéma) |
| To Kill a Mockingbird | `lib-qsj-litterature-americaine-20261012-03` (Littérature) |
| Tour Eiffel | `architecture-buzzer-europe-20261011-01` (Architecture, Tests) |
| Toy Story | `cinema-qcm-coulisses-20261011-08` (Cinéma) |
| Trois | `canada-geo-buzzer-villes-20261011-01` (Géographie); `lib-buzzer-contes-anglais-20261012-01` (Contes et légendes); `lib-buzzer-logique-20261012-02` (Logique et énigmes) |
| Vaiana | `lib-buzzer-disney-20261012-05` (Cinéma, Personnages Disney) |
| Vivaldi | `lib-qcm-classique-20261012-01` (Musique) |
| Wolverine | `lib-buzzer-marvel-20261012-03` (Super-héros, Héros Marvel) |
| Wonder Woman | `lib-buzzer-dc-20261012-05` (Super-héros, Héros DC) |
| XIII | `image-qsj-bd-request-xiii` (BD et manga) |

## Ambiguous exact-answer matches

These labels have multiple target entries and need canonical subject-identity resolution before migration.

| Item label | Candidate entry IDs |
|---|---|
| La Jeune Fille à la perle | `image-qsj-bd-request-xiii` |
| La Liberté guidant le peuple | `image-qsj-bd-request-xiii` |
| La Naissance de Vénus | `image-qsj-bd-request-xiii` |
| La Ronde de nuit | `image-qsj-bd-request-xiii` |
| Le Baiser | `image-qsj-bd-request-xiii` |
| Le Radeau de la Méduse | `image-qsj-bd-request-xiii` |
| Les Bourgeois de Calais | `image-qsj-bd-request-xiii` |
| Les Époux Arnolfini | `image-qsj-bd-request-xiii` |
| Notre-Dame de Paris | `image-qsj-bd-request-xiii` |
| Titanic | `image-qsj-bd-request-xiii` |
| Trois | `image-qsj-bd-request-xiii` |
