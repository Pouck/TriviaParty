#!/usr/bin/env python3
"""Consolidate conservative duplicate subject anchors in the canonical bank."""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank/questions.json"
MIGRATION = ROOT / "game-library/bank/migration.json"
BACKUP = ROOT / "review-backups/questions-before-subject-dedup-2026-10-29.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", value))


def add_unique(items: list, values: list) -> list:
    result = list(items)
    seen = {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in result}
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            result.append(value)
            seen.add(key)
    return result


def find_merges(bank: dict) -> list[tuple[str, str]]:
    subjects = bank["subjects"]
    canonical_by_label: dict[str, list[dict]] = defaultdict(list)
    for subject in subjects:
        if subject["type"] in {"person", "city"}:
            canonical_by_label[normalize(subject["label"])].append(subject)

    merges: list[tuple[str, str]] = []
    for subject in subjects:
        if subject["type"] != "question-anchor":
            continue
        candidates = canonical_by_label.get(normalize(subject["label"]), [])
        if len(candidates) == 1:
            target = candidates[0]
            if target["type"] == "person" or (
                target["type"] == "city" and normalize(subject["label"]) == "montreal"
            ):
                merges.append((subject["id"], target["id"]))
    return sorted(merges)


def apply_merges(bank: dict, merges: list[tuple[str, str]]) -> dict:
    source_to_target = dict(merges)
    by_id = {subject["id"]: subject for subject in bank["subjects"]}
    all_questions = {question["id"]: question for question in bank["questions"]}
    history = []

    for source_id, target_id in merges:
        source, target = by_id[source_id], by_id[target_id]
        target["aliases"] = add_unique(target.get("aliases", []), [source["label"], *source.get("aliases", [])])
        target["tagIds"] = add_unique(target.get("tagIds", []), source.get("tagIds", []))
        target["facts"] = add_unique(target.get("facts", []), source.get("facts", []))
        target["relations"] = add_unique(target.get("relations", []), source.get("relations", []))
        target["sources"] = add_unique(target.get("sources", []), source.get("sources", []))
        question_ids = [question["id"] for question in all_questions.values()
                        if source_id in question.get("subjectIds", [])]
        target["sourceQuestionIds"] = add_unique(
            target.get("sourceQuestionIds", []), question_ids + source.get("sourceQuestionIds", [])
        )
        history.append({"removedSubjectId": source_id, "canonicalSubjectId": target_id,
                        "matchRule": "normalized-label-and-existing-person-or-reviewed-city-identity"})

    for question in bank["questions"]:
        values = [source_to_target.get(subject_id, subject_id) for subject_id in question.get("subjectIds", [])]
        question["subjectIds"] = list(dict.fromkeys(values))

    for subject in bank["subjects"]:
        subject["relations"] = [
            {**relation, "targetId": source_to_target.get(relation["targetId"], relation["targetId"])}
            for relation in subject.get("relations", [])
        ]
        subject["candidateSubjectIds"] = list(dict.fromkeys(
            source_to_target.get(candidate_id, candidate_id)
            for candidate_id in subject.get("candidateSubjectIds", [])
            if candidate_id not in source_to_target or source_to_target[candidate_id] != subject["id"]
        ))

    bank["subjects"] = [subject for subject in bank["subjects"] if subject["id"] not in source_to_target]
    return {"subjectMerges": history}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the cleaned bank")
    args = parser.parse_args()
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    if bank.get("schemaVersion") != 3:
        raise SystemExit("Expected bank schema version 3")
    merges = find_merges(bank)
    print(f"Conservative subject merges available: {len(merges)}")
    if not args.apply:
        for source, target in merges:
            print(f"{source} -> {target}")
        return

    if BACKUP.exists():
        raise SystemExit(f"Refusing to overwrite backup: {BACKUP}")
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BANK, BACKUP)
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))
    migration["subjectMerges"] = migration.get("subjectMerges", [])
    migration.update(apply_merges(bank, merges))
    BANK.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MIGRATION.write_text(json.dumps(migration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated bank; snapshot saved to {BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
