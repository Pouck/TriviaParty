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
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates/politicians-2026-10-28"
REVIEW = ROOT / "build/image-qsj-gallery/review-imported-2026-10-28-0312Z.json"
REVISION = "image-qsj-politician-expansion-2026-10-28"
CATEGORY = "Histoire — Personnalités politiques — Qui suis-je ?"
PACKAGE_ID = "image-qsj-figures-politiques"

FIGURES = [
    {
        "id": "image-qsj-politician-margaret-thatcher",
        "file": "margaret-thatcher.jpg",
        "answer": "Margaret Thatcher",
        "aliases": ["Margaret Hilda Thatcher", "Baronne Thatcher"],
        "country": "Royaume-Uni",
        "role": "Première ministre du Royaume-Uni, 1979–1990",
        "creator": "White House Photographic Office",
        "creatorRole": "photographer",
        "imageTitle": "Margaret Thatcher headshot",
        "source": "https://commons.wikimedia.org/wiki/File:Margaret_Thatcher_headshot.jpg",
        "factSource": "https://www.gov.uk/government/history/past-prime-ministers/margaret-thatcher",
        "credit": "White House Photographic Office / Wikimedia Commons",
        "license": "Public domain in the United States; U.S. federal government work",
        "licenseUrl": "https://creativecommons.org/publicdomain/mark/1.0/",
        "downloadedFrom": "https://upload.wikimedia.org/wikipedia/commons/0/0a/Margaret_Thatcher_headshot.jpg",
        "explanation": "Première ministre britannique de 1979 à 1990, Margaret Thatcher fut la première femme à occuper ce poste au Royaume-Uni.",
    },
    {
        "id": "image-qsj-politician-jacinda-ardern",
        "file": "jacinda-ardern.jpg",
        "answer": "Jacinda Ardern",
        "aliases": ["Jacinda Kate Laurell Ardern", "Dame Jacinda Ardern"],
        "country": "Nouvelle-Zélande",
        "role": "Première ministre de Nouvelle-Zélande, 2017–2023",
        "creator": "New Zealand Labour Party",
        "creatorRole": "photographer / image publisher",
        "imageTitle": "Jacinda Ardern 2020",
        "source": "https://commons.wikimedia.org/wiki/File:Jacinda_Ardern_2020.jpg",
        "factSource": "https://www3.parliament.nz/en/mps-and-electorates/former-members-of-parliament/ardern-jacinda/",
        "credit": "New Zealand Labour Party / Wikimedia Commons",
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "downloadedFrom": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Jacinda_Ardern_2020.jpg",
        "explanation": "Jacinda Ardern a été première ministre de Nouvelle-Zélande de 2017 à 2023.",
    },
    {
        "id": "image-qsj-politician-mikhail-gorbachev",
        "file": "mikhail-gorbachev.jpg",
        "answer": "Mikhaïl Gorbatchev",
        "aliases": ["Mikhail Gorbachev", "Mikhaïl Sergueïevitch Gorbatchev", "Gorbatchev"],
        "country": "Union soviétique",
        "role": "Président de l’Union soviétique, 1990–1991; secrétaire général du PCUS, 1985–1991",
        "creator": "Вени Марковски (Veni Markovski)",
        "creatorRole": "photographer",
        "imageTitle": "Mikhail Gorbachev",
        "source": "https://commons.wikimedia.org/wiki/File:Mikhail_Gorbachev.jpg",
        "factSource": "https://www.nobelprize.org/prizes/peace/1990/gorbachev/facts/",
        "credit": "Veni Markovski / Wikimedia Commons",
        "license": "CC BY 3.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/3.0/",
        "downloadedFrom": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Mikhail_Gorbachev.jpg",
        "explanation": "Dernier dirigeant de l’Union soviétique, Mikhaïl Gorbatchev a reçu le prix Nobel de la paix en 1990.",
    },
    {
        "id": "image-qsj-politician-john-f-kennedy",
        "file": "john-f-kennedy.jpg",
        "answer": "John F. Kennedy",
        "aliases": ["John Fitzgerald Kennedy", "JFK"],
        "country": "États-Unis",
        "role": "35e président des États-Unis, 1961–1963",
        "creator": "Aaron Shikler",
        "creatorRole": "painter",
        "imageTitle": "John F Kennedy Official Portrait",
        "source": "https://commons.wikimedia.org/wiki/File:John_F_Kennedy_Official_Portrait.jpg",
        "factSource": "https://trumpwhitehouse.archives.gov/about-the-white-house/presidents/john-f-kennedy/",
        "credit": "Aaron Shikler / Wikimedia Commons",
        "license": "Public domain in the United States",
        "licenseUrl": "https://creativecommons.org/publicdomain/mark/1.0/",
        "downloadedFrom": "https://upload.wikimedia.org/wikipedia/commons/2/21/John_F_Kennedy_Official_Portrait.jpg",
        "explanation": "John F. Kennedy fut le 35e président des États-Unis, de 1961 à 1963. Le portrait est une peinture d’Aaron Shikler.",
    },
]


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
        print("Politician image expansion already applied.")
        return
    known_ids = {q["id"] for q in bank["questions"]}
    backup_dir = ROOT / "review-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for source, name in (
        (QUESTIONS, "questions-before-politician-image-qsj-2026-10-28.json"),
        (CREDITS, "credits-before-politician-image-qsj-2026-10-28.json"),
        (REVIEW, "gallery-review-before-politician-image-qsj-2026-10-28.json"),
    ):
        backup = backup_dir / name
        if not backup.exists():
            shutil.copyfile(source, backup)

    for figure in FIGURES:
        if figure["id"] in known_ids:
            raise ValueError(f"Question already exists without revision marker: {figure['id']}")
        data = (CANDIDATES / figure["file"]).read_bytes()
        filename = hashlib.sha256(data).hexdigest()[:24] + ".jpg"
        (MEDIA / filename).write_bytes(data)
        source_url = figure["source"]
        fact_source = figure["factSource"]
        bank["questions"].append({
            "id": figure["id"],
            "legacyIds": [figure["id"]],
            "topics": ["Histoire", "Personnalités politiques"],
            "prompt": "Qui suis-je ?",
            "answers": [figure["answer"], *figure["aliases"]],
            "content": {},
            "presentations": [{
                "id": figure["id"],
                "label": "Qui suis-je ? — image",
                "answerMode": "BUZZER",
                "topic": "Histoire",
                "legacyCategory": CATEGORY,
                "legacyPackageId": PACKAGE_ID,
                "content": {
                    "kind": "guessWho",
                    "prompt": "Qui suis-je ?",
                    "clues": [],
                    "imageRevealMode": "PIXELATE",
                    "imageRevealSteps": 6,
                    "imageUrl": "media/" + filename,
                    "basePoints": 30,
                    "penaltyPoints": 0,
                },
            }],
            "explanation": figure["explanation"],
            "legacyReviews": [],
            "imageFacts": {
                "subjectType": "political_figure",
                "subjectTitle": figure["answer"],
                "frenchTitle": figure["answer"],
                "facts": [
                    {"kind": "subject_title", "value": figure["answer"], "sourceUrl": source_url},
                    {"kind": "media_creator", "role": figure["creatorRole"], "value": figure["creator"], "sourceUrl": source_url},
                    {"kind": "location", "role": "country", "value": figure["country"], "sourceUrl": fact_source},
                    {"kind": "political_role", "value": figure["role"], "sourceUrl": fact_source},
                ],
                "sources": [source_url, fact_source],
            },
        })
        credits[filename] = {
            "filename": figure["file"],
            "title": figure["imageTitle"],
            "creator": figure["creator"],
            "credit": figure["credit"],
            "license": figure["license"],
            "licenseUrl": figure["licenseUrl"],
            "source": source_url,
            "downloadedFrom": figure["downloadedFrom"],
            "localSource": f"build/image-qsj-sampler/candidates/politicians-2026-10-28/{figure['file']}",
            "question": figure["answer"],
            "category": CATEGORY,
            "visualReview": "Visually checked: one clear color portrait or single painted portrait; no text, logos, or other people.",
        }
        review.setdefault("items", {})["gallery-" + filename.removesuffix(".jpg")] = {
            "rating": "review",
            "note": "New single-subject politician portrait; please review.",
        }

    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Added four single-subject portraits to the unified political-figures image category: Margaret Thatcher, Jacinda Ardern, Mikhail Gorbachev, and John F. Kennedy. Added reusable country and political-role facts with source links.",
        "updatedPresentations": len(FIGURES),
        "presentationIds": [figure["id"] for figure in FIGURES],
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": [figure["id"] for figure in FIGURES]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
