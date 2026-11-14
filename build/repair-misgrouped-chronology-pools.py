#!/usr/bin/env python3
"""Separate demo video-game ordering questions from the comics legacy pool."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
MIGRATION_PATH = ROOT / "game-library/bank/migration.json"
BACKUP_PATH = ROOT / "review-backups/questions-before-chronology-pool-metadata-repair-2026-10-29.json"
SHARED_OLD_ID = "lib-chronologie-bd-premieres-20261012"

RECLASSIFY = {
    "q4": ("lib-chronologie-consoles-demo", "Culture populaire – Consoles – Chronologie"),
    "q24": ("lib-chronologie-jeux-video-demo", "Culture populaire – Jeux vidéo – Chronologie"),
}


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    migration = json.loads(MIGRATION_PATH.read_text(encoding="utf-8"))
    if bank.get("schemaVersion") != 4:
        raise SystemExit("Expected canonical bank schema version 4")
    if BACKUP_PATH.exists():
        raise SystemExit(f"Refusing to overwrite {BACKUP_PATH}")
    updated = copy.deepcopy(bank)
    by_id = {subject["id"]: subject for subject in updated["subjects"]}
    changed = []
    for question in updated["questions"]:
        if question["id"] not in RECLASSIFY:
            continue
        new_package, new_category = RECLASSIFY[question["id"]]
        old_package = None
        for presentation in question.get("presentations", []):
            if presentation.get("legacyPackageId") == SHARED_OLD_ID:
                old_package = presentation["legacyPackageId"]
                presentation["legacyPackageId"] = new_package
                presentation["legacyCategory"] = new_category
                presentation["topic"] = "Jeux vidéo"
        if old_package is None:
            raise ValueError(f"Expected {question['id']} to use legacy package {SHARED_OLD_ID}")
        for subject_id in question.get("subjectIds", []):
            subject = by_id[subject_id]
            if subject["type"] == "chronology-item":
                subject["tagIds"] = list(dict.fromkeys(subject.get("tagIds", []) + ["gaming"]))
            for evidence in subject.get("chronologyEvidence", []):
                if evidence.get("sourceQuestionId") == question["id"] and evidence.get("sourceSetId") == SHARED_OLD_ID:
                    evidence["sourceSetId"] = new_package
        changed.append({"questionId": question["id"], "oldPackageId": old_package,
                        "newPackageId": new_package, "newCategory": new_category})

    if len(changed) != len(RECLASSIFY):
        raise ValueError(f"Expected {len(RECLASSIFY)} questions to be reclassified")
    shutil.copy2(BANK_PATH, BACKUP_PATH)
    BANK_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    migration["reclassifiedChronologyPools"] = changed
    pilot = migration.get("comicFirstAppearancePilot", {})
    pilot["sourceQuestionIds"] = sorted(
        question["id"] for question in updated["questions"]
        if question["id"].startswith("lib-chronologie-bd-premieres-")
    )
    migration["comicFirstAppearancePilot"] = pilot
    MIGRATION_PATH.write_text(json.dumps(migration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reclassified": changed, "backup": str(BACKUP_PATH.relative_to(ROOT))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
