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
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates/common-animals-2026-10-28"
REVISION = "image-qsj-common-farm-and-domestic-animals-2026-10-28"
CATEGORY = "Nature — Animaux — Qui suis-je ?"
PACKAGE_ID = "image-qsj-animaux"

ANIMALS = [
    {
        "id": "image-qsj-animal-donkey",
        "file": "donkey.jpg",
        "answer": "L’âne",
        "aliases": ["Un âne", "Âne", "Ânesse"],
        "title": "Donkey",
        "creator": "Superbass",
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "source": "https://commons.wikimedia.org/wiki/File:Donkey_0001.jpg",
        "credit": "Superbass / Wikimedia Commons",
        "explanation": "Âne domestique photographié au pâturage.",
    },
    {
        "id": "image-qsj-animal-goat",
        "file": "goat.jpg",
        "answer": "La chèvre",
        "aliases": ["Une chèvre", "Chèvre", "Bouc"],
        "title": "Goat portrait",
        "creator": "Ali",
        "license": "CC BY 2.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/2.0/",
        "source": "https://commons.wikimedia.org/wiki/File:Closeup_goat_portrait.jpg",
        "credit": "Ali / Wikimedia Commons",
        "explanation": "Portrait rapproché d’une chèvre domestique.",
    },
    {
        "id": "image-qsj-animal-domestic-cat",
        "file": "cat.jpg",
        "answer": "Le chat",
        "aliases": ["Un chat", "Chat domestique", "Chatte"],
        "title": "Domestic cat portrait",
        "creator": "The Roving Rokibul",
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "source": "https://commons.wikimedia.org/wiki/File:Domestic_cat_portrait.jpg",
        "credit": "The Roving Rokibul / Wikimedia Commons",
        "explanation": "Portrait d’un chat domestique.",
    },
    {
        "id": "image-qsj-animal-mallard-duck",
        "file": "duck.jpg",
        "answer": "Le canard colvert",
        "aliases": ["Un canard colvert", "Canard colvert", "Le colvert", "Canard"],
        "title": "Duck portrait (Anas platyrhynchos)",
        "creator": "Bobbydraco",
        "license": "CC0 1.0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "source": "https://commons.wikimedia.org/wiki/File:Duck_Portrait.jpg",
        "credit": "Bobbydraco / Wikimedia Commons",
        "explanation": "Portrait rapproché d’un canard colvert (Anas platyrhynchos).",
    },
    {
        "id": "image-qsj-animal-lamb",
        "file": "lamb.jpg",
        "answer": "L’agneau",
        "aliases": ["Un agneau", "Agneau", "Mouton"],
        "title": "Lamb",
        "creator": "Virginie Moerenhout",
        "license": "CC BY 2.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/2.0/",
        "source": "https://commons.wikimedia.org/wiki/File:Image_of_a_lamb.jpg",
        "credit": "Virginie Moerenhout / Wikimedia Commons",
        "explanation": "Agneau photographié dans un pré.",
    },
]


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
        print("Common farm and domestic animal expansion already applied.")
        return

    backup_dir = ROOT / "review-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for source, name in (
        (QUESTIONS, "questions-before-common-animal-image-qsj-2026-10-28.json"),
        (CREDITS, "credits-before-common-animal-image-qsj-2026-10-28.json"),
    ):
        backup = backup_dir / name
        if not backup.exists():
            shutil.copyfile(source, backup)

    existing = {q["id"] for q in bank["questions"]}
    for animal in ANIMALS:
        if animal["id"] in existing:
            raise ValueError(f"Question already exists without revision marker: {animal['id']}")
        source = CANDIDATES / animal["file"]
        data = source.read_bytes()
        filename = hashlib.sha256(data).hexdigest()[:24] + ".jpg"
        target = MEDIA / filename
        if not target.exists():
            target.write_bytes(data)
        image_url = "media/" + filename
        source_url = animal["source"]
        category = CATEGORY
        bank["questions"].append({
            "id": animal["id"],
            "legacyIds": [animal["id"]],
            "topics": ["Nature"],
            "prompt": "Qui suis-je ?",
            "answers": [animal["answer"], *animal["aliases"]],
            "content": {},
            "presentations": [{
                "id": animal["id"],
                "label": "Qui suis-je ? — image",
                "answerMode": "BUZZER",
                "topic": "Nature",
                "legacyCategory": category,
                "legacyPackageId": PACKAGE_ID,
                "content": {
                    "kind": "guessWho",
                    "prompt": "Qui suis-je ?",
                    "clues": [],
                    "imageRevealMode": "PIXELATE",
                    "imageRevealSteps": 6,
                    "imageUrl": image_url,
                    "basePoints": 30,
                    "penaltyPoints": 0,
                },
            }],
            "explanation": animal["explanation"],
            "legacyReviews": [],
            "imageFacts": {
                "subjectType": "animal",
                "subjectTitle": animal["title"],
                "frenchTitle": animal["answer"],
                "facts": [
                    {"kind": "subject_title", "value": animal["title"], "sourceUrl": source_url},
                    {"kind": "media_creator", "role": "photographer", "value": animal["creator"], "sourceUrl": source_url},
                ],
                "sources": [source_url],
            },
        })
        credits[filename] = {
            "filename": animal["file"],
            "title": animal["title"],
            "creator": animal["creator"],
            "credit": animal["credit"],
            "license": animal["license"],
            "licenseUrl": animal["licenseUrl"],
            "source": source_url,
            "downloadedFrom": source_url,
            "localSource": f"build/image-qsj-sampler/candidates/common-animals-2026-10-28/{animal['file']}",
            "question": animal["answer"],
            "category": category,
            "visualReview": "Reviewed image shows one clearly identifiable farm or domestic animal without answer-bearing text.",
        }

    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Expanded the unified animal image category with individual donkey, goat, domestic cat, mallard duck, and lamb photos to balance rare species with familiar farm and domestic animals.",
        "updatedPresentations": len(ANIMALS),
        "presentationIds": [animal["id"] for animal in ANIMALS],
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": [animal["id"] for animal in ANIMALS]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
