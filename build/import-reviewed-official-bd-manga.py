"""Import the visually reviewed official BD and manga character portraits."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
CREDITS_PATH = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
CANDIDATE_DIR = ROOT / "build/image-qsj-sampler/candidates/bd-manga-official"
MEDIA_DIR = ROOT / "game-library/bank/media"
REVISION = "2026-10-27-reviewed-official-bd-manga-portraits"
COMMONS = "https://www.tintin.com"

# Candidate key, display answer, answer aliases, franchise, image page, direct URL,
# concise independently verified reveal note, existing bank question id if any.
ITEMS = [
    ("snowy", "Milou", ["Snowy"], "Bande dessinée", "https://www.tintin.com/en/characters/snowy", "https://cdn001.tintin.com/public/tintin/img/characters/milou/milou@2x.png", "Le fidèle chien de Tintin.", "lib-buzzer-bd-franco-belge-20261012-01"),
    ("captain-haddock", "Capitaine Haddock", ["Captain Haddock", "Haddock"], "Bande dessinée", "https://www.tintin.com/en/characters/captain-haddock", "https://cdn001.tintin.com/public/tintin/img/characters/le-capitaine-haddock/le-capitaine-haddock@2x.png", "Ancien capitaine de marine et compagnon de Tintin.", "lib-buzzer-bd-franco-belge-20261012-05"),
    ("bianca-castafiore", "Bianca Castafiore", ["La Castafiore"], "Bande dessinée", "https://www.tintin.com/en/characters/bianca-castafiore", "https://cdn001.tintin.com/public/tintin/img/characters/bianca-castafiore/bianca-castafiore@2x.png", "La cantatrice milanaise de l'univers de Tintin.", None),
    ("professor-calculus", "Professeur Tournesol", ["Professor Calculus", "Tryphon Tournesol", "Cuthbert Calculus"], "Bande dessinée", "https://www.tintin.com/en/characters/professor-calculus", "https://cdn001.tintin.com/public/tintin/img/characters/le-professeur-tournesol/le-professeur-tournesol@2x.png", "Le professeur Tournesol est l'inventeur distrait des Aventures de Tintin.", None),
    ("rastapopoulos", "Roberto Rastapopoulos", ["Rastapopoulos"], "Bande dessinée", "https://www.tintin.com/en/characters/rastapopoulos", "https://cdn001.tintin.com/public/tintin/img/characters/rastapopoulos/rastapopoulos@2x.png", "Le milliardaire est l'un des principaux adversaires de Tintin.", None),
    ("general-alcazar", "Général Alcazar", ["General Alcazar", "Alcazar"], "Bande dessinée", "https://www.tintin.com/en/characters/general-alcazar", "https://cdn001.tintin.com/public/tintin/img/characters/le-general-alcazar/le-general-alcazar@2x.png", "Le général Alcazar est un ami de Tintin et dirigeant de la république de San Theodoros.", None),
    ("rascar-capac", "Rascar Capac", ["Rascar-Capac"], "Bande dessinée", "https://www.tintin.com/en/characters/rascar-capac", "https://cdn001.tintin.com/public/tintin/img/characters/rascar-capac/rascar-capac@2x.png", "La momie inca est au cœur des Sept Boules de cristal.", None),
    ("tchang", "Tchang", ["Chang"], "Bande dessinée", "https://www.tintin.com/en/characters/tchang", "https://cdn001.tintin.com/public/tintin/img/characters/tchang/tchang@2x.png", "Tchang est un ami proche de Tintin, notamment dans Le Lotus bleu.", None),
    ("luffy", "Monkey D. Luffy", ["Luffy"], "Manga", "https://one-piece.com/character/luffy/index.html", "https://one-piece.com/o/assets/images/anime/character/data/luffy/img.jpg", "Capitaine de l'équipage au chapeau de paille, il rêve de devenir le roi des pirates.", "lib-qcm-manga-20261012-02"),
    ("zoro", "Roronoa Zoro", ["Zoro"], "Manga", "https://one-piece.com/character/zoro/index.html", "https://one-piece.com/o/assets/images/anime/character/data/zoro/img.jpg", "Combattant et épéiste de l'équipage au chapeau de paille.", None),
    ("nami", "Nami", ["La navigatrice de l'équipage au chapeau de paille"], "Manga", "https://one-piece.com/character/nami/index.html", "https://one-piece.com/o/assets/images/anime/character/data/nami/img.jpg", "Navigatrice de l'équipage au chapeau de paille.", None),
    ("usopp", "Usopp", ["Pipo"], "Manga", "https://one-piece.com/character/usopp/index.html", "https://one-piece.com/o/assets/images/anime/character/data/usopp/img.jpg", "Tireur d'élite et conteur de l'équipage au chapeau de paille.", None),
    ("sanji", "Sanji", ["Vinsmoke Sanji"], "Manga", "https://one-piece.com/character/sanji/index.html", "https://one-piece.com/o/assets/images/anime/character/data/sanji/img.jpg", "Cuisinier de l'équipage au chapeau de paille.", None),
    ("chopper", "Tony Tony Chopper", ["Chopper"], "Manga", "https://one-piece.com/character/chopper/index.html", "https://one-piece.com/o/assets/images/anime/character/data/chopper/img.jpg", "Médecin de l'équipage au chapeau de paille.", None),
    ("robin", "Nico Robin", ["Robin (One Piece)"], "Manga", "https://one-piece.com/character/robin/index.html", "https://one-piece.com/o/assets/images/anime/character/data/robin/img.jpg", "Archéologue de l'équipage au chapeau de paille.", None),
    ("franky", "Franky", ["Cutty Flam"], "Manga", "https://one-piece.com/character/franky/index.html", "https://one-piece.com/o/assets/images/anime/character/data/franky/img.jpg", "Charpentier naval de l'équipage au chapeau de paille.", None),
    ("brook", "Brook", ["Soul King Brook"], "Manga", "https://one-piece.com/character/brook/index.html", "https://one-piece.com/o/assets/images/anime/character/data/brook/img.jpg", "Musicien de l'équipage au chapeau de paille.", None),
    ("Jinbe", "Jinbe", ["Jinbei"], "Manga", "https://one-piece.com/character/Jinbe/index.html", "https://one-piece.com/o/assets/images/anime/character/data/Jinbe/img.jpg", "Timonier de l'équipage au chapeau de paille.", None),
]


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
    raise SystemExit("Reviewed BD/manga portrait import already applied")
credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8"))
questions = bank["questions"]
by_id = {q["id"]: q for q in questions}
used_ids = {alias for q in questions for alias in q.get("legacyIds", [])}
presentations_added = created = attached = 0
new_ids: list[str] = []

# Ensure a recoverable pre-import snapshot exists, retaining the already-added Tintin portrait.
backup_dir = ROOT / "review-backups"
backup_dir.mkdir(exist_ok=True)
(backup_dir / "questions-before-official-bd-manga-portraits-2026-10-27.json").write_text(BANK_PATH.read_text(encoding="utf-8"), encoding="utf-8")
(backup_dir / "credits-before-official-bd-manga-portraits-2026-10-27.json").write_text(CREDITS_PATH.read_text(encoding="utf-8"), encoding="utf-8")

for key, answer, aliases, franchise, source, download_url, reveal_note, target_id in ITEMS:
    candidate_path = next(iter(CANDIDATE_DIR.glob(f"{key}.*")), None)
    if not candidate_path or candidate_path.name.startswith("official-"):
        raise FileNotFoundError(f"Missing visually reviewed image candidate for {key}")
    media_bytes = candidate_path.read_bytes()
    media_name = hashlib.sha256(media_bytes).hexdigest()[:24] + candidate_path.suffix.lower()
    media_path = MEDIA_DIR / media_name
    media_path.parent.mkdir(parents=True, exist_ok=True)
    if not media_path.exists():
        shutil.copyfile(candidate_path, media_path)

    category = "Personnages de bande dessinée" if franchise == "Bande dessinée" else "Personnages de manga"
    pres_id = f"image-qsj-{slug(category)}-{slug(answer)}-official-20261027"
    if pres_id in used_ids:
        raise ValueError(f"Presentation alias already exists: {pres_id}")
    question = by_id.get(target_id) if target_id else None
    if question:
        question["presentations"] = [p for p in question.get("presentations", []) if p.get("id") != pres_id]
    else:
        question = {
            "id": pres_id, "legacyIds": [], "topics": ["BD et manga", franchise],
            "prompt": "Qui suis-je ?", "answers": list(dict.fromkeys([answer, *aliases])),
            "content": {}, "presentations": [], "legacyReviews": [],
        }
        questions.append(question)
        by_id[pres_id] = question
        created += 1

    if "BD et manga" not in question.setdefault("topics", []):
        question["topics"].append("BD et manga")
    question["imageFacts"] = {
        "subjectType": "fictional_character", "subjectTitle": answer, "franchise": franchise,
        "facts": [
            {"kind": "subject_title", "value": answer, "sourceUrl": source},
            {"kind": "series", "value": "The Adventures of Tintin" if franchise == "Bande dessinée" else "One Piece", "sourceUrl": source},
            {"kind": "media_creator", "role": "official artwork copyright; not an open image license", "value": "Hergé / Tintinimaginatio" if franchise == "Bande dessinée" else "Eiichiro Oda / Shueisha / Fuji TV / Toei Animation", "sourceUrl": source},
        ],
        "sources": [source],
    }
    if not question.get("explanation"):
        question["explanation"] = reveal_note
    presentation = {
        "id": pres_id, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
        "topic": "BD et manga",
        "legacyCategory": f"BD et manga — {category} — Qui suis-je ?",
        "legacyPackageId": "image-qsj-" + slug(category),
        "content": {
            "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
            "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
            "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0,
        },
    }
    question.setdefault("presentations", []).append(presentation)
    question.setdefault("legacyIds", []).append(pres_id)
    used_ids.add(pres_id)
    new_ids.append(pres_id)
    presentations_added += 1

    source_title = "Tintin.com official character portrait" if franchise == "Bande dessinée" else "ONE PIECE.com official anime character portrait"
    credits[media_name] = {
        "filename": candidate_path.name,
        "title": source_title,
        "creator": "Hergé / Tintinimaginatio" if franchise == "Bande dessinée" else "Eiichiro Oda / Shueisha / Fuji TV / Toei Animation",
        "credit": "© Hergé / Tintinimaginatio" if franchise == "Bande dessinée" else "© Eiichiro Oda / Shueisha / Fuji TV / Toei Animation",
        "license": "Copyrighted official artwork; rights reserved; private local use only",
        "licenseUrl": "https://www.tintin.com/en/legals/terms" if franchise == "Bande dessinée" else "https://one-piece.com/agreement/",
        "source": source, "downloadedFrom": download_url,
        "localSource": "Official character page; portrait retained unchanged",
        "question": answer,
        "category": f"BD et manga — {category} — Qui suis-je ?",
        "visualReview": "Approved: one canonical character, no lettering, no second character; downloaded unchanged. Retained only for this private local game; do not redistribute.",
    }

bank.setdefault("revisionHistory", []).append({
    "id": REVISION,
    "note": "Expanded BD and manga image Qui suis-je coverage with 18 visually reviewed single-character portraits from official Tintin and One Piece pages. Copyrighted artwork is retained only for private local gameplay and must not be redistributed.",
    "createdQuestions": created,
    "addedPresentationsToExistingQuestions": presentations_added - created,
    "presentationIds": new_ids,
})
BANK_PATH.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"presentationsAdded": presentations_added, "newQuestions": created, "attachedToExisting": presentations_added - created, "ids": new_ids}, ensure_ascii=False, indent=2))
