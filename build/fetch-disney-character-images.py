from __future__ import annotations

import html
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/image-qsj-sampler/candidates"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"}
TARGETS = {
    "simba": ("Simba", "https://movies.disney.com/the-lion-king"),
    "elsa": ("Elsa", "https://frozen.disney.com/"),
    "cinderella": ("Cinderella", "https://princess.disney.com/cinderella"),
    "olaf": ("Olaf", "https://frozen.disney.com/"),
    "moana": ("Moana", "https://princess.disney.com/moana"),
    "peter-pan": ("Peter Pan", "https://movies.disney.com/peter-pan"),
    "ariel": ("Ariel", "https://princess.disney.com/ariel"),
    "mulan": ("Mulan", "https://princess.disney.com/mulan"),
    "belle": ("Belle", "https://princess.disney.com/belle"),
    "stitch": ("Stitch", "https://movies.disney.com/lilo-stitch"),
    "mickey": ("Mickey Mouse", "https://mickey.disney.com/"),
    "minnie": ("Minnie Mouse", "https://mickey.disney.com/"),
    "donald": ("Donald Duck", "https://mickey.disney.com/"),
    "goofy": ("Goofy", "https://mickey.disney.com/"),
    "pluto": ("Pluto", "https://mickey.disney.com/"),
    "anna": ("Anna", "https://frozen.disney.com/"),
    "tinker-bell": ("Tinker Bell", "https://fairies.disney.com/tinker-bell"),
    "snow-white": ("Snow White", "https://princess.disney.com/snow-white"),
    "maleficent": ("Maleficent", "https://movies.disney.com/maleficent"),
    "aladdin": ("Aladdin", "https://movies.disney.com/aladdin"),
}


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            src = a.get("data-src") or a.get("src") or a.get("data-lazy-src")
            if src:
                self.items.append((a.get("alt", ""), src))


def request(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30).read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pages = sorted({page for _, page in TARGETS.values()})
    page_images = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(request, page): page for page in pages}
        for future in as_completed(futures):
            page = futures[future]
            try:
                parser = Images()
                parser.feed(future.result().decode("utf-8", "replace"))
                page_images[page] = parser.items
            except Exception as exc:
                page_images[page] = []
                print("PAGE ERROR", page, type(exc).__name__, str(exc), flush=True)
    results = {}
    for key, (name, page) in TARGETS.items():
        choices = [(alt, src) for alt, src in page_images.get(page, []) if name.casefold() in html.unescape(alt).casefold() and ("lumiere-a.akamaihd.net" in src or "disney" in src)]
        choices = [(a, s) for a, s in choices if not any(no in a.casefold() for no in ("cosplay", "dress up", "inspired by", "real life"))]
        downloaded = False
        error = None
        for alt, src in choices:
            url = html.unescape(src)
            if url.startswith("//"):
                url = "https:" + url
            try:
                data = request(url)
                if len(data) < 8000:
                    continue
                path = OUT / f"disney-{key}.img"
                path.write_bytes(data)
                results[key] = {"title": name, "page": page, "alt": alt, "downloadedFrom": url, "candidate": str(path), "bytes": len(data)}
                downloaded = True
                break
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        if not downloaded:
            results[key] = {"title": name, "page": page, "error": error or "no matching official character image", "matches": len(choices)}
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
