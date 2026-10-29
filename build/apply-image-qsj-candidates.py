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
REVISION = "2026-10-27-image-qsj-animal-single-target-fixes"


def main() -> None:
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in questions.get("revisionHistory", [])):
        print("Image quality pass already applied.")
        return
    targets = json.loads(TARGETS.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    backup_dir = ROOT / "review-backups"
    backup_dir.mkdir(exist_ok=True)
    for source, dest in (
        (QUESTIONS, backup_dir / "questions-before-image-qsj-quality-2026-10-27.json"),
        (CREDITS, backup_dir / "credits-before-image-qsj-quality-2026-10-27.json"),
    ):
        if not dest.exists():
            shutil.copyfile(source, dest)
    updates = []
    for target in targets:
        record = metadata[target["key"]]
        source = ROOT / record["candidate"]
        image_bytes = source.read_bytes()
        digest = hashlib.sha256(image_bytes).hexdigest()[:24]
        suffix = source.suffix.lower()
        media_name = digest + suffix
        media_path = BANK / "media" / media_name
        if not media_path.exists():
            shutil.copyfile(source, media_path)
        found = []
        for question in questions["questions"]:
            for presentation in question.get("presentations", []):
                if presentation.get("id") == target["presentationId"]:
                    presentation["content"]["imageUrl"] = "media/" + media_name
                    found.append(question)
        if len(found) != 1:
            raise ValueError(f"Expected one presentation {target['presentationId']}, found {len(found)}")
        credits[media_name] = {
            "filename": record["fileTitle"].removeprefix("File:"),
            "title": target.get("displayTitle", record["fileTitle"].removeprefix("File:")),
            "creator": record.get("creator", ""),
            "credit": record.get("credit", ""),
            "license": record["license"],
            "licenseUrl": record["licenseUrl"],
            "source": record["sourcePage"],
            "downloadedFrom": record["downloadedFrom"],
            "localSource": record["candidate"],
            "question": found[0].get("answers", [""])[0],
            "category": next(p["legacyCategory"] for p in found[0]["presentations"] if p["id"] == target["presentationId"]),
            "visualReview": target.get("visualReview", "Visually reviewed candidate."),
        }
        updates.append(target["presentationId"])
    questions.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced answer-bearing or group-subject images with clearer single-target visual references, including the Hong Kong skyline and animal images.",
        "updatedPresentations": updates,
    })
    QUESTIONS.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentations": updates, "media": media_name, "revision": REVISION}, ensure_ascii=False))


if __name__ == "__main__":
    main()
