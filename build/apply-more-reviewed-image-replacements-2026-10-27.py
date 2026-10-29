"""Apply the verified NOAA single-whale replacement from the image review."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
CREDITS = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA = BANK / "media"
BACKUPS = ROOT / "review-backups"
REVIEW = ROOT / "build/image-qsj-gallery/review-imported-2026-10-27.json"
REVISION = "2026-10-27-noaa-single-sperm-whale-replacement"
PRESENTATION_ID = "image-qsj-nature-whale"
CANDIDATE = ROOT / "build/image-qsj-sampler/candidates/review-replacements-2026-10-27/sperm-whale-noaa.jpg"
SOURCE = "https://www.fisheries.noaa.gov/science-blog/diving-deep-sperm-whale-clicks"
DIRECT = "https://www.fisheries.noaa.gov/s3/styles/full_width/s3/2026-06/sperm-whale-20250711-sefsc-melissa-cook-permit25867.jpg?itok=ZpwYHTdS"


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(item.get("id") == REVISION for item in bank.get("revisionHistory", [])):
        print("NOAA whale replacement already applied.")
        return
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    target = next((p for q in bank["questions"] for p in q.get("presentations", []) if p.get("id") == PRESENTATION_ID), None)
    if target is None:
        raise ValueError(f"Missing presentation {PRESENTATION_ID}")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    for source, name in ((QUESTIONS, "questions-before-noaa-single-whale.json"),
                         (CREDITS, "credits-before-noaa-single-whale.json")):
        backup = BACKUPS / name
        if not backup.exists():
            shutil.copyfile(source, backup)
    data = CANDIDATE.read_bytes()
    filename = hashlib.sha256(data).hexdigest()[:24] + CANDIDATE.suffix.lower()
    (MEDIA / filename).write_bytes(data)
    target["content"]["imageUrl"] = "media/" + filename
    credits[filename] = {
        "filename": CANDIDATE.name,
        "title": "Sperm whale photographed from above",
        "creator": "Melissa Cook",
        "credit": "NOAA Fisheries/Melissa Cook (Permit #27867)",
        "license": "Public domain; work of the U.S. federal government",
        "licenseUrl": "",
        "source": SOURCE,
        "downloadedFrom": DIRECT,
        "localSource": "NOAA Fisheries single-whale photograph, visually reviewed 2026-10-27",
        "question": "Le cachalot",
        "category": target.get("legacyCategory", ""),
    }
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced the mother-and-calf sperm whale photo with a single sperm whale photograph from NOAA Fisheries, as requested in the image review.",
        "updatedPresentations": 1,
        "presentationIds": [PRESENTATION_ID],
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    review.setdefault("items", {})["gallery-" + filename.rsplit(".", 1)[0]] = {
        "rating": "review",
        "note": "Replacement image selected from your feedback; please review this version.",
    }
    REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"presentationId": PRESENTATION_ID, "image": filename}, indent=2))


if __name__ == "__main__":
    main()
