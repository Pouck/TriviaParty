#!/usr/bin/env python3
"""Add verified artwork creation dates and resolve safe painting chronology links."""

from __future__ import annotations

import argparse
import copy
import copy
import hashlib
import json
import re
import shutil
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MIGRATION_PATH = ROOT / "game-library/bank/migration.json"
BACKUP_PATH = ROOT / "review-backups/questions-before-painting-chronology-2026-10-29.json"
RAIMOND_ID = "person-0f0cf56746a0c196"

# The legacy item label is retained as provenance. Targets were checked against
# the work's title, artist and primary collection record. The title-only Venus
# ordering item remains ambiguous and is deliberately not redirected.
WORKS = {
    "Les Époux Arnolfini": ("subject-f6f8fd154e540c41", "Jan van Eyck", 1434, 1434, "year", "National Gallery, London", "https://www.nationalgallery.org.uk/paintings/jan-van-eyck-the-arnolfini-portrait"),
    "La Naissance de Vénus": ("subject-48c9591d9a68fd5d", "Sandro Botticelli", 1485, 1485, "circa-year", "Uffizi Galleries", "https://www.uffizi.it/en/artworks/birth-of-venus"),
    "La Naissance de Vénus (Bouguereau)": ("subject-40d6a35f9433b45d", "William-Adolphe Bouguereau", 1879, 1879, "year", "Musée d'Orsay", "https://www.musee-orsay.fr/en/artworks/naissance-de-venus-16649"),
    "La Naissance de Vénus (Cabanel)": ("subject-8ba0fd9735c75daa", "Alexandre Cabanel", 1863, 1863, "year", "Musée d'Orsay", "https://www.musee-orsay.fr/en/artworks/naissance-de-venus-98"),
    "Les Ménines": ("subject-7552eba8cae9cd2a", "Diego Velázquez", 1656, 1656, "year", "Museo del Prado", "https://www.museodelprado.es/en/the-collection/art-work/las-meninas/9fdc7800-9ade-48b0-ab8b-edee94ea877f"),
    "Impression, soleil levant": ("subject-e192ed34faa1c345", "Claude Monet", 1872, 1872, "year", "Musée Marmottan Monet", "https://www.marmottan.fr/en/notice/4014/"),
    "La Jeune Fille à la perle": ("subject-22fdf1c4f7f66b27", "Johannes Vermeer", 1665, 1665, "circa-year", "Mauritshuis", "https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring"),
    "La Ronde de nuit": ("subject-9d141d17b2b2f0a9", "Rembrandt van Rijn", 1642, 1642, "year", "Rijksmuseum", "https://www.rijksmuseum.nl/nl/collectie/object/De-Nachtwacht--3137deb45cd7765f9a76084a16c99544"),
    "Le Radeau de la Méduse": ("subject-3de4e2d280ec6c26", "Théodore Géricault", 1818, 1819, "year-range", "Musée du Louvre", "https://collections.louvre.fr/ark:/53355/cl010059199"),
    "Olympia": ("subject-72a511bb80380901", "Édouard Manet", 1863, 1863, "year", "Musée d'Orsay", "https://www.musee-orsay.fr/en/oeuvres/olympia-712"),
    "La Liberté guidant le peuple": ("subject-df8eefbce53d33c1", "Eugène Delacroix", 1830, 1830, "year", "Musée du Louvre", "https://collections.louvre.fr/ark:/53355/cl010065872"),
    "Le Cri — version peinte de 1893": ("chronology-item-1b534883012966a6", "Edvard Munch", 1893, 1893, "year", "eMunch.no research portal", "https://www.emunch.no/ENGART_emunch_jacobsen_2_eng.xhtml"),
    "La Nuit étoilée": ("subject-6113b0951bc2cf8e", "Vincent van Gogh", 1889, 1889, "year", "The Museum of Modern Art", "https://www.moma.org/collection/works/79802"),
    "Bal du moulin de la Galette": ("subject-30688f9a338c3314", "Pierre-Auguste Renoir", 1876, 1876, "year", "Musée d'Orsay", "https://www.musee-orsay.fr/en/artworks/bal-du-moulin-de-la-galette-497"),
    "Guernica": ("question-subject-d17e4f68dda24eb9", "Pablo Picasso", 1937, 1937, "year", "Museo Reina Sofía", "https://www.museoreinasofia.es/colecciones/obra/guernica/"),
    "Le Baiser de Klimt": ("subject-2cf9000992319809", "Gustav Klimt", 1907, 1909, "year-range", "Belvedere Museum Vienna", "https://sammlung.belvedere.at/objects/6678/der-kuss-liebespaar"),
    "American Gothic": ("subject-c9c8a4f1437fc038", "Grant Wood", 1930, 1930, "year", "Art Institute of Chicago", "https://www.artic.edu/artworks/6565/american-gothic"),
    "La Persistance de la mémoire": ("question-subject-c03ef8b6709c621a", "Salvador Dalí", 1931, 1931, "year", "The Museum of Modern Art", "https://www.moma.org/collection/works/79018"),
    "Campbell’s Soup Cans": ("chronology-item-98b33d9cac131656", "Andy Warhol", 1962, 1962, "year", "The Museum of Modern Art", "https://www.moma.org/collection/works/79809"),
    "Nighthawks": ("question-subject-66c8809b4d322b25", "Edward Hopper", 1942, 1942, "year", "Art Institute of Chicago", "https://archive.artic.edu/hopper/artwork/111628"),
}

RESOLVED_LEGACY_ITEMS = {
    "Les Époux Arnolfini": "subject-f6f8fd154e540c41",
    "Les Ménines": "subject-7552eba8cae9cd2a",
    "Impression, soleil levant": "subject-e192ed34faa1c345",
    "La Jeune Fille à la perle": "subject-22fdf1c4f7f66b27",
    "La Ronde de nuit": "subject-9d141d17b2b2f0a9",
    "Le Radeau de la Méduse": "subject-3de4e2d280ec6c26",
    "Olympia": "subject-72a511bb80380901",
    "La Liberté guidant le peuple": "subject-df8eefbce53d33c1",
    "Le Cri — version peinte de 1893": "chronology-item-1b534883012966a6",
    "La Nuit étoilée": "subject-6113b0951bc2cf8e",
    "Bal du moulin de la Galette": "subject-30688f9a338c3314",
    "Guernica": "question-subject-d17e4f68dda24eb9",
    "Le Baiser de Klimt": "subject-2cf9000992319809",
    "American Gothic": "subject-c9c8a4f1437fc038",
    "La Persistance de la mémoire": "question-subject-c03ef8b6709c621a",
    "Campbell’s Soup Cans": "chronology-item-98b33d9cac131656",
    "Nighthawks": "question-subject-66c8809b4d322b25",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", value))


def subject_id(prefix: str, key: str) -> str:
    return f"{prefix}-{hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]}"


def add_unique(items: list, values: list) -> list:
    result = list(items)
    seen = {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in result}
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            result.append(value)
            seen.add(key)
    return result


def build(bank: dict) -> dict:
    bank = copy.deepcopy(bank)
    subjects = {item["id"]: item for item in bank["subjects"]}
    if not set(target for target, *_ in WORKS.values()) <= subjects.keys():
        raise ValueError("A curated painting subject ID is missing from this bank revision")
    questions = bank["questions"]

    people: dict[str, str] = {
        normalize(subject["label"]): subject["id"]
        for subject in subjects.values() if subject.get("type") == "person"
    }
    for label in sorted({work[1] for work in WORKS.values()}):
        key = normalize(label)
        person_id = people.get(key) or subject_id("person", key)
        if person_id not in subjects:
            subjects[person_id] = {
                "id": person_id, "type": "person", "label": label,
                "aliases": [label], "tagIds": ["people"], "relations": [],
                "facts": [], "chronologyEvidence": [], "sourceQuestionIds": [],
                "identityStatus": "verified", "sources": [],
            }
            people[key] = person_id

    # Repair an inherited creator-role error: the Commons photographer was
    # copied into the depicted-work creator field for Cabanel's painting.
    cabanel_question = next(q for q in questions if q["id"] == "image-qsj-painting-rank-099")
    cabanel_url = "https://www.musee-orsay.fr/en/artworks/naissance-de-venus-98"
    facts = cabanel_question["imageFacts"]["facts"]
    for fact in facts:
        if fact.get("kind") == "subject_creator" and fact.get("role") == "painter":
            fact["value"] = "Alexandre Cabanel"
            fact["sourceUrl"] = cabanel_url
    cabanel_question["imageFacts"]["sources"] = add_unique(cabanel_question["imageFacts"].get("sources", []), [cabanel_url])

    for subject in subjects.values():
        for relation in subject.get("relations", []):
            if relation.get("role") == "painter" and relation.get("targetId") == RAIMOND_ID:
                relation["targetId"] = people[normalize("Alexandre Cabanel")]
        for fact in subject.get("facts", []):
            if fact.get("kind") == "subject_creator" and fact.get("role") == "painter" and fact.get("value") == "Raimond Spekking":
                fact["value"] = "Alexandre Cabanel"
                fact["sourceUrl"] = cabanel_url

    evidence_by_target: dict[str, list] = defaultdict(list)
    for question in questions:
        for item in question.get("content", {}).get("items", []):
            label = item.get("text", "").strip()
            target_id = RESOLVED_LEGACY_ITEMS.get(label)
            if target_id is None:
                continue
            # Existing item positions are preserved as historical evidence.
            evidence_by_target[target_id].extend(
                evidence for source_id in question.get("subjectIds", [])
                if source_id in subjects
                for evidence in subjects[source_id].get("chronologyEvidence", [])
                if evidence.get("sourceQuestionId") == question["id"] and evidence.get("itemId") == item.get("id")
            )
            question["subjectIds"] = [target_id if value in subjects and value != target_id
                                       and any(e.get("sourceQuestionId") == question["id"] and e.get("itemId") == item.get("id")
                                               for e in subjects[value].get("chronologyEvidence", []))
                                       else value for value in question.get("subjectIds", [])]

    for label, data in WORKS.items():
        target_id, creator, start, end, precision, source_name, source_url = data
        subject = subjects[target_id]
        original_label = subject["label"]
        subject["aliases"] = add_unique(subject.get("aliases", []), [original_label, label])
        subject["tagIds"] = add_unique(subject.get("tagIds", []), ["arts", "arts.painting"])
        subject["type"] = "painting"
        subject["identityStatus"] = "verified"
        subject["sources"] = add_unique(subject.get("sources", []), [source_url])
        creator_id = people[normalize(creator)]
        creator_fact = {"kind": "name", "value": creator, "role": "painter", "sourceUrl": source_url}
        subject["facts"] = add_unique(subject.get("facts", []), [creator_fact])
        relation = {"type": "created_by", "targetId": creator_id, "role": "painter"}
        subject["relations"] = add_unique(subject.get("relations", []), [relation])
        subject["chronologyFacts"] = add_unique(subject.get("chronologyFacts", []), [{
            "contextId": "artwork.creation", "earliestYear": start, "latestYear": end,
            "precision": precision, "sourceName": source_name, "sourceUrl": source_url,
        }])
        subject["chronologyEvidence"] = add_unique(subject.get("chronologyEvidence", []), evidence_by_target.get(target_id, []))
        source_questions = [q["id"] for q in questions if target_id in q.get("subjectIds", [])]
        subject["sourceQuestionIds"] = add_unique(subject.get("sourceQuestionIds", []), source_questions)

    # For legacy ordering questions, redirect only exact labels whose identity
    # is unambiguous in the authored item text and reviewed target record.
    redirect = dict(RESOLVED_LEGACY_ITEMS)
    # Resolve repeatable references by evidence, while keeping the Venus title
    # collision (three distinct paintings) attached to its ambiguous stub.
    for question in questions:
        ordering_items = question.get("content", {}).get("items", [])
        if not ordering_items:
            continue
        evidence_lookup = {
            evidence.get("itemId"): subject["id"]
            for subject in subjects.values()
            for evidence in subject.get("chronologyEvidence", [])
            if evidence.get("sourceQuestionId") == question["id"]
        }
        target_ids = []
        for item in ordering_items:
            target = redirect.get(item.get("text", "").strip())
            if target:
                target_ids.append(target)
            else:
                target_ids.append(evidence_lookup.get(item.get("id")))
        if all(target_ids):
            question["subjectIds"] = list(dict.fromkeys(target_ids))

    # Add creator relationships for newly curated subjects and keep the image
    # credit (Raimond Spekking) solely as a media fact, not the painter.
    for subject in subjects.values():
        subject["relations"] = [r for r in subject.get("relations", []) if r.get("targetId") != RAIMOND_ID]

    # Remove chronology placeholders that no question references after their
    # evidence has been transferred to the canonical work subjects.
    used = {value for q in questions for value in q.get("subjectIds", [])}
    removed_ids = {sid for sid, subject in subjects.items()
                   if subject.get("type") == "chronology-item" and sid not in used}
    for subject in subjects.values():
        subject["relations"] = [r for r in subject.get("relations", []) if r.get("targetId") not in removed_ids]
    for sid in removed_ids:
        del subjects[sid]

    # Any person record made only from the incorrect artist attribution is now
    # a true orphan and can be removed; media attribution remains on the query.
    linked = {r.get("targetId") for subject in subjects.values() for r in subject.get("relations", [])}
    referenced = {sid for q in questions for sid in q.get("subjectIds", [])}
    for sid, subject in list(subjects.items()):
        if sid == RAIMOND_ID and sid not in linked and sid not in referenced:
            del subjects[sid]

    bank["schemaVersion"] = 4
    bank["subjects"] = sorted(subjects.values(), key=lambda subject: subject["id"])
    return bank


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if bank.get("schemaVersion") != 3:
        raise SystemExit(f"Expected schema version 3; found {bank.get('schemaVersion')}")
    updated = build(bank)
    used = {sid for q in updated["questions"] for sid in q["subjectIds"]}
    known = {s["id"] for s in updated["subjects"]}
    if not used <= known:
        raise SystemExit("The update would leave a dangling question subject reference")
    if any(r.get("targetId") not in known for s in updated["subjects"] for r in s.get("relations", [])):
        raise SystemExit("The update would leave a dangling subject relation")
    print(json.dumps({"schemaVersion": 4, "subjects": len(updated["subjects"]),
                      "paintingCreationFacts": sum(len(s.get("chronologyFacts", [])) for s in updated["subjects"]),
                      "resolvedLegacyPaintingItems": len(RESOLVED_LEGACY_ITEMS)}, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write the bank.")
        return
    if BACKUP_PATH.exists():
        raise SystemExit(f"Refusing to overwrite backup: {BACKUP_PATH}")
    shutil.copy2(BANK_PATH, BACKUP_PATH)
    BANK_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    migration = json.loads(MIGRATION_PATH.read_text(encoding="utf-8"))
    migration["artworkChronologyEnrichment"] = {
        "contextId": "artwork.creation", "subjectIds": sorted({target for target, *_ in WORKS.values()}),
        "sourceQuestions": sorted({e["sourceQuestionId"] for s in bank["subjects"] for e in s.get("chronologyEvidence", [])
                                    if e.get("sourceSetId") == "arts-chronologie-peintures-dans-le-temps-20261011"}),
        "unresolvedLabel": "La Naissance de Vénus",
        "unresolvedReason": "The authored ordering label does not identify which of three distinct paintings it means.",
    }
    MIGRATION_PATH.write_text(json.dumps(migration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated bank; snapshot saved to {BACKUP_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
