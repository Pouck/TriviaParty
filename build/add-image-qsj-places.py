"""Grow the visual sculpture, landmark, landscape, and city categories."""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MEDIA_DIR = ROOT / "game-library/bank/media"
CREDITS_PATH = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
UA = "TriviaParty/1.0 (private educational game; image attribution recorded)"
REVISION_ID = "2026-10-26-places-image-qsj"

# Wikipedia article, category topic, French category label, reveal mode, French
# answer, acceptable aliases. Lead images must pass a Commons license check.
ITEMS = [
    # Sculpture: add twelve to bring the separate sculpture category to twenty.
    ("Christ the Redeemer (statue)", "Arts", "Sculptures célèbres", "UNCOVER", "Le Christ Rédempteur", ["Christ Rédempteur"]),
    ("Terracotta Army", "Arts", "Sculptures célèbres", "UNCOVER", "L’armée de terre cuite", ["Armée de terre cuite"]),
    ("Manneken Pis", "Arts", "Sculptures célèbres", "UNCOVER", "Le Manneken-Pis", ["Manneken-Pis"]),
    ("The Little Mermaid (statue)", "Arts", "Sculptures célèbres", "UNCOVER", "La Petite Sirène de Copenhague", ["La Petite Sirène"]),
    ("Great Sphinx of Giza", "Arts", "Sculptures célèbres", "UNCOVER", "Le Grand Sphinx de Gizeh", ["Le Sphinx de Gizeh"]),
    ("Great Buddha of Thailand", "Arts", "Sculptures célèbres", "UNCOVER", "Le Grand Bouddha de Thaïlande", ["Great Buddha of Thailand"]),
    ("The Gates of Hell", "Arts", "Sculptures célèbres", "UNCOVER", "La Porte de l’Enfer de Rodin", ["La Porte de l’Enfer"]),
    ("Angel of the North", "Arts", "Sculptures célèbres", "UNCOVER", "L’Ange du Nord", ["Angel of the North"]),
    ("Mamayev Kurgan", "Arts", "Sculptures célèbres", "UNCOVER", "La Mère-Patrie appelle", ["The Motherland Calls"]),
    ("Statue of Unity", "Arts", "Sculptures célèbres", "UNCOVER", "La Statue de l’Unité", ["Statue of Unity"]),
    ("Maman (sculpture)", "Arts", "Sculptures célèbres", "UNCOVER", "Maman de Louise Bourgeois", ["Maman"]),
    ("Puppy (sculpture)", "Arts", "Sculptures célèbres", "UNCOVER", "Puppy de Jeff Koons", ["Puppy"]),

    # Add two architecture entries.
    ("Parthenon", "Architecture", "Monuments et sites célèbres", "SHUFFLE", "Le Parthénon", []),
    ("Notre-Dame de Paris", "Architecture", "Monuments et sites célèbres", "SHUFFLE", "La cathédrale Notre-Dame de Paris", ["Notre-Dame de Paris"]),

    # Landscapes: fourteen new views.
    ("Grand Canyon", "Géographie", "Paysages célèbres", "PIXELATE", "Le Grand Canyon", []),
    ("Niagara Falls", "Géographie", "Paysages célèbres", "PIXELATE", "Les chutes du Niagara", ["Chutes Niagara"]),
    ("Sahara", "Géographie", "Paysages célèbres", "PIXELATE", "Le désert du Sahara", ["Sahara"]),
    ("Great Barrier Reef", "Géographie", "Paysages célèbres", "PIXELATE", "La Grande Barrière de corail", []),
    ("Iguazu Falls", "Géographie", "Paysages célèbres", "PIXELATE", "Les chutes d’Iguazú", ["Chutes d’Iguazú"]),
    ("Alps", "Géographie", "Paysages célèbres", "PIXELATE", "Les Alpes", []),
    ("Banff National Park", "Géographie", "Paysages célèbres", "PIXELATE", "Le parc national de Banff", ["Banff"]),
    ("Yellowstone National Park", "Géographie", "Paysages célèbres", "PIXELATE", "Le parc national de Yellowstone", ["Yellowstone"]),
    ("Victoria Falls", "Géographie", "Paysages célèbres", "PIXELATE", "Les chutes Victoria", []),
    ("Lake Louise (Alberta)", "Géographie", "Paysages célèbres", "PIXELATE", "Le lac Louise", ["Lake Louise"]),
    ("Mount Kilimanjaro", "Géographie", "Paysages célèbres", "PIXELATE", "Le Kilimandjaro", ["Mont Kilimandjaro"]),
    ("Aurora", "Géographie", "Paysages célèbres", "PIXELATE", "Une aurore boréale", ["Aurore boréale"]),
    ("Yosemite Valley", "Géographie", "Paysages célèbres", "PIXELATE", "La vallée de Yosemite", ["Yosemite"]),
    ("Uluru", "Géographie", "Paysages célèbres", "PIXELATE", "Uluru", ["Ayers Rock"]),

    # Cities: twelve more, each identified by a distinctive city view.
    ("New York City", "Géographie", "Villes célèbres en images", "UNCOVER", "New York", ["New York City"]),
    ("London", "Géographie", "Villes célèbres en images", "UNCOVER", "Londres", []),
    ("Tokyo", "Géographie", "Villes célèbres en images", "UNCOVER", "Tokyo", []),
    ("Istanbul", "Géographie", "Villes célèbres en images", "UNCOVER", "Istanbul", ["Constantinople"]),
    ("Venice", "Géographie", "Villes célèbres en images", "UNCOVER", "Venise", []),
    ("Rio de Janeiro", "Géographie", "Villes célèbres en images", "UNCOVER", "Rio de Janeiro", ["Rio"]),
    ("Hong Kong", "Géographie", "Villes célèbres en images", "UNCOVER", "Hong Kong", []),
    ("Toronto", "Géographie", "Villes célèbres en images", "UNCOVER", "Toronto", []),
    ("Mexico City", "Géographie", "Villes célèbres en images", "UNCOVER", "Mexico", ["Mexico City"]),
    ("Dubai", "Géographie", "Villes célèbres en images", "UNCOVER", "Dubaï", ["Dubai"]),
    ("Moscow", "Géographie", "Villes célèbres en images", "UNCOVER", "Moscou", []),
    ("Prague", "Géographie", "Villes célèbres en images", "UNCOVER", "Prague", []),
]


def request_json(base: str, params: dict) -> dict:
    request = urllib.request.Request(base + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                return json.load(response)
        except Exception:
            if attempt == 5:
                raise
            time.sleep(5 * (attempt + 1))
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
        print("This places and sculpture expansion is already present; no changes made.")
        return

    en_titles = [item[0] for item in ITEMS]
    pages = request_json("https://en.wikipedia.org/w/api.php", {
        "action": "query", "titles": "|".join(en_titles), "prop": "pageimages",
        "piprop": "name", "redirects": 1, "format": "json",
    })["query"]["pages"].values()
    pageimages = {page["title"]: page["pageimage"] for page in pages if page.get("pageimage")}
    missing = sorted(set(en_titles) - set(pageimages))
    if missing:
        raise RuntimeError("No lead image found for: " + ", ".join(missing))

    file_titles = ["File:" + filename.replace("_", " ") for filename in pageimages.values()]
    image_pages = request_json("https://commons.wikimedia.org/w/api.php", {
        "action": "query", "titles": "|".join(file_titles), "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": 1100, "format": "json",
    })["query"]["pages"].values()
    by_file = {page["title"].replace("_", " "): page.get("imageinfo", [{}])[0] for page in image_pages}
    missing_files = [title for title in file_titles if not by_file.get(title.replace("_", " "))]
    if missing_files:
        local_pages = request_json("https://en.wikipedia.org/w/api.php", {
            "action": "query", "titles": "|".join(missing_files), "prop": "imageinfo",
            "iiprop": "url|extmetadata|size", "iiurlwidth": 1100, "format": "json",
        })["query"]["pages"].values()
        by_file.update({page["title"].replace("_", " "): page.get("imageinfo", [{}])[0] for page in local_pages})

    questions = data["questions"]
    answer_index: dict[str, list[dict]] = {}
    ids = {alias for q in questions for alias in q["legacyIds"]}
    for q in questions:
        for answer in q.get("answers", []):
            answer_index.setdefault(norm(answer), []).append(q)
    credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8")) if CREDITS_PATH.exists() else {}
    presentation_ids: list[str] = []
    created = attached = 0

    for article, topic, category, mode, answer, aliases in ITEMS:
        file_title = "File:" + pageimages[article].replace("_", " ")
        info = by_file.get(file_title)
        if not info or not info.get("thumburl"):
            raise RuntimeError(f"No Commons file page for {article}: {file_title}")
        meta = info.get("extmetadata", {})
        license_name = plain(meta.get("LicenseShortName", {}).get("value", ""))
        if not (license_name.startswith(("CC BY", "CC-BY")) or license_name in {"CC0", "Public domain"}):
            raise RuntimeError(f"License needs manual review for {article}: {license_name}")

        url = info["thumburl"].replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
        request = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://commons.wikimedia.org/"})
        image_bytes = None
        for attempt in range(6):
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    image_bytes = response.read()
                break
            except urllib.error.HTTPError as error:
                if error.code != 429 or attempt == 5:
                    raise
                time.sleep(10 * (attempt + 1))
        if not image_bytes:
            raise RuntimeError(f"Could not download image for {article}")
        extension = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            extension = ".jpg"
        digest = hashlib.sha256(image_bytes).hexdigest()
        media_name = digest[:24] + extension
        media_path = MEDIA_DIR / media_name
        if not media_path.exists():
            media_path.write_bytes(image_bytes)

        slug = re.sub(r"[^a-z0-9]+", "-", norm(article)).strip("-")
        presentation_id = f"image-qsj-{slug}"
        if presentation_id in ids:
            raise ValueError(f"Presentation ID already exists: {presentation_id}")
        presentation = {
            "id": presentation_id, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
            "topic": topic, "legacyCategory": f"{topic} — {category} — Qui suis-je ?",
            "legacyPackageId": "image-qsj-" + re.sub(r"[^a-z0-9]+", "-", norm(category)).strip("-"),
            "content": {
                "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                "imageRevealMode": mode, "imageRevealSteps": 6,
                "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0,
            },
        }
        targets = next((answer_index[norm(value)] for value in [answer, *aliases] if answer_index.get(norm(value))), [])
        if targets:
            targets[0]["presentations"].append(presentation)
            targets[0]["legacyIds"].append(presentation_id)
            attached += 1
        else:
            question = {
                "id": presentation_id, "legacyIds": [presentation_id], "topics": [topic],
                "prompt": "Qui suis-je ?", "answers": [answer, *aliases], "content": {},
                "presentations": [presentation], "legacyReviews": [],
            }
            questions.append(question)
            for name in question["answers"]:
                answer_index.setdefault(norm(name), []).append(question)
            created += 1
        ids.add(presentation_id)
        source_domain = "commons.wikimedia.org" if "/commons/" in urllib.parse.urlparse(url).path else "en.wikipedia.org"
        credits[media_name] = {
            "filename": file_title.removeprefix("File:"), "title": article,
            "creator": plain(meta.get("Artist", {}).get("value", "")),
            "credit": plain(meta.get("Credit", {}).get("value", "")),
            "license": license_name, "licenseUrl": plain(meta.get("LicenseUrl", {}).get("value", "")),
            "source": f"https://{source_domain}/wiki/" + urllib.parse.quote(file_title.replace(" ", "_"), safe=":()_,'-"),
            "downloadedFrom": url, "localSource": "Wikimedia Commons thumbnail, resized to 1100 px width",
            "question": answer, "category": presentation["legacyCategory"],
        }
        presentation_ids.append(presentation_id)
        time.sleep(1)

    data.setdefault("revisionHistory", []).append({
        "id": REVISION_ID, "note": "Expanded picture rounds with sourced sculpture, landmark, landscape and city images.",
        "createdQuestions": created, "addedPresentationsToExistingQuestions": attached,
        "presentationIds": presentation_ids,
    })
    BANK_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(presentation_ids)} place/sculpture image questions ({created} new entries, {attached} attached).")


if __name__ == "__main__":
    main()
