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
CANDIDATE = ROOT / "build/image-qsj-sampler/candidates/pantheon-rome-front.jpg"
REVIEW = ROOT / "build/image-qsj-gallery/review-imported-2026-10-28-0312Z.json"
REVISION = "image-qsj-pantheon-more-complete-exterior-2026-10-28"
PRESENTATION_ID = "image-qsj-building-053"
SOURCE = "https://commons.wikimedia.org/wiki/File:Rome_Pantheon_front.jpg"


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
        print("Pantheon exterior replacement already applied.")
        return
    questions = next((q for q in bank["questions"] if any(p.get("id") == PRESENTATION_ID for p in q.get("presentations", []))), None)
    if questions is None:
        raise ValueError(f"Missing question presentation: {PRESENTATION_ID}")
    presentation = next(p for p in questions["presentations"] if p.get("id") == PRESENTATION_ID)
    data = CANDIDATE.read_bytes()
    filename = hashlib.sha256(data).hexdigest()[:24] + ".jpg"
    (MEDIA / filename).write_bytes(data)
    backup_dir = ROOT / "review-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for source, name in (
        (QUESTIONS, "questions-before-pantheon-exterior-replacement-2026-10-28.json"),
        (CREDITS, "credits-before-pantheon-exterior-replacement-2026-10-28.json"),
        (REVIEW, "gallery-review-before-pantheon-exterior-replacement-2026-10-28.json"),
    ):
        backup = backup_dir / name
        if not backup.exists():
            shutil.copyfile(source, backup)
    presentation["content"]["imageUrl"] = "media/" + filename
    source_url = "https://commons.wikimedia.org/wiki/File:Rome_Pantheon_front.jpg"
    credits[filename] = {
        "filename": "Rome_Pantheon_front.jpg",
        "title": "The Pantheon in Rome — front and rotunda",
        "creator": "Roberta Dragan",
        "credit": "Roberta Dragan / Wikimedia Commons",
        "license": "CC BY-SA 2.5",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/2.5/",
        "source": source_url,
        "downloadedFrom": "https://upload.wikimedia.org/wikipedia/commons/0/06/Rome_Pantheon_front.jpg",
        "localSource": "build/image-qsj-sampler/candidates/pantheon-rome-front.jpg",
        "question": "Panthéon de Rome",
        "category": presentation.get("legacyCategory", ""),
        "visualReview": "Full exterior view includes the portico and the cylindrical rotunda behind it; inscription is historical façade lettering and does not give the building's name.",
    }
    questions["imageFacts"] = {
        **questions.get("imageFacts", {}),
        "subjectTitle": "Pantheon Rome",
        "frenchTitle": "Panthéon de Rome",
        "facts": [
            {"kind": "subject_title", "value": "Pantheon Rome", "sourceUrl": source_url},
            {"kind": "media_creator", "role": "photographer", "value": "Roberta Dragan", "sourceUrl": source_url},
        ],
        "sources": [source_url],
    }
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced the distant incomplete Pantheon view with a full exterior photograph showing the portico and rotunda, addressing the latest gallery review.",
        "updatedPresentations": 1,
        "presentationIds": [PRESENTATION_ID],
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_doc = json.loads(REVIEW.read_text(encoding="utf-8"))
    review_doc.setdefault("items", {})["gallery-" + filename.removesuffix(".jpg")] = {
        "rating": "review",
        "note": "Pantheon replacement, chosen to show both the portico and rotunda; please review.",
    }
    REVIEW.write_text(json.dumps(review_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"presentation": PRESENTATION_ID, "image": filename}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
