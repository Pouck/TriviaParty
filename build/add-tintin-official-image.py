"""Add the visually reviewed official Tintin character portrait to the canonical bank."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank/questions.json"
CREDITS = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
SOURCE_IMAGE = ROOT / "build/image-qsj-sampler/candidates/bd-manga-official/tintin.png"
MEDIA = ROOT / "game-library/bank/media"
REVISION = "2026-10-27-official-tintin-character-image"
SOURCE = "https://www.tintin.com/en/characters/tintin"
IMAGE_URL = "https://cdn001.tintin.com/public/tintin/img/characters/tintin/tintin@2x.png"

bank = json.loads(BANK.read_text(encoding="utf-8"))
if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
    raise SystemExit("Revision already applied")
image_bytes = SOURCE_IMAGE.read_bytes()
media_name = hashlib.sha256(image_bytes).hexdigest()[:24] + ".png"
MEDIA.mkdir(parents=True, exist_ok=True)
(MEDIA / media_name).write_bytes(image_bytes)

question = next(q for q in bank["questions"] if "Tintin" in q.get("answers", []) and any("BD" in t for t in q.get("topics", [])))
presentation_id = "image-qsj-bd-personnages-de-bande-dessinee-tintin-official-20261027"
if presentation_id in {alias for q in bank["questions"] for alias in q.get("legacyIds", [])}:
    raise SystemExit("Presentation ID already exists")
question["topics"] = list(dict.fromkeys([*question.get("topics", []), "BD et manga"]))
question.setdefault("presentations", []).append({
    "id": presentation_id,
    "label": "Qui suis-je ? — image",
    "answerMode": "BUZZER",
    "topic": "BD et manga",
    "legacyCategory": "BD et manga — Personnages de bande dessinée — Qui suis-je ?",
    "legacyPackageId": "image-qsj-bd-personnages-de-bande-dessinee",
    "content": {
        "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
        "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
        "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0,
    },
})
question["legacyIds"].append(presentation_id)
question["imageFacts"] = {
    "subjectType": "fictional_character",
    "subjectTitle": "Tintin",
    "franchise": "Bande dessinée",
    "facts": [
        {"kind": "subject_title", "value": "Tintin", "sourceUrl": SOURCE},
        {"kind": "subject_creator", "role": "creator", "value": "Hergé (Georges Remi)", "sourceUrl": SOURCE},
        {"kind": "series", "value": "The Adventures of Tintin", "sourceUrl": SOURCE},
        {"kind": "debut", "value": "1929", "sourceUrl": SOURCE},
        {"kind": "media_creator", "role": "image credit; artwork copyright", "value": "Hergé / Tintinimaginatio", "sourceUrl": SOURCE},
    ],
    "sources": [SOURCE],
}
question["explanation"] = "Tintin est le héros des Aventures de Tintin, créé par Hergé en 1929. Sa houppette est son signe distinctif. Illustration officielle Tintinimaginatio."
bank.setdefault("revisionHistory", []).append({
    "id": REVISION,
    "note": "Added one visually reviewed, single-character official Tintin portrait. Copyrighted Hergé/Tintinimaginatio art is retained only for this private local game and must not be redistributed.",
    "createdQuestions": 0,
    "addedPresentationsToExistingQuestions": 1,
    "presentationIds": [presentation_id],
})
credits = json.loads(CREDITS.read_text(encoding="utf-8"))
credits[media_name] = {
    "filename": "tintin@2x.png",
    "title": "Tintin official character portrait",
    "creator": "Hergé (Georges Remi)",
    "credit": "Tintin © Hergé / Tintinimaginatio - 2026",
    "license": "Copyrighted artwork; all rights reserved; private local use only",
    "licenseUrl": "https://www.tintin.com/en/legals/terms",
    "source": SOURCE,
    "downloadedFrom": IMAGE_URL,
    "localSource": "Official Tintin CDN; portrait downloaded unchanged",
    "question": "Tintin",
    "category": "BD et manga — Personnages de bande dessinée — Qui suis-je ?",
    "visualReview": "Approved: official canonical upper-body Tintin portrait, one subject, no lettering or other characters. Retain only for private local gameplay; do not redistribute.",
}
BANK.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"media": media_name, "question": question["id"], "presentation": presentation_id}, ensure_ascii=False))
