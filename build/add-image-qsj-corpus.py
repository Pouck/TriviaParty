"""Add sourced image-reveal Qui suis-je? presentations to the canonical bank.

Images come from the project's already-imported, credited Wikimedia assets.
This is an authoring script, not a package builder: it edits only the canonical
question bank and its image credit/coverage notes.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MEDIA_DIR = ROOT / "game-library/bank/media"

# source folder, subject, category suffix, image reveal style, image slug ->
# (French answer, optional existing canonical question id, optional aliases).
GROUPS = [
    {
        "folder": "arts-2026-10-11", "topic": "Arts",
        "category": "Peintures célèbres", "mode": "PIXELATE",
        "items": {
            "baiser": ("Le Baiser de Gustav Klimt", None, ["Le Baiser"]),
            "cene": ("La Cène de Léonard de Vinci", None, ["La Cène"]),
            "cri": ("Le Cri d’Edvard Munch", None, ["Le Cri"]),
            "galette": ("Bal du moulin de la Galette", None, ["Le Bal du moulin de la Galette"]),
            "gothic": ("American Gothic", None, []),
            "impression": ("Impression, soleil levant", None, ["Impression, Sunrise"]),
            "joconde": ("La Joconde", None, ["Mona Lisa"]),
            "liberte": ("La Liberté guidant le peuple", None, []),
            "menines": ("Les Ménines", None, ["Las Meninas"]),
            "naissance": ("La Naissance de Vénus", None, []),
            "nuit": ("La Nuit étoilée", None, ["The Starry Night"]),
            "olympia": ("Olympia d’Édouard Manet", None, ["Olympia"]),
            "perle": ("La Jeune Fille à la perle", None, ["Girl with a Pearl Earring"]),
            "radeau": ("Le Radeau de la Méduse", None, []),
            "ronde": ("La Ronde de nuit", None, ["La Garde de nuit"]),
            "vague": ("La Grande Vague de Kanagawa", None, ["La Grande Vague"]),
        },
    },
    {
        "folder": "arts-2026-10-11", "topic": "Arts",
        "category": "Sculptures célèbres", "mode": "UNCOVER",
        "items": {
            "danseuse": ("La Petite Danseuse de quatorze ans", None, ["Petite danseuse de quatorze ans"]),
            "david": ("Le David de Michel-Ange", None, ["David de Michel-Ange"]),
            "discobole": ("Le Discobole", None, ["Discobolos"]),
            "laocoon": ("Laocoon et ses fils", None, ["Groupe du Laocoon"]),
            "penseur": ("Le Penseur de Rodin", None, ["Le Penseur"]),
            "pieta": ("La Pietà de Michel-Ange", None, ["La Pietà"]),
            "venus": ("La Vénus de Milo", None, ["Vénus de Milo"]),
            "victoire": ("La Victoire de Samothrace", None, ["Victoire de Samothrace"]),
        },
    },
    {
        "folder": "architecture-2026-10-11", "topic": "Architecture",
        "category": "Monuments et sites célèbres", "mode": "SHUFFLE",
        "items": {
            "alhambra": ("L’Alhambra", None, ["Alhambra"]),
            "angkor": ("Angkor Vat", None, ["Angkor Wat"]),
            "arc": ("L’arc de Triomphe", None, ["Arc de Triomphe"]),
            "bigben": ("Big Ben et le palais de Westminster", None, ["Big Ben"]),
            "burj": ("Le Burj Khalifa", None, ["Burj Khalifa"]),
            "colosseum": ("Le Colisée", "architecture-qsj-antiquite-20261011-01", ["Colisée"]),
            "eiffel": ("La tour Eiffel", "architecture-buzzer-europe-20261011-01", ["Tour Eiffel"]),
            "fallingwater": ("Fallingwater, la maison sur la cascade", None, ["Fallingwater"]),
            "forbidden": ("La Cité interdite", None, ["Cité interdite"]),
            "goldengate": ("Le Golden Gate Bridge", None, ["Golden Gate Bridge"]),
            "guggenheim": ("Le musée Guggenheim de New York", None, ["Musée Guggenheim"]),
            "habitat": ("Habitat 67", None, []),
            "machu": ("Le site du Machu Picchu", None, ["Machu Picchu"]),
            "moai": ("Les moaï d’Ahu Tongariki", "arts-qsj-sculptures-mysteres-20261011-04", ["Moaï", "Les moaï"]),
            "pisa": ("La tour penchée de Pise", None, ["Tour de Pise"]),
            "sydney": ("L’opéra de Sydney", "architecture-qsj-modernes-20261011-02", ["Opéra de Sydney"]),
            "taj": ("Le Taj Mahal", "architecture-qsj-civilisations-20261011-02", ["Taj Mahal"]),
            "wall": ("La Grande Muraille de Chine", None, ["Grande Muraille de Chine"]),
        },
    },
    {
        "folder": "library-2026-10-12", "topic": "Nature",
        "category": "Animaux à reconnaître", "mode": "BLUR",
        "items": {
            "ant": ("La fourmi", None, ["Fourmi"]),
            "beaver": ("Le castor", "lib-buzzer-animaux-terrestres-20261012-02", ["Castor"]),
            "bee": ("L’abeille", "lib-qcm-insectes-20261012-04", ["Abeille"]),
            "butterfly": ("Le papillon monarque", None, ["Papillon monarque"]),
            "cow": ("La vache", None, ["Vache"]),
            "dolphin": ("Le grand dauphin", None, ["Dauphin"]),
            "giraffe": ("La girafe", None, ["Girafe"]),
            "hedgehog": ("Le hérisson", None, ["Hérisson"]),
            "horse": ("Le cheval", None, ["Cheval"]),
            "ladybird": ("La coccinelle à sept points", "lib-qcm-insectes-20261012-02", ["Coccinelle"]),
            "lion": ("Le lion d’Afrique", None, ["Lion"]),
            "octopus": ("La pieuvre commune", None, ["Pieuvre", "Poulpe"]),
            "ostrich": ("L’autruche", "lib-buzzer-oiseaux-20261012-01", ["Autruche"]),
            "owl": ("Le grand-duc d’Amérique", None, ["Grand-duc"]),
            "peacock": ("Le paon bleu", None, ["Paon"]),
            "pig": ("Le porc", None, ["Cochon"]),
            "raven": ("Le grand corbeau", None, ["Corbeau"]),
            "seahorse": ("L’hippocampe", "lib-qcm-animaux-marins-20261012-04", ["Hippocampe"]),
            "seal": ("Le phoque commun", None, ["Phoque"]),
            "swan": ("Le cygne tuberculé", None, ["Cygne"]),
            "toucan": ("Le toucan toco", None, ["Toucan"]),
            "turtle": ("La tortue verte", "lib-buzzer-animaux-marins-20261012-02", ["Tortue", "Tortue marine"]),
            "whale": ("Le cachalot", None, ["Cachalot"]),
            "wolf": ("Le loup gris", None, ["Loup"]),
            "zebra": ("Le zèbre des plaines", None, ["Zèbre"]),
        },
    },
    {
        "folder": "library-2026-10-12", "topic": "Géographie",
        "category": "Paysages célèbres", "mode": "PIXELATE",
        "items": {
            "everest": ("Le mont Everest", None, ["Everest"]),
            "forest": ("La forêt amazonienne", None, ["Amazonie"]),
            "fuji": ("Le mont Fuji", None, ["Mont Fuji", "Fuji"]),
            "lake": ("L’étang Walden", None, ["Walden Pond"]),
            "river": ("Le fleuve Saint-Laurent", None, ["Saint-Laurent"]),
        },
    },
    {
        "folder": "architecture-2026-10-11", "topic": "Géographie",
        "category": "Paysages célèbres", "mode": "PIXELATE",
        "items": {
            "machu": ("Le Machu Picchu dans les Andes", None, ["Machu Picchu"]),
        },
    },
    {
        "folder": "library-2026-10-12", "topic": "Géographie",
        "category": "Villes célèbres en images", "mode": "UNCOVER",
        "sourceFolders": {
            "alhambra": "architecture-2026-10-11",
            "forbidden": "architecture-2026-10-11",
            "goldengate": "architecture-2026-10-11",
        },
        "items": {
            "montreal": ("Montréal", None, ["Montreal"]),
            "eiffel": ("Paris", None, []),
            "colosseum": ("Rome", "lib-buzzer-geographie-villes-20261012-02", []),
            "sydney": ("Sydney", None, []),
            "alhambra": ("Grenade, en Andalousie", None, ["Granada"]),
            "forbidden": ("Pékin", None, ["Beijing"]),
            "goldengate": ("San Francisco", None, []),
            "pyramids": ("Gizeh, près du Caire", None, ["Gizeh"]),
        },
    },
]


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return re.sub(r"^(le|la|les|l|un|une|des|the)\s+", "", value)


def main() -> None:
    data = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if any(row.get("id") == "2026-10-25-image-qsj-expansion" for row in data.get("revisionHistory", [])):
        print("This image QSJ expansion is already present; no changes made.")
        return
    questions = data["questions"]
    ids = {alias for q in questions for alias in q["legacyIds"]}
    by_id = {q["id"]: q for q in questions}
    answer_index: dict[str, list[dict]] = {}
    for q in questions:
        for answer in q.get("answers", []):
            answer_index.setdefault(norm(answer), []).append(q)

    credits: dict[str, dict] = {}
    created = attached = 0
    presentation_ids: set[str] = set()
    for group in GROUPS:
        package_id = "image-qsj-" + re.sub(r"[^a-z0-9]+", "-", norm(group["category"])).strip("-")
        legacy_category = f"{group['topic']} — {group['category']} — Qui suis-je ?"
        for slug, (answer, explicit_target, aliases) in group["items"].items():
            asset_folder = group.get("sourceFolders", {}).get(slug, group["folder"])
            asset_dir = ROOT / "package-examples" / asset_folder / "assets"
            asset_json = json.loads((asset_dir / f"{slug}.json").read_text(encoding="utf-8"))
            image_path = asset_dir / asset_json["file"]
            digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
            media_name = digest[:24] + image_path.suffix.lower()
            media_path = MEDIA_DIR / media_name
            if not media_path.exists():
                shutil.copyfile(image_path, media_path)

            targets = [by_id[explicit_target]] if explicit_target else []
            if not targets:
                for name in [answer, *aliases]:
                    found = answer_index.get(norm(name), [])
                    if found:
                        targets = [found[0]]
                        break

            presentation_id = f"image-qsj-{group['topic'].lower().replace('é','e')}-{slug}"
            if presentation_id in ids or presentation_id in presentation_ids:
                raise ValueError(f"Presentation ID already exists: {presentation_id}")
            presentation_ids.add(presentation_id)
            content = {
                "kind": "guessWho",
                "prompt": "Qui suis-je ?",
                "clues": [],
                "imageRevealMode": group["mode"],
                "imageRevealSteps": 6,
                "imageUrl": f"media/{media_name}",
                "basePoints": 30,
                "penaltyPoints": 0,
            }
            presentation = {
                "id": presentation_id,
                "label": "Qui suis-je ? — image",
                "answerMode": "BUZZER",
                "topic": group["topic"],
                "legacyCategory": legacy_category,
                "legacyPackageId": package_id,
                "content": content,
            }
            if targets:
                q = targets[0]
                q["presentations"].append(presentation)
                q["legacyIds"].append(presentation_id)
                attached += 1
            else:
                question = {
                    "id": presentation_id,
                    "legacyIds": [presentation_id],
                    "topics": [group["topic"]],
                    "prompt": "Qui suis-je ?",
                    "answers": [answer, *[a for a in aliases if norm(a) != norm(answer)]],
                    "content": {},
                    "presentations": [presentation],
                    "explanation": f"{asset_json.get('title', answer)} — {asset_json.get('artist', '')}.",
                    "legacyReviews": [],
                }
                questions.append(question)
                by_id[question["id"]] = question
                for name in question["answers"]:
                    answer_index.setdefault(norm(name), []).append(question)
                created += 1
            ids.add(presentation_id)

            credits[media_name] = {
                "filename": asset_json["file"],
                "title": asset_json.get("title", answer),
                "creator": asset_json.get("artist", ""),
                "credit": asset_json.get("credit", ""),
                "license": asset_json.get("license", ""),
                "licenseUrl": asset_json.get("licenseUrl", ""),
                "source": asset_json.get("commons", asset_json.get("download", "")),
                "localSource": image_path.relative_to(ROOT).as_posix(),
                "question": answer,
                "category": legacy_category,
            }

    data.setdefault("revisionHistory", []).append({
        "id": "2026-10-25-image-qsj-expansion",
        "note": "Added progressive image-identification presentations using existing, locally credited photo assets.",
        "createdQuestions": created,
        "addedPresentationsToExistingQuestions": attached,
        "presentationIds": sorted(presentation_ids),
    })
    BANK_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    credit_path = ROOT / "game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json"
    old_credits = {}
    if credit_path.exists():
        old_credits = json.loads(credit_path.read_text(encoding="utf-8"))
    old_credits.update(credits)
    credit_path.write_text(json.dumps(old_credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Created {created} new questions; added {attached} image presentations to existing entries.")
    print(f"Added {len(presentation_ids)} visual Qui suis-je? presentations across {len({g['topic'] + ' — ' + g['category'] for g in GROUPS})} image categories.")
    print(f"Recorded credits for {len(credits)} unique media files.")


if __name__ == "__main__":
    main()
