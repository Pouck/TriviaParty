"""Import visually approved painting candidates into the canonical image bank."""
from __future__ import annotations

import hashlib
import json
import shutil
import unicodedata
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
CREDITS = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
TARGETS = ROOT / "build/image-qsj-candidate-targets.json"
METADATA = ROOT / "build/image-qsj-sampler/candidates/quality-pass/metadata.json"
REVIEW = ROOT / "build/image-qsj-sampler/candidates/painting-approved-keys.json"
REVISION = "2026-10-27-image-qsj-paintings-top100-expansion"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def main() -> None:
    data = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in data.get("revisionHistory", [])):
        raise SystemExit("This revision already exists; make a new review revision before importing more.")
    approved = set(json.loads(REVIEW.read_text(encoding="utf-8")))
    targets = {t["key"]: t for t in json.loads(TARGETS.read_text(encoding="utf-8"))}
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    media_dir = BANK / "media"
    questions = data["questions"]
    ids = {q["id"] for q in questions}
    answer_index: dict[str, dict] = {}
    for q in questions:
        for answer in q.get("answers", []):
            answer_index.setdefault(norm(answer), q)
    added = attached = 0
    presentation_ids = []
    for key in sorted(approved, key=lambda k: targets[k]["benchmarkRank"]):
        target = targets[key]
        record = metadata[key]
        if record.get("license", "").casefold() not in {"public domain", "public domain mark", "cc0", "cc by 4.0", "cc by-sa 4.0", "cc by 3.0", "cc by-sa 3.0", "cc by-sa 2.5"}:
            raise ValueError(f"Unapproved or unreviewed license for {key}: {record.get('license')}")
        source = ROOT / record["candidate"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:24]
        media_name = digest + source.suffix.lower()
        media_path = media_dir / media_name
        if not media_path.exists():
            shutil.copyfile(source, media_path)
        presentation_id = target["presentationId"]
        if presentation_id in ids:
            raise ValueError(f"Duplicate presentation id: {presentation_id}")
        title = target["displayTitle"]
        matches = answer_index.get(norm(title))
        content = {
            "kind": "guessWho",
            "prompt": "Qui suis-je ?",
            "clues": [],
            "imageRevealMode": "PIXELATE",
            "imageRevealSteps": 6,
            "imageUrl": "media/" + media_name,
            "basePoints": 30,
            "penaltyPoints": 0,
        }
        presentation = {
            "id": presentation_id,
            "label": "Qui suis-je ? — image",
            "answerMode": "BUZZER",
            "topic": "Arts",
            "legacyCategory": "Arts — Peintures célèbres — Qui suis-je ?",
            "legacyPackageId": "image-qsj-peintures-celebres",
            "content": content,
        }
        if matches:
            matches.setdefault("presentations", []).append(presentation)
            matches.setdefault("legacyIds", []).append(presentation_id)
            attached += 1
            q = matches
        else:
            q = {
                "id": presentation_id,
                "legacyIds": [presentation_id],
                "topics": ["Arts"],
                "prompt": "Qui suis-je ?",
                "answers": [title],
                "content": {},
                "presentations": [presentation],
                "explanation": f"{title} — {target.get('artist', '')}.",
                "legacyReviews": [],
            }
            questions.append(q)
            answer_index[norm(title)] = q
            added += 1
        ids.add(presentation_id)
        presentation_ids.append(presentation_id)
        credits[media_name] = {
            "filename": record["fileTitle"].removeprefix("File:"),
            "title": title,
            "creator": record.get("creator") or target.get("artist", ""),
            "credit": record.get("credit", ""),
            "license": record["license"],
            "licenseUrl": record.get("licenseUrl", ""),
            "source": target["sourcePage"],
            "downloadedFrom": record["downloadedFrom"],
            "localSource": record["candidate"],
            "question": q.get("answers", [title])[0],
            "category": "Arts — Peintures célèbres — Qui suis-je ?",
            "benchmark": "The 100 Most Famous Paintings in the World",
            "benchmarkRank": target["benchmarkRank"],
            "visualReview": "Approved from the painting candidate contact sheet; artwork image, not a poster or text-bearing reproduction.",
        }
    backup = ROOT / "review-backups"
    backup.mkdir(exist_ok=True)
    for src, dest in ((QUESTIONS, backup / "questions-before-image-qsj-paintings-top100.json"), (CREDITS, backup / "credits-before-image-qsj-paintings-top100.json")):
        if not dest.exists():
            shutil.copyfile(src, dest)
    data.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Expanded famous-painting image questions using visually approved, rights-checked candidates from a published top-100 fame list. Existing canonical questions were reused where the title matched.",
        "createdQuestions": added,
        "addedPresentationsToExistingQuestions": attached,
        "presentationIds": presentation_ids,
    })
    QUESTIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"createdQuestions": added, "attachedPresentations": attached, "added": len(presentation_ids)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
