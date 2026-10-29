"""Replace missed character image targets with individually verified Commons files."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("character_collector", ROOT / "build/add-image-qsj-characters.py")
collector = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = collector
spec.loader.exec_module(collector)

BANK_PATH = ROOT / "game-library/bank/questions.json"
CREDITS_PATH = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA_DIR = ROOT / "game-library/bank/media"
REVISION_ID = "2026-10-26-character-image-qsj-verified-replacements"

# Four candidates from the first replacement pass proved unrelated on visual
# review. Remove those entries, then add only the explicitly named files below.
REJECT_IDS = {
    "image-qsj-bd-personnages-de-bande-dessinee-blueberry-comics",
    "image-qsj-bd-personnages-de-bande-dessinee-xiii-comics",
    "image-qsj-personnages-pixar-dug-up",
    "image-qsj-personnages-pixar-rex-toy-story",
}

# topic, category, name, accepted answer, aliases, Commons file, proof text
TARGETS = [
    ("BD et manga", "BD - Personnages de bande dessinée", "Suske en Wiske", "Suske en Wiske", ["Spike and Suzy"], "File:Suske en Wiske Middelkerke.jpg", "suske en wiske"),
    ("BD et manga", "BD - Personnages de bande dessinée", "Jommeke", "Jommeke", ["Jeremy"], "File:Temse statue Jommeke 01.jpg", "jommeke"),
    ("BD et manga", "BD - Personnages de bande dessinée", "Mafalda", "Mafalda", [], "File:Estatua de Mafalda en Lima, Perú 05.jpg", "mafalda"),
    ("BD et manga", "BD - Personnages de bande dessinée", "Jerom", "Jerom", [], "File:Statue of Jerom from Suske en Wiske on Zeedijk, Middelkerke (DSCF9898).jpg", "jerom"),
    ("BD et manga", "BD - Personnages de bande dessinée", "Le Chat de Philippe Geluck", "Le Chat de Philippe Geluck", ["Le Chat"], "File:Chat-Genève-04a.jpg", "philippe geluck"),
    ("Dessins animés", "Personnages de dessins animés", "Hello Kitty", "Hello Kitty", [], "File:Hello Kitty 2016 (29085848864).jpg", "hello kitty"),
    ("Personnages Pixar", "Personnages Pixar", "Bo Peep (Toy Story)", "Bo Peep", ["La Bergère"], "File:Cosplay at Lucca Comics 2017 - Woody and Bo Peep.jpg", "bo peep"),
    ("Personnages Pixar", "Personnages Pixar", "Forky", "Forky", ["Fourchette"], "File:Cosplay attribute of Forky from Toy Story at Brussels Comic Con 2022 (51960795536).jpg", "forky"),
    ("Personnages Pixar", "Personnages Pixar", "Sulley", "Sulli", ["Sulley"], "File:NTF 2014 - Monsters Inc Sully (15799522115).jpg", "sully"),
    ("Personnages Pixar", "Personnages Pixar", "Mr. Incredible", "M. Indestructible", ["Mr Incredible"], "File:NYCC 2013 - Mister Incredible (10311547144).jpg", "mister incredible"),
    ("Personnages Pixar", "Personnages Pixar", "Mei Lee (Turning Red)", "Mei Lee", ["Meilin Lee"], "File:Cosplay of Mei Lee at Made in Asia 2022 (52124212089).jpg", "mei lee"),
    ("Personnages Pixar", "Personnages Pixar", "Sarge (Toy Story)", "Sarge", ["Sergeant"], "File:Sarge (Toy Story).jpg", "sarge"),
    ("Personnages Pixar", "Personnages Pixar", "Green Army Men (Toy Story)", "Les soldats verts de Toy Story", ["Green Army Men"], "File:Cosplay of Green Army Men (Toy Story) Disney Pixar Pier (July 2023).JPG", "green army men"),
    ("Héros DC", "Héros DC", "Black Canary", "Black Canary", ["Dinah Lance"], "File:New York Comic Con 2017 Cosplay of Black Canary.jpg", "black canary"),
    ("Personnages de manga", "Personnages de manga", "Itachi Uchiha", "Itachi Uchiha", ["Itachi"], "File:Cosplay d'Itachi Uchiwa @aanthonym.jpg", "itachi"),
]


def main() -> None:
    data = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION_ID for row in data.get("revisionHistory", [])):
        print("Verified replacement images are already present; no changes made.")
        return

    credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8"))
    removed_media = set()
    for question in data.get("questions", []):
        if question.get("id") in REJECT_IDS:
            for presentation in question.get("presentations", []):
                if presentation.get("id") in REJECT_IDS:
                    removed_media.add(presentation.get("content", {}).get("imageUrl", "").removeprefix("media/"))
    data["questions"] = [q for q in data["questions"] if q.get("id") not in REJECT_IDS]
    for media_name in removed_media:
        credits.pop(media_name, None)

    file_titles = [target[5] for target in TARGETS]
    metadata = {}
    for start in range(0, len(file_titles), 35):
        response = collector.api({
            "action": "query", "titles": "|".join(file_titles[start:start + 35]),
            "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1100,
            "format": "json",
        })
        for page in response.get("query", {}).get("pages", {}).values():
            if page.get("imageinfo"):
                metadata[page["title"]] = page["imageinfo"][0]

    for target in TARGETS:
        topic, category, name, answer, aliases, file_title, proof = target
        info = metadata.get(file_title)
        if not info or not info.get("thumburl"):
            raise ValueError(f"Commons file is unavailable: {file_title}")
        license_ok, license_name = collector.license_allowed(info.get("extmetadata", {}))
        if not license_ok:
            raise ValueError(f"Commons license is not allowed: {file_title} ({license_name})")
        ext = info.get("extmetadata", {})
        searchable = (file_title + " " + collector.plain(ext.get("ImageDescription", {}).get("value", ""))).casefold()
        if proof not in collector.norm(searchable):
            raise ValueError(f"Subject check failed for {file_title}: expected {proof!r}")

    questions = data["questions"]
    used_ids = {legacy_id for q in questions for legacy_id in q.get("legacyIds", [])}
    staged = []
    for index, target in enumerate(TARGETS):
        topic, category, name, answer, aliases, file_title, proof = target
        info = metadata[file_title]
        ext = info.get("extmetadata", {})
        thumb_url = info["thumburl"].replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
        image_bytes = collector.download(thumb_url)
        extension = Path(urllib.parse.urlparse(thumb_url).path).suffix.lower() or ".jpg"
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            extension = ".jpg"
        media_name = hashlib.sha256(image_bytes).hexdigest()[:24] + extension
        if media_name in credits:
            raise ValueError(f"Replacement media is already credited: {media_name}")
        category_slug = re.sub(r"[^a-z0-9]+", "-", collector.norm(category)).strip("-")
        character_slug = re.sub(r"[^a-z0-9]+", "-", collector.norm(name)).strip("-")
        presentation_id = f"image-qsj-{category_slug}-{character_slug}"
        if presentation_id in used_ids:
            raise ValueError(f"Presentation ID already exists: {presentation_id}")
        presentation = {
            "id": presentation_id, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
            "topic": topic,
            "legacyCategory": f"{topic} — {category} — Qui suis-je ?",
            "legacyPackageId": "image-qsj-" + category_slug,
            "content": {"kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                        "imageRevealMode": ("PIXELATE", "UNCOVER", "SHUFFLE", "BLUR")[index % 4],
                        "imageRevealSteps": 6, "imageUrl": "media/" + media_name,
                        "basePoints": 30, "penaltyPoints": 0},
        }
        aliases = list(dict.fromkeys([answer, *aliases, name]))
        question = {"id": presentation_id, "legacyIds": [presentation_id], "topics": [topic],
                    "prompt": "Qui suis-je ?", "answers": aliases, "content": {},
                    "presentations": [presentation], "legacyReviews": []}
        source_title = file_title.removeprefix("File:")
        credit = {
            "filename": source_title, "title": source_title,
            "creator": collector.plain(ext.get("Artist", {}).get("value", "")),
            "credit": collector.plain(ext.get("Credit", {}).get("value", "")),
            "license": collector.plain(ext.get("LicenseShortName", {}).get("value", "")),
            "licenseUrl": collector.plain(ext.get("LicenseUrl", {}).get("value", "")),
            "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(source_title.replace(" ", "_"), safe=":()_,'-"),
            "downloadedFrom": thumb_url, "localSource": "Wikimedia Commons thumbnail, resized to 1100 px width",
            "question": answer, "category": presentation["legacyCategory"],
        }
        staged.append((question, media_name, image_bytes, credit, presentation_id))

    for media_name in removed_media:
        if media_name:
            old_path = MEDIA_DIR / media_name
            if old_path.exists():
                old_path.unlink()
    for question, media_name, image_bytes, credit, presentation_id in staged:
        (MEDIA_DIR / media_name).write_bytes(image_bytes)
        questions.append(question)
        credits[media_name] = credit
        used_ids.add(presentation_id)

    data.setdefault("revisionHistory", []).append({
        "id": "2026-10-26-rejected-ambiguous-character-images",
        "note": "Removed four character image entries whose Commons files depicted unrelated subjects.",
        "removedPresentationIds": sorted(REJECT_IDS),
    })
    data["revisionHistory"].append({
        "id": REVISION_ID,
        "note": "Filled character category gaps with individually verified, freely licensed Commons images.",
        "createdQuestions": len(staged), "addedPresentationsToExistingQuestions": 0,
        "presentationIds": [row[4] for row in staged],
    })
    BANK_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Replaced 4 incorrect entries and added {len(staged)} verified character images.")
    print(f"Saved {len(data['questions'])} bank entries and {len(credits)} media credits.")


if __name__ == "__main__":
    main()
