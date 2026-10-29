"""Replace the Loki image flagged for missing visual character cues."""
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
REVISION = "2026-10-27-loki-character-cues-image-review"
PRESENTATION_ID = "image-qsj-heros-marvel-loki-marvel-comics"
CANDIDATE = ROOT / "build/image-qsj-sampler/candidates/review-replacements-2026-10-27/loki-official-single.jpeg"
SOURCE = "https://marvel.disney.co.jp/movie/thor-br/character/loki"
DIRECT = "https://lumiere-a.akamaihd.net/v1/images/th_character_12525_12461_139f828f.jpeg?region=0%2C0%2C800%2C800"


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(item.get("id") == REVISION for item in bank.get("revisionHistory", [])):
        print("Loki replacement already applied.")
        return
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    question = None
    target = None
    for q in bank["questions"]:
        for p in q.get("presentations", []):
            if p.get("id") == PRESENTATION_ID:
                question, target = q, p
                break
    if target is None:
        raise ValueError(f"Missing presentation {PRESENTATION_ID}")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    for source, name in ((QUESTIONS, "questions-before-loki-single-character-art.json"),
                         (CREDITS, "credits-before-loki-single-character-art.json")):
        backup = BACKUPS / name
        if not backup.exists():
            shutil.copyfile(source, backup)
    data = CANDIDATE.read_bytes()
    filename = hashlib.sha256(data).hexdigest()[:24] + CANDIDATE.suffix.lower()
    (MEDIA / filename).write_bytes(data)
    target["content"]["imageUrl"] = "media/" + filename
    credits[filename] = {
        "filename": CANDIDATE.name,
        "title": "Loki in his iconic horned helmet and green costume",
        "creator": "Marvel Studios / Marvel Comics; individual artist not identified on source page",
        "credit": "Marvel / Disney Japan",
        "license": "Copyrighted official character image; retained for user's private, noncommercial local app only; not an open redistribution license",
        "licenseUrl": "",
        "source": SOURCE,
        "downloadedFrom": DIRECT,
        "localSource": "Official Marvel Japan character page; visually reviewed 2026-10-27",
        "question": question.get("answers", ["Loki"])[0],
        "category": target.get("legacyCategory", ""),
    }
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced the Loki image with an official Marvel character portrait showing the horned helmet and green costume called out in the image review.",
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
