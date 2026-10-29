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
CANDIDATES = ROOT / "build/image-qsj-sampler/candidates"
BACKUPS = ROOT / "review-backups"
REVISION = "2026-10-26-replace-more-cosplay-with-official-art"
SOURCES = {
    "image-qsj-personnages-de-manga-naruto-uzumaki": ("naruto-naruto-official.gif", "Naruto Uzumaki", "TV Tokyo", "https://www.tv-tokyo.co.jp/contents/naruto/chara.html", "https://www.tv-tokyo.co.jp/contents/naruto/images/chara_naruto_a.gif"),
    "image-qsj-personnages-de-manga-sakura-haruno": ("naruto-sakura-official.gif", "Sakura Haruno", "TV Tokyo", "https://www.tv-tokyo.co.jp/contents/naruto/chara.html", "https://www.tv-tokyo.co.jp/contents/naruto/images/chara_sakura_a.gif"),
    "image-qsj-personnages-de-manga-kakashi-hatake": ("naruto-kakashi-official.gif", "Kakashi Hatake", "TV Tokyo", "https://www.tv-tokyo.co.jp/contents/naruto/chara.html", "https://www.tv-tokyo.co.jp/contents/naruto/images/chara_kakasi_a.gif"),
    "image-qsj-personnages-de-manga-itachi-uchiha": ("itachi-chara_18_2.png", "Itachi Uchiha", "TV Tokyo", "https://www.tv-tokyo.co.jp/anime/naruto/sp/chara/chara_detail.html", "https://www.tv-tokyo.co.jp/anime/naruto/sp/images/chara/chara_18_2.png"),
    "image-qsj-personnages-de-manga-edward-elric": ("official-edward.png", "Edward Elric", "Fullmetal Alchemist: Brotherhood", "https://fullmetalalchemistusa.com/character/", "https://fullmetalalchemistusa.com/img/in/character/cha_01.png"),
    "image-qsj-personnages-disney-stitch-lilo-stitch": ("official-stitch.jpg", "Stitch", "Disney", "https://movies.disney.com/lilo-and-stitch", "https://lumiere-a.akamaihd.net/v1/images/p_liloandstitch_19755_0ba5c55e.jpeg?region=0,0,540,810"),
    "image-qsj-personnages-disney-goofy": ("official-goofy.jpg", "Goofy", "Disney", "https://movies.disney.com/a-goofy-movie", "https://lumiere-a.akamaihd.net/v1/images/p_agoofymovie_19641_e786ad86.jpeg?region=0,0,540,810"),
    "image-qsj-personnages-disney-tinker-bell": ("official-tinkerbell.jpg", "Tinker Bell", "Disney Fairies", "https://fairies.disney.com/tinker-bell", "https://lumiere-a.akamaihd.net/v1/images/2b65901707e2087367946f7b7772fd8335c6c9e5.jpeg?region=0%2C0%2C600%2C600"),
    "image-qsj-personnages-pixar-bo-peep-toy-story": ("official-bopeep.webp", "Bo Peep", "Disney and Pixar", "https://www.disneyplus.com/en-gb/explore/articles/toy-story-characters-cast", "https://disney.images.edge.bamgrid.com/ripcut-delivery/v2/variant/disney/A7FF479D7D5BA06ABA43FA085385F5913764BEBAA3262DA5ABD5126DEDF8EFF9/compose?format=webp&width=2560"),
    "image-qsj-personnages-pixar-forky": ("official-forky.jpg", "Forky", "Disney and Pixar", "https://www.disney.co.jp/movie/toy4/character/forky", "https://lumiere-a.akamaihd.net/v1/images/12488_12452_12539_12473_12540_12522_12540_4_65372_49be77fe.jpeg?region=0%2C0%2C144%2C144"),
    "image-qsj-personnages-pixar-sadness-inside-out": ("pixar-sadness-official.jpg", "Sadness", "Pixar", "https://www.pixar.com/inside-out", "https://images.squarespace-cdn.com/content/v1/60241cb68df65b530cd84d95/47fba61d-b6a0-4be2-8126-b8e514740bec/io_sad11.jpg"),
    "image-qsj-personnages-pixar-miguel-coco": ("pixar-coco2-official.jpg", "Miguel", "Pixar", "https://www.pixar.com/coco", "https://images.squarespace-cdn.com/content/v1/60241cb68df65b530cd84d95/1718234902896-QK0W67FKFEKL5G22TOZ9/2.jpg"),
}


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
        print("Remaining official character art replacements are already applied.")
        return
    by_id = {p["id"]: (q, p) for q in bank["questions"] for p in q.get("presentations", [])}
    missing = set(SOURCES) - set(by_id)
    if missing:
        raise ValueError(f"Missing target presentations: {sorted(missing)}")
    credits = json.loads(CREDITS.read_text(encoding="utf-8"))
    BACKUPS.mkdir(parents=True, exist_ok=True)
    qbackup = BACKUPS / "question-bank-before-remaining-official-art-2026-10-26.json"
    cbackup = BACKUPS / "image-credits-before-remaining-official-art-2026-10-26.json"
    if not qbackup.exists():
        shutil.copyfile(QUESTIONS, qbackup)
    if not cbackup.exists():
        shutil.copyfile(CREDITS, cbackup)
    for pid, (candidate_name, title, publisher, page, direct) in SOURCES.items():
        candidate = CANDIDATES / candidate_name
        data = candidate.read_bytes()
        ext = candidate.suffix.lower()
        filename = hashlib.sha256(data).hexdigest()[:24] + ext
        (MEDIA / filename).write_bytes(data)
        question, presentation = by_id[pid]
        presentation["content"]["imageUrl"] = "media/" + filename
        credits[filename] = {
            "filename": candidate.name,
            "title": title + " — official character image",
            "creator": publisher + "; individual artist or photographer not identified on source page",
            "credit": publisher,
            "license": "Copyrighted official character image; retained for user's private, noncommercial local app only; not an open redistribution license",
            "licenseUrl": "",
            "source": page,
            "downloadedFrom": direct,
            "localSource": "Official character profile or film page image, downloaded 2026-10-26",
            "question": question.get("answers", [title])[0],
            "category": presentation.get("legacyCategory", ""),
        }
    ids = list(SOURCES)
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Replaced additional cosplay photos with official character portraits and film art.",
        "updatedPresentations": len(ids),
        "presentationIds": ids,
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updatedPresentations": ids, "backup": str(qbackup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
