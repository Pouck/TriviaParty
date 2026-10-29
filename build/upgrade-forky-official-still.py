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
REVISION = "2026-10-26-upgrade-forky-to-official-film-still"
PID = "image-qsj-personnages-pixar-forky"
CANDIDATE = ROOT / "build/image-qsj-sampler/candidates/forky-hires-still.jpeg"
SOURCE = "https://lumiere-a.akamaihd.net/v1/images/forkyasksaquestion_whatismoney_pubstill_55c3d4e6.jpeg?region=0,0,2048,1150"


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
        print("Forky's official film still is already applied.")
        return
    question = next(q for q in bank["questions"] for p in q.get("presentations", []) if p.get("id") == PID)
    presentation = next(p for p in question["presentations"] if p.get("id") == PID)
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    BACKUPS.mkdir(parents=True, exist_ok=True)
    qb = BACKUPS / "question-bank-before-forky-film-still-2026-10-26.json"
    cb = BACKUPS / "image-credits-before-forky-film-still-2026-10-26.json"
    if not qb.exists():
        shutil.copyfile(QUESTIONS, qb)
    if not cb.exists():
        shutil.copyfile(CREDITS, cb)
    data = CANDIDATE.read_bytes()
    filename = hashlib.sha256(data).hexdigest()[:24] + ".jpeg"
    (MEDIA / filename).write_bytes(data)
    presentation["content"]["imageUrl"] = "media/" + filename
    credits[filename] = {
        "filename": CANDIDATE.name,
        "title": "Forky — official Toy Story 4 film still",
        "creator": "Disney/Pixar; individual artist or photographer not identified on source page",
        "credit": "Disney/Pixar",
        "license": "Copyrighted official character image; retained for user's private, noncommercial local app only; not an open redistribution license",
        "licenseUrl": "",
        "source": "https://press.disney.co.uk/gallery/forky-asks-a-question-stills",
        "downloadedFrom": SOURCE,
        "localSource": "Official Disney/Pixar publicity still, downloaded 2026-10-26",
        "question": question.get("answers", ["Forky"])[0],
        "category": presentation.get("legacyCategory", ""),
    }
    bank.setdefault("revisionHistory", []).append({"id": REVISION, "note": "Upgraded Forky's small profile icon to a full-size official Toy Story 4 still.", "updatedPresentations": 1, "presentationIds": [PID]})
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentation": PID, "image": filename, "backup": str(qb)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
