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
REVISION = "2026-10-26-replace-more-dc-cosplay-with-official-art"
SOURCES = {
    "image-qsj-heros-dc-black-canary": ("dc-black-canary-official.jpg", "Black Canary", "https://www.dc.com/characters/black-canary", "https://static.dc.com/dc/files/default_images/Char_Thumb_BlackCanary_5c41184e20ee69.98463239.jpg"),
    "image-qsj-heros-dc-batgirl": ("dc-batgirl-official.jpg", "Batgirl", "https://www.dc.com/characters/batgirl", "https://static.dc.com/dc/files/default_images/Char_Thumb_Batgirl_5c410fd9aa14d0.53215721.jpg"),
    "image-qsj-heros-dc-robin-character": ("dc-robin-official.jpg", "Robin", "https://www.dc.com/characters/robin", "https://static.dc.com/dc/files/default_images/Char_Thumb_Robin_5c5c888fd675e4.98555002.jpg"),
    "image-qsj-heros-dc-shazam-character": ("dc-shazam-official.jpg", "Shazam", "https://www.dc.com/characters/shazam", "https://static.dc.com/dc/files/default_images/Char_Thumb_Shazam_5c53a74aefbb12.02099042.jpg"),
    "image-qsj-heros-dc-penguin-character": ("dc-penguin-official.jpg", "The Penguin", "https://www.dc.com/characters/the-penguin", "https://static.dc.com/dc/files/default_images/Char_Thumb_Penguin_5c5250a8ad2602.47297230.jpg"),
    "image-qsj-heros-dc-cyborg-dc-comics": ("dc-cyborg-official.jpg", "Cyborg", "https://www.dc.com/characters/cyborg", "https://static.dc.com/dc/files/default_images/Char_Thumb_Cyborg_20190116_5c3fcd9048a0e1.41912254.jpg"),
    "image-qsj-heros-dc-lex-luthor": ("dc-lex-luthor-official.jpg", "Lex Luthor", "https://www.dc.com/characters/lex-luthor", "https://static.dc.com/dc/files/default_images/Char_Thumb_LexLuthor_5c4a62d2862528.01646688.jpg"),
    "image-qsj-heros-dc-batwoman": ("dc-batwoman-official.jpg", "Batwoman", "https://www.dc.com/characters/batwoman", "https://static.dc.com/dc/files/default_images/Char_Thumb_Batwoman_5c4111746bf769.13954525.jpg"),
}


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(entry.get("id") == REVISION for entry in bank.get("revisionHistory", [])):
        print("Additional DC replacements are already applied.")
        return
    by_presentation = {p["id"]: (q, p) for q in bank["questions"] for p in q.get("presentations", [])}
    if not set(SOURCES).issubset(by_presentation):
        raise ValueError("A DC presentation target is missing from the canonical bank.")
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    BACKUPS.mkdir(parents=True, exist_ok=True)
    qbackup = BACKUPS / "question-bank-before-more-dc-art-2026-10-26.json"
    cbackup = BACKUPS / "image-credits-before-more-dc-art-2026-10-26.json"
    if not qbackup.exists():
        shutil.copyfile(QUESTIONS, qbackup)
    if not cbackup.exists():
        shutil.copyfile(CREDITS, cbackup)
    changed = []
    for pid, (candidate_name, title, page, download) in SOURCES.items():
        data = (CANDIDATES / candidate_name).read_bytes()
        filename = hashlib.sha256(data).hexdigest()[:24] + ".jpg"
        (MEDIA / filename).write_bytes(data)
        question, presentation = by_presentation[pid]
        presentation["content"]["imageUrl"] = "media/" + filename
        credits[filename] = {
            "filename": candidate_name,
            "title": title + " — official DC comic illustration",
            "creator": "DC Comics; individual artist not identified on source page",
            "credit": "DC Comics / DC.com",
            "license": "Copyrighted official character art; retained for user's private, noncommercial local app only; not an open redistribution license",
            "licenseUrl": "",
            "source": page,
            "downloadedFrom": download,
            "localSource": "Official DC character profile image, downloaded 2026-10-26",
            "question": question.get("answers", [title])[0],
            "category": presentation.get("legacyCategory", ""),
        }
        changed.append(pid)
    bank.setdefault("revisionHistory", []).append({"id": REVISION, "note": "Replaced eight additional DC event and costume photos with official comic illustrations.", "updatedPresentations": len(changed), "presentationIds": changed})
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentations": changed, "backup": str(qbackup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
