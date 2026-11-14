#!/usr/bin/env python3
"""Link unambiguous comic, superhero and architecture chronology labels."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MIGRATION_PATH = ROOT / "game-library/bank/migration.json"
BACKUP_PATH = ROOT / "review-backups/questions-before-curated-chronology-links-2026-10-29.json"

# Each identity was checked against the accepted answer, question prompt and
# verified subject type. Labels whose item could mean a film/work or character
# (for example Cinderella or Batman in a film-release pool) are not included.
LINKS = {
    "Spirou": "subject-5f79436528d3efdb",
    "Astérix": "subject-6dc33641391738ca",
    "Tintin": "subject-96da7a72b89f412a",
    "Gaston Lagaffe": "subject-09efa3ac686b17f8",
    "Lucky Luke": "subject-4fa7e1f2733422e2",
    "Marsupilami": "subject-456a71ae161a416b",
    "Boule et Bill": "subject-9c3383d247a2eef4",
    "Achille Talon": "subject-e457a53bf666e5b8",
    "Iznogoud": "subject-e6d6fd51117d6ee5",
    "Largo Winch": "subject-9eca45b4b9853624",
    "Batman": "subject-dc2fb3e7353776b7",
    "Wonder Woman": "subject-300b445f588fd917",
    "Superman": "subject-d2bcaa78a36f6a14",
    "Wolverine": "subject-f768bf679209fd16",
    "Captain America": "subject-42ca198989b87031",
    "Hulk": "subject-8cd41f3fe96f2fe3",
    "Iron Man": "subject-eab00ce3c19635ce",
    "Black Panther": "subject-2dd18e58f8e57c4d",
    "Deadpool": "subject-c2208b0b7f749907",
    "Doctor Strange": "subject-f20ec6c09d53ce46",
    "Tour Eiffel": "subject-9fac09ff0c399021",
    "Burj Khalifa": "subject-155fecc75421c33d",
    "Opéra de Sydney": "subject-86f0c67fe706570d",
    "Empire State Building": "subject-47b8256b775b61a2",
}


def build(bank: dict) -> tuple[dict, list[dict]]:
    bank = copy.deepcopy(bank)
    by_id = {subject["id"]: subject for subject in bank["subjects"]}
    if not set(LINKS.values()) <= by_id.keys():
        raise ValueError("A curated subject ID is missing")
    evidence_by_target: dict[str, list] = {target: [] for target in LINKS.values()}
    linked_occurrences = 0

    for question in bank["questions"]:
        items = question.get("content", {}).get("items", [])
        if not items:
            continue
        ids_by_label = {item.get("text", "").strip(): item.get("id") for item in items}
        old_by_item = {
            evidence.get("itemId"): by_id[subject_id]
            for subject_id in question.get("subjectIds", [])
            if subject_id in by_id
            for evidence in by_id[subject_id].get("chronologyEvidence", [])
            if evidence.get("sourceQuestionId") == question["id"]
        }
        replacement = []
        changed = False
        for item in items:
            label = item.get("text", "").strip()
            target_id = LINKS.get(label)
            source = old_by_item.get(item.get("id"))
            if not target_id or source is None:
                replacement.append(source["id"] if source else None)
                continue
            target = by_id[target_id]
            target["aliases"] = list(dict.fromkeys(target.get("aliases", []) + [label]))
            target["tagIds"] = list(dict.fromkeys(target.get("tagIds", []) + source.get("tagIds", [])))
            evidence_by_target[target_id].extend(
                evidence for evidence in source.get("chronologyEvidence", [])
                if evidence.get("sourceQuestionId") == question["id"] and evidence.get("itemId") == item.get("id")
            )
            target["sourceQuestionIds"] = list(dict.fromkeys(
                target.get("sourceQuestionIds", []) + [question["id"]]
            ))
            replacement.append(target_id)
            changed = changed or target_id != source["id"]
            linked_occurrences += 1
        if changed and all(replacement):
            question["subjectIds"] = list(dict.fromkeys(replacement))

    for target_id, evidence in evidence_by_target.items():
        target = by_id[target_id]
        existing = {json.dumps(value, sort_keys=True, ensure_ascii=False) for value in target.get("chronologyEvidence", [])}
        for value in evidence:
            key = json.dumps(value, sort_keys=True, ensure_ascii=False)
            if key not in existing:
                target.setdefault("chronologyEvidence", []).append(value)
                existing.add(key)

    referenced = {sid for question in bank["questions"] for sid in question.get("subjectIds", [])}
    removed = [subject for subject in bank["subjects"]
               if subject["type"] == "chronology-item" and subject["id"] not in referenced]
    removed_ids = {subject["id"] for subject in removed}
    bank["subjects"] = [subject for subject in bank["subjects"] if subject["id"] not in removed_ids]
    history = [{"removedSubjectId": subject["id"], "canonicalSubjectId": LINKS.get(subject["label"]),
                "label": subject["label"]} for subject in removed]
    return bank, [{"linkedOccurrences": linked_occurrences, "removedSubjects": history}]


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    if bank.get("schemaVersion") != 4:
        raise SystemExit("Expected schema version 4")
    updated, history = build(bank)
    known = {subject["id"] for subject in updated["subjects"]}
    assert all(set(question.get("subjectIds", [])) <= known for question in updated["questions"])
    print(json.dumps({"subjects": len(updated["subjects"]), **history[0]}, ensure_ascii=False, indent=2))
    if BACKUP_PATH.exists():
        raise SystemExit(f"Refusing to overwrite {BACKUP_PATH}")
    shutil.copy2(BANK_PATH, BACKUP_PATH)
    BANK_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    migration = json.loads(MIGRATION_PATH.read_text(encoding="utf-8"))
    migration["curatedChronologyLinks"] = history[0]
    MIGRATION_PATH.write_text(json.dumps(migration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated bank; snapshot saved to {BACKUP_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
