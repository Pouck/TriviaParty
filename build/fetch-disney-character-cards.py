from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/image-qsj-sampler/candidates"
SOURCES = {
    "moana": ("https://princess.disney.com/", "https://lumiere-a.akamaihd.net/v1/images/ct_princess_moana_3497_0a28209c.jpeg?region=0,0,800,800"),
    "ariel": ("https://princess.disney.com/", "https://lumiere-a.akamaihd.net/v1/images/ct_princess_ariel_3497_d17c9d8a.jpeg?region=0,0,800,800"),
    "cinderella": ("https://princess.disney.com/", "https://lumiere-a.akamaihd.net/v1/images/ct_princess_cinderella_3497_4440a5f3.jpeg?region=0,0,800,800"),
    "belle": ("https://princess.disney.com/", "https://lumiere-a.akamaihd.net/v1/images/ct_princess_belle_3497_15a33a9c.jpeg?region=0,0,800,800"),
    "snow-white": ("https://princess.disney.com/", "https://lumiere-a.akamaihd.net/v1/images/ct_princess_snowwhite_3497_e41686e8.jpeg?region=0,0,800,800"),
    "mulan": ("https://princess.disney.com/", "https://lumiere-a.akamaihd.net/v1/images/ct_princess_mulan_3497_da24206c.jpeg?region=0,0,800,800"),
    "elsa": ("https://characters.disney.com/elsa", "https://lumiere-a.akamaihd.net/v1/images/ct_frozen_elsa_18466_22a50822_ad6090d1.jpeg?region=0,0,600,600"),
    "anna": ("https://characters.disney.com/elsa", "https://lumiere-a.akamaihd.net/v1/images/ct_frozen_anna_18466_6775584b_520ae44b.jpeg?region=0,0,600,600"),
    "olaf": ("https://characters.disney.com/elsa", "https://lumiere-a.akamaihd.net/v1/images/ct_frozen_olaf_18466_eabe1344_2dd6212f.jpeg?region=0,0,600,600"),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for key, (page, url) in SOURCES.items():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; TriviaPartyPrivate/1.0)"})
        data = urllib.request.urlopen(req, timeout=30).read()
        path = OUT / f"disney-{key}-official.jpg"
        path.write_bytes(data)
        manifest[key] = {"source": page, "downloadedFrom": url, "candidate": str(path), "bytes": len(data)}
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
