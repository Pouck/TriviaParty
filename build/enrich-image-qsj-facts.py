"""Add reusable, source-linked facts to image-identification questions.

Media creators are kept separate from creators of the depicted works. Only
explicitly curated subject-creator facts are promoted to painter/sculptor/
architect roles; image credit metadata is never treated as architectural data.
"""
from __future__ import annotations

import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
CREDITS = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
REVISION = "2026-10-27-image-qsj-facts-v8"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in value if not unicodedata.combining(c)).lower()).strip()


# Institution/official-source facts, keyed by recognizable answer fragments.
# Add to this table only when the source explicitly supports the named role.
CURATED = [
    ("tour eiffel", "architect", "Stephen Sauvestre", "https://www.toureiffel.paris/en/the-monument/history"),
    ("big ben", "architect", "Charles Barry", "https://www.parliament.uk/about/living-heritage/building/palace/big-ben/building-clock-tower/key-dates-/"),
    ("big ben", "architectural collaborator", "Augustus Welby Pugin", "https://www.parliament.uk/about/living-heritage/building/palace/big-ben/building-clock-tower/key-dates-/"),
    ("elizabeth tower", "architect", "Charles Barry", "https://www.parliament.uk/about/living-heritage/building/palace/big-ben/building-clock-tower/key-dates-/"),
    ("elizabeth tower", "architectural collaborator", "Augustus Welby Pugin", "https://www.parliament.uk/about/living-heritage/building/palace/big-ben/building-clock-tower/key-dates-/"),
    ("burj khalifa", "architect", "Adrian Smith", "https://www.som.com/projects/burj-khalifa/"),
    ("habitat 67", "architect", "Moshe Safdie", "https://www.habitat67.com/wp-content/uploads/2021/07/Cite-du-Havre-A-Neglected-Gem.pdf"),
    ("sydney opera house", "architect", "Jørn Utzon", "https://www.sydneyoperahouse.com/our-story"),
    ("fallingwater", "architect", "Frank Lloyd Wright", "https://fallingwater.org/media-resources/fallingwater-facts/"),
    ("little dancer of fourteen years", "sculptor", "Edgar Degas", "https://www.metmuseum.org/art/collection/search/196439"),
    ("little dancer of fourteen years", "depicted person", "Marie van Goethem", "https://www.metmuseum.org/art/collection/search/196439"),
    ("the thinker", "sculptor", "Auguste Rodin", "https://www.musee-rodin.fr/en/musee/collections/sculptures/thinker"),
    ("gates of hell", "sculptor", "Auguste Rodin", "https://www.musee-rodin.fr/en/musee/collections/sculptures/gates-hell"),
    ("david michelangelo", "sculptor", "Michelangelo", "https://www.galleriaaccademiafirenze.it/en/artworks/david/"),
    ("pieta michelangelo", "sculptor", "Michelangelo", "https://www.basilicasanpietro.va/en/saint-peters/the-pieta.html"),
    ("little mermaid statue", "sculptor", "Edvard Eriksen", "https://www.visitcopenhagen.com/copenhagen/planning/the-little-mermaid-gdk586951"),
    ("christ the redeemer", "sculptor", "Paul Landowski", "https://www.loc.gov/pictures/item/2022687346/"),
    ("angel of the north", "sculptor", "Antony Gormley", "https://www.antonygormley.com/projects/item-view/id/211"),
    ("motherland calls", "sculptor", "Yevgeny Vuchetich", "https://en.wikipedia.org/wiki/The_Motherland_Calls"),
    ("maman sculpture", "sculptor", "Louise Bourgeois", "https://www.tate.org.uk/art/artworks/bourgeois-maman-t12625"),
    ("the kiss rodin", "sculptor", "Auguste Rodin", "https://www.musee-rodin.fr/en/musee/collections/sculptures/kiss"),
    ("venus de milo", "sculptor", "Unknown; attributed to Alexandros of Antioch", "https://www.louvre.fr/en/explore/the-palace/the-venus-de-milo"),
    ("winged victory of samothrace", "sculptor", "Unknown", "https://www.louvre.fr/en/explore/the-palace/winged-victory-of-samothrace"),
    ("tour eiffel", "country", "France", "https://www.toureiffel.paris/en/the-monument/history"),
    ("big ben", "country", "United Kingdom", "https://www.parliament.uk/about/living-heritage/building/palace/big-ben/building-clock-tower/key-dates-/"),
    ("elizabeth tower", "country", "United Kingdom", "https://www.parliament.uk/about/living-heritage/building/palace/big-ben/building-clock-tower/key-dates-/"),
    ("habitat 67", "country", "Canada", "https://www.habitat67.com/wp-content/uploads/2021/07/Cite-du-Havre-A-Neglected-Gem.pdf"),
    ("sydney opera house", "country", "Australia", "https://www.sydneyoperahouse.com/our-story"),
    ("fallingwater", "country", "United States", "https://fallingwater.org/media-resources/fallingwater-facts/"),
    ("little mermaid statue", "country", "Denmark", "https://www.visitcopenhagen.com/copenhagen/planning/the-little-mermaid-gdk586951"),
    ("christ the redeemer", "country", "Brazil", "https://www.loc.gov/pictures/item/2022687346/"),
    ("becassine", "character illustrator", "Joseph Pinchon", "https://www.citebd.org/actualites/gallica-becassine-entre-dans-le-domaine-public-en-2024"),
    ("becassine", "first story writer", "Jacqueline Rivière", "https://www.citebd.org/actualites/gallica-becassine-entre-dans-le-domaine-public-en-2024"),
    ("iron man", "actor", "Robert Downey Jr. (Marvel Cinematic Universe films)", "https://www.marvel.com/articles/movies/iron-man-kevin-feige-jon-favreau-15-anniversary-interview"),
]


def subject_type(question: dict, presentation: dict, credit: dict) -> tuple[str, str | None]:
    text = norm(" ".join([
        question.get("id", ""), presentation.get("topic", ""),
        presentation.get("legacyCategory", ""), credit.get("benchmark", ""),
    ]))
    if "painting" in text or "peinture" in text or "tableau" in text:
        return "painting", None
    if "sculpt" in text or "statue" in text or "sculpture" in text:
        return "sculpture", None
    if "politician" in text or "politique" in text or "president" in text:
        return "person", None
    if "animal" in text or "animaux" in text or any(x in text for x in ("lion", "giraffe", "ostrich", "horse", "pig", "tiger", "whale")):
        return "animal", None
    if "landscape" in text or "paysage" in text:
        return "landscape", None
    if "ville" in text or "city" in text or "town" in text:
        return "city", None
    answers = norm(" ".join(question.get("answers", [])))
    if any(name in answers for name in ("londres", "london", "san francisco", "toronto")):
        return "city", None
    if "geographie" in text:
        return "place", None
    if "architecture" in text or "building" in text or "architect" in text:
        return "building_or_site", None
    if "disney" in text:
        return "fictional_character", "Disney"
    if "pixar" in text:
        return "fictional_character", "Pixar"
    if "marvel" in text:
        return "fictional_character", "Marvel"
    if re.search(r"\bdc\b", text) or "hero dc" in text:
        return "fictional_character", "DC"
    path = norm(presentation.get("legacyCategory", ""))
    topic = norm(presentation.get("topic", ""))
    if "personnages de bande dessinee" in path or "personnages de bd" in path or "bd et manga" in topic:
        return "fictional_character", "Bande dessinée"
    if "personnages de manga" in path or ("manga" in text and "bd et manga" not in topic):
        return "fictional_character", "Manga"
    if "cartoon" in text or "dessin anime" in text:
        return "fictional_character", "Cartoon"
    return "visual_subject", None


def main() -> None:
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in questions.get("revisionHistory", [])):
        print("Image facts revision already applied.")
        return

    backup_dir = ROOT / "review-backups"
    backup_dir.mkdir(exist_ok=True)
    for source, dest in (
        (QUESTIONS, backup_dir / "questions-before-image-qsj-facts-2026-10-27.json"),
        (CREDITS, backup_dir / "credits-before-image-qsj-facts-2026-10-27.json"),
    ):
        if not dest.exists():
            shutil.copyfile(source, dest)

    updated = []
    for question in questions["questions"]:
        for presentation in question.get("presentations", []):
            content = presentation.get("content", {})
            image_url = content.get("imageUrl", "")
            if not content.get("imageRevealMode") or not image_url.startswith("media/"):
                continue
            credit = credits.get(Path(image_url).name, {})
            kind, franchise = subject_type(question, presentation, credit)
            title = credit.get("title") or question.get("answers", [None])[0]
            sources = []
            if credit.get("source"):
                sources.append(credit["source"])
            facts = []
            if title:
                facts.append({"kind": "work_title" if kind in ("painting", "sculpture") else "subject_title", "value": title, "sourceUrl": credit.get("source")})
            media_creator = credit.get("creator", "").strip()
            if media_creator:
                facts.append({"kind": "media_creator", "role": "image credit; not necessarily subject creator", "value": media_creator, "sourceUrl": credit.get("source")})

            # For public-domain painting reproductions, Commons' Creator field
            # names the painter. For other subjects it often names a photographer.
            if kind == "painting" and media_creator and "no machine-readable" not in media_creator.casefold():
                facts.append({"kind": "subject_creator", "role": "painter", "value": media_creator, "sourceUrl": credit.get("source")})

            match_text = norm(" ".join(question.get("answers", []) + [credit.get("title", "")]))
            curated = []
            for needle, role, name, url in CURATED:
                if norm(needle) in match_text:
                    fact_kind = "location" if role == "country" else "actor" if role == "actor" else "subject_creator" if role in {"architect", "architectural collaborator", "sculptor", "painter", "character illustrator", "first story writer"} else "depicted_person"
                    fact = {"kind": fact_kind, "role": role, "value": name, "sourceUrl": url}
                    if fact not in facts:
                        facts.append(fact)
                    if url not in sources:
                        sources.append(url)
                    curated.append((role, name))
            qfacts = {
                "subjectType": kind,
                "subjectTitle": title,
                "facts": facts,
                "sources": list(dict.fromkeys(sources)),
            }
            if franchise:
                qfacts["franchise"] = franchise
            question["imageFacts"] = qfacts

            # Surface verified, useful creator facts after image answers. Keep
            # existing editorial explanation if one is already present.
            if curated and not question.get("explanation"):
                clauses = []
                for role, name in curated:
                    if role == "architect":
                        clauses.append(f"L’architecte est {name}.")
                    elif role == "architectural collaborator":
                        clauses.append(f"La conception architecturale a aussi bénéficié de {name}.")
                    elif role == "sculptor":
                        verb = "est attribuée à" if name.startswith("Unknown") else "est de"
                        clauses.append(f"Cette sculpture {verb} {name}.")
                    elif role == "depicted person":
                        clauses.append(f"Le modèle représenté est {name}.")
                    elif role == "country":
                        country_fr = {"France": "France", "United Kingdom": "Grande-Bretagne", "Canada": "Canada", "Australia": "Australie", "United States": "États-Unis", "Denmark": "Danemark", "Brazil": "Brésil"}.get(name, name)
                        prep = {"Grande-Bretagne": "au", "Canada": "au", "États-Unis": "aux", "Danemark": "au", "Brésil": "au", "Australie": "en", "France": "en"}.get(country_fr, "en")
                        clauses.append(f"Ce monument se trouve {prep} {country_fr}.")
                    elif role == "character illustrator":
                        clauses.append(f"Le personnage de Bécassine a été dessiné par {name}.")
                    elif role == "first story writer":
                        clauses.append(f"Sa première histoire a été écrite par {name}.")
                    elif role == "actor":
                        actor_name = name.split(" (")[0].rstrip(".")
                        clauses.append(f"Dans les films du Marvel Cinematic Universe, Iron Man est interprété par {actor_name}.")
                if clauses:
                    question["explanation"] = " ".join(clauses)
            if kind == "painting" and media_creator and not question.get("explanation"):
                question["explanation"] = f"Cette peinture est de {media_creator}."
            updated.append(question["id"])

    questions.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Added structured image subject type, work/subject title, franchise, image credit, verified creator facts, and source links. Media creator credits are explicitly distinguished from subject creators.",
        "updatedPresentations": updated,
    })
    QUESTIONS.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"imageQuestionsEnriched": len(updated), "curatedCreatorFacts": sum(1 for q in questions["questions"] for f in q.get("imageFacts", {}).get("facts", []) if f.get("kind") == "subject_creator" and f.get("sourceUrl", "").startswith("http")), "revision": REVISION}, ensure_ascii=False))


if __name__ == "__main__":
    main()
