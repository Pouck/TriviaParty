from __future__ import annotations

from html.parser import HTMLParser
import json
import urllib.request

URLS = {
    "elsa": ("Elsa", "https://characters.disney.com/elsa"),
    "anna": ("Anna", "https://characters.disney.com/anna"),
    "olaf": ("Olaf", "https://characters.disney.com/olaf"),
}


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "img":
            src = values.get("data-src") or values.get("src") or values.get("data-lazy-src")
            if src:
                self.images.append({"alt": values.get("alt", ""), "src": src, "title": values.get("title", "")})


for label, (name, url) in URLS.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"})
        raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        parser = Parser()
        parser.feed(raw)
        matches = [item for item in parser.images if name.casefold() in (item["alt"] + " " + item["src"]).casefold()]
        print(label, json.dumps(matches[:15], ensure_ascii=False))
    except Exception as exc:
        print(label, type(exc).__name__, str(exc))
