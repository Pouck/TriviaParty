#!/usr/bin/env python3
"""Audit chronology item overlap with reusable canonical question entries."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
REPORT_PATH = ROOT / "game-library/bank/DYNAMIC-AFFINITY-AUDIT.md"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    entries = bank["questions"]
    answer_index: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        if any(p.get("content", {}).get("kind") == "ordering" for p in entry.get("presentations", [])):
            continue
        for answer in entry.get("answers", []):
            key = normalize(answer)
            if key:
                answer_index[key].append(entry)

    groups: dict[str, list[dict]] = defaultdict(list)
    item_labels: dict[str, str] = {}
    matched: dict[str, list[dict]] = {}
    occurrence_count = 0
    ordering_count = 0
    for entry in entries:
        for presentation in entry.get("presentations", []):
            if presentation.get("content", {}).get("kind") != "ordering":
                continue
            ordering_count += 1
            groups[presentation.get("legacyPackageId") or presentation.get("legacyCategory", "(unknown)")].append(entry)
            for item in entry.get("content", {}).get("items", []):
                label = item.get("text", "").strip()
                key = normalize(label)
                if not key:
                    continue
                item_labels.setdefault(key, label)
                candidates = answer_index.get(key, [])
                if candidates:
                    matched[key] = candidates
                    occurrence_count += 1

    lines = [
        "# Dynamic affinity audit",
        "",
        "Generated from `questions.json` by `build/audit-question-bank-affinities.py`.",
        "Exact normalized answer matches are candidates only; they do not authorize a merge.",
        "",
        "## Bank totals",
        "",
        f"- Canonical entries: {len(entries)}",
        f"- Ordering presentations: {ordering_count}",
        f"- Distinct normalized ordering item labels: {len(item_labels)}",
        f"- Labels matching another entry's accepted answer: {len(matched)} ({occurrence_count} item occurrences)",
        f"- Candidate target entries: {len({entry['id'] for candidates in matched.values() for entry in candidates})}",
        f"- Ordering source pools: {len(groups)}",
        "",
        "## Existing ordering pools",
        "",
        "Combination counts are mathematical upper bounds from item counts and authored set size. They assume all items in a pool share a valid comparator; that assumption must be verified before generating a package.",
        "",
        "| Legacy pool | Existing sets | Unique items | Items per set | Potential sets at typical size |",
        "|---|---:|---:|---:|---:|",
    ]
    for pool, source_entries in sorted(groups.items()):
        items = {
            normalize(item.get("text", ""))
            for entry in source_entries
            for item in entry.get("content", {}).get("items", [])
            if normalize(item.get("text", ""))
        }
        sizes = [len(entry.get("content", {}).get("items", [])) for entry in source_entries]
        typical_size = round(sum(sizes) / len(sizes))
        combinations = math.comb(len(items), typical_size) if len(items) >= typical_size else 0
        lines.append(
            f"| {markdown(pool)} | {len(source_entries)} | {len(items)} | "
            f"{min(sizes)}–{max(sizes)} | C({len(items)}, {typical_size}) = {combinations:,} |"
        )

    lines.extend([
        "",
        "## Item labels that match existing entries",
        "",
        "| Ordering item | Candidate entry IDs and tags |",
        "|---|---|",
    ])
    for key, candidates in sorted(matched.items(), key=lambda pair: normalize(item_labels[pair[0]])):
        label = item_labels[key]
        targets = []
        for entry in candidates:
            tags = ", ".join(entry.get("topics", []))
            targets.append(f"`{entry['id']}` ({markdown(tags)})")
        lines.append(f"| {markdown(label)} | {'; '.join(targets)} |")

    ambiguous = [(key, label, candidates) for key, label in item_labels.items() if len(answer_index.get(key, [])) > 1]
    lines.extend([
        "",
        "## Ambiguous exact-answer matches",
        "",
        "These labels have multiple target entries and need entity-level resolution before migration.",
        "",
        "| Item label | Candidate entry IDs |",
        "|---|---|",
    ])
    for _, label, candidates in sorted(ambiguous, key=lambda row: normalize(row[1])):
        target_ids = "; ".join("`" + candidate["id"] + "`" for candidate in candidates)
        lines.append(f"| {markdown(label)} | {target_ids} |")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
