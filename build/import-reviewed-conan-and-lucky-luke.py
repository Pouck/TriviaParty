"""Import official single-subject Detective Conan and Lucky Luke portraits."""
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
REVISION = "2026-10-27-reviewed-conan-lucky-luke-portraits"
CONAN_PAGE = "https://www.conan-portal.com/index.html"
LL_PAGE = "https://www.dargaud.com/bd/lucky-luke"

# candidate key, answer, aliases, franchise series, short fact, official page, source owner
ITEMS = [
    ("conan-character-01", "Conan Edogawa", ["Detective Conan", "Conan"], "Detective Conan", "Collégien en apparence, il est en réalité le lycéen détective Shinichi Kudo, transformé par un poison.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-02", "Shinichi Kudo", ["Shinichi Kudō", "Kudo Shinichi"], "Detective Conan", "Lycéen détective, il poursuit ses enquêtes sous l'identité de Conan Edogawa.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-03", "Ran Mouri", ["Ran Mori", "Mouri Ran"], "Detective Conan", "Amie d'enfance de Shinichi Kudo et championne de karaté.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-04", "Kogoro Mouri", ["Kogoro Mori", "Mouri Kogoro"], "Detective Conan", "Détective privé dont les affaires sont souvent résolues à son insu par Conan.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-05", "Ai Haibara", ["Shiho Miyano", "Sherry"], "Detective Conan", "Ancienne membre de l'Organisation des hommes en noir, elle a aussi été rajeunie par le poison.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-06", "Hiroshi Agasa", ["Professor Agasa", "Dr Agasa"], "Detective Conan", "Inventeur et ami de Conan, il l'aide avec des gadgets et protège son secret.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-07", "Heiji Hattori", ["Hattori Heiji"], "Detective Conan", "Lycéen détective d'Osaka, souvent présenté comme le rival amical de Shinichi.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-09", "Kazuha Toyama", ["Toyama Kazuha"], "Detective Conan", "Amie d'enfance de Heiji Hattori et pratiquante d'aïkido.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-10", "Kaito Kid", ["Kaitou Kid", "Kid the Phantom Thief", "Kaito Kuroba"], "Detective Conan", "Cambrioleur de génie et rival récurrent de Conan.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-11", "Shuichi Akai", ["Shūichi Akai", "Subaru Okiya"], "Detective Conan", "Agent du FBI et tireur d'élite connu sous le nom de code Silver Bullet.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-12", "Rei Furuya", ["Toru Amuro", "Tōru Amuro", "Bourbon"], "Detective Conan", "Agent de la police secrète infiltré dans l'Organisation des hommes en noir sous le nom de Bourbon.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-13", "Gin", ["Gin (Detective Conan)"], "Detective Conan", "Membre influent de l'Organisation des hommes en noir.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-14", "Vodka", ["Vodka (Detective Conan)"], "Detective Conan", "Partenaire de Gin au sein de l'Organisation des hommes en noir.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-15", "Vermouth", ["Chris Vineyard", "Sharon Vineyard"], "Detective Conan", "Actrice et membre de haut rang de l'Organisation des hommes en noir.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("conan-character-16", "Kir", ["Rena Mizunashi", "Hidemi Hondou", "Hidemi Hondo"], "Detective Conan", "Espionne infiltrée au sein de l'Organisation des hommes en noir.", CONAN_PAGE, "Gosho Aoyama / Shogakukan"),
    ("lucky-luke-billy-kid", "Billy the Kid", ["Billy le Kid"], "Lucky Luke", "Héros du Far West parodique, adversaire colérique de Lucky Luke et amateur de pâtisseries.", LL_PAGE, "Morris / Dargaud"),
]

def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")

bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
    raise SystemExit("This reviewed portrait import has already been applied")
credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8"))
questions = bank["questions"]
used_ids = {alias for q in questions for alias in [q["id"], *q.get("legacyIds", [])]}
backup = ROOT / "review-backups"
backup.mkdir(exist_ok=True)
(backup / "questions-before-conan-lucky-luke-2026-10-27.json").write_text(BANK_PATH.read_text(encoding="utf-8"), encoding="utf-8")
(backup / "credits-before-conan-lucky-luke-2026-10-27.json").write_text(CREDITS_PATH.read_text(encoding="utf-8"), encoding="utf-8")

added_ids = []
for key, answer, aliases, franchise, fact, source, creator in ITEMS:
    candidates = list(CANDIDATE_DIR.glob(f"{key}.*"))
    if len(candidates) != 1:
        raise FileNotFoundError(f"Expected one reviewed candidate for {key}, found {len(candidates)}")
    candidate = candidates[0]
    data = candidate.read_bytes()
    filename = hashlib.sha256(data).hexdigest()[:24] + candidate.suffix.lower()
    target = MEDIA_DIR / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(candidate, target)

    category = "Personnages de bande dessinée" if franchise == "Lucky Luke" else "Personnages de manga"
    pres_id = f"image-qsj-{slug(category)}-{slug(answer)}-official-20261027-c"
    if pres_id in used_ids:
        raise ValueError(f"Duplicate presentation id: {pres_id}")
    q = {
        "id": pres_id,
        "legacyIds": [pres_id],
        "topics": ["BD et manga", franchise],
        "prompt": "Qui suis-je ?",
        "answers": list(dict.fromkeys([answer, *aliases])),
        "content": {},
        "explanation": fact,
        "imageFacts": {
            "subjectType": "fictional_character",
            "subjectTitle": answer,
            "franchise": franchise,
            "facts": [
                {"kind": "subject_title", "value": answer, "sourceUrl": source},
                {"kind": "series", "value": franchise, "sourceUrl": source},
                {"kind": "media_creator", "role": "official artwork copyright holder; no open license indicated", "value": creator, "sourceUrl": source},
            ],
            "sources": [source],
        },
        "presentations": [{
            "id": pres_id,
            "label": "Qui suis-je ? — image",
            "answerMode": "BUZZER",
            "topic": "BD et manga",
            "legacyCategory": f"BD et manga — {category} — Qui suis-je ?",
            "legacyPackageId": f"image-qsj-{slug(category)}",
            "content": {
                "kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                "imageRevealMode": "PIXELATE", "imageRevealSteps": 6,
                "imageUrl": f"media/{filename}", "basePoints": 30, "penaltyPoints": 0,
            },
        }],
        "legacyReviews": [],
    }
    questions.append(q)
    used_ids.add(pres_id)
    added_ids.append(pres_id)
    direct = f"https://www.conan-portal.com/img/{key.rsplit('-',1)[-1]}.jpg" if franchise == "Detective Conan" else "https://www.dargaud.com/sites/dargaud.com/files/2020-03/lucky_luke_personnages_billy_the_kid_0.png"
    credits[filename] = {
        "filename": candidate.name,
        "title": f"{franchise} official character portrait",
        "creator": creator,
        "credit": f"© {creator}",
        "license": "Copyrighted official artwork; rights reserved; private local use only",
        "licenseUrl": source,
        "source": source,
        "downloadedFrom": direct,
        "localSource": "Official character page; image retained unchanged",
        "question": answer,
        "category": f"BD et manga — {category} — Qui suis-je ?",
        "visualReview": "Approved: one canonical character, no visible lettering, no second subject; retained unchanged for this private local game only. Do not redistribute.",
    }

bank.setdefault("revisionHistory", []).append({
    "id": REVISION,
    "note": "Added visually reviewed single-character official art from the Detective Conan/Shogakukan portal and Dargaud's Lucky Luke character page. Excluded the Detective Boys group portrait, the Calamity Jane art with a second faded silhouette, and Sailor Moon character cards with prominent text. Copyrighted artwork is for private local gameplay only.",
    "createdQuestions": len(added_ids),
    "addedPresentationsToExistingQuestions": 0,
    "presentationIds": added_ids,
})
BANK_PATH.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"added": len(added_ids), "questions": added_ids}, ensure_ascii=False, indent=2))
