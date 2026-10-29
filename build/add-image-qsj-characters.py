"""Add free-licensed, recognizable character cosplay/photo images to the bank.

The image itself must come from a Commons category for the named character (or
be a Commons search result whose title/description identifies that character).
Only Public Domain, CC0, CC BY, and CC BY-SA images are accepted.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MEDIA_DIR = ROOT / "game-library/bank/media"
CREDITS_PATH = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
UA = "TriviaParty image-bank collector/1.0 (https://github.com/Pouck/TriviaParty) urllib"
REVISION_ID = "2026-10-26-character-image-qsj-replacements"
ALLOWED_LICENSES = {"CC0", "Public domain"}
ALLOWED_LICENSE_PREFIXES = ("CC BY", "CC-BY")
MIN_REQUEST_INTERVAL = 1.0
_last_request_at = 0.0


def pace_requests() -> None:
    global _last_request_at
    now = time.monotonic()
    delay = MIN_REQUEST_INTERVAL - (now - _last_request_at)
    if delay > 0:
        time.sleep(delay)
    _last_request_at = time.monotonic()


def retry_delay(headers, attempt: int) -> float:
    value = headers.get("Retry-After") if headers else None
    if value:
        try:
            return max(5.0, float(value))
        except ValueError:
            try:
                return max(5.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
            except Exception:
                pass
    return max(5.0, 5.0 * (2 ** attempt))

# (character name used in Commons, French accepted answer, other aliases)
GROUPS = [
    ("BD et manga", "BD — Personnages de bande dessinée", "BD et manga", [
        ("Tintin", "Tintin", ["Les Aventures de Tintin"]),
        ("Milou", "Milou", ["Snowy"]),
        ("Captain Haddock", "Le capitaine Haddock", ["Capitaine Haddock", "Haddock"]),
        ("Astérix", "Astérix", ["Asterix"]),
        ("Yoko Tsuno", "Yoko Tsuno", []),        ("Valerian and Laureline", "Valerian et Laureline", ["Valerian"]),        ("Lucky Luke", "Lucky Luke", []),
        ("Jolly Jumper", "Jolly Jumper", []),
        ("Marsupilami", "Le Marsupilami", ["Marsupilami"]),
        ("Smurfs", "Les Schtroumpfs", ["Schtroumpf", "Smurfs"]),
        ("Gaston Lagaffe", "Gaston Lagaffe", ["Gaston"]),
        ("Blueberry (comics)", "Blueberry", ["Mike Blueberry"]),        ("Spirou", "Spirou", []),
        ("Fantasio", "Fantasio", []),
        ("Bécassine", "Bécassine", []),
        ("Titeuf", "Titeuf", []),
        ("Boule et Bill", "Boule et Bill", ["Boule", "Bill"]),
        ("Corto Maltese", "Corto Maltese", []),        ("Blake and Mortimer", "Blake et Mortimer", ["Blake", "Mortimer"]),        ("XIII (comics)", "XIII", ["Jason Fly"]),    ]),
    ("Dessins animés", "Personnages de dessins animés", "Culture populaire", [
        ("SpongeBob SquarePants", "Bob l’éponge", ["SpongeBob"]),
        ("Kermit the Frog", "Kermit la grenouille", ["Kermit"]),        ("Bugs Bunny", "Bugs Bunny", []),
        ("Daffy Duck", "Daffy Duck", []),
        ("Minions (Despicable Me)", "Les Minions", ["Minion"]),        ("Tom and Jerry", "Tom et Jerry", ["Tom", "Jerry"]),
        ("Scooby-Doo", "Scooby-Doo", ["Scooby Doo"]),
        ("Shaggy Rogers", "Sammy Rogers", ["Shaggy"]),
        ("Garfield", "Garfield", []),
        ("Homer Simpson", "Homer Simpson", ["Homer"]),
        ("Bart Simpson", "Bart Simpson", ["Bart"]),
        ("Fred Flintstone", "Fred Pierrafeu", ["Fred Flintstone"]),
        ("Popeye", "Popeye", []),
        ("Betty Boop", "Betty Boop", []),
        ("Peppa Pig", "Peppa Pig", ["Peppa"]),        ("Shaun the Sheep", "Shaun le mouton", ["Shaun"]),        ("Wallace and Gromit", "Wallace et Gromit", ["Wallace", "Gromit"]),        ("Yogi Bear", "Yogi l’ours", ["Yogi Bear"]),
        ("Moomin", "Moomin", ["Moomintroll"]),        ("Calimero", "Calimero", []),
    ]),
    ("Personnages Disney", "Personnages Disney", "Cinéma", [
        ("Mickey Mouse", "Mickey Mouse", ["Mickey"]),
        ("Minnie Mouse", "Minnie Mouse", ["Minnie"]),
        ("Donald Duck", "Donald Duck", ["Donald"]),
        ("Goofy", "Dingo", ["Goofy"]),
        ("Pluto (Disney)", "Pluto", []),
        ("Elsa (Frozen)", "Elsa", ["Reine des neiges"]),
        ("Anna (Frozen)", "Anna", []),
        ("Olaf (Frozen)", "Olaf", []),
        ("Stitch (Lilo & Stitch)", "Stitch", ["Expérience 626"]),
        ("Ariel (The Little Mermaid)", "Ariel", []),
        ("Belle (Beauty and the Beast)", "Belle", []),
        ("Cinderella (Disney character)", "Cendrillon", ["Cinderella"]),
        ("Mulan (Disney character)", "Mulan", []),
        ("Simba", "Simba", []),
        ("Aladdin (Disney character)", "Aladdin", []),        ("Moana (Disney character)", "Vaiana", ["Moana"]),
        ("Tinker Bell", "Clochette", ["Tinker Bell"]),
        ("Peter Pan (Disney character)", "Peter Pan", []),
        ("Snow White (Disney character)", "Blanche-Neige", ["Snow White"]),
        ("Maleficent", "Maléfique", ["Maleficent"]),
    ]),
    ("Personnages Pixar", "Personnages Pixar", "Cinéma", [
        ("Woody (Toy Story)", "Woody", ["Shérif Woody"]),
        ("Buzz Lightyear", "Buzz l’Éclair", ["Buzz Lightyear"]),
        ("Jessie (Toy Story)", "Jessie", []),
        ("Nemo", "Nemo", []),
        ("Dory (Finding Nemo)", "Dory", []),
        ("Dug (Up)", "Dug", ["Dug the dog"]),        ("Bo Peep (Toy Story)", "Bo Peep", ["Bergere"]),        ("WALL-E", "WALL-E", ["Wall-E"]),
        ("Forky", "Forky", ["Fourchette"]),        ("Mater (Cars)", "Martin", ["Mater"]),
        ("Remy (Ratatouille)", "Rémy", ["Remy"]),
        ("Joy (Inside Out)", "Joie", ["Joy"]),
        ("Sadness (Inside Out)", "Tristesse", ["Sadness"]),
        ("Anger (Inside Out)", "Anger", ["Colere"]),        ("Elastigirl", "Elastigirl", ["Mme Indestructible"]),
        ("Rex (Toy Story)", "Rex", []),        ("Miguel (Coco)", "Miguel", []),
        ("Bing Bong (Inside Out)", "Bing Bong", []),        ("Russell (Up)", "Russell", []),
        ("Jack-Jack Parr", "Jack-Jack", []),    ]),
    ("Héros Marvel", "Héros Marvel", "Super-héros", [
        ("Spider-Man", "Spider-Man", ["Spiderman", "Peter Parker"]),
        ("Iron Man", "Iron Man", ["Ironman", "Tony Stark"]),
        ("Captain America", "Captain America", ["Steve Rogers"]),
        ("Wolverine", "Wolverine", ["Logan"]),
        ("Hulk", "Hulk", ["Bruce Banner"]),
        ("Thor (Marvel Comics)", "Thor", []),
        ("Black Panther (character)", "Black Panther", ["Panthère noire", "T’Challa"]),
        ("Black Widow (Natasha Romanova)", "Black Widow", ["Veuve noire", "Natasha Romanoff"]),
        ("Doctor Strange", "Docteur Strange", ["Doctor Strange"]),
        ("Groot", "Groot", []),
        ("Ant-Man", "Ant-Man", ["L’Homme-fourmi"]),
        ("Deadpool", "Deadpool", []),
        ("Loki (Marvel Comics)", "Loki", []),
        ("Hawkeye (Clint Barton)", "Hawkeye", ["Œil-de-Faucon"]),
        ("Scarlet Witch", "La Sorcière rouge", ["Scarlet Witch", "Wanda Maximoff"]),
        ("Captain Marvel (Marvel Comics)", "Captain Marvel", ["Carol Danvers"]),
        ("Daredevil (Marvel Comics character)", "Daredevil", []),
        ("Venom (character)", "Venom", []),
        ("Star-Lord", "Star-Lord", ["Peter Quill"]),
        ("Thanos", "Thanos", []),
    ]),
    ("Héros DC", "Héros DC", "Super-héros", [
        ("Batman", "Batman", ["Bruce Wayne"]),
        ("Superman", "Superman", ["Clark Kent"]),
        ("Wonder Woman", "Wonder Woman", ["Diana Prince"]),
        ("Joker (character)", "Le Joker", ["Joker"]),
        ("Harley Quinn", "Harley Quinn", []),
        ("Green Arrow", "Green Arrow", ["Oliver Queen"]),        ("Aquaman", "Aquaman", ["Arthur Curry"]),
        ("Robin (character)", "Robin", []),
        ("Catwoman", "Catwoman", ["Femme-chat"]),
        ("Green Lantern", "Green Lantern", ["Lanterne verte"]),
        ("Batwoman", "Batwoman", ["Kate Kane"]),        ("Batgirl", "Batgirl", []),
        ("Nightwing", "Nightwing", []),
        ("Poison Ivy (character)", "Poison Ivy", ["Empoisonneuse"]),
        ("John Constantine (character)", "John Constantine", ["Constantine"]),        ("Penguin (character)", "Le Pingouin", ["Penguin"]),
        ("Bane (DC Comics)", "Bane", []),
        ("Shazam (character)", "Shazam", ["Captain Marvel"]),
        ("Cyborg (DC Comics)", "Cyborg", []),
        ("Lex Luthor", "Lex Luthor", []),
    ]),
    ("Personnages de manga", "Personnages de manga", "BD et manga", [
        ("Naruto Uzumaki", "Naruto Uzumaki", ["Naruto"]),
        ("Levi Ackerman", "Levi Ackerman", ["Levi"]),        ("Sailor Moon (character)", "Sailor Moon", ["Usagi Tsukino"]),
        ("Monkey D. Luffy", "Monkey D. Luffy", ["Luffy"]),
        ("Pikachu", "Pikachu", []),
        ("Ash Ketchum", "Sacha Ketchum", ["Ash Ketchum", "Sacha"]),
        ("Tanjiro Kamado", "Tanjiro Kamado", ["Tanjiro"]),
        ("Izuku Midoriya", "Izuku Midoriya", ["Deku"]),
        ("Sasuke Uchiha", "Sasuke Uchiha", ["Sasuke"]),
        ("Kakashi Hatake", "Kakashi Hatake", ["Kakashi"]),
        ("Eren Yeager", "Eren Jäger", ["Eren Yeager"]),
        ("Vegeta", "Vegeta", []),
        ("Ichigo Kurosaki", "Ichigo Kurosaki", ["Ichigo"]),
        ("Light Yagami", "Light Yagami", ["Light", "Kira"]),
        ("Astro Boy", "Astro Boy", ["Astro"]),
        ("Totoro", "Totoro", ["Mon voisin Totoro"]),
        ("Satoru Gojo", "Satoru Gojo", ["Gojo"]),        ("Edward Elric", "Edward Elric", ["Ed Elric"]),
        ("Natsu Dragneel", "Natsu Dragneel", ["Natsu"]),        ("Sakura Haruno", "Sakura Haruno", ["Sakura"]),
    ]),
]


def api(params: dict) -> dict:
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            pace_requests()
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.load(response)
            if payload.get("error", {}).get("code") in {"ratelimited", "maxlag"}:
                delay = retry_delay({}, attempt)
                if delay > 60:
                    raise RuntimeError(f"Commons requested a {delay:.0f}s retry delay; stopping safely.")
                print(f"Commons API asked us to slow down; waiting {delay:.0f}s.", flush=True)
                time.sleep(delay)
                continue
            return payload
        except urllib.error.HTTPError as error:
            if error.code not in {429, 503} or attempt == 4:
                raise
            delay = retry_delay(error.headers, attempt)
            if delay > 60:
                raise RuntimeError(f"Commons requested a {delay:.0f}s retry delay; stopping safely.") from error
            print(f"Commons returned {error.code}; respecting Retry-After for {delay:.0f}s.", flush=True)
            time.sleep(delay)
    raise RuntimeError("Unreachable")


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://commons.wikimedia.org/"})
    for attempt in range(5):
        try:
            pace_requests()
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in {429, 503} or attempt == 4:
                raise
            delay = retry_delay(error.headers, attempt)
            if delay > 60:
                raise RuntimeError(f"Commons requested a {delay:.0f}s retry delay; stopping safely.") from error
            print(f"Image host returned {error.code}; respecting Retry-After for {delay:.0f}s.", flush=True)
            time.sleep(delay)
    raise RuntimeError("Unreachable")


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(value: str) -> str:
    parser = TextOnly()
    parser.feed(value or "")
    return re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return re.sub(r"^(le|la|les|l|un|une|des|the)\s+", "", value)


def license_allowed(meta: dict) -> tuple[bool, str]:
    name = plain(meta.get("LicenseShortName", {}).get("value", ""))
    return name.startswith(ALLOWED_LICENSE_PREFIXES) or name in ALLOWED_LICENSES, name


def candidates_for(character: str, include_statues: bool) -> tuple[list[str], bool]:
    # Query the tightly categorized cosplay set first. For BD characters, try
    # their named statues as well; those are often the Commons source photos.
    base = re.sub(r"\s*\([^)]*\)", "", character).strip()
    variants = list(dict.fromkeys([character, base]))
    titles = []
    for value in variants:
        titles.append(f"Category:Cosplay of {value}")
        if include_statues:
            # French and Belgian comics have many public character statues.
            titles.append(f"Category:Statues of {value}")
    for category in titles:
        try:
            result = api({"action": "query", "list": "categorymembers", "cmtitle": category,
                          "cmtype": "file", "cmlimit": 20, "format": "json"})
            files = [row["title"] for row in result.get("query", {}).get("categorymembers", [])]
            if files:
                return files[:12], True
        except Exception:
            continue
    try:
        result = api({"action": "query", "list": "search", "srnamespace": 6,
                      "srsearch": f'"{base}" cosplay OR "{base}" statue',
                          "srlimit": 12, "format": "json"})
        files = [row["title"] for row in result.get("query", {}).get("search", [])]
        if files:
            return files, False
    except Exception:
        pass
    return [], False


def main() -> None:
    data = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION_ID for row in data.get("revisionHistory", [])):
        print("Character image questions are already present; no changes made.")
        return

    targets = []
    candidate_titles: list[str] = []
    existing_ids = {p.get("id") for q in data.get("questions", []) for p in q.get("presentations", [])}
    for topic, category, subject, people in GROUPS:
        group_target_count = len(targets)
        for name, answer, aliases in people:
            category_slug = re.sub(r"[^a-z0-9]+", "-", norm(category)).strip("-")
            character_slug = re.sub(r"[^a-z0-9]+", "-", norm(name)).strip("-")
            if f"image-qsj-{category_slug}-{character_slug}" in existing_ids:
                continue
            files, from_category = candidates_for(name, category.startswith("BD —"))
            targets.append({"topic": topic, "category": category, "subject": subject,
                            "name": name, "answer": answer, "aliases": aliases,
                            "files": files, "fromCategory": from_category})
            candidate_titles.extend(files)
        # All actual requests are globally paced in api()/download().
        resolved = sum(bool(target["files"]) for target in targets[group_target_count:])
        pending = len(targets) - group_target_count
        print(f"Found image candidates for {resolved}/{pending} replacement targets in {category}.", flush=True)
    unique_titles = list(dict.fromkeys(candidate_titles))

    infos = {}
    for start in range(0, len(unique_titles), 35):
        batch = unique_titles[start:start + 35]
        result = api({"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                      "iiprop": "url|extmetadata|size", "iiurlwidth": 1100, "format": "json"})
        for page in result.get("query", {}).get("pages", {}).values():
            if page.get("imageinfo"):
                infos[page["title"]] = page["imageinfo"][0]
        time.sleep(0.5)

    questions = data["questions"]
    answer_index: dict[str, list[dict]] = {}
    used_ids = {alias for q in questions for alias in q["legacyIds"]}
    for q in questions:
        for answer in q.get("answers", []):
            answer_index.setdefault(norm(answer), []).append(q)
    credits = json.loads(CREDITS_PATH.read_text(encoding="utf-8")) if CREDITS_PATH.exists() else {}
    used_media = set(credits.keys())
    presentation_ids = []
    counts: Counter[str] = Counter()
    created = attached = skipped = 0

    for target_index, target in enumerate(targets, start=1):
        info = None
        file_title = ""
        for candidate in target["files"]:
            metadata = infos.get(candidate, {})
            if not metadata or not metadata.get("thumburl"):
                continue
            licensed, license_name = license_allowed(metadata.get("extmetadata", {}))
            if not licensed:
                continue
            text = (candidate + " " + plain(metadata.get("extmetadata", {}).get("ImageDescription", {}).get("value", ""))).casefold()
            if not target["fromCategory"]:
                base_name = re.sub(r"\s*\([^)]*\)", "", target["name"]).strip()
                tokens = [token for token in re.findall(r"[a-z0-9]+", norm(base_name)) if len(token) > 3]
                if tokens and not all(token in norm(text) for token in tokens):
                    continue
            if re.search(r"\b(group|groups|team|family|mashup|crowd|lineup)\b", candidate, re.I):
                continue
            file_title, info = candidate, metadata
            break
        if not info:
            skipped += 1
            if target_index % 20 == 0:
                print(f"Reviewed {target_index}/{len(targets)} character targets.", flush=True)
            continue

        extmeta = info.get("extmetadata", {})
        thumb_url = info["thumburl"].replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
        image_bytes = download(thumb_url)
        extension = Path(urllib.parse.urlparse(thumb_url).path).suffix.lower() or ".jpg"
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            extension = ".jpg"
        media_name = hashlib.sha256(image_bytes).hexdigest()[:24] + extension
        if media_name in used_media:
            skipped += 1
            continue
        media_path = MEDIA_DIR / media_name
        if not media_path.exists():
            media_path.write_bytes(image_bytes)
        used_media.add(media_name)

        category_slug = re.sub(r"[^a-z0-9]+", "-", norm(target["category"])).strip("-")
        character_slug = re.sub(r"[^a-z0-9]+", "-", norm(target["name"])).strip("-")
        presentation_id = f"image-qsj-{category_slug}-{character_slug}"
        if presentation_id in used_ids:
            raise ValueError(f"Presentation ID already exists: {presentation_id}")
        mode = ("PIXELATE", "UNCOVER", "SHUFFLE", "BLUR")[len(presentation_ids) % 4]
        presentation = {
            "id": presentation_id, "label": "Qui suis-je ? — image", "answerMode": "BUZZER",
            "topic": target["topic"],
            "legacyCategory": f"{target['topic']} — {target['category']} — Qui suis-je ?",
            "legacyPackageId": "image-qsj-" + category_slug,
            "content": {"kind": "guessWho", "prompt": "Qui suis-je ?", "clues": [],
                        "imageRevealMode": mode, "imageRevealSteps": 6,
                        "imageUrl": "media/" + media_name, "basePoints": 30, "penaltyPoints": 0},
        }
        aliases = [target["answer"], *target["aliases"], target["name"]]
        matches = next((answer_index[norm(answer)] for answer in aliases if answer_index.get(norm(answer))), [])
        if matches:
            question = matches[0]
            question["presentations"].append(presentation)
            question["legacyIds"].append(presentation_id)
            if target["topic"] not in question["topics"]:
                question["topics"].append(target["topic"])
            attached += 1
        else:
            question = {"id": presentation_id, "legacyIds": [presentation_id], "topics": [target["topic"]],
                        "prompt": "Qui suis-je ?", "answers": list(dict.fromkeys(aliases)), "content": {},
                        "presentations": [presentation], "legacyReviews": []}
            questions.append(question)
            for answer in question["answers"]:
                answer_index.setdefault(norm(answer), []).append(question)
            created += 1
        used_ids.add(presentation_id)
        presentation_ids.append(presentation_id)
        counts[presentation["legacyCategory"]] += 1
        source_title = file_title.removeprefix("File:")
        credits[media_name] = {
            "filename": source_title, "title": source_title,
            "creator": plain(extmeta.get("Artist", {}).get("value", "")),
            "credit": plain(extmeta.get("Credit", {}).get("value", "")),
            "license": plain(extmeta.get("LicenseShortName", {}).get("value", "")),
            "licenseUrl": plain(extmeta.get("LicenseUrl", {}).get("value", "")),
            "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(source_title.replace(" ", "_"), safe=":()_,'-"),
            "downloadedFrom": thumb_url, "localSource": "Wikimedia Commons thumbnail, resized to 1100 px width",
            "question": target["answer"], "category": presentation["legacyCategory"],
        }
        if target_index % 20 == 0:
            print(f"Downloaded {len(presentation_ids)} images; reviewed {target_index}/{len(targets)} targets.", flush=True)

    data.setdefault("revisionHistory", []).append({
        "id": REVISION_ID,
        "note": "Added image reveal variants for notable BD, animated-film, superhero and manga characters using credited Wikimedia photographs.",
        "createdQuestions": created, "addedPresentationsToExistingQuestions": attached,
        "skippedTargets": skipped, "presentationIds": presentation_ids,
    })
    BANK_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CREDITS_PATH.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(presentation_ids)} character images ({created} new entries, {attached} attached; skipped {skipped}).")
    for category, count in counts.items():
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()
