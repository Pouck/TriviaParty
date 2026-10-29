from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
CREDITS = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA = BANK / "media"
INDEX = ROOT / "build/image-qsj-sampler/audit/index.csv"
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates"
BACKUPS = ROOT / "review-backups"
REVISION = "2026-10-26-visual-audit-character-and-landmark-cleanup"

# Portraits available from already downloaded official studio character pages.
REPLACE = {
    36: ("disney-simba.img", "Simba", "Disney official character image", "https://characters.disney.com/"),
    90: ("official-peterpan.jpg", "Peter Pan", "Disney official character image", "https://movies.disney.com/peter-pan"),
    195: ("disney-mickey.img", "Mickey Mouse", "Disney official character image", "https://characters.disney.com/"),
    196: ("disney-minnie.img", "Minnie Mouse", "Disney official character image", "https://characters.disney.com/"),
    199: ("disney-pluto.img", "Pluto", "Disney official character image", "https://characters.disney.com/"),
    203: ("disney-maleficent.img", "Maleficent", "Disney official character image", "https://movies.disney.com/maleficent"),
    254: ("disney-aladdin.img", "Aladdin", "Disney official character image", "https://movies.disney.com/aladdin"),
}

# These image sources are cosplayers, parade/theme-park performers, statues,
# exhibit props, unrelated subjects, or known incomplete/broken renders.
DROP = {
    48, 50, 51, 52, 66, 67, 69, 81, 82, 83, 84, 86, 91, 96, 97, 100,
    107, 178, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
    192, 193, 194, 195, 196, 197, 199, 203, 208, 215, 216, 238, 239, 240,
    241, 243, 244, 245, 248, 249, 250, 251, 252, 253, 257, 258, 259, 260,
    261, 262, 263, 264, 269, 272,
}


def main() -> None:
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in questions.get("revisionHistory", [])):
        print("Visual audit revision already applied.")
        return
    rows = {int(r["Number"]): r for r in csv.DictReader(INDEX.open(encoding="utf-8-sig"))}
    by_file = {}
    for q in questions["questions"]:
        for p in q.get("presentations", []):
            name = p.get("content", {}).get("imageUrl", "").removeprefix("media/")
            if name:
                by_file[name] = (q, p)

    BACKUPS.mkdir(parents=True, exist_ok=True)
    for source, dest in ((QUESTIONS, BACKUPS / "questions-before-visual-audit-2026-10-26.json"),
                         (CREDITS, BACKUPS / "credits-before-visual-audit-2026-10-26.json")):
        if not dest.exists():
            shutil.copyfile(source, dest)

    replaced, removed_presentations, removed_questions = [], [], []
    for number, (candidate_name, title, source_page, _) in REPLACE.items():
        old_file = rows[number]["File"]
        if old_file not in by_file:
            raise ValueError(f"Missing image bank reference for sampler row {number}")
        candidate = CANDIDATES / candidate_name
        data = candidate.read_bytes()
        ext = candidate.suffix.lower().replace(".img", ".jpg")
        filename = hashlib.sha256(data).hexdigest()[:24] + ext
        (MEDIA / filename).write_bytes(data)
        q, p = by_file[old_file]
        p["content"]["imageUrl"] = "media/" + filename
        credits[filename] = {
            "filename": candidate.name,
            "title": title + " — official character image",
            "creator": "Disney; individual artist not identified on source page",
            "credit": "Disney",
            "license": "Copyrighted official image retained for private, noncommercial local app use; not licensed for redistribution",
            "licenseUrl": "",
            "source": source_page,
            "downloadedFrom": source_page,
            "localSource": "Existing downloaded official Disney character art; 2026-10-26 visual audit",
            "question": q.get("answers", [title])[0],
            "category": p.get("legacyCategory", ""),
        }
        replaced.append(p["id"])

    drop_files = {rows[n]["File"] for n in DROP - set(REPLACE)}
    kept_questions = []
    for q in questions["questions"]:
        old = q.get("presentations", [])
        kept = [p for p in old if p.get("content", {}).get("imageUrl", "").removeprefix("media/") not in drop_files]
        removed_presentations.extend(p["id"] for p in old if p not in kept)
        if old and not kept:
            removed_questions.append(q["id"])
        if kept or not old:
            q["presentations"] = kept
            kept_questions.append(q)
    questions["questions"] = kept_questions
    questions.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Full visual sampler audit: replaced several Disney exhibit/costume depictions with official character images and retired image prompts showing cosplay, statues, parade/theme-park material, unrelated subjects, or unusable renders. Other non-image presentations were retained where present.",
        "updatedPresentations": replaced,
        "removedPresentations": removed_presentations,
        "removedQuestions": removed_questions,
        "samplerRowsAudited": sorted(DROP),
    })
    QUESTIONS.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"replaced": replaced, "removedPresentations": removed_presentations,
                      "removedQuestions": removed_questions, "backup": str(BACKUPS)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
