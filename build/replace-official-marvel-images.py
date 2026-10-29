from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
CREDITS = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA = BANK / "media"
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates"
BACKUPS = ROOT / "review-backups"
REVISION = "2026-10-26-replace-marvel-cosplay-with-official-character-art"
CHARACTERS = {
    "iron-man": ("image-qsj-heros-marvel-iron-man", "Iron Man", "iron-man-tony-stark"),
    "spider-man": ("image-qsj-heros-marvel-spider-man", "Spider-Man", "spider-man-peter-parker"),
    "wolverine": ("image-qsj-heros-marvel-wolverine", "Wolverine", "wolverine-james-howlett"),
    "thor": ("image-qsj-heros-marvel-thor-marvel-comics", "Thor", "thor-thor-odinson"),
    "captain-america": ("image-qsj-heros-marvel-captain-america", "Captain America", "captain-america-steve-rogers"),
    "hulk": ("image-qsj-heros-marvel-hulk", "Hulk", "hulk-bruce-banner"),
    "black-panther": ("image-qsj-heros-marvel-black-panther-character", "Black Panther", "black-panther-t-challa"),
    "doctor-strange": ("image-qsj-heros-marvel-doctor-strange", "Doctor Strange", "doctor-strange-stephen-strange"),
    "groot": ("image-qsj-heros-marvel-groot", "Groot", "groot"),
    "black-widow": ("image-qsj-heros-marvel-black-widow-natasha-romanova", "Black Widow", "black-widow-natasha-romanova/in-comics/"),
    "ant-man": ("image-qsj-heros-marvel-ant-man", "Ant-Man", "ant-man-scott-lang"),
    "deadpool": ("image-qsj-heros-marvel-deadpool", "Deadpool", "deadpool-wade-wilson"),
    "loki": ("image-qsj-heros-marvel-loki-marvel-comics", "Loki", "loki"),
    "hawkeye": ("image-qsj-heros-marvel-hawkeye-clint-barton", "Hawkeye", "hawkeye-clint-barton"),
    "scarlet-witch": ("image-qsj-heros-marvel-scarlet-witch", "Scarlet Witch", "scarlet-witch-wanda-maximoff"),
    "captain-marvel": ("image-qsj-heros-marvel-captain-marvel-marvel-comics", "Captain Marvel", "captain-marvel-carol-danvers"),
    "daredevil": ("image-qsj-heros-marvel-daredevil-marvel-comics-character", "Daredevil", "daredevil-matthew-murdock"),
    "venom": ("image-qsj-heros-marvel-venom-character", "Venom", "venom-eddie-brock"),
    "star-lord": ("image-qsj-heros-marvel-star-lord", "Star-Lord", "star-lord-peter-quill/in-comics/"),
    "thanos": ("image-qsj-heros-marvel-thanos", "Thanos", "thanos"),
}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"}


def source_for(slug: str) -> tuple[str, str | None]:
    page = "https://www.marvel.com/characters/" + slug
    try:
        request = urllib.request.Request(page, headers=HEADERS)
        body = urllib.request.urlopen(request, timeout=30).read().decode("utf-8", "replace")
        match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)', body, re.I)
        if not match:
            match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image', body, re.I)
        return page, html.unescape(match.group(1)) if match else None
    except Exception:
        return page, None


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(entry.get("id") == REVISION for entry in bank.get("revisionHistory", [])):
        print("Official Marvel character art replacements are already applied.")
        return
    by_presentation = {p["id"]: (q, p) for q in bank["questions"] for p in q.get("presentations", [])}
    if not {v[0] for v in CHARACTERS.values()}.issubset(by_presentation):
        raise ValueError("A Marvel image presentation is missing from the canonical bank.")
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    BACKUPS.mkdir(parents=True, exist_ok=True)
    qbackup = BACKUPS / "question-bank-before-official-marvel-art-2026-10-26.json"
    cbackup = BACKUPS / "image-credits-before-official-marvel-art-2026-10-26.json"
    if not qbackup.exists():
        shutil.copyfile(QUESTIONS, qbackup)
    if not cbackup.exists():
        shutil.copyfile(CREDITS, cbackup)
    source_info = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(source_for, slug): key for key, (_, _, slug) in CHARACTERS.items()}
        for future in as_completed(futures):
            source_info[futures[future]] = future.result()
    changed = []
    for key, (pid, title, _) in CHARACTERS.items():
        candidate = CANDIDATES / f"marvel-{key}-official.webp"
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        data = candidate.read_bytes()
        name = hashlib.sha256(data).hexdigest()[:24] + ".webp"
        (MEDIA / name).write_bytes(data)
        question, presentation = by_presentation[pid]
        presentation["content"]["imageUrl"] = "media/" + name
        page, downloaded = source_info.get(key, ("https://www.marvel.com/characters/", None))
        credits[name] = {
            "filename": candidate.name,
            "title": title + " — official Marvel character image",
            "creator": "Marvel Studios / Marvel Comics; individual artist or photographer not identified on source page",
            "credit": "Marvel",
            "license": "Copyrighted official character image; retained for user's private, noncommercial local app only; not an open redistribution license",
            "licenseUrl": "",
            "source": page,
            "downloadedFrom": downloaded or page,
            "localSource": "Official Marvel character profile image, downloaded 2026-10-26",
            "question": question.get("answers", [title])[0],
            "category": presentation.get("legacyCategory", ""),
        }
        changed.append(pid)
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced Marvel cosplay and event photos with official Marvel character images.",
        "updatedPresentations": len(changed),
        "presentationIds": changed,
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentations": changed, "sourcePagesWithoutDirectImageUrl": [k for k, (_, direct) in source_info.items() if not direct], "backup": str(qbackup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
