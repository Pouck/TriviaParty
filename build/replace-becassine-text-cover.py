"""Replace Bécassine's answer-bearing album cover with a reviewed original panel."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTION_ID = "image-qsj-bd-personnages-de-bande-dessinee-becassine"
PRESENTATION_ID = QUESTION_ID
REVISION = "2026-10-27-replace-becassine-answer-bearing-cover"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Becassine_chez_les_Turcs_p11-a4.jpg"
SOURCE_IMAGE = ROOT / "build/image-qsj-sampler/candidates/quality-pass/bd-becassine-turcs-11.jpg"


def main() -> None:
    questions_path = BANK / "questions.json"
    credits_path = BANK / "IMAGE-QSJ-MEDIA-CREDITS.json"
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    credits = json.loads(credits_path.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in questions.get("revisionHistory", [])):
        print("Bécassine replacement already applied.")
        return
    if not SOURCE_IMAGE.is_file():
        raise FileNotFoundError(SOURCE_IMAGE)

    backups = ROOT / "review-backups"
    backups.mkdir(exist_ok=True)
    for source, dest in (
        (questions_path, backups / "questions-before-becassine-text-cover-2026-10-27.json"),
        (credits_path, backups / "credits-before-becassine-text-cover-2026-10-27.json"),
    ):
        if not dest.exists():
            shutil.copyfile(source, dest)

    target = next(q for q in questions["questions"] if q["id"] == QUESTION_ID)
    presentation = next(p for p in target["presentations"] if p["id"] == PRESENTATION_ID)
    data = SOURCE_IMAGE.read_bytes()
    filename = hashlib.sha256(data).hexdigest()[:24] + SOURCE_IMAGE.suffix.lower()
    media_path = BANK / "media" / filename
    if not media_path.exists():
        shutil.copyfile(SOURCE_IMAGE, media_path)
    presentation["content"]["imageUrl"] = "media/" + filename

    candidate = json.loads((ROOT / "build/image-qsj-sampler/candidates/quality-pass/metadata.json").read_text(encoding="utf-8"))["bd-becassine-turcs-11"]
    credits[filename] = {
        "filename": "Becassine chez les Turcs p11-a4.jpg",
        "title": "Bécassine (Joseph Pinchon illustration)",
        "creator": candidate.get("creator", ""),
        "credit": candidate.get("credit", ""),
        "license": candidate["license"],
        "licenseUrl": candidate.get("licenseUrl", ""),
        "source": SOURCE_PAGE,
        "downloadedFrom": candidate.get("downloadedFrom", ""),
        "localSource": candidate["candidate"],
        "question": target.get("answers", [""])[0],
        "category": presentation["legacyCategory"],
        "visualReview": "Approved: original Pinchon drawing, one dominant Bécassine in her canonical green dress, white coiffe, apron and clogs; no lettering. A small portrait within the scene is secondary and does not compete with the main figure.",
    }
    questions.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced the Bécassine album cover with large printed lettering by a text-free original character panel from the public-domain Gallica album.",
        "updatedPresentations": [PRESENTATION_ID],
    })
    questions_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"presentation": PRESENTATION_ID, "image": filename, "source": SOURCE_PAGE}, ensure_ascii=False))


if __name__ == "__main__":
    main()
