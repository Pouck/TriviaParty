from __future__ import annotations

import re
import urllib.request

URLS = [
    "https://www.marvel.com/characters/iron-man-tony-stark",
    "https://www.marvel.com/characters/spider-man-peter-parker",
    "https://naruto-official.com/en/anime/naruto1",
]

for url in URLS:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"})
    try:
        data = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace")
        print("URL", url, "BYTES", len(data))
        for pattern in (r'<meta[^>]+property=["\']og:image["\'][^>]+>', r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']'):
            found = re.findall(pattern, data, flags=re.I)
            if found:
                print("OG", found[:2])
                break
        print("MARVEL_MEDIA", re.findall(r'https?://[^"\']+(?:cdn\.marvel\.com|static\.dc\.com)[^"\']+\.(?:jpg|png|webp)', data, flags=re.I)[:3])
    except Exception as exc:
        print("ERR", type(exc).__name__, str(exc))
