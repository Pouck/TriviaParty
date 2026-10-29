from __future__ import annotations

import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/image-qsj-sampler/candidates"
SOURCES = {
    "black-canary": "https://www.dc.com/characters/black-canary",
    "batgirl": "https://www.dc.com/characters/batgirl",
    "robin": "https://www.dc.com/characters/robin",
    "shazam": "https://www.dc.com/characters/shazam",
    "penguin": "https://www.dc.com/characters/the-penguin",
    "cyborg": "https://www.dc.com/characters/cyborg",
    "lex-luthor": "https://www.dc.com/characters/lex-luthor",
    "batwoman": "https://www.dc.com/characters/batwoman",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"}


def get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=25).read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, page in SOURCES.items():
        try:
            body = get(page).decode("utf-8", "replace")
            match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)', body, re.I)
            if not match:
                match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image', body, re.I)
            if not match:
                results[name] = {"error": "no Open Graph image", "source": page}
                continue
            image_url = html.unescape(match.group(1))
            image = get(image_url)
            path = OUT / f"dc-{name}-official.jpg"
            path.write_bytes(image)
            results[name] = {"source": page, "downloadedFrom": image_url, "candidate": str(path), "bytes": len(image)}
        except Exception as exc:
            results[name] = {"error": f"{type(exc).__name__}: {exc}", "source": page}
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
