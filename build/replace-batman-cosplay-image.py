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
CANDIDATE = ROOT / "build/image-qsj-sampler/candidates/batman-official.jpg"
BACKUPS = ROOT / "review-backups"
REVISION = "2026-10-26-replace-batman-cosplay-with-official-art"
PRESENTATION_ID = "image-qsj-heros-dc-batman"


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(entry.get("id") == REVISION for entry in bank.get("revisionHistory", [])):
        print("Batman official-art replacement is already applied.")
        return
    if not CANDIDATE.is_file():
        raise FileNotFoundError(CANDIDATE)
    presentation = next(
        p
        for q in bank["questions"]
        for p in q.get("presentations", [])
        if p.get("id") == PRESENTATION_ID
    )
    old_url = presentation["content"]["imageUrl"]
    old_name = old_url.rsplit("/", 1)[-1]
    image_bytes = CANDIDATE.read_bytes()
    new_name = hashlib.sha256(image_bytes).hexdigest()[:24] + ".jpg"
    MEDIA.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(parents=True, exist_ok=True)
    question_backup = BACKUPS / "question-bank-before-batman-image-2026-10-26.json"
    credit_backup = BACKUPS / "image-credits-before-batman-image-2026-10-26.json"
    if not question_backup.exists():
        shutil.copyfile(QUESTIONS, question_backup)
    if not credit_backup.exists():
        shutil.copyfile(CREDITS, credit_backup)
    (MEDIA / new_name).write_bytes(image_bytes)
    presentation["content"]["imageUrl"] = "media/" + new_name
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced the Batman cosplay photo with official Batman comic art from DC's official character page.",
        "updatedPresentations": 1,
        "presentationIds": [PRESENTATION_ID],
        "previousImage": "media/" + old_name,
        "replacementImage": "media/" + new_name,
    })
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    credits[new_name] = {
        "filename": "Batman-Powers.jpg",
        "title": "Batman — official DC comic illustration",
        "creator": "DC Comics; individual artist not identified on source page",
        "credit": "DC Comics / DC.com",
        "license": "Copyrighted official character art; retained for user's private, noncommercial local app only; not an open redistribution license",
        "licenseUrl": "",
        "source": "https://www.dc.com/characters/batman",
        "downloadedFrom": "https://static.dc.com/2024-03/Batman-Powers.jpg",
        "localSource": "Official DC character profile image, downloaded 2026-10-26",
        "question": "Batman",
        "category": "Héros DC — Héros DC — Qui suis-je ?",
    }
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"presentation": PRESENTATION_ID, "previousImage": old_name, "replacementImage": new_name,
                      "backup": str(question_backup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
