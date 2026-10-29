from __future__ import annotations

import html
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/image-qsj-sampler/candidates"
CHARACTERS = {
    "iron-man": "iron-man-tony-stark",
    "spider-man": "spider-man-peter-parker",
    "wolverine": "wolverine-james-howlett",
    "thor": "thor-thor-odinson",
    "captain-america": "captain-america-steve-rogers",
    "hulk": "hulk-bruce-banner",
    "black-panther": "black-panther-t-challa",
    "doctor-strange": "doctor-strange-stephen-strange",
    "groot": "groot",
    "black-widow": "black-widow-natasha-romanova/in-comics/",
    "ant-man": "ant-man-scott-lang",
    "deadpool": "deadpool-wade-wilson",
    "loki": "loki",
    "hawkeye": "hawkeye-clint-barton",
    "scarlet-witch": "scarlet-witch-wanda-maximoff",
    "captain-marvel": "captain-marvel-carol-danvers",
    "daredevil": "daredevil-matthew-murdock",
    "venom": "venom-eddie-brock",
    "star-lord": "star-lord-peter-quill/in-comics/",
    "thanos": "thanos",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"}


def fetch(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60).read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}

    def one(key: str, slug: str):
        path = OUT / f"marvel-{key}-official.webp"
        if path.is_file() and path.stat().st_size > 5000:
            return key, {"status": "candidate already downloaded", "candidate": str(path), "bytes": path.stat().st_size}
        page = slug if slug.startswith("https://") else "https://www.marvel.com/characters/" + slug
        try:
            try:
                body = fetch(page).decode("utf-8", "replace")
            except Exception:
                if slug.endswith("/"):
                    raise
                page += "/"
                body = fetch(page).decode("utf-8", "replace")
            match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)', body, re.I)
            if not match:
                match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image', body, re.I)
            if not match:
                return key, {"error": "no Open Graph image", "source": page}
            image_url = html.unescape(match.group(1))
            data = fetch(image_url)
            path.write_bytes(data)
            return key, {"source": page, "downloadedFrom": image_url, "candidate": str(path), "bytes": len(data)}
        except Exception as exc:
            return key, {"error": f"{type(exc).__name__}: {exc}", "source": page}

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(one, key, slug) for key, slug in CHARACTERS.items()]
        for future in as_completed(futures):
            key, data = future.result()
            results[key] = data
            print(key, data, flush=True)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
