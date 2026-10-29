"""Replace ambiguous Pixar image hits with visually checked, licensed sources."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("character_collector", ROOT / "build/add-image-qsj-characters.py")
collector = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = collector
spec.loader.exec_module(collector)

BANK = ROOT / "game-library/bank/questions.json"
CREDITS = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
MEDIA = ROOT / "game-library/bank/media"
REVISION_ID = "2026-10-26-repair-pixar-image-sources"

# old id, replacement id, answer, aliases, Commons file, subject proof.
# The Edna Mode photo has no character name in its caption; it was visually
# checked and shows her iconic bob, glasses, and red jacket.
REPAIRS = [
    ("image-qsj-personnages-pixar-nemo", "image-qsj-personnages-pixar-nemo", "Nemo", [],
     "File:HK Kln Bay Telford Plaza Nemo Disney Pixar Xmas 2007 a.jpg", "nemo"),
    ("image-qsj-personnages-pixar-dory-finding-nemo", "image-qsj-personnages-pixar-edna-mode", "Edna Mode", ["Edna"],
     "File:DH25 cosplay 07.jpg", None),
    ("image-qsj-personnages-pixar-wall-e", "image-qsj-personnages-pixar-wall-e", "WALL-E", ["Wall-E"],
     "File:205 MNACTEC (Terrassa), exposició temporal Robots, WALL·E, de Disney Pixar (2008).jpg", "wall e"),
    ("image-qsj-personnages-pixar-mater-cars", "image-qsj-personnages-pixar-lightning-mcqueen", "Lightning McQueen", ["Flash McQueen"],
     "File:HCCD25 - Lightning McQueen.jpg", "lightning mcqueen"),
    ("image-qsj-personnages-pixar-remy-ratatouille", "image-qsj-personnages-pixar-remy-ratatouille", "Rémy", ["Remy", "Remy (Ratatouille)"],
     "File:DragonCon 2012 - Thursday Night - Ratatouille Cosplayer.jpg", "ratatouille"),
    ("image-qsj-personnages-pixar-joy-inside-out", "image-qsj-personnages-pixar-joy-inside-out", "Joie", ["Joy", "Joy (Inside Out)"],
     "File:Japan Expo 2024 - Cosplay of Joy.jpg", "cosplay of joy"),
    ("image-qsj-personnages-pixar-sadness-inside-out", "image-qsj-personnages-pixar-sadness-inside-out", "Tristesse", ["Sadness", "Sadness (Inside Out)"],
     "File:Inside Out - Sadness - Cosplayer at the 2015 Comic-Con International.jpg", "cosplay of sadness"),
    ("image-qsj-personnages-pixar-miguel-coco", "image-qsj-personnages-pixar-miguel-coco", "Miguel", ["Miguel (Coco)"],
     "File:Hector and Miguel Cosplay WonderCon 2018.jpg", "hector and miguel"),
    ("image-qsj-personnages-pixar-russell-up", "image-qsj-personnages-pixar-russell-up", "Russell", ["Russell (Up)"],
     "File:San Diego Comic-Con 2011 - Russell from Pixar's Up (6039799010).jpg", "russell from pixar s up"),
]


def main() -> None:
    data = json.loads(BANK.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION_ID for row in data.get("revisionHistory", [])):
        print("Pixar image sources have already been repaired.")
        return
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    titles = [row[4] for row in REPAIRS]
    response = collector.api({
        "action": "query", "titles": "|".join(titles), "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": 1100, "format": "json",
    })
    metadata = {page["title"]: page["imageinfo"][0]
                for page in response.get("query", {}).get("pages", {}).values()
                if page.get("imageinfo")}

    # Validate licenses and source captions before downloading or editing data.
    for old_id, new_id, answer, aliases, file_title, proof in REPAIRS:
        info = metadata.get(file_title)
        if not info or not info.get("thumburl"):
            raise ValueError(f"Commons file is unavailable: {file_title}")
        licensed, license_name = collector.license_allowed(info.get("extmetadata", {}))
        if not licensed:
            raise ValueError(f"Commons license is not allowed: {file_title} ({license_name})")
        if proof:
            ext = info.get("extmetadata", {})
            subject = collector.norm(file_title + " " + collector.plain(ext.get("ImageDescription", {}).get("value", "")))
            if proof not in subject:
                raise ValueError(f"Subject check failed for {file_title}: expected {proof!r}")

    staged = []
    for row in REPAIRS:
        old_id, new_id, answer, aliases, file_title, proof = row
        info = metadata[file_title]
        ext = info.get("extmetadata", {})
        thumb = info["thumburl"].replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
        image_bytes = collector.download(thumb)
        extension = Path(urllib.parse.urlparse(thumb).path).suffix.lower() or ".jpg"
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            extension = ".jpg"
        media_name = hashlib.sha256(image_bytes).hexdigest()[:24] + extension
        staged.append((row, info, ext, thumb, image_bytes, media_name))

    questions = data["questions"]
    used_ids = {legacy_id for q in questions for legacy_id in q.get("legacyIds", [])}
    for old_id, new_id, answer, aliases, file_title, proof in REPAIRS:
        old_question = next((q for q in questions if q.get("id") == old_id), None)
        if old_question is None:
            raise ValueError(f"Could not find Pixar entry {old_id}")
        if new_id != old_id and new_id in used_ids:
            raise ValueError(f"Replacement ID already exists: {new_id}")

    old_media = set()
    for question in questions:
        for presentation in question.get("presentations", []):
            if presentation.get("id") in {r[0] for r in REPAIRS}:
                old_name = presentation.get("content", {}).get("imageUrl", "").removeprefix("media/")
                if old_name:
                    old_media.add(old_name)
                credits.pop(old_name, None)

    for staged_row in staged:
        row, info, ext, thumb, image_bytes, media_name = staged_row
        old_id, new_id, answer, aliases, file_title, proof = row
        question = next(q for q in questions if q.get("id") == old_id)
        presentation = next(p for p in question.get("presentations", []) if p.get("id") == old_id)
        if new_id != old_id:
            presentation["id"] = new_id
            presentation["legacyIds"] = [new_id]
            question["id"] = new_id
            question["legacyIds"] = [new_id]
            question["answers"] = list(dict.fromkeys([answer, *aliases]))
        presentation["label"] = "Qui suis-je ? — image"
        presentation["content"]["imageUrl"] = "media/" + media_name
        presentation["legacyCategory"] = "Personnages Pixar — Personnages Pixar — Qui suis-je ?"
        presentation["legacyPackageId"] = "image-qsj-personnages-pixar"
        (MEDIA / media_name).write_bytes(image_bytes)
        source_title = file_title.removeprefix("File:")
        credits[media_name] = {
            "filename": source_title, "title": source_title,
            "creator": collector.plain(ext.get("Artist", {}).get("value", "")),
            "credit": collector.plain(ext.get("Credit", {}).get("value", "")),
            "license": collector.plain(ext.get("LicenseShortName", {}).get("value", "")),
            "licenseUrl": collector.plain(ext.get("LicenseUrl", {}).get("value", "")),
            "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(source_title.replace(" ", "_"), safe=":()_,'-"),
            "downloadedFrom": thumb, "localSource": "Wikimedia Commons thumbnail, resized to 1100 px width",
            "question": answer, "category": presentation["legacyCategory"],
        }

    still_used = {p.get("content", {}).get("imageUrl", "").removeprefix("media/")
                  for q in questions for p in q.get("presentations", [])}
    for media_name in old_media - still_used:
        old_path = MEDIA / media_name
        if old_path.exists():
            old_path.unlink()
    data.setdefault("revisionHistory", []).append({
        "id": REVISION_ID,
        "note": "Replaced nine unrelated or weak Pixar image matches with licensed character photos and cosplay images.",
        "updatedPresentations": len(REPAIRS), "presentationIds": [r[1] for r in REPAIRS],
    })
    BANK.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Repaired {len(REPAIRS)} Pixar image presentations with licensed, subject-matched sources.")


if __name__ == "__main__":
    main()
