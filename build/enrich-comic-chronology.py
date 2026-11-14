#!/usr/bin/env python3
"""Resolve and date the legacy Franco-Belgian comics first-appearance pool."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MIGRATION_PATH = ROOT / "game-library/bank/migration.json"
BACKUP_PATH = ROOT / "review-backups/questions-before-comic-first-appearance-2026-10-29.json"
SET_ID = "lib-chronologie-bd-premieres-20261012"
CONTEXT_ID = "comics.first_appearance"
COMIC_TAGS = ["literature", "literature.comics"]

# Dates refer to first publication of the character/series in comics, whether
# in a periodical or an album. Every year has a linked source supporting it.
ENTRIES = {
    "Spirou": ("subject-5f79436528d3efdb", 1938, "Dupuis", "https://www.dupuis.com/actualites/FR/bon-anniversaire-spirou/3119"),
    "Astérix": ("subject-6dc33641391738ca", 1959, "Institut René Goscinny", "https://www.institut-goscinny.org/bibliographie/asterix-dans-pilote/"),
    "Tintin": ("subject-96da7a72b89f412a", 1929, "Tintin official site", "https://www.tintin.com/en/characters/tintin"),
    "Gaston Lagaffe": ("subject-09efa3ac686b17f8", 1957, "Bibliothèque publique d'information", "https://www.dupuis.com/uploads/GASTON_SUPP.pdf"),
    "Les Schtroumpfs": ("franchise-943fa5f13ba801bc", 1958, "Peyo Company", "https://www.smurf.com/en/news/smurfy-birthday"),
    "Lucky Luke": ("subject-4fa7e1f2733422e2", 1946, "Dargaud", "https://www.dargaud.com/bd/lucky-luke"),
    "Marsupilami": ("subject-456a71ae161a416b", 1952, "Dupuis", "https://www.dupuis.com/seriebd/marsupilami-par/13621"),
    "Blake et Mortimer": ("franchise-5f4790c5d18ab6a1", 1946, "Dargaud", "https://www.dargaud.com/actualites/jove-blake-et-mortimer-fetent-leurs-75-ans-photo"),
    "Boule et Bill": ("subject-9c3383d247a2eef4", 1959, "Dargaud", "https://www.dargaud.com/bd/boule-bill/boule-bill"),
    "Le Chat de Geluck": ("franchise-18e251a5d94dd96f", 1983, "Philippe Geluck official site", "https://lechat.com/philippe-geluck/"),
    "Achille Talon": ("subject-e457a53bf666e5b8", 1963, "Dargaud", "https://www.dargaud.com/bd/achille-talon/achille-talon-integrales"),
    "Iznogoud": ("subject-e6d6fd51117d6ee5", 1962, "Iznogoud official site", "https://www.iznogoud.com/naissance_vizir"),
    # Lou's first magazine publication (2003), rather than the first album (2004).
    "Lou !": ("franchise-6ff17c7d98235bdd", 2003, "Cité internationale de la bande dessinée et de l'image", "https://www.citebd.org/neuvieme-art/lou-et-titeuf-grandir-avec-la-bande-dessinee-de-jeunesse"),
    "XIII": ("subject-75eb47ed6ef8f974", 1984, "Dargaud", "https://www.dargaud.com/actualites/xiii-40-ans-dune-serie-culte-photo"),
    "Largo Winch": ("subject-9eca45b4b9853624", 1990, "Dupuis", "https://www.dupuis.com/seriebd/largo-winch-l-integrale/4064"),
}

NEW_SERIES = {
    "Blake et Mortimer": ("Les Aventures de Blake et Mortimer", ["Blake & Mortimer"]),
    "Le Chat de Geluck": ("Le Chat (Philippe Geluck comic series)", ["Le Chat"]),
    "Lou !": ("Lou ! (Julien Neel comic series)", ["Lou"]),
}


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if bank.get("schemaVersion") != 4:
        raise SystemExit("Expected canonical bank schema version 4")
    if BACKUP_PATH.exists():
        raise SystemExit(f"Refusing to overwrite {BACKUP_PATH}")
    updated = copy.deepcopy(bank)
    subjects = {subject["id"]: subject for subject in updated["subjects"]}

    # Create canonical series records for chronology stubs that had no existing
    # verified identity. IDs are stable and explicitly recorded in this script.
    for label, (subject_id, year, source_name, source_url) in ENTRIES.items():
        if subject_id in subjects:
            continue
        if label not in NEW_SERIES:
            raise ValueError(f"Missing expected canonical subject for {label}: {subject_id}")
        canonical_label, aliases = NEW_SERIES[label]
        chronology_stub_id = next((s["id"] for s in subjects.values()
                                   if s["type"] == "chronology-item" and s["label"] == label), None)
        stub = subjects.get(chronology_stub_id) if chronology_stub_id else None
        series = {
            "id": subject_id, "type": "franchise", "label": canonical_label,
            "aliases": list(dict.fromkeys([label, *aliases])), "tagIds": COMIC_TAGS.copy(),
            "relations": [], "facts": [{"kind": "series_title", "value": label, "sourceUrl": source_url}],
            "chronologyEvidence": copy.deepcopy(stub.get("chronologyEvidence", [])) if stub else [],
            "sourceQuestionIds": copy.deepcopy(stub.get("sourceQuestionIds", [])) if stub else [],
            "identityStatus": "verified", "sources": [source_url], "candidateSubjectIds": [],
        }
        subjects[subject_id] = series

    question_by_id = {question["id"]: question for question in updated["questions"]}
    linked_occurrences = 0
    for question in updated["questions"]:
        for subject_id in list(question.get("subjectIds", [])):
            subject = subjects.get(subject_id)
            if subject is None:
                continue
            for evidence in subject.get("chronologyEvidence", []):
                if evidence.get("sourceQuestionId") != question["id"] or evidence.get("sourceSetId") != SET_ID:
                    continue
                item_id = evidence.get("itemId")
                item = next((value for value in question.get("content", {}).get("items", [])
                             if value.get("id") == item_id), None)
                if item is None:
                    raise ValueError(f"Missing chronology item {item_id} in {question['id']}")
                label = item["text"].strip()
                # A few built-in demo questions inherited the same legacy
                # source-set identifier; leave unrelated labels untouched.
                if label not in ENTRIES:
                    continue
                target_id, year, source_name, source_url = ENTRIES[label]
                target = subjects[target_id]
                if subject_id != target_id:
                    target["chronologyEvidence"] = _unique_dicts(
                        target.get("chronologyEvidence", []) + [copy.deepcopy(evidence)])
                    target["sourceQuestionIds"] = list(dict.fromkeys(
                        target.get("sourceQuestionIds", []) + [question["id"]]))
                    question["subjectIds"] = [target_id if value == subject_id else value
                                               for value in question["subjectIds"]]
                target["tagIds"] = list(dict.fromkeys(target.get("tagIds", []) + COMIC_TAGS))
                target["aliases"] = list(dict.fromkeys(target.get("aliases", []) + [label]))
                target["sources"] = list(dict.fromkeys(target.get("sources", []) + [source_url]))
                fact = {"contextId": CONTEXT_ID, "earliestYear": year, "latestYear": year,
                        "precision": "year", "sourceName": source_name, "sourceUrl": source_url,
                        "milestone": "first publication in comics"}
                if not any(old.get("contextId") == CONTEXT_ID for old in target.get("chronologyFacts", [])):
                    target.setdefault("chronologyFacts", []).append(fact)
                linked_occurrences += 1

    referenced = {sid for question in updated["questions"] for sid in question.get("subjectIds", [])}
    # Remove only chronology stubs for this curated set that no question uses.
    removed_ids = {subject_id for subject_id, subject in subjects.items()
                   if subject["type"] == "chronology-item" and subject_id not in referenced
                   and any(evidence.get("sourceSetId") == SET_ID
                           for evidence in subject.get("chronologyEvidence", []))}
    for subject_id in removed_ids:
        del subjects[subject_id]
    updated["subjects"] = list(subjects.values())

    # Ensure every source record's references remain valid and the complete
    # pilot produced 15 unique, dated subjects.
    target_ids = {value[0] for value in ENTRIES.values()}
    if linked_occurrences != 15:
        raise ValueError(f"Expected 15 linked comic items, got {linked_occurrences}")
    if not target_ids <= subjects.keys():
        raise ValueError("A curated canonical comic subject is missing")
    if any(len(subjects[sid].get("chronologyFacts", [])) == 0 for sid in target_ids):
        raise ValueError("A curated comic subject has no chronology date fact")
    known_ids = set(subjects)
    if any(set(question.get("subjectIds", [])) - known_ids for question in updated["questions"]):
        raise ValueError("Question references a missing subject after cleanup")

    shutil.copy2(BANK_PATH, BACKUP_PATH)
    BANK_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    migration = json.loads(MIGRATION_PATH.read_text(encoding="utf-8"))
    migration["comicFirstAppearancePilot"] = {
        "contextId": CONTEXT_ID, "linkedOccurrences": linked_occurrences,
        "canonicalSubjects": len(target_ids), "sourcedDateFacts": len(target_ids),
        "removedUnreferencedChronologySubjects": sorted(removed_ids),
        "sourceQuestionIds": sorted(qid for qid, question in question_by_id.items()
                                     if any(e.get("sourceSetId") == SET_ID
                                            for sid in question.get("subjectIds", [])
                                            for e in subjects[sid].get("chronologyEvidence", []))),
    }
    MIGRATION_PATH.write_text(json.dumps(migration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(migration["comicFirstAppearancePilot"], ensure_ascii=False, indent=2))


def _unique_dicts(values: list[dict]) -> list[dict]:
    output, seen = [], set()
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            output.append(value)
            seen.add(key)
    return output


if __name__ == "__main__":
    main()
