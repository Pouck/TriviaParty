"""Add the first source-verified BD character image portraits requested on 2026-10-28."""
from __future__ import annotations

import json
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS_PATH = BANK / "questions.json"
CREDITS_PATH = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA = BANK / "media"
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates/official-bd-2026-10-28"
REVISION = "2026-10-28-requested-bd-character-portraits"
CATEGORY = "BD et manga — Personnages de bande dessinée — Qui suis-je ?"
PACKAGE = "image-qsj-personnages-de-bande-dessinee"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join("".join(ch if ch.isalnum() else " " for ch in value).split())


TARGETS = [
    {
        "key": "lucky-luke", "answers": ["Lucky Luke"],
        "title": "Lucky Luke", "franchise": "Lucky Luke",
        "image": "lucky-luke-character.png", "source": "https://www.dargaud.com/bd/lucky-luke",
        "creator": "Morris", "credit": "Dargaud / Lucky Comics",
        "description": "Portrait officiel du personnage principal de la série Lucky Luke.",
    },
    {
        "key": "gaston-lagaffe", "answers": ["Gaston Lagaffe", "Gaston"],
        "title": "Gaston Lagaffe", "franchise": "Gaston",
        "image": "gaston-universe.png", "source": "https://www.dupuis.com/univers/FR/gaston.html",
        "creator": "André Franquin", "credit": "Éditions Dupuis",
        "description": "Illustration officielle isolée de Gaston Lagaffe.",
    },
    {
        "key": "boule-et-bill", "answers": ["Boule et Bill", "Boule & Bill"],
        "title": "Boule et Bill", "franchise": "Boule et Bill",
        "image": "boule-bill.jpg", "source": "https://www.dargaud.com/actualites/atelier-jeunesse-la-tete-de-bill-en-origami-photo",
        "creator": "Jean Roba", "credit": "Dargaud",
        "pair": True,
        "description": "Illustration en couleur montrant ensemble Boule et Bill.",
    },
    {
        "key": "valerian-et-laureline", "answers": ["Valérian et Laureline", "Valerian et Laureline", "Valérian & Laureline"],
        "title": "Valérian et Laureline", "franchise": "Valérian et Laureline",
        "image": "valerian-characters.png", "source": "https://www.dargaud.com/bd/valerian",
        "creator": "Pierre Christin et Jean-Claude Mézières", "credit": "Dargaud",
        "pair": True,
        "description": "Illustration en couleur montrant ensemble Valérian et Laureline.",
    },
    {
        "key": "marsupilami", "answers": ["Le Marsupilami", "Marsupilami"],
        "title": "Marsupilami", "franchise": "Marsupilami",
        "image": "marsupilami-art.png", "source": "https://www.dupuis.com/univers/FR/marsupilami.html",
        "creator": "André Franquin", "credit": "Éditions Dupuis",
        "description": "Illustration officielle isolée du Marsupilami.",
    },
    {
        "key": "largo-winch", "answers": ["Largo Winch"],
        "title": "Largo Winch", "franchise": "Largo Winch",
        "image": "largo-winch-character.jpg", "source": "https://www.largowinch.com/personnages",
        "creator": "Jean Van Hamme et Philippe Francq", "credit": "Éditions Dupuis",
        "description": "Portrait officiel de Largo Winch publié sur le site de la série.",
    },
    {
        "key": "alix", "answers": ["Alix", "Alix Graccus"],
        "title": "Alix", "franchise": "Alix",
        "image": "alix-rtbf.jpg", "source": "https://www.rtbf.be/article/le-heros-de-bande-dessinee-alix-debarque-au-musee-9968996",
        "creator": "Jacques Martin", "credit": "RTBF / Casterman exhibition artwork",
        "description": "Portrait couleur d’Alix publié à l’occasion d’une rétrospective consacrée au héros.",
    },
    {
        "key": "calvin-et-hobbes", "answers": ["Calvin et Hobbes", "Calvin and Hobbes", "Calvin & Hobbes"],
        "title": "Calvin et Hobbes", "franchise": "Calvin et Hobbes",
        "image": "calvin-hobbes.jpg", "source": "https://www.bostonglobe.com/opinion/2013/10/30/bill-watterson-calvin-and-hobbes-creator-taught-lessons-that-still-resonate/wz0OMRRkqKEvnF0U0tY4DI/story.html",
        "creator": "Bill Watterson", "credit": "Bill Watterson / The Boston Globe",
        "description": "Illustration couleur montrant ensemble Calvin et Hobbes, sans texte dans l’image.",
        "pair": True,
    },
    {
        "key": "spirou-et-fantasio", "answers": ["Spirou et Fantasio", "Spirou & Fantasio"],
        "title": "Spirou et Fantasio", "franchise": "Spirou et Fantasio",
        "image": "spirou-fantasio.jpg", "source": "https://www.dupuis.com/seriebd/spirou-et-fantasio/124",
        "creator": "Rob-Vel; André Franquin and later series artists", "credit": "Éditions Dupuis",
        "description": "Illustration couleur du duo Spirou et Fantasio.",
        "pair": True,
    },
    {
        "key": "spirou-solo", "answers": ["Spirou", "Spirou (Spirou et Fantasio)"],
        "title": "Spirou", "franchise": "Spirou et Fantasio",
        "image": "spirou-universe.png", "source": "https://www.dupuis.com/univers/FR/spirou.html",
        "creator": "Rob-Vel; André Franquin and later series artists", "credit": "Éditions Dupuis",
        "description": "Portrait couleur centré sur Spirou, issu de la galerie officielle Dupuis; Spip apparaît comme son compagnon.",
    },
    {
        "key": "fantasio-solo", "answers": ["Fantasio", "Fantasio (Spirou et Fantasio)"],
        "title": "Fantasio", "franchise": "Spirou et Fantasio",
        "image": "fantasio-yoann-2dg.jpg", "source": "https://www.2dgalleries.com/art/fantasio-173381",
        "creator": "Yoann", "credit": "Yoann / 2D Galleries",
        "description": "Illustration couleur de Fantasio seul près de sa voiture; l’inscription manuscrite hors personnage est une dédicace, pas le nom du héros.",
    },
    {
        "key": "valerian-solo", "answers": ["Valérian", "Valerian", "Valérian (Valérian et Laureline)"],
        "title": "Valérian", "franchise": "Valérian et Laureline",
        "image": "valerian-europe-comics.jpg", "source": "https://www.europecomics.com/valerian-mezieres-art-comics/",
        "creator": "Pierre Christin et Jean-Claude Mézières", "credit": "Europe Comics / Dargaud",
        "description": "Illustration couleur montrant Valérian seul en combinaison spatiale dans un décor extraterrestre, sans texte.",
    },
    {
        "key": "iznogoud", "answers": ["Iznogoud"],
        "title": "Iznogoud", "franchise": "Iznogoud",
        "image": "iznogoud-home-made-licensing.webp", "source": "https://www.homemadelicensing.com/artistes/iznogoud.php",
        "creator": "René Goscinny et Jean Tabary", "credit": "© IMAV éditions / Goscinny - Tabary",
        "description": "Portrait couleur d’Iznogoud seul, publié par le représentant des droits de la série; seul le crédit de copyright borde l’image.",
    },
    {
        "key": "johan-et-pirlouit", "answers": ["Johan et Pirlouit", "Johan & Pirlouit"],
        "title": "Johan et Pirlouit", "franchise": "Johan et Pirlouit",
        "image": "johan-pirlouit.jpg", "source": "https://www.dupuis.com/seriebd/johan-et-pirlouit/54",
        "creator": "Peyo", "credit": "Éditions Dupuis",
        "description": "Illustration couleur des deux personnages principaux, Johan et Pirlouit.",
        "pair": True,
    },
    {
        "key": "xiii", "answers": ["XIII", "Treize", "Jason Fly"],
        "title": "XIII", "franchise": "XIII",
        "image": "xiii-character.png", "source": "https://www.dargaud.com/bd/xiii",
        "creator": "Jean Van Hamme et William Vance", "credit": "Dargaud",
        "description": "Portrait couleur de XIII tiré de la fiche officielle des personnages de la série.",
    },
    {
        "key": "benoit-brisefer", "answers": ["Benoît Brisefer", "Benoit Brisefer", "Benny Breakiron"],
        "title": "Benoît Brisefer", "franchise": "Benoît Brisefer",
        "image": "benoit-brisefer-peyo.png", "source": "https://www.peyo.company/en/brands/benny-breakiron",
        "creator": "Peyo", "credit": "Peyo Company",
        "description": "Illustration couleur isolée de Benoît Brisefer, publiée dans la galerie officielle des personnages Peyo.",
    },
    {
        "key": "lanfeust-de-troy", "answers": ["Lanfeust", "Lanfeust de Troy"],
        "title": "Lanfeust", "franchise": "Lanfeust de Troy",
        "image": "lanfeust-institut-francais.jpg", "source": "https://ifdigital.institutfrancais.com/en/creation/lanfeust-de-troy",
        "creator": "Christophe Arleston et Didier Tarquin", "credit": "Institut français — IFdigital",
        "description": "Lanfeust seul, épée levée, dans une illustration couleur tirée de la présentation culturelle de la série.",
    },
    {
        "key": "scrameustache", "answers": ["Le Scrameustache", "Scrameustache"],
        "title": "Le Scrameustache", "franchise": "Le Scrameustache",
        "image": "scrameustache-bdbest.png", "source": "https://www.bd-best.com/le-scrameustache-vu-par-l-oncle-georges-news-6347.html",
        "creator": "Gos", "credit": "BD-Best / illustration de l’Oncle Georges",
        "description": "Portrait couleur isolé du héros extraterrestre, sans texte dans l’image.",
    },
    {
        "key": "rahan", "answers": ["Rahan"],
        "title": "Rahan", "franchise": "Rahan",
        "image": "rahan-lexpress.jpg", "source": "https://www.lexpress.fr/culture/art/rahan-vendu-aux-encheres_1724733.html",
        "creator": "Roger Lécureux et André Chéret", "credit": "André Chéret / L’Express",
        "description": "Illustration couleur d’action centrée sur Rahan, sans titre ni texte dans l’image.",
    },
    {
        "key": "blacksad", "answers": ["Blacksad", "John Blacksad"],
        "title": "Blacksad", "franchise": "Blacksad",
        "image": "blacksad-zonanegativa.jpg", "source": "https://www.zonanegativa.com/blacksad-7-todo-cae-segunda-parte-de-juan-diaz-canales-y-juanjo-guarnido/",
        "creator": "Juan Díaz Canales et Juanjo Guarnido", "credit": "Juanjo Guarnido / Zona Negativa article reproduction",
        "description": "Illustration couleur centrée sur John Blacksad; aucun autre personnage ni texte n’apparaît dans l’image.",
    },
    {
        "key": "conan", "answers": ["Conan", "Conan the Barbarian", "Conan le Barbare"],
        "title": "Conan le Barbare", "franchise": "Conan the Barbarian",
        "image": "conan-wikipedia.png", "source": "https://en.wikipedia.org/wiki/Conan_the_Barbarian",
        "creator": "Robert E. Howard; artwork attribution as listed on Wikipedia", "credit": "Wikipedia article image; rights remain with the original artist / publisher",
        "description": "Illustration couleur d’un Conan seul, armé d’une épée et d’un bouclier, sans couverture ni lettrage.",
    },
    {
        "key": "natacha-solo", "answers": ["Natacha", "Natacha (hôtesse de l’air)"],
        "title": "Natacha", "franchise": "Natacha",
        "image": "natacha-dupuis.jpg", "source": "https://www.dupuis.com/seriebd/natacha/89",
        "creator": "François Walthéry et Gos", "credit": "Éditions Dupuis",
        "description": "Portrait couleur individuel de Natacha, héroïne de la série de François Walthéry.",
    },
    {
        "key": "bill-solo", "answers": ["Bill (Boule et Bill)", "Bill le chien", "Bill"],
        "title": "Bill", "franchise": "Boule et Bill",
        "image": "bill-solo-pinterest.jpg", "source": "https://www.pinterest.com/pin/21673641945701204/",
        "creator": "Jean Roba", "credit": "Jean Roba / source Pinterest",
        "description": "Illustration couleur de Bill seul, sans Boule et sans texte dans l’image.",
    },
    {
        "key": "calvin", "answers": ["Calvin", "Calvin (Calvin et Hobbes)"],
        "title": "Calvin", "franchise": "Calvin et Hobbes",
        "image": "calvin-gocomics.png", "source": "https://www.gocomics.com/calvinandhobbes/about",
        "creator": "Bill Watterson", "credit": "GoComics / Andrews McMeel Syndication",
        "description": "Portrait couleur de Calvin seul, issu de la galerie officielle GoComics.",
    },
    {
        "key": "hobbes", "answers": ["Hobbes", "Hobbes (Calvin et Hobbes)"],
        "title": "Hobbes", "franchise": "Calvin et Hobbes",
        "image": "hobbes-gocomics.png", "source": "https://www.gocomics.com/calvinandhobbes/about",
        "creator": "Bill Watterson", "credit": "GoComics / Andrews McMeel Syndication",
        "description": "Portrait couleur de Hobbes seul, issu de la galerie officielle GoComics.",
    },
    {
        "key": "johan", "answers": ["Johan", "Johan (Johan et Pirlouit)"],
        "title": "Johan", "franchise": "Johan et Pirlouit",
        "image": "johan-peyo.png", "source": "https://www.peyo.company/en/brands/johan-and-peewit",
        "creator": "Peyo", "credit": "Peyo Company",
        "description": "Illustration individuelle officielle de Johan à cheval, issue de la galerie des personnages Peyo.",
    },
    {
        "key": "pirlouit", "answers": ["Pirlouit", "Peewit", "Pirlouit (Johan et Pirlouit)"],
        "title": "Pirlouit", "franchise": "Johan et Pirlouit",
        "image": "pirlouit-peyo.png", "source": "https://www.peyo.company/en/brands/johan-and-peewit",
        "creator": "Peyo", "credit": "Peyo Company",
        "description": "Illustration individuelle officielle de Pirlouit, issue de la galerie des personnages Peyo.",
    },
    {
        "key": "yoko-tsuno", "answers": ["Yoko Tsuno"],
        "title": "Yoko Tsuno", "franchise": "Yoko Tsuno",
        "image": "yoko-tsuno-rtve.jfif", "source": "https://www.rtve.es/noticias/20170530/yoko-tsuno-primera-heroina-asiatica-del-comic-europeo/1556100.shtml",
        "creator": "Roger Leloup", "credit": "RTVE / Dupuis",
        "description": "Illustration couleur centrée sur Yoko Tsuno en combinaison spatiale, sans texte ni autre personnage.",
    },
    {
        "key": "le-scorpion", "answers": ["Le Scorpion", "Scorpion (bande dessinée)"],
        "title": "Le Scorpion", "franchise": "Le Scorpion",
        "image": "le-scorpion-marini-2dg.jpg", "source": "https://www.2dgalleries.com/art/le-scorpion-1-216952",
        "creator": "Stephen Desberg et Enrico Marini", "credit": "Enrico Marini / 2D Galleries",
        "description": "Illustration couleur du Scorpion seul, en costume et chapeau à plume; sans autre personnage ni texte.",
    },
    {
        "key": "boule-solo", "answers": ["Boule", "Boule (Boule et Bill)"],
        "title": "Boule", "franchise": "Boule et Bill",
        "image": "boule-solo-dargaud.png", "source": "https://www.dargaud.com/bd/boule-et-bill",
        "creator": "Jean Roba", "credit": "Dargaud",
        "description": "Illustration couleur officielle de Boule seul, extraite de la galerie de personnages Dargaud.",
    },
    {
        "key": "laureline-solo", "answers": ["Laureline", "Laureline (Valérian et Laureline)"],
        "title": "Laureline", "franchise": "Valérian et Laureline",
        "image": "laureline-crop-official.png", "source": "https://www.dargaud.com/bd/valerian",
        "creator": "Pierre Christin et Jean-Claude Mézières", "credit": "Dargaud / Jean-Claude Mézières",
        "description": "Portrait recadré de Laureline, tiré de l’illustration officielle Dargaud du duo; aucun autre personnage ni texte dans le recadrage.",
    },
    {
        "key": "blueberry-solo", "answers": ["Blueberry", "Mike S. Blueberry"],
        "title": "Blueberry", "franchise": "Blueberry",
        "image": "blueberry-pin-portrait.jpg", "source": "https://i.pinimg.com/736x/21/5f/ef/215fefc3b379b31d6f61dc4cf9a83e63--jean-giraud-blueberry.jpg",
        "creator": "Jean-Michel Charlier et Jean Giraud", "credit": "Jean Giraud / image source Pinterest",
        "description": "Portrait couleur rapproché du héros Blueberry, sans texte ni autre personnage.",
    },
    {
        "key": "achille-talon-solo", "answers": ["Achille Talon"],
        "title": "Achille Talon", "franchise": "Achille Talon",
        "image": "achille-talon-cutout.png", "source": "https://www.realclipart.com/png/middle/252-2521928_achilles-clipart-talon-achille-talon.png",
        "creator": "Greg", "credit": "RealClipart character cutout; original artwork rights remain with their holder",
        "description": "Personnage en couleur détouré sur fond transparent; aucun texte ni autre personnage.",
    },
    {
        "key": "sylvain-solo", "answers": ["Sylvain", "Sylvain (Sylvain et Sylvette)"],
        "title": "Sylvain", "franchise": "Sylvain et Sylvette",
        "image": "sylvain-crop.jpg", "source": "https://www.mutualart.com/Artwork/Sylvain--Sylvette--et-leurs-amis/856101BBAE9018333F6DD5619E9BD60F",
        "creator": "Claude Dubois", "credit": "Claude Dubois / MutualArt auction reproduction",
        "description": "Recadrage couleur centré sur Sylvain à partir d’une illustration signée de Claude Dubois.",
    },
    {
        "key": "sylvette-solo", "answers": ["Sylvette", "Sylvette (Sylvain et Sylvette)"],
        "title": "Sylvette", "franchise": "Sylvain et Sylvette",
        "image": "sylvette-crop.jpg", "source": "https://www.mutualart.com/Artwork/Sylvain--Sylvette--et-leurs-amis/856101BBAE9018333F6DD5619E9BD60F",
        "creator": "Claude Dubois", "credit": "Claude Dubois / MutualArt auction reproduction",
        "description": "Recadrage couleur centré sur Sylvette à partir d’une illustration signée de Claude Dubois.",
    },
    {
        "key": "melusine-solo", "answers": ["Mélusine", "Melusine"],
        "title": "Mélusine", "franchise": "Mélusine",
        "image": "melusine-crop-dupuis.png", "source": "https://www.dupuis.com/melusine/bd/melusine-tome-1-sortileges/670",
        "creator": "François Gilson et Clarke", "credit": "Éditions Dupuis / Clarke",
        "description": "Recadrage couleur de Mélusine seule, sans lettrage de couverture ni autre personnage visible.",
    },
    {
        "key": "papyrus-solo", "answers": ["Papyrus", "Papyrus (bande dessinée)"],
        "title": "Papyrus", "franchise": "Papyrus",
        "image": "papyrus-animated-still.jpg", "source": "https://image.tmdb.org/t/p/original/thPVGktJlBIHITQLn2nBUJ3x7zq.jpg",
        "creator": "Lucien De Gieter", "credit": "Papyrus animated adaptation / image via TMDB",
        "description": "Papyrus seul au premier plan dans l’adaptation animée officielle de la série de BD créée par Lucien De Gieter.",
    },
]


def main() -> None:
    data = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    existing_revision = next((row for row in data.get("revisionHistory", []) if row.get("id") == REVISION), None)
    credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8"))
    used_ids = {p.get("id") for q in data["questions"] for p in q.get("presentations", [])}
    answers_index: dict[str, list[dict]] = {}
    for q in data["questions"]:
        for answer in q.get("answers", []):
            answers_index.setdefault(norm(answer), []).append(q)

    added: list[str] = []
    created = attached = 0
    MEDIA.mkdir(parents=True, exist_ok=True)
    for target in TARGETS:
        presentation_id = "image-qsj-bd-request-" + target["key"]
        if presentation_id in used_ids:
            continue
        source = CANDIDATES / target["image"]
        if not source.is_file():
            raise FileNotFoundError(source)
        image_name = target["image"]
        destination = MEDIA / image_name
        if not destination.exists():
            shutil.copyfile(source, destination)
        prompt = "Qui sont ces personnages ?" if target.get("pair") else "Qui suis-je ?"
        presentation = {
            "id": presentation_id, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
            "topic": "BD et manga", "legacyCategory": CATEGORY,
            "legacyPackageId": PACKAGE,
            "content": {"kind": "guessWho", "prompt": prompt, "clues": [],
                        "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
                        "imageUrl": "media/" + image_name, "basePoints": 30, "penaltyPoints": 0},
        }
        matching = next((answers_index[norm(name)] for name in target["answers"] if answers_index.get(norm(name))), [])
        facts = {
            "subjectType": "fictional_character_pair" if target.get("pair") else "fictional_character",
            "subjectTitle": target["title"],
            "facts": [
                {"kind": "subject_title", "value": target["title"], "sourceUrl": target["source"]},
                {"kind": "franchise", "value": target["franchise"], "sourceUrl": target["source"]},
                {"kind": "subject_creator", "value": target["creator"], "sourceUrl": target["source"], "role": "créateur(s) de la série"},
            ],
            "sources": [target["source"]], "franchise": target["franchise"],
        }
        if matching:
            question = matching[0]
            question["presentations"].append(presentation)
            if presentation_id not in question.setdefault("legacyIds", []):
                question["legacyIds"].append(presentation_id)
            if "BD et manga" not in question.setdefault("topics", []):
                question["topics"].append("BD et manga")
            question.setdefault("imageFacts", facts)
            attached += 1
        else:
            question = {
                "id": presentation_id, "legacyIds": [presentation_id], "topics": ["BD et manga"],
                "prompt": prompt, "answers": target["answers"], "content": {},
                "presentations": [presentation], "legacyReviews": [], "imageFacts": facts,
                "explanation": target["description"],
            }
            data["questions"].append(question)
            for answer in question["answers"]:
                answers_index.setdefault(norm(answer), []).append(question)
            created += 1
        used_ids.add(presentation_id)
        added.append(presentation_id)
        credits[image_name] = {
            "filename": image_name, "title": target["title"], "creator": target["creator"],
            "credit": target["credit"], "license": "All rights reserved; private local gameplay only",
            "licenseUrl": "", "source": target["source"], "downloadedFrom": target["source"],
            "localSource": (CANDIDATES / image_name).relative_to(ROOT).as_posix(),
            "question": target["title"], "category": CATEGORY,
            "visualReview": "User approved downloaded images for this batch; asset was visually checked before import.",
        }
    revision_row = {
        "id": REVISION,
        "note": "Added source-verified, review-pending portraits for requested BD characters, including separate image questions for individual members of selected duos. Pair artwork remains attached only to pair-named questions.",
        "createdQuestions": created + (existing_revision.get("createdQuestions", 0) if existing_revision else 0),
        "addedPresentationsToExistingQuestions": attached + (existing_revision.get("addedPresentationsToExistingQuestions", 0) if existing_revision else 0),
        "presentationIds": (existing_revision.get("presentationIds", []) if existing_revision else []) + added,
    }
    if existing_revision:
        existing_revision.update(revision_row)
    else:
        data.setdefault("revisionHistory", []).append(revision_row)
    QUESTIONS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(added)} presentations ({created} new questions, {attached} attached to existing answers).")
    print("\n".join(added))


if __name__ == "__main__":
    main()
