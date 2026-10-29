"""Add visually reviewed official Astérix and Dragon Ball character art."""
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
REVISION = "2026-10-27-reviewed-asterix-dragonball-portraits"
ASTERIX_PAGE = "https://asterix.com/en/the-gauls/"
DB_PAGE = "https://dragonball-super.com/en/"
DB_CREATOR_PAGE = "https://dragonball-super.com/en/"

# key, answer, accepted aliases, franchise, image page, direct asset URL,
# explanation / supplementary fact, existing canonical bank question ID
ITEMS = [
    ("asterix", "Astérix", ["Asterix"], "Bande dessinée", ASTERIX_PAGE,
     "https://asterix.com/wp-content/uploads/2024/11/video-tuto-asterix.png",
     "Le héros gaulois a été créé par René Goscinny et Albert Uderzo.", "lib-qsj-bd-franco-belge-20261012-01"),
    ("obelix", "Obélix", ["Obelix"], "Bande dessinée", ASTERIX_PAGE,
     "https://asterix.com/wp-content/uploads/2024/11/video-tuto-obelix.png",
     "Ami inséparable d'Astérix, il possède une force exceptionnelle depuis qu'il est tombé dans la potion magique enfant.", "lib-buzzer-bd-franco-belge-20261012-02"),
    ("idefix", "Idéfix", ["Idefix", "Dogmatix"], "Bande dessinée", ASTERIX_PAGE,
     "https://asterix.com/wp-content/uploads/2024/11/video-tuto-idefix.png",
     "Le petit chien d'Obélix est particulièrement attaché aux arbres.", None),
    ("panoramix", "Panoramix", ["Getafix"], "Bande dessinée", ASTERIX_PAGE,
     "https://asterix.com/wp-content/uploads/2024/11/video-tuto-panoramix.png",
     "Le druide du village prépare la potion magique.", "lib-qcm-bd-franco-belge-20261012-02"),
    ("falbala", "Falbala", [], "Bande dessinée", ASTERIX_PAGE,
     "https://asterix.com/wp-content/uploads/2024/11/video-tuto-falbala.png",
     "Falbala est une Gauloise du village d'Astérix.", None),
    ("goku", "Son Goku", ["Goku"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-goku.jpg",
     "Saiyan élevé sur Terre et héros de Dragon Ball, créé par Akira Toriyama.", "lib-buzzer-manga-20261012-02"),
    ("vegeta", "Vegeta", ["Prince Vegeta"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-vegeta.jpg", "Le prince des Saiyans est un rival puis un allié de Goku.", None),
    ("bulma", "Bulma", [], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-bulma.jpg", "Inventrice brillante et amie de longue date de Goku.", None),
    ("gohan", "Son Gohan", ["Gohan"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-gohan.jpg", "Fils de Goku et de Chichi.", None),
    ("pic", "Piccolo", [], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-pic.jpg", "Guerrier namek, d'abord ennemi puis mentor de Gohan.", None),
    ("kri", "Krilin", ["Krillin", "Kuririn"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-kri.jpg", "Ami et compagnon d'entraînement de Goku.", None),
    ("18", "C-18", ["Android 18", "Numéro 18"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-18.jpg", "Ancienne androïde de combat devenue l'une des alliées des héros.", None),
    ("tru", "Trunks", ["Trunks Brief"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-tru.jpg", "Fils de Vegeta et Bulma.", None),
    ("bu", "Majin Boo", ["Majin Buu", "Boo", "Buu"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-bu.jpg", "Être magique puissant dont plusieurs formes apparaissent dans Dragon Ball.", None),
    ("beerus", "Beerus", ["Bills"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-beerus.jpg", "Dieu de la destruction chargé de maintenir l'équilibre de l'univers.", None),
    ("yam", "Yamcha", [], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-yam.jpg", "Combattant et ancien bandit du désert, devenu l'ami de Goku.", None),
    ("chichi", "Chichi", ["Chi-Chi", "Milk"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-chichi.jpg", "Épouse de Goku et mère de Gohan et Goten.", None),
    ("kame", "Tortue Géniale", ["Master Roshi", "Kame-Sennin", "Muten Roshi"], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-kame.jpg", "Maître d'arts martiaux de Goku et Krilin.", None),
    ("videl", "Videl", [], "Manga", DB_PAGE,
     "https://dragonball-super.com/img/chara/cr-videl.jpg", "Combattante, fille de Mr Satan et épouse de Gohan.", None),
]


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
    raise SystemExit("Astérix/Dragon Ball portrait import already applied")
credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8"))
questions = bank["questions"]
by_id = {q["id"]: q for q in questions}
used_ids = {alias for q in questions for alias in q.get("legacyIds", [])}
backup_dir = ROOT / "review-backups"
backup_dir.mkdir(exist_ok=True)
(backup_dir / "questions-before-asterix-dragonball-portraits-2026-10-27.json").write_text(BANK_PATH.read_text(encoding="utf-8"), encoding="utf-8")
(backup_dir / "credits-before-asterix-dragonball-portraits-2026-10-27.json").write_text(CREDITS_PATH.read_text(encoding="utf-8"), encoding="utf-8")

added: list[str] = []
created = attached = 0
for key, answer, aliases, franchise, source, direct_url, note, target_id in ITEMS:
    candidate_path = next(iter(CANDIDATE_DIR.glob(f"{key}.*")), None)
    if not candidate_path:
        raise FileNotFoundError(f"Missing candidate image for {key}")
    image_bytes = candidate_path.read_bytes()
    media_name = hashlib.sha256(image_bytes).hexdigest()[:24] + candidate_path.suffix.lower()
    target = MEDIA_DIR / media_name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(candidate_path, target)

    category = "Personnages de bande dessinée" if franchise == "Bande dessinée" else "Personnages de manga"
    presentation_id = f"image-qsj-{slug(category)}-{slug(answer)}-official-20261027-b"
    if presentation_id in used_ids:
        raise ValueError(f"Presentation ID already exists: {presentation_id}")
    question = by_id.get(target_id) if target_id else None
    if question is None:
        question = {
            "id": presentation_id, "legacyIds": [], "topics": ["BD et manga", franchise],
            "prompt": "Qui suis-je ?", "answers": list(dict.fromkeys([answer, *aliases])),
            "content": {}, "presentations": [], "legacyReviews": [],
        }
        questions.append(question)
        by_id[presentation_id] = question
        created += 1
    else:
        attached += 1
    if "BD et manga" not in question.setdefault("topics", []):
        question["topics"].append("BD et manga")

    is_asterix = franchise == "Bande dessinée"
    series = "Astérix" if is_asterix else "Dragon Ball"
    creator = "René Goscinny / Albert Uderzo" if is_asterix else "Akira Toriyama"
    source_creator = "https://asterix.com/en/" if is_asterix else DB_CREATOR_PAGE
    copyright_holder = "Les Éditions Albert René / Goscinny - Uderzo" if is_asterix else "Bird Studio / Shueisha / Toei Animation"
    question["imageFacts"] = {
        "subjectType": "fictional_character", "subjectTitle": answer, "franchise": franchise,
        "facts": [
            {"kind": "subject_title", "value": answer, "sourceUrl": source},
            {"kind": "series", "value": series, "sourceUrl": source},
            {"kind": "subject_creator", "role": "creator of the original franchise", "value": creator, "sourceUrl": source_creator},
            {"kind": "media_creator", "role": "official artwork copyright holder; no open license indicated", "value": copyright_holder, "sourceUrl": source},
        ],
        "sources": list(dict.fromkeys([source, source_creator])),
    }
    if not question.get("explanation"):
        question["explanation"] = note
    question.setdefault("presentations", []).append({
        "id": presentation_id, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
        "topic": "BD et manga",
        "legacyCategory": f"BD et manga — {category} — Qui suis-je ?",
        "legacyPackageId": "image-qsj-" + slug(category),
        "content": {
            "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
            "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
            "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0,
        },
    })
    question.setdefault("legacyIds", []).append(presentation_id)
    used_ids.add(presentation_id)
    added.append(presentation_id)

    credits[media_name] = {
        "filename": candidate_path.name,
        "title": "Astérix official character drawing" if is_asterix else "Dragon Ball Super official character image",
        "creator": creator,
        "credit": "© 2025 Les Éditions Albert René / Goscinny - Uderzo" if is_asterix else "© Bird Studio / Shueisha / Toei Animation",
        "license": "Copyrighted official artwork; rights reserved; private local use only",
        "licenseUrl": "https://asterix.com/en/general-terms-and-conditions-of-use-of-the-site/" if is_asterix else "https://en.dragon-ball-official.com/",
        "source": source, "downloadedFrom": direct_url,
        "localSource": "Official character page; image retained unchanged",
        "question": answer,
        "category": f"BD et manga — {category} — Qui suis-je ?",
        "visualReview": "Approved: canonical individual character image; no lettering or second character. Copyrighted official art retained only for this private local game; do not redistribute.",
    }

bank.setdefault("revisionHistory", []).append({
    "id": REVISION,
    "note": "Expanded the BD character set with official Astérix drawings and the manga set with official Dragon Ball character art. Copyrighted images are restricted to private local gameplay and must not be redistributed.",
    "createdQuestions": created, "addedPresentationsToExistingQuestions": attached,
    "presentationIds": added,
})
BANK_PATH.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"presentationsAdded": len(added), "createdQuestions": created, "attached": attached, "ids": added}, ensure_ascii=False, indent=2))
