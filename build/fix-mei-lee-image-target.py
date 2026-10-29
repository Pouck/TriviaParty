"""Replace a mislabeled Pixar cosplay photo with the verified Carl/Russell photo."""
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

BANK = ROOT / "game-library/bank/questions.json"
CREDITS = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA = ROOT / "game-library/bank/media"
OLD_ID = "image-qsj-personnages-pixar-mei-lee-turning-red"
NEW_ID = "image-qsj-personnages-pixar-carl-fredricksen"
FILE = "File:D23 Expo 2011 - Carl Fredrickson and Russell from Pixar's Up (6075272345).jpg"


def main() -> None:
    data = json.loads(BANK.read_text(encoding="utf-8"))
    if any(r.get("id") == "2026-10-26-fix-mei-lee-image-target" for r in data.get("revisionHistory", [])):
        print("The Pixar image target has already been corrected.")
        return
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    response = collector.api({
        "action": "query", "titles": FILE, "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": 1100, "format": "json",
    })
    page = next((p for p in response.get("query", {}).get("pages", {}).values() if p.get("imageinfo")), None)
    if page is None:
        raise ValueError(f"Commons file is unavailable: {FILE}")
    info = page["imageinfo"][0]
    ext = info.get("extmetadata", {})
    licensed, license_name = collector.license_allowed(ext)
    if not licensed or "carl fredrickson" not in collector.norm(FILE):
        raise ValueError(f"The replacement source did not pass title/license checks: {license_name}")
    thumb = info["thumburl"].replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
    payload = collector.download(thumb)
    suffix = Path(urllib.parse.urlparse(thumb).path).suffix.lower() or ".jpg"
    media_name = hashlib.sha256(payload).hexdigest()[:24] + suffix

    old_question = next((q for q in data["questions"] if q.get("id") == OLD_ID), None)
    if old_question is None:
        raise ValueError(f"Could not find the mislabeled entry: {OLD_ID}")
    old_media = old_question["presentations"][0].get("content", {}).get("imageUrl", "").removeprefix("media/")
    data["questions"] = [q for q in data["questions"] if q.get("id") != OLD_ID]
    credits.pop(old_media, None)

    category = "Personnages Pixar"
    legacy_category = "Personnages Pixar — Personnages Pixar — Qui suis-je ?"
    presentation = {
        "id": NEW_ID, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
        "topic": "Personnages Pixar", "legacyCategory": legacy_category,
        "legacyPackageId": "image-qsj-personnages-pixar",
        "content": {"kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                    "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
                    "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0},
    }
    question = {"id": NEW_ID, "legacyIds": [NEW_ID], "topics": ["Personnages Pixar"],
                "prompt": "Qui suis-je ?", "answers": ["Carl Fredricksen", "Carl"], "content": {},
                "presentations": [presentation], "legacyReviews": []}
    data["questions"].append(question)
    source_title = FILE.removeprefix("File:")
    credits[media_name] = {
        "filename": source_title, "title": source_title,
        "creator": collector.plain(ext.get("Artist", {}).get("value", "")),
        "credit": collector.plain(ext.get("Credit", {}).get("value", "")),
        "license": collector.plain(ext.get("LicenseShortName", {}).get("value", "")),
        "licenseUrl": collector.plain(ext.get("LicenseUrl", {}).get("value", "")),
        "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(source_title.replace(" ", "_"), safe=":()_,'-"),
        "downloadedFrom": thumb, "localSource": "Wikimedia Commons thumbnail, resized to 1100 px width",
        "question": "Carl Fredricksen", "category": legacy_category,
    }
    (MEDIA / media_name).write_bytes(payload)
    remaining_refs = {p.get("content", {}).get("imageUrl", "").removeprefix("media/")
                      for q in data["questions"] for p in q.get("presentations", [])}
    if old_media and old_media not in remaining_refs:
        old_path = MEDIA / old_media
        if old_path.exists():
            old_path.unlink()
    data.setdefault("revisionHistory", []).append({
        "id": "2026-10-26-fix-mei-lee-image-target",
        "note": "Replaced an image depicting Sulley with a licensed photo of Carl Fredricksen and Russell.",
        "removedPresentationIds": [OLD_ID], "createdQuestions": 1,
        "addedPresentationsToExistingQuestions": 0, "presentationIds": [NEW_ID],
    })
    BANK.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Replaced {OLD_ID} with {NEW_ID} using {license_name} media.")


if __name__ == "__main__":
    main()
