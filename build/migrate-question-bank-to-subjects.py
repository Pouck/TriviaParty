#!/usr/bin/env python3
"""Add canonical subject identities and chronology evidence to the question bank.

The migration is conservative: image-fact subjects may be shared when their
typed subject title and franchise match exactly. Other questions receive a
question-local subject anchor. Chronology labels link only when image-fact
aliases resolve to one canonical subject; ambiguous labels stay unresolved.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_DIR = ROOT / "game-library/bank"
BANK_PATH = BANK_DIR / "questions.json"
BACKUP_PATH = ROOT / "review-backups/questions-before-subject-registry-2026-10-29.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", value))


def stable_id(prefix: str, key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def slug(value: str) -> str:
    return "-".join(normalize(value).split()) or "unknown"


TOPIC_PATHS = {
    "arts": ("arts",),
    "architecture": ("arts", "arts.architecture"),
    "litterature": ("literature",),
    "bande dessinee": ("literature", "literature.comics"),
    "bd et manga": ("literature", "literature.comics"),
    "manga": ("literature", "literature.manga"),
    "super heros": ("culture", "culture.superheroes"),
    "culture populaire": ("culture",),
    "heros dc": ("culture", "culture.superheroes", "culture.superheroes.dc"),
    "heros marvel": ("culture", "culture.superheroes", "culture.superheroes.marvel"),
    "personnages disney": ("culture", "culture.animation", "culture.animation.disney"),
    "personnages pixar": ("culture", "culture.animation", "culture.animation.pixar"),
    "detective conan": ("literature", "literature.manga", "literature.manga.detective-conan"),
    "jujutsu kaisen": ("literature", "literature.manga", "literature.manga.jujutsu-kaisen"),
    "personnages de manga": ("literature", "literature.manga"),
    "lucky luke": ("literature", "literature.comics", "literature.comics.lucky-luke"),
    "contes et legendes": ("folklore",),
    "mythologie": ("mythology",),
    "jeux video": ("gaming",),
    "cuisine": ("food",),
    "langue francaise": ("language", "language.french"),
    "logique et enigmes": ("puzzles",),
    "personnalites politiques": ("people", "people.politics"),
    "cinema": ("cinema",),
    "musique": ("music",),
    "histoire": ("history",),
    "geographie": ("geography",),
    "nature": ("nature",),
    "sciences": ("science",),
    "tests": ("legacy.tests",),
}

TAXONOMY_LABELS = {
    "arts": "Arts",
    "arts.architecture": "Architecture",
    "arts.painting": "Peinture",
    "arts.sculpture": "Sculpture",
    "literature": "Littérature",
    "literature.comics": "Bande dessinée",
    "literature.manga": "Manga",
    "culture": "Culture populaire",
    "culture.superheroes": "Super-héros",
    "culture.superheroes.dc": "Héros DC",
    "culture.superheroes.marvel": "Héros Marvel",
    "culture.animation": "Animation",
    "culture.animation.disney": "Disney",
    "culture.animation.pixar": "Pixar",
    "literature.manga.detective-conan": "Détective Conan",
    "literature.manga.jujutsu-kaisen": "Jujutsu Kaisen",
    "literature.comics.lucky-luke": "Lucky Luke",
    "cinema": "Cinéma",
    "music": "Musique",
    "history": "Histoire",
    "geography": "Géographie",
    "nature": "Nature",
    "science": "Sciences",
    "folklore": "Contes et légendes",
    "mythology": "Mythologie",
    "gaming": "Jeux vidéo",
    "food": "Cuisine",
    "language": "Langues",
    "language.french": "Français",
    "puzzles": "Logique et énigmes",
    "people": "Personnes",
    "people.politics": "Personnalités politiques",
    "legacy.tests": "Tests (historique)",
}


def topic_paths(label: str) -> tuple[str, ...]:
    key = normalize(label)
    return TOPIC_PATHS.get(key, ("legacy." + slug(label),))


def subject_identity(entry: dict) -> tuple[str, str] | None:
    facts = entry.get("imageFacts") or {}
    title = facts.get("subjectTitle", "").strip()
    subject_type = facts.get("subjectType", "").strip()
    if not title or not subject_type:
        return None
    franchise = facts.get("franchise", "").strip()
    creators = sorted({normalize(fact.get("value", "")) for fact in facts.get("facts", [])
                       if fact.get("kind") == "subject_creator" and fact.get("value")})
    key = "|".join((normalize(subject_type), normalize(title), normalize(franchise), ",".join(creators)))
    return stable_id("subject", key), key


def subject_aliases(entry: dict) -> list[str]:
    aliases = list(entry.get("answers", []))
    facts = entry.get("imageFacts") or {}
    aliases.extend([facts.get("subjectTitle", ""), facts.get("frenchTitle", "")])
    aliases.extend(f.get("value", "") for f in facts.get("facts", [])
                   if f.get("kind") in ("work_title", "subject_title", "franchise"))
    return list(dict.fromkeys(value.strip() for value in aliases if value and value.strip()))


def creator_values(entry: dict) -> list[tuple[str, str, str | None]]:
    result = []
    for fact in (entry.get("imageFacts") or {}).get("facts", []):
        if fact.get("kind") != "subject_creator" or not fact.get("value"):
            continue
        value = fact["value"].strip()
        role = (fact.get("role") or "creator").strip()
        result.append((value, role, fact.get("sourceUrl")))
    return result


def build_bank(bank: dict) -> dict:
    questions = bank["questions"]
    subjects: dict[str, dict] = {}
    question_subjects: dict[str, list[str]] = {}
    image_identity_ids: dict[str, str] = {}
    image_alias_index: dict[str, set[str]] = defaultdict(set)
    tag_parent: dict[str, str | None] = {}

    def add_tag(path: str) -> None:
        parts = path.split(".")
        for index in range(1, len(parts) + 1):
            current = ".".join(parts[:index])
            parent = ".".join(parts[:index - 1]) if index > 1 else None
            tag_parent.setdefault(current, parent)

    def make_subject(subject_id: str, subject_type: str, label: str,
                     status: str, aliases: list[str] | None = None,
                     tags: list[str] | None = None, facts: list[dict] | None = None,
                     sources: list[str] | None = None) -> dict:
        entry = subjects.get(subject_id)
        if entry is None:
            entry = {
                "id": subject_id,
                "type": subject_type,
                "label": label,
                "aliases": [],
                "tagIds": [],
                "relations": [],
                "facts": [],
                "chronologyEvidence": [],
                "sourceQuestionIds": [],
                "identityStatus": status,
                "sources": [],
            }
            subjects[subject_id] = entry
        for value in aliases or []:
            if value not in entry["aliases"]:
                entry["aliases"].append(value)
        for value in tags or []:
            add_tag(value)
            if value not in entry["tagIds"]:
                entry["tagIds"].append(value)
        for fact in facts or []:
            if fact not in entry["facts"]:
                entry["facts"].append(copy.deepcopy(fact))
        for source in sources or []:
            if source and source not in entry["sources"]:
                entry["sources"].append(source)
        return entry

    def image_tags(question: dict) -> list[str]:
        tags = list(dict.fromkeys(path for topic in question.get("topics", []) for path in topic_paths(topic)))
        subject_type = (question.get("imageFacts") or {}).get("subjectType", "")
        typed = {
            "painting": ["arts", "arts.painting"],
            "sculpture": ["arts", "arts.sculpture"],
            "building_or_site": ["arts", "arts.architecture"],
        }.get(subject_type, [])
        for tag in typed:
            add_tag(tag)
            if tag not in tags:
                tags.append(tag)
        return tags

    # Create explicit subjects for entries with verified image identity facts.
    for question in questions:
        identity = subject_identity(question)
        if not identity:
            continue
        subject_id, key = identity
        facts = question.get("imageFacts") or {}
        tags = image_tags(question)
        kind = normalize(facts.get("subjectType", "unknown")).replace(" ", "-")
        subject = make_subject(subject_id, kind, facts.get("subjectTitle", ""), "verified",
            subject_aliases(question), tags, facts.get("facts", []), facts.get("sources", []))
        question_subjects[question["id"]] = [subject_id]
        image_identity_ids[key] = subject_id
        for alias in subject_aliases(question):
            key_alias = normalize(alias)
            if key_alias:
                image_alias_index[key_alias].add(subject_id)
        if question["id"] not in subject["sourceQuestionIds"]:
            subject["sourceQuestionIds"].append(question["id"])

    # Keep other authored questions usable without guessing that equal answers
    # identify the same entity. These anchors can be consolidated in later audits.
    for question in questions:
        if question.get("id") in question_subjects:
            continue
        if any(p.get("content", {}).get("kind") == "ordering" for p in question.get("presentations", [])):
            continue
        answer = next(iter(question.get("answers", [])), "")
        label = answer or question.get("prompt", question["id"])
        subject_id = stable_id("question-subject", question["id"])
        tags = list(dict.fromkeys(path for topic in question.get("topics", []) for path in topic_paths(topic)))
        subject = make_subject(subject_id, "question-anchor", label, "question-scoped",
            question.get("answers", []), tags)
        subject["sourceQuestionIds"].append(question["id"])
        question_subjects[question["id"]] = [subject_id]

    # Add creator and franchise nodes and typed relationships. Media credits are
    # intentionally excluded from subject relationships.
    person_ids: dict[str, str] = {}
    for question in questions:
        subject_ids = question_subjects.get(question["id"], [])
        if not subject_ids:
            continue
        primary = subjects[subject_ids[0]]
        if not question.get("imageFacts"):
            continue
        for name, role, source_url in creator_values(question):
            key = ("person", normalize(name))
            person_id = person_ids.get(key[1])
            if not person_id:
                person_id = stable_id("person", key[1])
                make_subject(person_id, "person", name, "verified", [name], ["people"],
                    [{"kind": "name", "value": name, "role": role, "sourceUrl": source_url}], [source_url] if source_url else [])
                person_ids[key[1]] = person_id
            relation = {"type": "created_by", "targetId": person_id, "role": role}
            if relation not in primary["relations"]:
                primary["relations"].append(relation)
        franchise = question["imageFacts"].get("franchise")
        if franchise:
            franchise_id = stable_id("franchise", normalize(franchise))
            make_subject(franchise_id, "franchise", franchise, "verified", [franchise], ["culture"])
            relation = {"type": "part_of_franchise", "targetId": franchise_id}
            if relation not in primary["relations"]:
                primary["relations"].append(relation)

    # Convert each ordering list to references to reusable subjects. Only a
    # unique exact image-fact alias is linked automatically; collisions become
    # unresolved, provenance-bearing subjects instead of unsafe merges.
    ordering_questions = 0
    unresolved_labels: set[str] = set()
    for question in questions:
        presentations = [p for p in question.get("presentations", [])
                         if p.get("content", {}).get("kind") == "ordering"]
        if not presentations:
            continue
        ordering_questions += 1
        pool = presentations[0].get("legacyPackageId") or presentations[0].get("legacyCategory", "legacy")
        topic_tags = list(dict.fromkeys(path for topic in question.get("topics", []) for path in topic_paths(topic)))
        items = question.get("content", {}).get("items", [])
        correct_order = question.get("content", {}).get("correctOrderIds", [])
        positions = {item_id: index for index, item_id in enumerate(correct_order)}
        refs = []
        for item in items:
            label = item.get("text", "").strip()
            matches = image_alias_index.get(normalize(label), set())
            if len(matches) == 1:
                subject_id = next(iter(matches))
            else:
                context = "|".join((normalize(pool), normalize(label))) if len(matches) > 1 else "|".join((normalize(question.get("topics", ["legacy"])[0]), normalize(label)))
                subject_id = stable_id("chronology-item", context)
                status = "ambiguous" if len(matches) > 1 else "legacy-item-unresolved"
                unresolved_labels.add(label)
                subject = make_subject(subject_id, "chronology-item", label, status,
                    [label], topic_tags)
                if matches:
                    subject["candidateSubjectIds"] = sorted(matches)
            refs.append(subject_id)
            subject = subjects[subject_id]
            if question["id"] not in subject["sourceQuestionIds"]:
                subject["sourceQuestionIds"].append(question["id"])
            evidence = {
                "sourceQuestionId": question["id"],
                "sourceSetId": pool,
                "sourcePrompt": question.get("prompt", ""),
                "position": positions.get(item.get("id")),
                "itemId": item.get("id"),
            }
            if evidence not in subject["chronologyEvidence"]:
                subject["chronologyEvidence"].append(evidence)
        question_subjects[question["id"]] = list(dict.fromkeys(refs))

    for question in questions:
        question["subjectIds"] = question_subjects.get(question["id"], [])

    taxonomy = [{"id": tag, "label": TAXONOMY_LABELS.get(tag, tag.split(".")[-1].replace("-", " ").title()),
                 "parentId": parent}
                for tag, parent in sorted(tag_parent.items())]
    bank["schemaVersion"] = 3
    bank["taxonomy"] = taxonomy
    bank["subjects"] = sorted(subjects.values(), key=lambda value: value["id"])
    return bank, {"orderingQuestions": ordering_questions, "subjectCount": len(subjects),
                  "unresolvedChronologyLabels": len(unresolved_labels),
                  "linkedQuestionCount": sum(bool(ids) for ids in question_subjects.values())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write schemaVersion 3 to the canonical bank")
    args = parser.parse_args()
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if bank.get("schemaVersion") == 3:
        raise SystemExit("Bank is already version 3; refusing to duplicate subject records.")
    if bank.get("schemaVersion") != 2:
        raise SystemExit(f"Expected schema version 2; found {bank.get('schemaVersion')!r}.")
    migrated, summary = build_bank(bank)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write the migration.")
        return
    if not BACKUP_PATH.exists():
        shutil.copy2(BANK_PATH, BACKUP_PATH)
    BANK_PATH.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote schemaVersion 3 bank; snapshot saved at {BACKUP_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
