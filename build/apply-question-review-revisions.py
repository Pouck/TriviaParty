"""Historical package compatibility exporter; does not author game-library/bank.

New question edits belong in the canonical bank. This script is retained to
reproduce legacy archives and migration checks only.
"""
import json
import zipfile
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "game-library" / "current"

REVISIONS = {
    "canada-moins-facile-20261010-01": {"prompt": "Classez ces trois repères canadiens du plus ancien au plus récent.", "items": [{"id": "item-0", "text": "Vimy"}, {"id": "item-1", "text": "Création des provinces de l’Alberta et de la Saskatchewan"}, {"id": "item-2", "text": "Naufrage de l’Empress of Ireland"}]},
    "canada-moins-facile-20261010-02": {"prompt": "Classez ces batailles où des Canadiens ont combattu, du plus ancien au plus récent.", "items": [{"id": "item-0", "text": "Débarquement de Dieppe"}, {"id": "item-1", "text": "Défense de Hong Kong pendant la Seconde Guerre mondiale"}, {"id": "item-2", "text": "Débarquement sur Juno Beach en Normandie"}]},
    "canada-moins-facile-20261010-03": {"prompt": "Classez ces repères de l’histoire du Canada du plus ancien au plus récent.", "items": [{"id": "item-0", "text": "Ouverture de la Voie maritime du Saint-Laurent"}, {"id": "item-1", "text": "Exposition universelle de Montréal (Expo 67)"}, {"id": "item-2", "text": "Entrée de Terre-Neuve dans la Confédération canadienne"}]},
    "fr-renaissance-chronologie-20261010-01": {"prompt": "Classez du plus ancien au plus récent ces repères du règne de François Ier.", "items": [{"id": "item-0", "text": "Avènement de François Ier au trône"}, {"id": "item-1", "text": "Début de la construction du château de Chambord"}, {"id": "item-2", "text": "Arrivée de Léonard de Vinci à la cour de France"}]},
    "fr-renaissance-chronologie-20261010-02": {"prompt": "Classez du plus ancien au plus récent ces publications et décisions de la Renaissance française.", "items": [{"id": "item-0", "text": "Publication de Défense et illustration de la langue française par Joachim du Bellay"}, {"id": "item-1", "text": "Promulgation de l’ordonnance de Villers-Cotterêts par François Ier"}, {"id": "item-2", "text": "Publication de Gargantua par François Rabelais"}]},
    "fr-renaissance-chronologie-20261010-03": {"prompt": "Classez ces événements des guerres de Religion en France du plus ancien au plus récent.", "items": [{"id": "item-0", "text": "Massacre de la Saint-Barthélemy à Paris"}, {"id": "item-1", "text": "Conjuration d’Amboise"}, {"id": "item-2", "text": "Massacre de Wassy"}]},
    "fr-renaissance-chronologie-20261010-04": {"prompt": "Classez du plus ancien au plus récent ces événements de l’histoire de France.", "items": [{"id": "item-0", "text": "Assassinat du roi Henri III à Saint-Cloud"}, {"id": "item-1", "text": "Signature de l’édit de Nantes par Henri IV"}, {"id": "item-2", "text": "Bataille de Marignan"}]},
    "lib-qcm-histoire-etats-unis-20261012-02": {"_removeImage": True},
    "us-societe-crises-et-culture-20261010-01": {"options": ["A — L’Express abolitionniste", "B — Le Chemin de fer clandestin (Underground Railroad)", "C — Le Freedom Trail", "D — La Ligne de la liberté"], "correctOptionIndex": 1},
    "lib-buzzer-animaux-marins-20261012-04": {"prompt": "Quel grand cétacé prédateur est reconnaissable à son dos noir et à son ventre blanc ?"},
    "lib-buzzer-chanson-francophone-20261012-04": {"_removeImage": True},
    "lib-buzzer-dc-20261012-02": {"_removeImage": True},
    "lib-buzzer-dc-20261012-05": {"_removeImage": True},
    "lib-buzzer-explorateurs-20261012-02": {"_removeImage": True},
    "lib-buzzer-histoire-france-generale-20261012-02": {"_removeImage": True},
    "lib-buzzer-inventions-canada-20261012-01": {"_removeImage": True},
    "monde-xixe-empires-et-industrie-04-20261010": {"prompt": "Quel principe la conférence de Berlin (1884–1885) fixa-t-elle pour revendiquer un territoire en Afrique ?", "options": ["A — Occuper effectivement le territoire", "B — Le découvrir en premier", "C — Obtenir l’accord de tous les royaumes voisins", "D — Y ouvrir un comptoir commercial"], "correctOptionIndex": 0},
    "architecture-qsj-modernes-20261011-02": {"clues": ["Le projet de mon architecte danois remporte un concours international en 1957.", "Je suis construit à Bennelong Point, au bord d’un port australien.", "Mes grandes coques blanches abritent des salles de spectacle.", "Je réunis plusieurs scènes où se produisent des compagnies artistiques résidentes."]},
    "architecture-qsj-antiquite-20261011-03": {"clues": ["Je suis un monument funéraire de la IVe dynastie égyptienne.", "Je suis la seule merveille de l’Antiquité encore largement conservée.", "Deux autres grandes pyramides se dressent à mes côtés.", "Une galerie ascendante mène à la chambre funéraire dite du Roi."]},
    "lib-qcm-jazz-blues-20261012-04": {"prompt": "Quel instrument à anche simple Charlie Parker a-t-il rendu célèbre dans le bebop ?", "_removeImage": True},
    "charades-nun-ace": {"prompt": "Je suis un nombre de trois chiffres. Mon chiffre des centaines vaut trois fois celui des unités. Mon chiffre des dizaines vaut deux fois celui des unités. La somme de mes chiffres est 12. Quel nombre suis-je ?", "acceptableAnswers": ["642"], "allowFuzzyMatch": False},
    # These image files are present in the package already; retain their correct references.
    "arts-qcm-peintures-classiques-20261011-01": {"imageUrl": "images/arts-qcm-peintures-classiques-20261011/joconde.jpg"},
    "arts-qcm-peintures-classiques-20261011-03": {"imageUrl": "images/arts-qcm-peintures-classiques-20261011/naissance.jpg"},
    "arts-buzzer-regards-scenes-20261011-04": {"_removeImage": True},
    "arts-buzzer-regards-scenes-20261011-08": {"_removeImage": True},
    "arts-buzzer-tableaux-celebres-20261011-02": {"_removeImage": True},
    "arts-buzzer-tableaux-celebres-20261011-06": {"_removeImage": True},
    "arts-qsj-sculptures-mysteres-20261011-05": {"clues": ["Je suis une œuvre de la Renaissance conservée au musée du Bargello.", "Je porte un chapeau et des bottes, tout en étant presque nu.", "La tête de Goliath repose à mes pieds ; mon matériau est le bronze.", "Ma posture déhanchée contraste avec la raideur de nombreuses figures médiévales."]},
    "lib-buzzer-bd-franco-belge-20261012-02": {"_removeImage": True},
    "lib-buzzer-manga-20261012-01": {"_removeImage": True},
    "lib-qcm-manga-20261012-04": {"_removeImage": True},
    # No source-material image is included in these archives, so remove generic substitutes.
    "lib-buzzer-bd-franco-belge-20261012-03": {"_removeImage": True},
    "lib-buzzer-manga-20261012-03": {"_removeImage": True},
    "lib-qcm-bd-franco-belge-20261012-01": {"_removeImage": True},
    "lib-qcm-bd-franco-belge-20261012-04": {"_removeImage": True},
    "lib-qcm-disney-20261012-01": {"_removeImage": True},
    "lib-qcm-disney-20261012-04": {"_removeImage": True},
    "lib-qcm-manga-20261012-01": {"_removeImage": True},
    "cinema-chronologie-sagas-20261011-04": {"items": [{"id": "item-1", "text": "Harry Potter à l’école des sorciers"}, {"id": "item-2", "text": "Harry Potter et la Coupe de feu"}, {"id": "item-0", "text": "Harry Potter et l’Ordre du Phénix"}], "correctOrderIds": ["item-1", "item-2", "item-0"]},
    "cinema-qcm-coulisses-20261011-07": {"options": ["A — L’Étrange Noël de monsieur Jack (The Nightmare Before Christmas)", "B — Coraline", "C — Kubo et l’Armure magique", "D — Wallace et Gromit : Le Mystère du lapin-garou"]},
    "cinema-qsj-films-20261011-05": {"clues": ["Une malédiction transforme certains de mes personnages en squelettes sous la lumière de la lune.", "Will Turner cherche à sauver Elizabeth Swann, enlevée à Port Royal.", "Le capitaine Barbossa a pris le navire d’un pirate excentrique incarné par Johnny Depp.", "L’action se déroule dans les Caraïbes, à l’époque des flibustiers."], "acceptableAnswers": ["Pirates des Caraïbes : La Malédiction du Black Pearl (Pirates of the Caribbean: The Curse of the Black Pearl)", "Pirates of the Caribbean: The Curse of the Black Pearl", "Pirates des Caraïbes : La Malédiction du Black Pearl", "La Malédiction du Black Pearl", "Pirates des Caraïbes 1"]},
    "arts-qsj-peintures-mysteres-20261011-04": {"clues": ["Une inscription affirme que mon peintre était présent en 1434.", "Mon miroir convexe révèle d’autres personnages.", "Je montre un couple debout et un petit chien.", "De nombreux objets domestiques de la scène ont été interprétés comme des symboles."]},
    "arts-qsj-sculptures-mysteres-20261011-03": {"clues": ["Je fais partie d’une série de sculptures de Constantin Brancusi.", "Ma forme abandonne les détails anatomiques au profit d’une ligne élancée.", "Je suggère l’élan du vol sans montrer de plumes ni d’ailes déployées.", "Brancusi a décliné cette forme en plusieurs versions de bronze et de marbre."]},
    "lib-qsj-litterature-americaine-20261012-05": {"clues": ["Je suis un récit d’Hemingway.", "Mon héros est un vieux pêcheur cubain.", "Il lutte contre un grand marlin.", "Ce roman publié en 1952 vaut à son auteur le prix Pulitzer en 1953."], "acceptableAnswers": ["Le Vieil Homme et la Mer (The Old Man and the Sea)", "The Old Man and the Sea", "Le Vieil Homme et la Mer"]},
    "lib-qsj-litterature-anglaise-20261012-05": {"clues": ["Je suis un récit de Lewis Carroll.", "Une petite fille tombe dans un terrier.", "Un chapelier et un chat étrange apparaissent.", "John Tenniel illustre la première édition de ce récit, parue en 1865."], "acceptableAnswers": ["Alice au pays des merveilles (Alice’s Adventures in Wonderland)", "Alice’s Adventures in Wonderland", "Alice au pays des merveilles"]},
    "canada-buzzer-culture-20261011-09": {"prompt": "Au Parlement fédéral du Canada, quelle institution constitue la chambre haute ?", "acceptableAnswers": ["Le Sénat du Canada", "Le Sénat", "Sénat du Canada"]},
    "canada-qcm-moderne-20261011-03": {"prompt": "En quelle année Agnes Macphail devient-elle la première femme élue à la Chambre des communes du Canada ?", "options": ["A — 1921", "B — 1917", "C — 1929", "D — 1935"], "correctOptionIndex": 0},
    "lib-buzzer-disney-20261012-02": {"_removeImage": True},
    "lib-buzzer-disney-20261012-04": {"_removeImage": True},
    "lib-buzzer-ghibli-20261012-01": {"_removeImage": True},
    "lib-buzzer-ghibli-20261012-03": {"_removeImage": True},
    "lib-qcm-ghibli-20261012-02": {"_removeImage": True},
    "lib-qcm-ghibli-20261012-04": {"_removeImage": True},
    "lib-buzzer-contes-anglais-20261012-01": {"_removeImage": True},
    "lib-buzzer-contes-anglais-20261012-03": {"_removeImage": True},
    "lib-buzzer-contes-anglais-20261012-04": {"prompt": "Quel compagnon de Robin des Bois est réputé pour sa grande taille et sa force ?"},
    "lib-buzzer-contes-anglais-20261012-05": {"prompt": "Quel personnage minuscule des contes anglais tire son nom d’une mesure équivalant à la largeur d’un pouce ?"},
    "lib-buzzer-contes-francais-20261012-02": {"_removeImage": True},
    "lib-buzzer-contes-francais-20261012-03": {"_removeImage": True},
    "lib-buzzer-legendes-france-20261012-01": {"_removeImage": True},
    "lib-buzzer-legendes-france-20261012-02": {"_removeImage": True},
    "lib-buzzer-legendes-france-20261012-04": {"prompt": "Quelle créature énigmatique aurait attaqué des habitants du Gévaudan entre 1764 et 1767 ?"},
    "lib-buzzer-recits-autochtones-20261012-03": {"_removeImage": True},
    "lib-buzzer-recits-autochtones-20261012-04": {"prompt": "Dans un récit de création oneida, quel animal plonge au fond de l’eau et en rapporte un peu de terre ?"},
    "lib-buzzer-table-ronde-20261012-01": {"_removeImage": True},
    "lib-buzzer-table-ronde-20261012-03": {"_removeImage": True},
    "lib-qcm-contes-anglais-20261012-01": {"_removeImage": True},
    "lib-qcm-contes-anglais-20261012-03": {"_removeImage": True},
    "lib-qcm-contes-francais-20261012-02": {"_removeImage": True},
    "lib-qcm-contes-francais-20261012-04": {"_removeImage": True},
    "lib-qcm-legendes-france-20261012-04": {"_removeImage": True},
    "lib-qcm-recits-autochtones-20261012-01": {"_removeImage": True},
    "lib-qcm-recits-autochtones-20261012-02": {"_removeImage": True},
    "lib-qcm-table-ronde-20261012-02": {"_removeImage": True},
    "lib-qcm-table-ronde-20261012-04": {"_removeImage": True},
    "lib-qsj-contes-francais-20261012-04": {"clues": ["Je vis avec une famille qui me traite mal.", "Ma marraine m’aide à aller au bal.", "Je dois partir avant minuit.", "Je perds une pantoufle de verre en quittant le palais."]},
    "lib-qsj-legendes-france-20261012-05": {"clues": ["Mon histoire se déroule au XVIIIe siècle.", "Des attaques frappent une région de France.", "Mon identité exacte reste discutée.", "Mon nom est associé à celui d’une ancienne province du Massif central."]},
    "lib-qsj-recits-autochtones-20261012-01": {"clues": ["Mon récit est notamment raconté par les Oneida.", "Des oiseaux me portent après ma chute.", "Une tortue me reçoit au-dessus de l’eau.", "Mon arrivée marque le début d’un récit de création."]},
    "lib-qsj-recits-autochtones-20261012-04": {"clues": ["Je suis un héros de récits wabanaki.", "Je suis notamment associé à la tradition mi’kmaq.", "Une Première Nation de Nouvelle-Écosse porte mon nom.", "Dans les récits, je façonne le monde et viens en aide aux humains."]},
    "lib-buzzer-cuisine-saveurs-20261012-02": {"prompt": "Quel dessert français se garnit souvent de sucre, de confiture ou de chocolat avant d’être roulé ?"},
    "lib-qcm-cuisine-saveurs-20261012-03": {"prompt": "Quelle viennoiserie française se caractérise par sa pâte levée feuilletée au beurre ?"},
    "q13": {"_removeImage": True}, "q14": {"_removeImage": True},
    # Avoid repeating the same Statue of Liberty fact in another arts package.
    "arts-buzzer-marbre-bronze-20261011-08": {"prompt": "Quel sculpteur français a conçu la statue de la Liberté ?", "acceptableAnswers": ["Frédéric Auguste Bartholdi", "Auguste Bartholdi", "Bartholdi"]},
    "lib-buzzer-devinettes-20261012-01": {"prompt": "Dans une course, vous dépassez la personne en deuxième position. À quelle place êtes-vous maintenant ?", "acceptableAnswers": ["Deuxième", "La deuxième place", "2e"], "allowFuzzyMatch": False},
    "lib-buzzer-devinettes-20261012-02": {"prompt": "Un fermier doit traverser une rivière avec un loup, une chèvre et un chou. Sa barque ne transporte que lui et un seul des trois. Que doit-il faire traverser en premier ?", "acceptableAnswers": ["La chèvre", "Chèvre"], "allowFuzzyMatch": False, "_removeImage": True},
    "lib-buzzer-devinettes-20261012-03": {"prompt": "Un homme regarde un portrait et dit : « Je n’ai ni frère ni sœur, mais le père de cet homme est le fils de mon père. » Qui est sur le portrait ?", "acceptableAnswers": ["Son fils", "Le fils de l’homme", "Son enfant"], "allowFuzzyMatch": False},
    "lib-buzzer-devinettes-20261012-04": {"prompt": "Je pense à un nombre. Je le multiplie par 3, j’ajoute 6, puis je divise le résultat par 3. J’obtiens 8. Quel était le nombre ?", "acceptableAnswers": ["6"], "allowFuzzyMatch": False, "_removeImage": True},
    "lib-buzzer-devinettes-20261012-05": {"prompt": "Un escargot grimpe 3 mètres le jour et glisse de 2 mètres la nuit. Combien de jours lui faut-il pour sortir d’un puits de 10 mètres ?", "acceptableAnswers": ["8 jours", "Huit jours", "8"], "allowFuzzyMatch": False},
    "lib-qcm-devinettes-20261012-01": {"prompt": "Trois boîtes portent les étiquettes « pommes », « oranges » et « mélange ». Toutes les étiquettes sont fausses. Quelle boîte faut-il ouvrir pour pouvoir réétiqueter les trois en tirant un seul fruit ?", "options": ["A — Celle étiquetée « pommes »", "B — Celle étiquetée « oranges »", "C — Celle étiquetée « mélange »", "D — N’importe laquelle"], "correctOptionIndex": 2},
    "lib-qcm-devinettes-20261012-02": {"prompt": "Un pont doit être franchi de nuit avec une seule lampe. Quatre personnes mettent 1, 2, 7 et 10 minutes à traverser ; deux au plus peuvent avancer ensemble, à la vitesse de la plus lente. Quel est le temps minimal pour faire passer tout le monde ?", "options": ["A — 15 minutes", "B — 17 minutes", "C — 19 minutes", "D — 20 minutes"], "correctOptionIndex": 1, "_removeImage": True},
    "lib-qcm-devinettes-20261012-03": {"prompt": "Quel nombre complète la suite : 2, 6, 12, 20, 30, … ?", "options": ["A — 36", "B — 40", "C — 42", "D — 44"], "correctOptionIndex": 2},
    "lib-qcm-devinettes-20261012-04": {"prompt": "Quel nombre complète la suite de Fibonacci : 1, 1, 2, 3, 5, … ?", "options": ["A — 7", "B — 8", "C — 9", "D — 10"], "correctOptionIndex": 1, "_removeImage": True},
    "lib-qcm-devinettes-20261012-05": {"prompt": "Une famille compte cinq garçons. Chaque garçon a la même sœur. Combien d’enfants y a-t-il dans la famille ?", "options": ["A — 5", "B — 6", "C — 10", "D — 11"], "correctOptionIndex": 1},
}

PACKAGE_RENAMES = {
    "lib-buzzer-devinettes-20261012": ("Logique et énigmes — Déduction — Buzzer", "Logique et énigmes — Déduction — Buzzer"),
    "lib-qcm-devinettes-20261012": ("Logique et énigmes — Déduction — QCM", "Logique et énigmes — Déduction — QCM"),
}

ART_IMAGES = {
    "arts-buzzer-regards-scenes-20261011-04": ("arts-buzzer-regards-scenes-20261011", "nighthawks.jpg", "nighthawks.jpg", "Nighthawks", "Edward Hopper", "https://commons.wikimedia.org/wiki/File:Nighthawks_by_Edward_Hopper_1942.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg/1024px-Nighthawks_by_Edward_Hopper_1942.jpg"),
    "arts-buzzer-regards-scenes-20261011-08": ("arts-buzzer-selection-variee-20261012", "starry-night.jpg", "starry-night.jpg", "The Starry Night", "Vincent van Gogh", "https://commons.wikimedia.org/wiki/File:Vincent_Van_Gogh_Starry_Night.jpg", "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"),
    "arts-buzzer-tableaux-celebres-20261011-02": ("arts-buzzer-tableaux-celebres-20261011", "girl-with-pearl.jpg", "girl-with-pearl.jpg", "Girl with a Pearl Earring", "Johannes Vermeer", "https://commons.wikimedia.org/wiki/File:1665_Girl_with_a_Pearl_Earring.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/1665_Girl_with_a_Pearl_Earring.jpg/768px-1665_Girl_with_a_Pearl_Earring.jpg"),
    "arts-buzzer-tableaux-celebres-20261011-06": ("arts-buzzer-tableaux-celebres-20261011", "las-meninas.jpg", "las-meninas.jpg", "Las Meninas", "Diego Velázquez", "https://commons.wikimedia.org/wiki/File:Diego_Vel%C3%A1zquez_-_Las_Meninas.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Diego_Vel%C3%A1zquez_-_Las_Meninas.jpg/768px-Diego_Vel%C3%A1zquez_-_Las_Meninas.jpg"),
}
ART_BY_PACKAGE = {}
for question_id, (package_id, filename, localname, title, artist, commons, download) in ART_IMAGES.items():
    ART_BY_PACKAGE.setdefault(package_id, {})[filename] = dict(slug=filename.rsplit(".", 1)[0], title=title,
        file=filename, commons=commons, download=download, artist=artist, license="Public domain",
        licenseUrl="https://commons.wikimedia.org/wiki/Commons:Reuse_of_PD-Art_photographs",
        credit="Wikimedia Commons", changes="Miniature Wikimedia de l’œuvre originale.", originalPackage=package_id)
ART_BY_PACKAGE["arts-buzzer-selection-variee-20261012"]["starry-night.jpg"].update(
    credit="Google Arts & Culture via Wikimedia Commons",
    license="Public Domain Mark 1.0",
    licenseUrl="https://creativecommons.org/publicdomain/mark/1.0/")

october_24_revisions = ROOT / "build/question-review-revisions-2026-10-24.json"
if october_24_revisions.exists():
    for question_id, patch in json.loads(october_24_revisions.read_text(encoding="utf-8")).items():
        REVISIONS.setdefault(question_id, {}).update(patch)

def apply(q):
    patch = dict(REVISIONS.get(q.get("id"), {}))
    changed = False
    # GuessWho clues belong only in the progressive clue list. Older revision
    # passes copied them into prompt as well, so remove those duplicate lines.
    if q.get("kind") == "guessWho" and "\n" in q.get("prompt", ""):
        q["prompt"] = "Qui suis-je ?"
        changed = True
    if "clues" in patch:
        clues = patch.pop("clues")
        if clues and clues[0].strip().casefold() == "qui suis-je ?":
            clues = clues[1:]
        q["clues"] = clues
        q["prompt"] = "Qui suis-je ?"
        changed = True
    if not patch and not changed:
        return False
    remove_image = patch.pop("_removeImage", False)
    q.update(patch)
    if remove_image:
        q.pop("imageUrl", None)
    if q.get("id") in ART_IMAGES:
        package_id, filename, _, *_ = ART_IMAGES[q["id"]]
        q["imageUrl"] = f"images/{package_id}/{filename}"
    if q.get("id", "").startswith("lib-buzzer-devinettes-20261012-"):
        q["category"] = PACKAGE_RENAMES["lib-buzzer-devinettes-20261012"][0]
    elif q.get("id", "").startswith("lib-qcm-devinettes-20261012-"):
        q["category"] = PACKAGE_RENAMES["lib-qcm-devinettes-20261012"][0]
    return True

changed = set()
for archive in LIB.glob("*.zip"):
    with zipfile.ZipFile(archive, "r") as src:
        members = [(i, src.read(i.filename)) for i in src.infolist()]
    present_names = {info.filename for info, _ in members}
    replacements = {}
    extra_images = {}
    for info, data in members:
        if info.filename == "game.json":
            try:
                game = json.loads(data.decode("utf-8"))
                if game.get("id") in PACKAGE_RENAMES:
                    game["name"] = PACKAGE_RENAMES[game["id"]][1]
                    replacements[info.filename] = (json.dumps(game, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            except Exception:
                pass
        if info.filename.endswith(".json") and "question-bank/" in info.filename:
            try:
                obj = json.loads(data.decode("utf-8"))
            except Exception:
                continue
            if archive.stem in PACKAGE_RENAMES:
                obj["category"] = PACKAGE_RENAMES[archive.stem][0]
            qs = obj if isinstance(obj, list) else obj.get("questions", [])
            n = sum(apply(q) for q in qs if isinstance(q, dict))
            for q in qs:
                if isinstance(q, dict) and q.get("id") in ART_IMAGES:
                    package_id, filename, localname, *_ = ART_IMAGES[q["id"]]
                    if package_id == archive.stem and f"images/{package_id}/{filename}" not in present_names:
                        extra_images[f"images/{package_id}/{filename}"] = (ROOT / "build/review-source-images" / localname).read_bytes()
            if n:
                changed.update(q["id"] for q in qs if isinstance(q, dict) and q.get("id") in REVISIONS)
                replacements[info.filename] = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if replacements or extra_images:
        credits_path = "images/credits.json"
        if extra_images:
            try:
                credits = json.loads(next(data for info, data in members if info.filename == credits_path).decode("utf-8"))
            except StopIteration:
                credits = []
            known = {x.get("slug") for x in credits}
            credits.extend(v for v in ART_BY_PACKAGE.get(archive.stem, {}).values() if v["slug"] not in known)
            replacements[credits_path] = (json.dumps(credits, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        tmp = archive.with_suffix(".review-tmp.zip")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
            for info, data in members:
                dst.writestr(info, replacements.get(info.filename, data))
            for name, data in extra_images.items():
                dst.writestr(name, data)
        tmp.replace(archive)

# Keep editable source trees in sync with the shipped current packages.
for source in (LIB / "sources").glob("*"):
    game_path = source / "game.json"
    if game_path.exists():
        game = json.loads(game_path.read_text(encoding="utf-8"))
        if game.get("id") in PACKAGE_RENAMES:
            game["name"] = PACKAGE_RENAMES[game["id"]][1]
            game_path.write_text(json.dumps(game, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    package_images = ART_BY_PACKAGE.get(source.name, {})
    if package_images:
        image_dir = source / "images" / source.name
        image_dir.mkdir(parents=True, exist_ok=True)
        for filename in package_images:
            shutil.copyfile(ROOT / "build/review-source-images" / filename, image_dir / filename)
        credit_path = source / "images" / "credits.json"
        credits = json.loads(credit_path.read_text(encoding="utf-8")) if credit_path.exists() else []
        known = {x.get("slug") for x in credits}
        credits.extend(v for v in package_images.values() if v["slug"] not in known)
        credit_path.parent.mkdir(parents=True, exist_ok=True)
        credit_path.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for bank in (source / "question-bank").glob("*.json") if (source / "question-bank").exists() else []:
        obj = json.loads(bank.read_text(encoding="utf-8"))
        if source.name in PACKAGE_RENAMES:
            obj["category"] = PACKAGE_RENAMES[source.name][0]
        qs = obj if isinstance(obj, list) else obj.get("questions", [])
        if any(q.get("id") in REVISIONS for q in qs if isinstance(q, dict)):
            for q in qs:
                if isinstance(q, dict): apply(q)
            bank.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Keep the human-editable question inventory aligned with the package data.
catalog_path = LIB / "CATALOGUE.json"
if catalog_path.exists():
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    for item in catalog:
        if item.get("id") in PACKAGE_RENAMES:
            item["name"] = PACKAGE_RENAMES[item["id"]][1]
            item["subject"] = "Logique et énigmes"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
readme = LIB / "README.md"
if readme.exists():
    text = readme.read_text(encoding="utf-8")
    for package_id, (_, name) in PACKAGE_RENAMES.items():
        text = text.replace(f"| Logique et énigmes | Devinettes — Objets familiers — {'Buzzer' if package_id.startswith('lib-buzzer') else 'QCM'} |", f"| Logique et énigmes | {name} |")
    readme.write_text(text, encoding="utf-8")

csv_path = LIB / "QUESTIONS-ET-REPONSES.csv"
if csv_path.exists():
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    fields = list(rows[0]) if rows else []
    prompt_updates = {qid: patch.get("prompt") for qid, patch in REVISIONS.items() if patch.get("prompt")}
    answer_updates = {
        "arts-buzzer-marbre-bronze-20261011-08": "Frédéric Auguste Bartholdi",
        "canada-buzzer-culture-20261011-09": "Le Sénat du Canada",
        "lib-qsj-litterature-americaine-20261012-05": "Le Vieil Homme et la Mer (The Old Man and the Sea)",
        "lib-qsj-litterature-anglaise-20261012-05": "Alice au pays des merveilles (Alice’s Adventures in Wonderland)",
        "cinema-qsj-films-20261011-05": "Pirates des Caraïbes : La Malédiction du Black Pearl (Pirates of the Caribbean: The Curse of the Black Pearl)",
    }
    option_updates = {
        "canada-qcm-moderne-20261011-03": REVISIONS["canada-qcm-moderne-20261011-03"]["options"],
        "us-societe-crises-et-culture-20261010-01": REVISIONS["us-societe-crises-et-culture-20261010-01"]["options"],
    }
    correct_answer_updates = {
        "canada-qcm-moderne-20261011-03": "A — 1921",
        "us-societe-crises-et-culture-20261010-01": "B — Le Chemin de fer clandestin (Underground Railroad)",
    }
    category_updates = {"lib-buzzer-devinettes-20261012": PACKAGE_RENAMES["lib-buzzer-devinettes-20261012"][0],
                        "lib-qcm-devinettes-20261012": PACKAGE_RENAMES["lib-qcm-devinettes-20261012"][0]}
    for row in rows:
        qid = row.get("ID question")
        patch = REVISIONS.get(qid, {})
        if "options" in patch:
            row["Choix"] = " | ".join(patch["options"])
            row["Réponse"] = patch["options"][patch.get("correctOptionIndex", 0)]
        if qid in prompt_updates: row["Question"] = prompt_updates[qid]
        if qid in answer_updates: row["Réponse"] = answer_updates[qid]
        if qid in option_updates:
            row["Choix"] = " | ".join(option_updates[qid])
            row["Réponse"] = correct_answer_updates[qid]
        if qid in REVISIONS and "clues" in REVISIONS[qid]:
            clues = REVISIONS[qid]["clues"]
            if clues and clues[0].strip().casefold() == "qui suis-je ?": clues = clues[1:]
            row["Indices"] = " | ".join(clues)
        if row.get("ID forfait") in category_updates:
            row["Forfait"] = category_updates[row["ID forfait"]]
        if qid in REVISIONS and REVISIONS[qid].get("_removeImage"):
            row["Image"] = ""
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

missing = set(REVISIONS) - changed
if missing:
    raise SystemExit("Review IDs were not found in current ZIPs: " + ", ".join(sorted(missing)))
print(f"Applied review revisions to {len(changed)} questions.")
