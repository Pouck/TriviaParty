from __future__ import annotations

import re
import urllib.request

URLS = [
    "https://characters.disney.com/elsa",
    "https://characters.disney.com/moana",
    "https://characters.disney.com/cinderella",
    "https://characters.disney.com/mickey-mouse",
    "https://characters.disney.com/stitch",
    "https://www.pixar.com/characters",
    "https://www.pixar.com/toy-story",
]
for url in URLS:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"})
        data = urllib.request.urlopen(request, timeout=25).read().decode("utf-8", "replace")
        meta = re.findall(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)', data, re.I)
        print(url, "bytes", len(data), "og", meta[:1], "img", re.findall(r'<img[^>]+src=["\']([^"\']+)', data, re.I)[:5])
    except Exception as exc:
        print(url, type(exc).__name__, str(exc))
