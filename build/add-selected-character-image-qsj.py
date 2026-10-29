"""Add a small, individually reviewed starter set of character photographs."""
from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MEDIA_DIR = ROOT / "game-library/bank/media"
CREDITS_PATH = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
REVISION_ID = "2026-10-26-character-photo-starter"
UA = "TriviaParty/1.0 (private educational game; Commons attribution recorded)"

# answer, alternatives, topic, category, image URL, Commons file page, author,
# license label, license URL, reveal mode, optional existing bank question id
ITEMS = [
    ("Spider-Man", ["Spiderman", "Peter Parker"], "Super-héros", "Héros Marvel",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Spider-Man_cosplay.jpg/1280px-Spider-Man_cosplay.jpg",
     "https://commons.wikimedia.org/wiki/File:Spider-Man_cosplay.jpg", "ManoSolo13241324", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/", "SHUFFLE", "lib-buzzer-marvel-20261012-02"),
    ("Batman", ["Bruce Wayne"], "Super-héros", "Héros DC",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Batman_cosplayer_%2826892483334%29.jpg/1280px-Batman_cosplayer_%2826892483334%29.jpg",
     "https://commons.wikimedia.org/wiki/File:Batman_cosplayer_(26892483334).jpg", "Gage Skidmore", "CC BY-SA 2.0", "https://creativecommons.org/licenses/by-sa/2.0/", "PIXELATE", "lib-qsj-dc-20261012-02"),
    ("Buzz l’Éclair", ["Buzz Lightyear", "Buzz"], "Cinéma", "Personnages Pixar",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Buzz_Lightyear_cosplayer_%2852109894037%29.jpg/1280px-Buzz_Lightyear_cosplayer_%2852109894037%29.jpg",
     "https://commons.wikimedia.org/wiki/File:Buzz_Lightyear_cosplayer_(52109894037).jpg", "Gage Skidmore", "CC BY-SA 2.0", "https://creativecommons.org/licenses/by-sa/2.0/", "UNCOVER", None),
    ("Naruto Uzumaki", ["Naruto"], "BD et manga", "Personnages de manga",
     "https://upload.wikimedia.org/wikipedia/commons/1/17/Cosplayer_of_Naruto_Uzumaki_from_Naruto_20150628c.jpg",
     "https://commons.wikimedia.org/wiki/File:Cosplayer_of_Naruto_Uzumaki_from_Naruto_20150628c.jpg", "八木清介", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/", "BLUR", "lib-buzzer-manga-20261012-04"),
    ("Astérix", ["Asterix"], "BD et manga", "BD — Personnages de bande dessinée",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Statue_%C3%A0_Ast%C3%A9rix.jpg/1280px-Statue_%C3%A0_Ast%C3%A9rix.jpg",
     "https://commons.wikimedia.org/wiki/File:Statue_%C3%A0_Ast%C3%A9rix.jpg", "Mathious Ier", "CC0", "https://creativecommons.org/publicdomain/zero/1.0/", "UNCOVER", "lib-qsj-bd-franco-belge-20261012-01"),
    ("Bob l’éponge", ["SpongeBob", "SpongeBob SquarePants"], "Culture populaire", "Personnages de dessins animés",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Spongebob_hugs_a_fan_%283689068930%29.jpg/1280px-Spongebob_hugs_a_fan_%283689068930%29.jpg",
     "https://commons.wikimedia.org/wiki/File:Spongebob_hugs_a_fan_(3689068930).jpg", "Shaun C. Williams", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/", "PIXELATE", None),
    ("Mickey Mouse", ["Mickey"], "Cinéma", "Personnages Disney",
     "https://upload.wikimedia.org/wikipedia/commons/d/d4/Mickey_Mouse.png",
     "https://commons.wikimedia.org/wiki/File:Mickey_Mouse.png", "Walt Disney and Ub Iwerks", "Public domain (1928; U.S. publication before 1931)", "https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/United_States", "UNCOVER", None),
]


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return re.sub(r"^(le|la|les|l|un|une|des|the)\s+", "", value)


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", norm(value)).strip("-")


def main() -> None:
    data = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION_ID for row in data.get("revisionHistory", [])):
        print("The reviewed starter images are already present; no changes made.")
        return
    credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8")) if CREDITS_PATH.exists() else {}
    questions = data["questions"]
    by_id = {q["id"]: q for q in questions}
    answer_index = {}
    used_ids = {alias for q in questions for alias in q["legacyIds"]}
    for q in questions:
        for answer in q.get("answers", []):
            answer_index.setdefault(norm(answer), []).append(q)

    presentation_ids = []
    created = attached = 0
    for answer, aliases, topic, category, url, source, creator, license_name, license_url, mode, target_id in ITEMS:
        request = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://commons.wikimedia.org/"})
        with urllib.request.urlopen(request, timeout=40) as response:
            image_bytes = response.read()
        extension = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
        media_name = hashlib.sha256(image_bytes).hexdigest()[:24] + extension
        media_path = MEDIA_DIR / media_name
        if not media_path.exists():
            media_path.write_bytes(image_bytes)

        category_slug = safe_slug(category)
        character_slug = safe_slug(answer)
        presentation_id = f"image-qsj-{category_slug}-{character_slug}"
        if presentation_id in used_ids:
            raise ValueError(f"Presentation ID already exists: {presentation_id}")
        presentation = {
            "id": presentation_id, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
            "topic": topic, "legacyCategory": f"{topic} — {category} — Qui suis-je ?",
            "legacyPackageId": "image-qsj-" + category_slug,
            "content": {"kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                        "imageRevealMode": mode, "imageRevealSteps": 6,
                        "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0},
        }
        target = by_id.get(target_id) if target_id else None
        if target is None:
            target = next((answer_index[norm(value)][0] for value in [answer, *aliases]
                           if answer_index.get(norm(value))), None)
        if target:
            target["presentations"].append(presentation)
            target["legacyIds"].append(presentation_id)
            if topic not in target["topics"]:
                target["topics"].append(topic)
            attached += 1
        else:
            question = {"id": presentation_id, "legacyIds": [presentation_id], "topics": [topic],
                        "prompt": "Qui suis-je ?", "answers": list(dict.fromkeys([answer, *aliases])),
                        "content": {}, "presentations": [presentation], "legacyReviews": []}
            questions.append(question)
            for name in question["answers"]:
                answer_index.setdefault(norm(name), []).append(question)
            created += 1
        used_ids.add(presentation_id)
        presentation_ids.append(presentation_id)
        credits[media_name] = {
            "filename": Path(urllib.parse.urlparse(url).path).name,
            "title": Path(urllib.parse.urlparse(source).path).name.removeprefix("File:"),
            "creator": creator, "credit": creator, "license": license_name, "licenseUrl": license_url,
            "source": source, "downloadedFrom": url, "localSource": "Wikimedia Commons; downloaded unchanged",
            "question": answer, "category": presentation["legacyCategory"],
        }
        time.sleep(0.8)

    data.setdefault("revisionHistory", []).append({
        "id": REVISION_ID, "note": "Added seven individually reviewed character images with Commons source and license records.",
        "createdQuestions": created, "addedPresentationsToExistingQuestions": attached,
        "presentationIds": presentation_ids,
    })
    BANK_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(presentation_ids)} character presentations ({created} new entries, {attached} attached to existing questions).")


if __name__ == "__main__":
    main()
