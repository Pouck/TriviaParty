"""Fetch character portraits from official BD/manga publishers for visual review.

These are copyrighted candidate assets for this private local game only. The
script never imports them into the question bank; a human visual review is
required first, and the sources are retained in metadata.json.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/image-qsj-sampler/candidates/bd-manga-official"
UA = "TriviaPartyPrivateLocalQuiz/1.0 (candidate visual review; no redistribution)"

TINTIN = {
    "tintin": ("Tintin", "https://cdn001.tintin.com/public/tintin/img/characters/tintin/tintin@2x.png", "https://www.tintin.com/en/characters/tintin"),
    "snowy": ("Snowy (Milou)", "https://cdn001.tintin.com/public/tintin/img/characters/milou/milou@2x.png", "https://www.tintin.com/en/characters/snowy"),
    "captain-haddock": ("Captain Haddock", "https://cdn001.tintin.com/public/tintin/img/characters/le-capitaine-haddock/le-capitaine-haddock@2x.png", "https://www.tintin.com/en/characters/captain-haddock"),
    "thomson-and-thompson": ("Thomson and Thompson", "https://cdn001.tintin.com/public/tintin/img/characters/dupond-et-dupont/dupond-et-dupont@2x.png", "https://www.tintin.com/en/characters/thomson-and-thompson"),
    "bianca-castafiore": ("Bianca Castafiore", "https://cdn001.tintin.com/public/tintin/img/characters/bianca-castafiore/bianca-castafiore@2x.png", "https://www.tintin.com/en/characters/bianca-castafiore"),
    "professor-calculus": ("Professor Calculus", "https://cdn001.tintin.com/public/tintin/img/characters/le-professeur-tournesol/le-professeur-tournesol@2x.png", "https://www.tintin.com/en/characters/professor-calculus"),
    "rastapopoulos": ("Rastapopoulos", "https://cdn001.tintin.com/public/tintin/img/characters/rastapopoulos/rastapopoulos@2x.png", "https://www.tintin.com/en/characters/rastapopoulos"),
    "general-alcazar": ("General Alcazar", "https://cdn001.tintin.com/public/tintin/img/characters/le-general-alcazar/le-general-alcazar@2x.png", "https://www.tintin.com/en/characters/general-alcazar"),
    "professor-tarragon": ("Professor Tarragon", "https://cdn001.tintin.com/public/tintin/img/characters/le-professeur-bergamotte/le-professeur-bergamotte@2x.png", "https://www.tintin.com/en/characters/professor-tarragon"),
    "rascar-capac": ("Rascar Capac", "https://cdn001.tintin.com/public/tintin/img/characters/rascar-capac/rascar-capac@2x.png", "https://www.tintin.com/en/characters/rascar-capac"),
    "tchang": ("Tchang", "https://cdn001.tintin.com/public/tintin/img/characters/tchang/tchang@2x.png", "https://www.tintin.com/en/characters/tchang"),
}
ONE_PIECE = {
    slug: (name, f"https://one-piece.com/o/assets/images/anime/character/data/{slug}/img.jpg", f"https://one-piece.com/character/{slug}/index.html")
    for slug, name in [
        ("luffy", "Monkey D. Luffy"), ("zoro", "Roronoa Zoro"), ("nami", "Nami"),
        ("usopp", "Usopp"), ("sanji", "Sanji"), ("chopper", "Tony Tony Chopper"),
        ("robin", "Nico Robin"), ("franky", "Franky"), ("brook", "Brook"), ("Jinbe", "Jinbe"),
    ]
}
ASTERIX = {
    key: (title, f"https://asterix.com/wp-content/uploads/2024/11/video-tuto-{key}.png", "https://asterix.com/en/the-gauls/")
    for key, title in [
        ("asterix", "Astérix"), ("obelix", "Obélix"), ("idefix", "Idéfix"),
        ("panoramix", "Panoramix"), ("falbala", "Falbala"),
    ]
}
DRAGON_BALL = {
    code: (title, f"https://dragonball-super.com/img/chara/cr-{code}.jpg", "https://dragonball-super.com/en/")
    for code, title in [
        ("goku", "Son Goku"), ("vegeta", "Vegeta"), ("bulma", "Bulma"),
        ("gohan", "Son Gohan"), ("pic", "Piccolo"), ("kri", "Krillin"),
        ("18", "Android 18"), ("tru", "Trunks"), ("bu", "Majin Buu"),
        ("beerus", "Beerus"), ("yam", "Yamcha"), ("chichi", "Chi-Chi"),
        ("kame", "Master Roshi"), ("videl", "Videl"),
    ]
}

OUT.mkdir(parents=True, exist_ok=True)
metadata = {}
for franchise, items in (("Bande dessinée", TINTIN), ("Bande dessinée", ASTERIX), ("Manga", ONE_PIECE), ("Manga", DRAGON_BALL)):
    for key, (title, url, page) in items.items():
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": page})
        try:
            with urllib.request.urlopen(req, timeout=35) as response:
                data = response.read()
                content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/") or len(data) < 1500:
                raise ValueError(f"unexpected response {content_type}, {len(data)} bytes")
            ext = ".png" if "png" in content_type else ".jpg" if "jpeg" in content_type else ".webp" if "webp" in content_type else ".gif"
            path = OUT / f"{key}{ext}"
            path.write_bytes(data)
            metadata[key] = {
                "title": title, "franchise": franchise, "candidate": path.relative_to(ROOT).as_posix(),
                "downloadedFrom": url, "sourcePage": page, "contentType": content_type,
                "bytes": len(data), "license": "Copyrighted official artwork; rights reserved; private local review only",
                "review": "Pending visual inspection; not imported into the question bank",
            }
            print(f"OK {key} {content_type} {len(data)}")
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            metadata[key] = {"title": title, "franchise": franchise, "downloadedFrom": url, "sourcePage": page, "candidateStatus": str(exc)}
            print(f"SKIP {key}: {exc}")
        time.sleep(0.15)

(OUT / "official-candidate-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Saved {sum('candidate' in x for x in metadata.values())}/{len(metadata)} official candidate portraits to {OUT}")
