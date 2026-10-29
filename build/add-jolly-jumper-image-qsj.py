"""Create the first BD image-reveal variant from the existing local source art."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MEDIA_DIR = ROOT / "game-library/bank/media"
CREDITS_PATH = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
REVISION_ID = "2026-10-26-jolly-jumper-image-qsj"
QUESTION_ID = "lib-buzzer-bd-franco-belge-20261012-03"
PRESENTATION_ID = "image-qsj-bd-personnages-jolly-jumper"


def main() -> None:
    data = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION_ID for row in data.get("revisionHistory", [])):
        print("Jolly Jumper's image presentation is already present; no changes made.")
        return
    source_dir = ROOT / "package-examples/library-2026-10-12/assets"
    metadata = json.loads((source_dir / "bd-character-03.json").read_text(encoding="utf-8"))
    source = source_dir / metadata["file"]
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    media_name = digest[:24] + source.suffix.lower()
    destination = MEDIA_DIR / media_name
    if not destination.exists():
        shutil.copyfile(source, destination)

    question = next(q for q in data["questions"] if q["id"] == QUESTION_ID)
    presentation = {
        "id": PRESENTATION_ID,
        "label": "Qui suis-je ? — image",
        "answerMode": "BUZZER",
        "topic": "BD et manga",
        "legacyCategory": "BD et manga — Personnages de BD — Qui suis-je ?",
        "legacyPackageId": "image-qsj-bd-personnages",
        "content": {
            "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
            "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
            "imageUrl": f"media/{media_name}", "basePoints": 30, "penaltyPoints": 0,
        },
    }
    question["presentations"].append(presentation)
    question["legacyIds"].append(PRESENTATION_ID)
    data.setdefault("revisionHistory", []).append({
        "id": REVISION_ID,
        "note": "Added a six-stage picture question for Jolly Jumper using the existing local Dargaud illustration.",
        "createdQuestions": 0, "addedPresentationsToExistingQuestions": 1,
        "presentationIds": [PRESENTATION_ID],
    })

    credits_path = CREDITS_PATH
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}
    credits[media_name] = {
        "filename": metadata["file"], "title": metadata["title"],
        "creator": metadata["artist"], "credit": metadata["credit"],
        "license": metadata["license"], "licenseUrl": metadata["licenseUrl"],
        "source": metadata["commons"], "downloadedFrom": metadata["download"],
        "localSource": source.relative_to(ROOT).as_posix(),
        "changes": metadata["changes"], "question": "Jolly Jumper",
        "category": presentation["legacyCategory"],
    }
    BANK_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Added one picture-based Jolly Jumper presentation to the existing BD question.")


if __name__ == "__main__":
    main()
