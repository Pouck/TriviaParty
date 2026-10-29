from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
import time
import urllib.error
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "build/image-qsj-candidate-targets.json"
OUT = ROOT / "build/image-qsj-sampler/candidates/quality-pass"
META_OUT = OUT / "metadata.json"
UA = "TriviaPartyPrivateImageReview/1.0 (local private-use quiz; attribution retained)"
LAST_REQUEST = 0.0


def get(url: str) -> bytes:
    global LAST_REQUEST
    for attempt in range(6):
        delay = 1.5 - (time.monotonic() - LAST_REQUEST)
        if delay > 0:
            time.sleep(delay)
        request = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                LAST_REQUEST = time.monotonic()
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 5:
                raise
            retry_after = error.headers.get("Retry-After", "")
            try:
                wait = max(5.0, min(60.0, float(retry_after)))
            except ValueError:
                wait = min(60.0, 5.0 * (2 ** attempt))
            print(f"Commons rate limit for {url}; retrying after {wait:.0f}s", flush=True)
            time.sleep(wait)
            LAST_REQUEST = time.monotonic()


def api(params: dict) -> dict:
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "format": "json", **params}
    )
    for attempt in range(6):
        result = json.loads(get(url))
        error = result.get("error", {})
        code = str(error.get("code", "")).casefold()
        if not error:
            return result
        if not any(tag in code for tag in ("ratelimit", "maxlag", "readonly", "too-busy")) or attempt == 5:
            raise RuntimeError(f"Wikimedia API error: {error}")
        wait = min(120, 30 * (attempt + 1))
        print(f"Commons API {code}; backing off {wait}s", flush=True)
        time.sleep(wait)
        global LAST_REQUEST
        LAST_REQUEST = time.monotonic()
    raise RuntimeError("Wikimedia API retry loop exhausted")


def plain(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]*>", "", value)).strip()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads(META_OUT.read_text(encoding="utf-8")) if META_OUT.exists() else {}
    selected_keys = set(sys.argv[1:])
    for target in json.loads(TARGETS.read_text(encoding="utf-8")):
        if selected_keys and target["key"] not in selected_keys:
            continue
        if target.get("skip"):
            continue
        prior = records.get(target["key"], {})
        prior_path = ROOT / prior.get("candidate", "__missing__")
        if prior.get("candidate") and prior_path.exists() and not target.get("refresh"):
            records[target["key"]] = {**prior, **target, "candidate": prior["candidate"], "downloadedFrom": prior["downloadedFrom"], "creator": prior.get("creator", ""), "credit": prior.get("credit", ""), "license": prior.get("license", ""), "licenseUrl": prior.get("licenseUrl", ""), "bytes": prior.get("bytes", 0)}
            continue
        if target.get("searchQuery"):
            search_query = re.sub(r"\s+Wikimedia Commons$", "", target["searchQuery"], flags=re.IGNORECASE)
            result = api({
                "generator": "search", "gsrsearch": search_query,
                "gsrnamespace": 6, "gsrlimit": 10, "prop": "imageinfo",
                "iiprop": "url|extmetadata|mime", "iiurlwidth": 1400,
            })
            pages = list(result.get("query", {}).get("pages", {}).values())
            desired = set(re.findall(r"[a-z0-9]+", target.get("displayTitle", "").casefold()))
            query_terms = set(re.findall(r"[a-z0-9]+", search_query.casefold()))
            query_terms -= {"the", "a", "an", "and", "of", "in", "at", "to", "full", "view", "exterior", "exteriors", "image", "photo", "picture", "building"}
            query_specific = query_terms - desired
            pages.sort(key=lambda p: (
                -4 * len(desired & set(re.findall(r"[a-z0-9]+", p.get("title", "").casefold())))
                - len(query_specific & set(re.findall(r"[a-z0-9]+", p.get("title", "").casefold()))),
                p.get("index", 999),
            ))
            page = None
            info = None
            for candidate_page in pages:
                candidate_info = candidate_page.get("imageinfo", [{}])[0]
                if not candidate_info.get("mime", "").startswith("image/"):
                    continue
                candidate_ext = candidate_info.get("extmetadata", {})
                candidate_license = plain(candidate_ext.get("LicenseShortName", {}).get("value", ""))
                if any(tag in candidate_license.casefold() for tag in ("cc", "public domain", "pd")):
                    page, info = candidate_page, candidate_info
                    break
            if not page:
                records[target["key"]] = {**target, "candidateStatus": "no suitable Commons result"}
                print(json.dumps({
                    "debugSearch": target["key"],
                    "resultCount": len(pages),
                    "results": [
                        {
                            "title": p.get("title"),
                            "mime": p.get("imageinfo", [{}])[0].get("mime"),
                            "license": plain(p.get("imageinfo", [{}])[0].get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")),
                        }
                        for p in pages[:5]
                    ],
                }, ensure_ascii=False), flush=True)
                print(json.dumps(records[target["key"]], ensure_ascii=False), flush=True)
                META_OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                continue
            title = page["title"]
            target["fileTitle"] = title
            target["sourcePage"] = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":_()'!,.-")
        else:
            title = target["fileTitle"]
            result = api({"prop": "imageinfo", "titles": title, "iiprop": "url|extmetadata", "iiurlwidth": 1400})
            page = next(iter(result["query"]["pages"].values()))
            if "imageinfo" not in page:
                raise RuntimeError(f"Wikimedia Commons has no image metadata for {title}")
            info = page["imageinfo"][0]
        ext = info.get("extmetadata", {})
        license_name = plain(ext.get("LicenseShortName", {}).get("value", ""))
        if not any(tag in license_name.casefold() for tag in ("cc", "public domain", "pd")):
            raise RuntimeError(f"Unapproved license {license_name!r} for {title}")
        image = get(info.get("thumburl", info["url"]))
        if not image.startswith((b"\xff\xd8", b"\x89PNG", b"RIFF")):
            raise RuntimeError(f"Unrecognized image data for {title}")
        suffix = ".jpg" if image.startswith(b"\xff\xd8") else ".png" if image.startswith(b"\x89PNG") else ".webp"
        path = OUT / (target["key"] + suffix)
        path.write_bytes(image)
        records[target["key"]] = {
            **target,
            "candidate": path.relative_to(ROOT).as_posix(),
            "downloadedFrom": info.get("thumburl", info["url"]),
            "creator": plain(ext.get("Artist", {}).get("value", "")),
            "credit": plain(ext.get("Credit", {}).get("value", "")),
            "license": license_name,
            "licenseUrl": plain(ext.get("LicenseUrl", {}).get("value", "")),
            "bytes": len(image),
        }
        print(json.dumps(records[target["key"]], ensure_ascii=False), flush=True)
        META_OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    META_OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
