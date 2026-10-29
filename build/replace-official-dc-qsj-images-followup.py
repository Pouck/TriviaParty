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
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates"
BACKUPS = ROOT / "review-backups"
REVISION = "2026-10-26-replace-more-dc-costume-photos-with-official-art"
SOURCES = {
    "image-qsj-heros-dc-bane-dc-comics": (
        "bane-official.jpg", "Bane", "https://www.dc.com/characters/bane",
        "https://static.dc.com/dc/files/default_images/Char_Thumb_Bane_5c410f07428e44.78856363.jpg",
    ),
    "image-qsj-heros-dc-green-arrow": (
        "green-arrow-official.jpg", "Green Arrow", "https://www.dc.com/characters/green-arrow",
        "https://static.dc.com/dc/files/default_images/Char_Thumb_GreenArrow_5c4915494b3fb9.17530021.jpg",
    ),
    "image-qsj-heros-dc-nightwing": (
        "nightwing-official.jpg", "Nightwing", "https://www.dc.com/characters/nightwing",
        "https://static.dc.com/dc/files/default_images/Char_Thumb_Nightwing_2_5c50fa380942a3.78305981.jpg",
    ),
    "image-qsj-heros-dc-poison-ivy-character": (
        "poison-ivy-official.jpg", "Poison Ivy", "https://www.dc.com/characters/poison-ivy",
        "https://static.dc.com/dc/files/default_images/Char_Thumb_PoisonIvy_5c5252e46f2247.19314178.jpg",
    ),
}


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(entry.get("id") == REVISION for entry in bank.get("revisionHistory", [])):
        print("Follow-up DC art replacements are already applied.")
        return
    by_presentation = {
        presentation["id"]: (question, presentation)
        for question in bank["questions"]
        for presentation in question.get("presentations", [])
    }
    if not set(SOURCES).issubset(by_presentation):
        raise ValueError("A DC target presentation is missing from the canonical bank.")
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    BACKUPS.mkdir(parents=True, exist_ok=True)
    question_backup = BACKUPS / "question-bank-before-more-official-dc-art-2026-10-26.json"
    credit_backup = BACKUPS / "image-credits-before-more-official-dc-art-2026-10-26.json"
    if not question_backup.exists():
        shutil.copyfile(QUESTIONS, question_backup)
    if not credit_backup.exists():
        shutil.copyfile(CREDITS, credit_backup)
    changed = []
    for presentation_id, (candidate_name, title, source_page, download_url) in SOURCES.items():
        candidate = CANDIDATES / candidate_name
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        question, presentation = by_presentation[presentation_id]
        image_bytes = candidate.read_bytes()
        media_name = hashlib.sha256(image_bytes).hexdigest()[:24] + ".jpg"
        (MEDIA / media_name).write_bytes(image_bytes)
        presentation["content"]["imageUrl"] = "media/" + media_name
        credits[media_name] = {
            "filename": candidate_name,
            "title": title + " — official DC comic illustration",
            "creator": "DC Comics; individual artist not identified on source page",
            "credit": "DC Comics / DC.com",
            "license": "Copyrighted official character art; retained for user's private, noncommercial local app only; not an open redistribution license",
            "licenseUrl": "",
            "source": source_page,
            "downloadedFrom": download_url,
            "localSource": "Official DC character profile image, downloaded 2026-10-26",
            "question": question.get("answers", [title])[0],
            "category": presentation.get("legacyCategory", ""),
        }
        changed.append(presentation_id)
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced additional DC convention/costume photos with official DC character illustrations.",
        "updatedPresentations": len(changed),
        "presentationIds": changed,
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentations": changed, "backup": str(question_backup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
