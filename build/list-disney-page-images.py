from __future__ import annotations

import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"}
PAGES = {
    "princess": "https://princess.disney.com/",
    "elsa": "https://characters.disney.com/elsa",
    "mickey": "https://mickey.disney.com/",
}
NAMES = ("moana", "cinderella", "mulan", "belle", "ariel", "snow white", "elsa", "anna", "olaf", "mickey", "minnie", "donald", "goofy", "pluto", "maleficent", "tinker bell")


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            src = a.get("data-src") or a.get("src") or a.get("data-lazy-src")
            if src:
                self.images.append({"alt": a.get("alt", ""), "src": src})


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    p = Parser()
    p.feed(raw)
    return p.images


with ThreadPoolExecutor(max_workers=4) as pool:
    tasks = {pool.submit(get, url): key for key, url in PAGES.items()}
    found = {}
    for future in as_completed(tasks):
        key = tasks[future]
        try:
            found[key] = future.result()
        except Exception as exc:
            found[key] = [{"alt": "ERROR " + repr(exc), "src": ""}]
for key, items in found.items():
    print("PAGE", key)
    for item in items:
        if "ct_princess_" in item["src"] or "ct_frozen_" in item["src"]:
            print(json.dumps(item, ensure_ascii=True))
