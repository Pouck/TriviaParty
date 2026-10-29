"""Fetch official candidate character portraits for private visual review only."""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/image-qsj-sampler/candidates/bd-manga-official"
OUT.mkdir(parents=True, exist_ok=True)

# key, title, franchise, page, direct image URL, file extension
ITEMS = [
    ("sailor-moon", "Sailor Moon", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/moon.png?20230324=", ".png"),
    ("sailor-mercury", "Sailor Mercury", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/mercury.png?20230324=", ".png"),
    ("sailor-mars", "Sailor Mars", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/mars.png?20230324=", ".png"),
    ("sailor-jupiter", "Sailor Jupiter", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/jupiter.png?20230324=", ".png"),
    ("sailor-venus", "Sailor Venus", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/venus.png?20230324=", ".png"),
    ("tuxedo-mask", "Tuxedo Mask", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/tuxedo.png?20230324=", ".png"),
    ("sailor-uranus", "Sailor Uranus", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/uranus.png?20230324=", ".png"),
    ("sailor-neptune", "Sailor Neptune", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/neptune.png?20230324=", ".png"),
    ("sailor-pluto", "Sailor Pluto", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/pluto.png?20230324=", ".png"),
    ("sailor-saturn", "Sailor Saturn", "Manga", "https://2023.sailormoon-movie.jp/character/", "https://2023.sailormoon-movie.jp/assets/images/char/popup/pc/saturn.png?20230324=", ".png"),
    ("lucky-luke-calamity-jane", "Calamity Jane", "Bande dessinée", "https://www.dargaud.com/bd/lucky-luke", "https://www.dargaud.com/sites/dargaud.com/files/2020-03/lucky_luke_personnages_calamity%20jane_0.png", ".png"),
    ("lucky-luke-billy-kid", "Billy the Kid", "Bande dessinée", "https://www.dargaud.com/bd/lucky-luke", "https://www.dargaud.com/sites/dargaud.com/files/2020-03/lucky_luke_personnages_billy_the_kid_0.png", ".png"),
    ("conan-character-01", "Detective Conan official character 01", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara01.jpg", ".jpg"),
    ("conan-character-02", "Detective Conan official character 02", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara02.jpg", ".jpg"),
    ("conan-character-03", "Detective Conan official character 03", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara03.jpg", ".jpg"),
    ("conan-character-04", "Detective Conan official character 04", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara04.jpg", ".jpg"),
    ("conan-character-05", "Detective Conan official character 05", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara05.jpg", ".jpg"),
    ("conan-character-06", "Detective Conan official character 06", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara06.jpg", ".jpg"),
    ("conan-character-07", "Detective Conan official character 07", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara07.jpg", ".jpg"),
    ("conan-character-08", "Detective Conan official character 08", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara08.jpg", ".jpg"),
    ("conan-character-09", "Detective Conan official character 09", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara09.jpg", ".jpg"),
    ("conan-character-10", "Detective Conan official character 10", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara10.jpg", ".jpg"),
    ("conan-character-11", "Detective Conan official character 11", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara11.jpg", ".jpg"),
    ("conan-character-12", "Detective Conan official character 12", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara12.jpg", ".jpg"),
    ("conan-character-13", "Detective Conan official character 13", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara13.jpg", ".jpg"),
    ("conan-character-14", "Detective Conan official character 14", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara14.jpg", ".jpg"),
    ("conan-character-15", "Detective Conan official character 15", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara15.jpg", ".jpg"),
    ("conan-character-16", "Detective Conan official character 16", "Manga", "https://www.conan-portal.com/index.html", "https://www.conan-portal.com/img/chara16.jpg", ".jpg"),
    ("jujutsu-yuji", "Yuji Itadori", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail1.png", ".png"),
    ("jujutsu-megumi", "Megumi Fushiguro", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail2.png", ".png"),
    ("jujutsu-nobara", "Nobara Kugisaki", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail3.png", ".png"),
    ("jujutsu-gojo", "Satoru Gojo", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail4.png", ".png"),
    ("jujutsu-maki", "Maki Zen'in", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail6.png", ".png"),
    ("jujutsu-inumaki", "Toge Inumaki", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail7.png", ".png"),
    ("jujutsu-panda", "Panda", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail8.png", ".png"),
    ("jujutsu-nanami", "Kento Nanami", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail9.png", ".png"),
    ("jujutsu-todo", "Aoi Todo", "Manga", "https://jujutsukaisen.jp/character/index_1st.php", "https://jujutsukaisen.jp/images/chara_detail13.png", ".png"),
]

metadata = {}
for key, title, franchise, page, url, ext in ITEMS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TriviaPartyPrivateLocalQuiz/1.0", "Referer": page})
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read()
            ctype = response.headers.get("Content-Type", "")
        if not ctype.startswith("image/") or len(data) < 1500:
            raise ValueError(f"unexpected response: {ctype}, {len(data)} bytes")
        path = OUT / f"{key}{ext}"
        path.write_bytes(data)
        metadata[key] = {"title": title, "franchise": franchise, "candidate": path.relative_to(ROOT).as_posix(), "downloadedFrom": url, "sourcePage": page, "contentType": ctype, "bytes": len(data), "license": "Copyrighted official artwork; rights reserved; private local review only", "review": "Pending visual inspection; not imported into the question bank"}
        print(f"OK {key} {len(data)} bytes")
    except Exception as exc:
        metadata[key] = {"title": title, "franchise": franchise, "downloadedFrom": url, "sourcePage": page, "candidateStatus": str(exc)}
        print(f"SKIP {key}: {exc}")
    time.sleep(.15)

(OUT / "next-candidate-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
