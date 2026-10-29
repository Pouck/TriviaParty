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
REVISION = "2026-10-26-replace-disney-cosplay-with-official-character-art"
SOURCES = {
    "image-qsj-personnages-disney-moana-disney-character": ("moana", "Moana", "https://princess.disney.com/"),
    "image-qsj-personnages-disney-ariel-the-little-mermaid": ("ariel", "Ariel", "https://princess.disney.com/"),
    "image-qsj-personnages-disney-cinderella-disney-character": ("cinderella", "Cinderella", "https://princess.disney.com/"),
    "image-qsj-personnages-disney-belle-beauty-and-the-beast": ("belle", "Belle", "https://princess.disney.com/"),
    "image-qsj-personnages-disney-snow-white-disney-character": ("snow-white", "Snow White", "https://princess.disney.com/"),
    "image-qsj-personnages-disney-mulan-disney-character": ("mulan", "Mulan", "https://princess.disney.com/"),
    "image-qsj-personnages-disney-elsa-frozen": ("elsa", "Elsa", "https://characters.disney.com/elsa"),
    "image-qsj-personnages-disney-anna-frozen": ("anna", "Anna", "https://characters.disney.com/elsa"),
    "image-qsj-personnages-disney-olaf-frozen": ("olaf", "Olaf", "https://characters.disney.com/elsa"),
}


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(entry.get("id") == REVISION for entry in bank.get("revisionHistory", [])):
        print("Official Disney character art replacements are already applied.")
        return
    by_presentation = {p["id"]: (q, p) for q in bank["questions"] for p in q.get("presentations", [])}
    if not set(SOURCES).issubset(by_presentation):
        raise ValueError("A Disney image presentation is missing from the canonical bank.")
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    BACKUPS.mkdir(parents=True, exist_ok=True)
    qbackup = BACKUPS / "question-bank-before-official-disney-art-2026-10-26.json"
    cbackup = BACKUPS / "image-credits-before-official-disney-art-2026-10-26.json"
    if not qbackup.exists():
        shutil.copyfile(QUESTIONS, qbackup)
    if not cbackup.exists():
        shutil.copyfile(CREDITS, cbackup)
    changed = []
    for pid, (key, title, page) in SOURCES.items():
        candidate = CANDIDATES / f"disney-{key}-official.jpg"
        data = candidate.read_bytes()
        filename = hashlib.sha256(data).hexdigest()[:24] + ".jpg"
        (MEDIA / filename).write_bytes(data)
        question, presentation = by_presentation[pid]
        presentation["content"]["imageUrl"] = "media/" + filename
        credits[filename] = {
            "filename": candidate.name,
            "title": title + " — official Disney character art",
            "creator": "Disney; individual artist not identified on source page",
            "credit": "Disney",
            "license": "Copyrighted official character image; retained for user's private, noncommercial local app only; not an open redistribution license",
            "licenseUrl": "",
            "source": page,
            "downloadedFrom": "Official Disney Lumiere CDN; direct image URL recorded in build/fetch-disney-character-cards.py",
            "localSource": "Official Disney character profile image, downloaded 2026-10-26",
            "question": question.get("answers", [title])[0],
            "category": presentation.get("legacyCategory", ""),
        }
        changed.append(pid)
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced Disney costume/event photos and weak promotional group images with official single-character art.",
        "updatedPresentations": len(changed),
        "presentationIds": changed,
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentations": changed, "backup": str(qbackup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
