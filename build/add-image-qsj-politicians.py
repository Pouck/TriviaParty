"""Add public/free-licensed portraits for politician Qui suis-je? questions."""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MEDIA_DIR = ROOT / "game-library/bank/media"
CREDITS_PATH = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
UA = "TriviaParty/1.0 (private educational game; image attribution recorded)"
REVISION_ID = "2026-10-26-politician-image-qsj"

# English Wikipedia title, French answer, French alternatives, short context.
PEOPLE = [
    ("George Washington", "George Washington", ["Washington"], "Premier président des États-Unis."),
    ("Abraham Lincoln", "Abraham Lincoln", ["Lincoln"], "Président des États-Unis pendant la guerre de Sécession."),
    ("Napoleon", "Napoléon Bonaparte", ["Napoléon"], "Empereur des Français et figure majeure de l’histoire européenne."),
    ("Charles de Gaulle", "Charles de Gaulle", ["De Gaulle"], "Chef de la France libre puis président de la République française."),
    ("John A. Macdonald", "John A. Macdonald", ["John Alexander Macdonald"], "Premier ministre fondateur du Canada."),
    ("Wilfrid Laurier", "Wilfrid Laurier", ["Sir Wilfrid Laurier"], "Premier ministre du Canada de 1896 à 1911."),
    ("William Lyon Mackenzie King", "William Lyon Mackenzie King", ["Mackenzie King"], "Premier ministre du Canada pendant une grande partie de la Seconde Guerre mondiale."),
    ("Lester B. Pearson", "Lester B. Pearson", ["Lester Pearson"], "Premier ministre canadien et lauréat du prix Nobel de la paix."),
    ("Pierre Trudeau", "Pierre Elliott Trudeau", ["Pierre Trudeau"], "Premier ministre du Canada et père de la Constitution de 1982."),
    ("Justin Trudeau", "Justin Trudeau", [], "Premier ministre du Canada de 2015 à 2025."),
    ("Franklin D. Roosevelt", "Franklin D. Roosevelt", ["F. D. Roosevelt", "FDR"], "Président des États-Unis pendant la Grande Dépression et la Seconde Guerre mondiale."),
    ("Winston Churchill", "Winston Churchill", ["Churchill"], "Premier ministre britannique pendant la majeure partie de la Seconde Guerre mondiale."),
    ("Nelson Mandela", "Nelson Mandela", ["Mandela"], "Président sud-africain après l’apartheid et militant anti-apartheid."),
    ("Mahatma Gandhi", "Mahatma Gandhi", ["Gandhi"], "Dirigeant du mouvement pour l’indépendance de l’Inde."),
    ("Rosa Parks", "Rosa Parks", [], "Militante des droits civiques aux États-Unis."),
    ("Martin Luther King Jr.", "Martin Luther King Jr.", ["Martin Luther King"], "Pasteur et dirigeant du mouvement américain des droits civiques."),
    ("Julius Caesar", "Jules César", ["César"], "Général et homme politique romain de la fin de la République."),
    ("Cleopatra", "Cléopâtre", ["Cléopâtre VII"], "Reine d’Égypte de la dynastie ptolémaïque."),
    ("Elizabeth II", "Élisabeth II", ["Elizabeth II", "Reine Élisabeth II"], "Reine du Royaume-Uni et du Canada de 1952 à 2022."),
    ("Barack Obama", "Barack Obama", ["Obama"], "Président des États-Unis de 2009 à 2017."),
]


def api(base: str, params: dict) -> dict:
    url = base + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                return json.load(response)
        except Exception:
            if attempt == 5:
                raise
            time.sleep(4 * (attempt + 1))
    raise RuntimeError("Unreachable")


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(value: str) -> str:
    parser = TextOnly()
    parser.feed(value or "")
    return re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return re.sub(r"^(le|la|les|l|un|une|des|the)\s+", "", value)


def main() -> None:
    data = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION_ID for row in data.get("revisionHistory", [])):
        print("Politician image questions are already present; no changes made.")
        return

    titles = [person[0] for person in PEOPLE]
    pages = api("https://en.wikipedia.org/w/api.php", {
        "action": "query", "titles": "|".join(titles), "prop": "pageimages",
        "piprop": "name", "redirects": 1, "format": "json",
    })["query"]["pages"].values()
    image_by_title = {}
    for page in pages:
        if page.get("pageimage"):
            image_by_title[page["title"]] = page["pageimage"]
    if len(image_by_title) < len(PEOPLE):
        missing = sorted(set(titles) - set(image_by_title))
        raise RuntimeError(f"No Wikipedia lead image found for: {', '.join(missing)}")

    file_titles = ["File:" + image_by_title[title].replace("_", " ") for title in image_by_title]
    info = api("https://commons.wikimedia.org/w/api.php", {
        "action": "query", "titles": "|".join(file_titles), "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": 1100, "format": "json",
    })["query"]["pages"].values()
    by_file = {page["title"].replace("_", " "): page.get("imageinfo", [{}])[0] for page in info}

    questions = data["questions"]
    by_id = {q["id"]: q for q in questions}
    answer_index: dict[str, list[dict]] = {}
    legacy_ids = {alias for q in questions for alias in q["legacyIds"]}
    for q in questions:
        for answer in q.get("answers", []):
            answer_index.setdefault(norm(answer), []).append(q)

    credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8")) if CREDITS_PATH.exists() else {}
    created = attached = 0
    presentation_ids = []
    for page_title, answer, aliases, explanation in PEOPLE:
        file_title = "File:" + image_by_title[page_title].replace("_", " ")
        image_info = by_file.get(file_title)
        if not image_info or not image_info.get("thumburl"):
            raise RuntimeError(f"Commons image metadata not found for {page_title}: {file_title}")
        meta = image_info.get("extmetadata", {})
        license_name = plain(meta.get("LicenseShortName", {}).get("value", ""))
        if not (license_name.startswith("CC BY") or license_name in {"CC0", "Public domain"}):
            raise RuntimeError(f"Image license needs manual review for {page_title}: {license_name}")

        thumbnail_url = image_info["thumburl"].replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
        request = urllib.request.Request(thumbnail_url, headers={"User-Agent": UA, "Referer": "https://commons.wikimedia.org/"})
        for attempt in range(6):
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    image_bytes = response.read()
                break
            except urllib.error.HTTPError as error:
                if error.code != 429 or attempt == 5:
                    raise
                time.sleep(10 * (attempt + 1))
        extension = Path(urllib.parse.urlparse(thumbnail_url).path).suffix.lower() or ".jpg"
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            extension = ".jpg"
        digest = hashlib.sha256(image_bytes).hexdigest()
        media_name = digest[:24] + extension
        media_path = MEDIA_DIR / media_name
        if not media_path.exists():
            media_path.write_bytes(image_bytes)

        slug = re.sub(r"[^a-z0-9]+", "-", norm(page_title)).strip("-")
        presentation_id = f"image-qsj-figures-politiques-{slug}"
        if presentation_id in legacy_ids:
            raise ValueError(f"Presentation ID already exists: {presentation_id}")
        presentation_ids.append(presentation_id)
        presentation = {
            "id": presentation_id,
            "label": "Qui suis-je ? — image",
            "answerMode": "BUZZER",
            "topic": "Histoire",
            "legacyCategory": "Histoire — Personnalités politiques — Qui suis-je ?",
            "legacyPackageId": "image-qsj-figures-politiques",
            "content": {
                "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                "imageRevealMode": "BLUR", "imageRevealSteps": 6,
                "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0,
            },
        }

        targets = []
        for candidate in [answer, *aliases]:
            if answer_index.get(norm(candidate)):
                targets = [answer_index[norm(candidate)][0]]
                break
        if targets:
            targets[0]["presentations"].append(presentation)
            targets[0]["legacyIds"].append(presentation_id)
            attached += 1
        else:
            question = {
                "id": presentation_id, "legacyIds": [presentation_id], "topics": ["Histoire"],
                "prompt": "Qui suis-je ?", "answers": [answer, *aliases], "content": {},
                "presentations": [presentation], "explanation": explanation, "legacyReviews": [],
            }
            questions.append(question)
            by_id[question["id"]] = question
            for name in question["answers"]:
                answer_index.setdefault(norm(name), []).append(question)
            created += 1
        legacy_ids.add(presentation_id)

        source_file = file_title.removeprefix("File:")
        credits[media_name] = {
            "filename": source_file,
            "title": page_title,
            "creator": plain(meta.get("Artist", {}).get("value", "")),
            "credit": plain(meta.get("Credit", {}).get("value", "")),
            "license": license_name,
            "licenseUrl": plain(meta.get("LicenseUrl", {}).get("value", "")),
            "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(file_title.replace(" ", "_"), safe=":()_,'-"),
            "downloadedFrom": thumbnail_url,
            "localSource": "Wikimedia Commons thumbnail, resized to 1100 px width",
            "question": answer,
            "category": presentation["legacyCategory"],
        }
        time.sleep(1.0)

    data.setdefault("revisionHistory", []).append({
        "id": REVISION_ID,
        "note": "Added 20 six-stage portrait-identification presentations with Wikimedia Commons attribution metadata.",
        "createdQuestions": created,
        "addedPresentationsToExistingQuestions": attached,
        "presentationIds": presentation_ids,
    })
    BANK_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(presentation_ids)} politician image presentations ({created} new entries, {attached} attached to existing questions).")


if __name__ == "__main__":
    main()
