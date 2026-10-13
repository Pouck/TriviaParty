# Histoire de France — Vérification et utilisation

Cinq archives importables, 24 questions en français : deux forfaits Moyen Âge (6 chacun), une chronologie Renaissance (4), deux quiz Renaissance (4 chacun). Choix multiples simultanés, 15 secondes, 15 → 10 → 5 points par tranches de 5 secondes, aucune pénalité ordinaire. Les mises suivent les règles de l’application.

Les bonnes réponses sont réparties exactement entre A, B, C et D (6 chacune). Les choix ont été mélangés dans les archives ; ils ne changent pas automatiquement à chaque partie. Les fichiers JSON modifiables sont dans `sources/`. Le corrigé détaillé est dans `QUESTIONS-ET-CORRIGE.csv`. Les explications historiques du CSV ne sont pas affichées par l’application, qui révèle la bonne option.

## Corrections et limites

- **Gaule** : prélude antique dans un forfait médiéval ; son territoire ne correspond pas exactement à la France actuelle. Pour une catégorie strictement médiévale, remplacer cette question par une question sur Clovis. Le contenu fourni est conservé avec une formulation géographique prudente.
- **Carcassonne** : la croisade contre les Albigeois ne ciblait pas une seule ville. La question porte maintenant sur le siège de 1209. [Ministère de la Culture](https://citedecarcassonne.culture.gouv.fr/fr/les-trencavel-et-la-croisades-contre-les-albigeois-1209-1229).
- **Notre-Dame** : gothique, mais ne crée pas ce style. [Histoire et architecture de Notre-Dame](https://www.notredamedeparis.fr/en/understand/architecture/).
- **Sorbonne** : distinguer le collège de Robert de Sorbon de l’Université de Paris. La source institutionnelle distingue sa création en 1253 et sa confirmation en 1257 ; la question évite une date de fondation ambiguë. [Histoire de la Sorbonne](https://www.sorbonne.fr/la-sorbonne/histoire-de-la-sorbonne/la-fondation-de-la-sorbonne-au-moyen-age-par-le-theologien-robert-de-sorbon/).
- **Épée bâtarde** : suppression de l’affirmation non étayée selon laquelle elle aurait été interdite dans les duels. La réponse décrit la prise à une ou deux mains. [Metropolitan Museum](https://www.metmuseum.org/art/collection/search/35888).
- **Procès d’animaux** : suppression de la généralisation concernant avocats et exécutions pour tous les animaux. Les procès criminels de bétail et les procédures religieuses contre les nuisibles sont distincts ; certains exemples célèbres sont postérieurs au Moyen Âge. [Archives de sciences sociales des religions, Persée](https://www.persee.fr/doc/assr_0003-9659_1971_num_32_1_1875_t1_0269_0000_2).
- **Peste** : la question vise l’épidémie, sans imposer une mortalité universelle ni une amélioration automatique de la condition paysanne. [Larousse](https://www.larousse.fr/encyclopedie/divers/peste/78778).
- **Lois somptuaires** : formulation générale, sans affirmer un système uniforme et entièrement déterminé par la classe sociale. [Larousse, Histoire de France](https://www.larousse.fr/archives/histoire_de_france/page/1181).
- **Palais de la Cité** : suppression du récit d’un déménagement direct au Louvre. [Ville de Paris](https://parcoursrevolution.paris.fr/fr/points-interet/32-le-palais-de-la-cite-et-la-conciergerie).
- **Métiers** : emploi du terme « communautés de métiers », historiquement plus prudent que « corporations » ; suppression du monopole prétendu sur toute l’économie. [Larousse](https://www.larousse.fr/dictionnaires/college/corporation/9623).
- **Dîme** : suppression de « taxe exonérée d’impôt », expression incohérente ; le dixième est une référence traditionnelle, pas un taux uniforme. [Larousse](https://www.larousse.fr/dictionnaires/francais/d%C3%AEme/25583).
- **Chronologie royale** : 1515 → 1516 → 1519. Marignan se déroule en septembre 1515, et non au début de l’année. [Dossier du château de Chambord](https://cdn1.chambord.org/fr/wp-content/uploads/sites/2/2019/03/Dossier-de-presse-exposition-15192019-Chambord.pdf).
- **Gargantua et Pléiade** : première publication de Gargantua généralement située vers 1534–1535. La « formation de la Pléiade » est un repère imprécis : remplacée par la publication de *Défense et illustration de la langue française* (1549), qui conserve le thème littéraire et l’ordre attendu. [Gargantua : datation](https://fr.wikipedia.org/wiki/Gargantua), [Du Bellay, BnF](https://essentiels.bnf.fr/fr/extrait/dd23a9ae-96ac-4f4b-8eae-0582c77178fe-exhortation-francais-ecrire-en-leur-langue).
- **Guerres de Religion** : Wassy 1562 → Amboise 1563 → Saint-Barthélemy 1572 ; Henri III 1589 avant Nantes 1598. [Musée protestant](https://museeprotestant.org/notice/les-huit-guerres-de-religion-1562-1598/).
- **Catherine de Médicis** : question recentrée sur son identité familiale ; retrait des affirmations culinaires et de la présentation comme souveraine unique pendant trois règnes. [Ville d’Anet](https://www.ville-anet.fr/uploads/CATHERINE%20DE%20MEDICIS%20POUR%20FACEBOOK%20PDF.pdf).
- **Chenonceau** : c’est la galerie, et non tout l’édifice, qui repose sur un pont au-dessus du Cher. [Château de Chenonceau](https://www.chenonceau.com/chateau-renaissance/pieces/).
- **Louvre** : destruction du donjon en 1528, nomination de Pierre Lescot en 1546. [Musée du Louvre](https://www.louvre.fr/en/explore/the-palace/at-the-heart-of-the-renaissance-palace).
- **Ambroise Paré** : ne pas confondre les pansements des plaies par armes à feu avec les ligatures lors des amputations ; éviter de lui attribuer l’invention de toute ligature. [Science Museum Group Journal](https://journal.sciencemuseum.ac.uk/article/they-had-no-fever/), [Université de Genève](https://www.unige.ch/medecine/exposition-Bodmer/ambroise-pare).
- **Montaigne** : question fondée sur la publication des *Essais* en 1580, plutôt que sur une invention absolue du genre. [BnF](https://classes.bnf.fr/dossitsm/b-montai.htm).
- **Villers-Cotterêts** : réponse recentrée sur les actes judiciaires, sans assimiler la mesure à un changement immédiat de la langue de tous les Français. [Centre des monuments nationaux](https://www.cite-langue-francaise.fr/en/discover/the-ordinance-of-villers-cotterets).
- **Offices** : suppression de l’équivalence automatique entre achat d’un office et anoblissement. [Larousse](https://www.larousse.fr/dictionnaires/francais/v%C3%A9nalit%C3%A9/81353).

## Suggestions

La chronologie reste en choix multiples pour la comparer aux forfaits grec et romain à cartes mobiles. À 15 secondes, ses trois événements et quatre ordres demandent davantage de lecture que les quiz courts : envisager 20 ou 25 secondes après un essai en groupe.

Léonard de Vinci et Villers-Cotterêts apparaissent dans la chronologie et dans un quiz thématique : il s’agit de questions différentes, mais jouer les forfaits à la suite peut donner des indices. Les introductions, propositions de nouvelles catégories et résultats de recherche du texte collé ne sont pas des questions et ont été exclus.
