"""Apply two checked, single-character replacements from the user's image review."""
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
REVISION = "2026-10-27-user-reviewed-image-replacements-peterpan-forky"

REPLACEMENTS = {
    "image-qsj-personnages-disney-peter-pan-disney-character": {
        "file": "peter-pan-single.jpeg",
        "title": "Peter Pan — single-character film still",
        "source": "https://movies.disney.com/peter-pan",
        "downloadedFrom": "https://lumiere-a.akamaihd.net/v1/images/g_peterpan_homeentertainment_02_7df76a82.jpeg?region=0%2C0%2C1200%2C560",
        "reviewId": "gallery-{}",
        "answer": "Peter Pan",
        "category": "Personnages Disney",
    },
    "image-qsj-personnages-pixar-forky": {
        "file": "forky-single.jpeg",
        "title": "Forky — official Toy Story character image",
        "source": "https://toystory.disney.com/",
        "downloadedFrom": "https://lumiere-a.akamaihd.net/v1/images/t_toystory_forky_characterimage_v3_f12a4e75.jpeg?region=0%2C0%2C600%2C600",
        "reviewId": "gallery-{}",
        "answer": "Forky",
        "category": "Personnages Pixar",
    },
}


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(item.get("id") == REVISION for item in bank.get("revisionHistory", [])):
        print("Replacement revision already applied.")
        return
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    by_id = {p["id"]: (q, p) for q in bank["questions"] for p in q.get("presentations", [])}
    missing = set(REPLACEMENTS) - set(by_id)
    if missing:
        raise ValueError(f"Missing target presentations: {sorted(missing)}")

    BACKUPS.mkdir(parents=True, exist_ok=True)
    for source, target in ((QUESTIONS, "questions-before-peterpan-forky-replacements.json"),
                           (CREDITS, "image-credits-before-peterpan-forky-replacements.json")):
        backup = BACKUPS / target
        if not backup.exists():
            shutil.copyfile(source, backup)

    changed = []
    review = json.loads(REVIEW.read_text(encoding="utf-8")) if REVIEW.exists() else {"schema": "qsj-image-gallery-review-v1", "items": {}}
    review.setdefault("items", {})
    for pid, meta in REPLACEMENTS.items():
        candidate = ROOT / "build/image-qsj-sampler/candidates/review-replacements-2026-10-27" / meta["file"]
        data = candidate.read_bytes()
        filename = hashlib.sha256(data).hexdigest()[:24] + candidate.suffix.lower()
        (MEDIA / filename).write_bytes(data)
        question, presentation = by_id[pid]
        presentation["content"]["imageUrl"] = "media/" + filename
        credits[filename] = {
            "filename": candidate.name,
            "title": meta["title"],
            "creator": "Disney animation production; individual artist not identified on source page",
            "credit": "Disney",
            "license": "Copyrighted official character image; retained for user's private, noncommercial local app only; not an open redistribution license",
            "licenseUrl": "",
            "source": meta["source"],
            "downloadedFrom": meta["downloadedFrom"],
            "localSource": "Official Disney film or character page; selected after visual inspection on 2026-10-27",
            "question": question.get("answers", [meta["answer"]])[0],
            "category": presentation.get("legacyCategory", meta["category"]),
        }
        review["items"][meta["reviewId"].format(filename.rsplit(".", 1)[0])] = {
            "rating": "review",
            "note": "Replacement image selected from your feedback; please review this version.",
        }
        changed.append({"presentationId": pid, "answer": meta["answer"], "image": filename})

    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced the multi-character Peter Pan poster and multi-character Forky image with single-character Disney artwork. Both replacements are marked for user review in the image gallery.",
        "updatedPresentations": len(changed),
        "presentationIds": [item["presentationId"] for item in changed],
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"replacements": changed, "backupDirectory": str(BACKUPS)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
