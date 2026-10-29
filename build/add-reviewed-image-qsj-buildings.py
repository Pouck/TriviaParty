"""Import visually reviewed iconic-building image candidates into the canonical bank."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
CREDITS = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
TARGETS = ROOT / "build/image-qsj-candidate-targets.json"
METADATA = ROOT / "build/image-qsj-sampler/candidates/quality-pass/metadata.json"
REVIEW = ROOT / "build/image-qsj-sampler/candidates/building-approved-keys.json"
REVISION = "2026-10-27-image-qsj-buildings-reviewed-expansion"


def main() -> None:
    data = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in data.get("revisionHistory", [])):
        raise SystemExit("This revision already exists; create a new reviewed revision before importing more.")
    approved = json.loads(REVIEW.read_text(encoding="utf-8"))
    targets = {t["key"]: t for t in json.loads(TARGETS.read_text(encoding="utf-8"))}
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    questions = data["questions"]
    ids = {q["id"] for q in questions}
    presentation_ids = {p["id"] for q in questions for p in q.get("presentations", [])}
    updates: list[str] = []
    media_dir = BANK / "media"
    for key in approved:
        target = targets[key]
        record = metadata[key]
        license_name = record.get("license", "")
        if license_name.casefold() not in {
            "public domain", "public domain mark", "cc0", "cc by 4.0", "cc by 2.0", "cc by-sa 2.0",
            "cc by-sa 4.0", "cc by 3.0", "cc by-sa 3.0", "cc by-sa 2.5",
        }:
            raise ValueError(f"Unapproved license for {key}: {license_name}")
        source = ROOT / record["candidate"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:24]
        media_name = digest + source.suffix.lower()
        media_path = media_dir / media_name
        if not media_path.exists():
            shutil.copyfile(source, media_path)
        pid = target["presentationId"]
        question_id = pid
        if pid in presentation_ids or question_id in ids:
            raise ValueError(f"Duplicate question or presentation id: {pid}")
        title = target["displayTitle"]
        presentation = {
            "id": pid,
            "label": "Qui suis-je ? — image",
            "answerMode": "BUZZER",
            "topic": "Architecture",
            "legacyCategory": "Architecture — Monuments et sites célèbres — Qui suis-je ?",
            "legacyPackageId": "image-qsj-monuments-celebres",
            "content": {
                "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
                "imageUrl": "media/" + media_name,
                "basePoints": 30, "penaltyPoints": 0,
            },
        }
        questions.append({
            "id": question_id,
            "legacyIds": [question_id],
            "topics": ["Architecture"],
            "prompt": "Qui suis-je ?",
            "answers": [title],
            "content": {},
            "presentations": [presentation],
            "explanation": title + ".",
            "legacyReviews": [],
        })
        ids.add(question_id)
        presentation_ids.add(pid)
        credits[media_name] = {
            "filename": record["fileTitle"].removeprefix("File:"),
            "title": title,
            "creator": record.get("creator", ""),
            "credit": record.get("credit", ""),
            "license": license_name,
            "licenseUrl": record.get("licenseUrl", ""),
            "source": record.get("sourcePage", ""),
            "downloadedFrom": record.get("downloadedFrom", ""),
            "localSource": record["candidate"],
            "question": title,
            "category": presentation["legacyCategory"],
            "visualReview": target.get("visualReview", "Visually reviewed iconic-building candidate."),
        }
        updates.append(pid)
    data.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Added visually reviewed, source-credited iconic building and landmark image questions from published global architecture and landmark selections.",
        "updatedPresentations": updates,
    })
    QUESTIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": updates, "revision": REVISION}, ensure_ascii=False))


if __name__ == "__main__":
    main()
