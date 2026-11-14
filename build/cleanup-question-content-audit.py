#!/usr/bin/env python3
"""Archive demo-only content and consolidate exact duplicate image questions."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MIGRATION_PATH = ROOT / "game-library/bank/migration.json"
BACKUP_PATH = ROOT / "review-backups/questions-before-content-audit-cleanup-2026-10-29.json"
ARCHIVE_PATH = ROOT / "review-backups/questions-excluded-and-merged-2026-10-29.json"

DUPLICATE_PAIRS = [
    ("image-qsj-arts-baiser", "image-qsj-painting-rank-011"),
    ("image-qsj-arts-radeau", "image-qsj-painting-rank-025"),
    ("image-qsj-arts-ronde", "image-qsj-painting-rank-027"),
]


def merge_json(base, extra):
    if isinstance(base, dict) and isinstance(extra, dict):
        result = copy.deepcopy(base)
        for key, value in extra.items():
            result[key] = merge_json(result[key], value) if key in result else copy.deepcopy(value)
        return result
    if isinstance(base, list) and isinstance(extra, list):
        result = copy.deepcopy(base)
        for value in extra:
            if value not in result:
                result.append(copy.deepcopy(value))
        return result
    if base == extra:
        return copy.deepcopy(base)
    raise ValueError(f"Conflicting values while merging duplicate records: {base!r} != {extra!r}")


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    migration = json.loads(MIGRATION_PATH.read_text(encoding="utf-8"))
    if bank.get("schemaVersion") != 4:
        raise SystemExit("Expected canonical bank schema version 4")
    for path in (BACKUP_PATH, ARCHIVE_PATH):
        if path.exists():
            raise SystemExit(f"Refusing to overwrite {path}")

    updated = copy.deepcopy(bank)
    originals = {question["id"]: question for question in updated["questions"]}
    for canonical_id, duplicate_id in DUPLICATE_PAIRS:
        if canonical_id not in originals or duplicate_id not in originals:
            raise ValueError(f"Missing expected duplicate pair: {canonical_id}, {duplicate_id}")

    # Exclude records whose every active presentation is explicitly test/demo.
    test_only = [question for question in updated["questions"] if question.get("presentations")
                 and all(presentation.get("legacyCategory", "").strip().casefold().startswith("test")
                         or presentation.get("legacyPackageId", "").casefold().startswith("test-")
                         for presentation in question["presentations"])]
    test_only_ids = {question["id"] for question in test_only}
    retired_test_presentations = []

    # Merge only pairs whose question data and sole image presentation are the
    # same except IDs, answer aliases, and additive image metadata.
    merged_records = []
    remove_question_ids = set(test_only_ids)
    for canonical_id, duplicate_id in DUPLICATE_PAIRS:
        canonical = copy.deepcopy(originals[canonical_id])
        duplicate = copy.deepcopy(originals[duplicate_id])
        for key in ("topics", "prompt", "content", "subjectIds", "review"):
            if canonical.get(key) != duplicate.get(key):
                raise ValueError(f"Duplicate pair differs in {key}: {canonical_id}, {duplicate_id}")
        if len(canonical.get("presentations", [])) != 1 or len(duplicate.get("presentations", [])) != 1:
            raise ValueError(f"Expected one presentation in duplicate pair {canonical_id}, {duplicate_id}")
        first_presentation, duplicate_presentation = canonical["presentations"][0], duplicate["presentations"][0]
        first_data = {key: value for key, value in first_presentation.items() if key != "id"}
        duplicate_data = {key: value for key, value in duplicate_presentation.items() if key != "id"}
        if first_data != duplicate_data:
            raise ValueError(f"Duplicate presentations differ: {canonical_id}, {duplicate_id}")
        if not first_data.get("content", {}).get("imageUrl"):
            raise ValueError(f"Expected shared image asset in {canonical_id}, {duplicate_id}")

        canonical["answers"] = list(dict.fromkeys(canonical.get("answers", []) + duplicate.get("answers", [])))
        explanations = [value for value in (canonical.get("explanation"), duplicate.get("explanation")) if value]
        if explanations:
            # These pairs have the same visual question; keep the fuller
            # explanation, which includes the dated work or French title.
            canonical["explanation"] = max(explanations, key=lambda value: (len(value), value))
        else:
            canonical.pop("explanation", None)
        canonical["legacyIds"] = list(dict.fromkeys(canonical.get("legacyIds", []) + duplicate.get("legacyIds", [])))
        canonical["legacyReviews"] = list(dict.fromkeys(canonical.get("legacyReviews", []) + duplicate.get("legacyReviews", [])))
        for history_key in ("reviewHistory",):
            canonical[history_key] = list(dict.fromkeys(canonical.get(history_key, []) + duplicate.get(history_key, [])))
            if not canonical[history_key]:
                canonical.pop(history_key)
        if canonical.get("imageFacts") is not None and duplicate.get("imageFacts") is not None:
            canonical["imageFacts"] = merge_json(canonical["imageFacts"], duplicate["imageFacts"])
        elif duplicate.get("imageFacts") is not None:
            canonical["imageFacts"] = copy.deepcopy(duplicate["imageFacts"])

        merged_records.append({
            "canonicalQuestionId": canonical_id,
            "mergedQuestionId": duplicate_id,
            "retiredDuplicatePresentation": copy.deepcopy(duplicate_presentation),
            "mergedAnswers": copy.deepcopy(duplicate.get("answers", [])),
            "retainedLegacyIds": copy.deepcopy(duplicate.get("legacyIds", [duplicate_id])),
        })
        originals[canonical_id] = canonical
        remove_question_ids.add(duplicate_id)

    active_questions = []
    for question in updated["questions"]:
        if question["id"] in remove_question_ids:
            continue
        if question["id"] in {record["canonicalQuestionId"] for record in merged_records}:
            question = originals[question["id"]]
        kept_presentations = []
        for presentation in question.get("presentations", []):
            is_test = presentation.get("legacyCategory", "").strip().casefold().startswith("test") \
                or presentation.get("legacyPackageId", "").casefold().startswith("test-")
            if is_test:
                retired_test_presentations.append({
                    "questionId": question["id"],
                    "presentation": copy.deepcopy(presentation),
                })
            else:
                kept_presentations.append(presentation)
        if not kept_presentations:
            raise ValueError(f"Question lost all presentations unexpectedly: {question['id']}")
        question["presentations"] = kept_presentations
        question["topics"] = [topic for topic in question.get("topics", []) if topic.strip().casefold() != "tests"]
        if not question["topics"]:
            raise ValueError(f"Question lost all topics unexpectedly: {question['id']}")
        active_questions.append(question)

    # Test labels were presentation provenance, not subject taxonomy. Remove
    # their legacy tag and source links, then keep only subjects reachable from
    # active questions through verified relations/candidate links.
    subjects = {subject["id"]: subject for subject in updated["subjects"]}
    for subject in subjects.values():
        subject["tagIds"] = [tag for tag in subject.get("tagIds", []) if tag != "legacy.tests"]
        subject["sourceQuestionIds"] = [qid for qid in subject.get("sourceQuestionIds", []) if qid not in test_only_ids]
        subject["chronologyEvidence"] = [evidence for evidence in subject.get("chronologyEvidence", [])
                                         if evidence.get("sourceQuestionId") not in test_only_ids]

    active_refs = {sid for question in active_questions for sid in question.get("subjectIds", [])}
    reachable = set(active_refs)
    pending = list(active_refs)
    while pending:
        subject = subjects.get(pending.pop())
        if subject is None:
            continue
        targets = {relation.get("targetId") for relation in subject.get("relations", [])}
        targets.update(subject.get("candidateSubjectIds", []))
        for target in targets - reachable:
            if target in subjects:
                reachable.add(target)
                pending.append(target)
    removed_subject_ids = set(subjects) - reachable
    kept_subjects = [subject for subject in updated["subjects"] if subject["id"] in reachable]
    for subject in kept_subjects:
        subject["relations"] = [relation for relation in subject.get("relations", [])
                                if relation.get("targetId") in reachable]
        subject["candidateSubjectIds"] = [candidate for candidate in subject.get("candidateSubjectIds", [])
                                          if candidate in reachable]

    # Prune the now-empty legacy taxonomy branch while retaining every other
    # node that is assigned directly or is an ancestor of an assigned tag.
    used_tags = {tag for subject in kept_subjects for tag in subject.get("tagIds", [])}
    taxonomy_by_id = {tag["id"]: tag for tag in updated.get("taxonomy", [])}
    for tag_id in list(used_tags):
        parent = taxonomy_by_id.get(tag_id, {}).get("parentId")
        while parent:
            used_tags.add(parent)
            parent = taxonomy_by_id.get(parent, {}).get("parentId")
    updated["taxonomy"] = [tag for tag in updated.get("taxonomy", []) if tag["id"] in used_tags]
    updated["questions"] = active_questions
    updated["subjects"] = kept_subjects

    source_bank_questions = {question["id"]: question for question in bank["questions"]}
    archive = {
        "description": "Question records and presentations excluded or merged during the high-confidence content audit cleanup. This archive is not loaded for play.",
        "excludedDemoQuestions": copy.deepcopy(test_only),
        "retiredTestPresentations": retired_test_presentations,
        "duplicatePairs": [
            {"retainedQuestionBeforeMerge": copy.deepcopy(source_bank_questions[record["canonicalQuestionId"]]),
             "duplicateQuestionBeforeMerge": copy.deepcopy(source_bank_questions[record["mergedQuestionId"]])}
            for record in merged_records
        ],
    }

    cleanup = {
        "excludedDemoQuestionIds": sorted(test_only_ids),
        "excludedDemoQuestionCount": len(test_only),
        "excludedDemoPresentationIds": sorted(presentation["id"] for question in test_only
                                              for presentation in question["presentations"]),
        "excludedDemoPresentationCount": sum(len(question["presentations"]) for question in test_only),
        "retiredTestPresentationIds": sorted(item["presentation"]["id"] for item in retired_test_presentations),
        "retiredTestPresentationCount": len(retired_test_presentations),
        "totalTestPresentationCount": sum(len(question["presentations"]) for question in test_only)
            + len(retired_test_presentations),
        "duplicateQuestionMerges": merged_records,
        "removedUnreachableSubjectIds": sorted(removed_subject_ids),
        "activeQuestionCount": len(active_questions),
        "activeSubjectCount": len(kept_subjects),
        "archivePath": str(ARCHIVE_PATH.relative_to(ROOT)),
        "snapshotPath": str(BACKUP_PATH.relative_to(ROOT)),
    }

    # Structural checks before touching the working bank.
    all_question_ids = {question["id"] for question in active_questions}
    all_aliases = [alias for question in active_questions for alias in question["legacyIds"]]
    known_subjects = {subject["id"] for subject in kept_subjects}
    if len(all_aliases) != len(set(all_aliases)):
        raise ValueError("Duplicate legacy aliases after question merge")
    if any(not question["subjectIds"] or set(question["subjectIds"]) - known_subjects for question in active_questions):
        raise ValueError("Active question has missing subject reference")
    if any(presentation["id"] not in question["legacyIds"]
           for question in active_questions for presentation in question["presentations"]):
        raise ValueError("Active presentation has no retained legacy alias")
    if any(relation.get("targetId") not in known_subjects
           for subject in kept_subjects for relation in subject.get("relations", [])):
        raise ValueError("Dangling relation after subject pruning")
    if len(all_question_ids) != len(active_questions):
        raise ValueError("Duplicate active question IDs")

    updated["subjects"] = kept_subjects
    migration["questionContentAuditCleanup"] = cleanup
    shutil.copy2(BANK_PATH, BACKUP_PATH)
    ARCHIVE_PATH.write_text(json.dumps(archive, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    BANK_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MIGRATION_PATH.write_text(json.dumps(migration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(cleanup, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
