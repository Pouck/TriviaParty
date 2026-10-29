from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
CREDITS = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA = BANK / "media"
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates"
BACKUPS = ROOT / "review-backups"
REVISION = "2026-10-26-replace-pixar-cosplay-with-official-film-art"
PAGES = {
    "woody": ("image-qsj-personnages-pixar-woody-toy-story", "Sheriff Woody", "https://characters.disney.com/toy-story/woody", "https://lumiere-a.akamaihd.net/v1/images/t_toystory_sheriffwoody_characterimage_v3_7a3eae5d.jpeg?region=0%2C0%2C600%2C600"),
    "buzz": ("image-qsj-personnages-pixar-buzz-lightyear", "Buzz Lightyear", "https://characters.disney.com/toy-story/buzz-lightyear", "https://lumiere-a.akamaihd.net/v1/images/t_toystory_buzzlightyear_characterimage_v3_dca01509.jpeg?region=0,0,600,600"),
    "jessie": ("image-qsj-personnages-pixar-jessie-toy-story", "Jessie", "https://characters.disney.com/toy-story/jessie", "https://lumiere-a.akamaihd.net/v1/images/t_toystory_jessie_characterimage_v3_82c1d64f.jpeg?region=0,0,600,600"),
    "nemo": ("image-qsj-personnages-pixar-nemo", "Nemo", "https://www.pixar.com/finding-nemo", "Nemo11.jpg"),
    "edna": ("image-qsj-personnages-pixar-edna-mode", "Edna Mode", "https://www.pixar.com/the-incredibles", "Edna13.jpg"),
    "mcqueen": ("image-qsj-personnages-pixar-lightning-mcqueen", "Lightning McQueen", "https://www.pixar.com/cars", "McQueen13.jpg"),
    "remy": ("image-qsj-personnages-pixar-remy-ratatouille", "Remy", "https://www.pixar.com/ratatouille", "Remy16.jpg"),
    "joy": ("image-qsj-personnages-pixar-joy-inside-out", "Joy", "https://www.pixar.com/inside-out", "io_joy3.jpg"),
    "elastigirl": ("image-qsj-personnages-pixar-elastigirl", "Elastigirl", "https://www.pixar.com/the-incredibles", "Elastigirl15.jpg"),
    "mr-incredible": ("image-qsj-personnages-pixar-mr-incredible", "Mr. Incredible", "https://www.pixar.com/the-incredibles", "MrIncredible16.jpg"),
    "sulley": ("image-qsj-personnages-pixar-sulley", "Sulley", "https://www.pixar.com/monsters-inc", "Sulley21.jpg"),
}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"}


def direct_url(page: str, filename: str) -> str:
    if page.startswith("https://characters.disney.com/"):
        return filename
    request = urllib.request.Request(page, headers=HEADERS)
    body = urllib.request.urlopen(request, timeout=30).read().decode("utf-8", "replace")
    match = re.search(r"https://images\.squarespace-cdn\.com/[^\"\\ ]*" + re.escape(filename), body, re.I)
    if not match:
        raise ValueError(f"Could not locate official Pixar image {filename}")
    return html.unescape(match.group(0)).split("?", 1)[0]


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(entry.get("id") == REVISION for entry in bank.get("revisionHistory", [])):
        print("Official Pixar character replacements are already applied.")
        return
    by_presentation = {p["id"]: (q, p) for q in bank["questions"] for p in q.get("presentations", [])}
    if any(pid not in by_presentation for pid, *_ in PAGES.values()):
        raise ValueError("A Pixar presentation is missing from the canonical bank.")
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    BACKUPS.mkdir(parents=True, exist_ok=True)
    qbackup = BACKUPS / "question-bank-before-official-pixar-art-2026-10-26.json"
    cbackup = BACKUPS / "image-credits-before-official-pixar-art-2026-10-26.json"
    if not qbackup.exists():
        shutil.copyfile(QUESTIONS, qbackup)
    if not cbackup.exists():
        shutil.copyfile(CREDITS, cbackup)
    updated = []
    for key, (pid, title, page, filename) in PAGES.items():
        candidate = CANDIDATES / f"pixar-{key}-official.jpg"
        data = candidate.read_bytes()
        digest_name = hashlib.sha256(data).hexdigest()[:24] + ".jpg"
        (MEDIA / digest_name).write_bytes(data)
        question, presentation = by_presentation[pid]
        presentation["content"]["imageUrl"] = "media/" + digest_name
        source = direct_url(page, filename)
        credits[digest_name] = {
            "filename": candidate.name,
            "title": title + " — official character image",
            "creator": "Disney/Pixar; individual artist or photographer not identified on source page",
            "credit": "Disney/Pixar",
            "license": "Copyrighted official character image; retained for user's private, noncommercial local app only; not an open redistribution license",
            "licenseUrl": "",
            "source": page,
            "downloadedFrom": source,
            "localSource": "Official Disney character profile or Pixar film page image, downloaded 2026-10-26",
            "question": question.get("answers", [title])[0],
            "category": presentation.get("legacyCategory", ""),
        }
        updated.append(pid)
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced Pixar costume and convention photos with official Disney character portraits or Pixar film images.",
        "updatedPresentations": len(updated),
        "presentationIds": updated,
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentations": updated, "backup": str(qbackup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
