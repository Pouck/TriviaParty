#!/usr/bin/env python3
"""Generate a cleanup and dynamic chronology audit from the canonical bank."""

from __future__ import annotations

import itertools
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from canonical_question_bank import identity as question_identity, materialize

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "game-library/bank/questions.json"
REPORT_PATH = ROOT / "game-library/bank/DYNAMIC-AFFINITY-AUDIT.md"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", value))


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    questions = bank["questions"]
    subjects = bank["subjects"]
    subject_by_id = {subject["id"]: subject for subject in subjects}
    question_by_id = {question["id"]: question for question in questions}
    q_refs = {subject_id for question in questions for subject_id in question.get("subjectIds", [])}
    relation_refs = {relation["targetId"] for subject in subjects for relation in subject.get("relations", [])}
    orphaned = [subject for subject in subjects if subject["id"] not in q_refs and subject["id"] not in relation_refs]
    chronology_only = [subject for subject in orphaned if subject.get("chronologyFacts")]
    ordinary_orphaned = [subject for subject in orphaned if not subject.get("chronologyFacts")]
    ordering = [question for question in questions if any(
        presentation.get("content", {}).get("kind") == "ordering"
        for presentation in question.get("presentations", []))]
    question_anchors = [subject for subject in subjects if subject["type"] == "question-anchor"]
    identity_counts = Counter(subject["identityStatus"] for subject in subjects)
    subject_types = Counter(subject["type"] for subject in subjects)
    taxonomy = bank.get("taxonomy", [])
    taxonomy_by_id = {tag["id"]: tag for tag in taxonomy}
    tag_usage = Counter(tag_id for subject in subjects for tag_id in subject.get("tagIds", []))
    # Parent nodes are useful selection categories even when no subject points
    # at them directly. Count all ancestors of assigned tags as used.
    for tag_id in list(tag_usage):
        parent_id = taxonomy_by_id.get(tag_id, {}).get("parentId")
        while parent_id:
            tag_usage[parent_id] += 1
            parent_id = taxonomy_by_id.get(parent_id, {}).get("parentId")
    unused_tags = [tag for tag in taxonomy if tag["id"] not in tag_usage]

    contexts: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for subject in subjects:
        for fact in subject.get("chronologyFacts", []):
            contexts[fact["contextId"]].append((subject, fact))
    def disjoint(a: dict, b: dict) -> bool:
        return a["latestYear"] < b["earliestYear"] or b["latestYear"] < a["earliestYear"]

    def safe_triples(values: list[tuple[dict, dict]]) -> int:
        precise = [value for value in values if value[1].get("precision") != "circa-year"]
        return sum(
            all(disjoint(first[1], second[1]) for first, second in itertools.combinations(combo, 2))
            for combo in itertools.combinations(precise, 3)
        )

    ordering_pools: dict[str, list[dict]] = defaultdict(list)
    label_subjects: dict[str, set[str]] = defaultdict(set)
    for question in ordering:
        presentations = [p for p in question.get("presentations", [])
                         if p.get("content", {}).get("kind") == "ordering"]
        presentation = presentations[0] if presentations else {}
        pool = presentation.get("legacyPackageId") or presentation.get("legacyCategory", "(unknown)")
        ordering_pools[pool].append(question)
        for item in question.get("content", {}).get("items", []):
            item_key = normalize(item.get("text", ""))
            if item_key:
                for subject_id in question.get("subjectIds", []):
                    subject = subject_by_id.get(subject_id)
                    if subject and item.get("text") in subject.get("aliases", []) + [subject.get("label", "")]:
                        label_subjects[item_key].add(subject_id)

    missing_answers = Counter()
    missing_explanations = 0
    presentation_identities: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for question in questions:
        for presentation in question.get("presentations", []):
            rendered = materialize(question, presentation)
            presentation_identities[repr(question_identity(rendered))].append(
                (question["id"], presentation["id"]))
        kinds = {p.get("content", {}).get("kind", "unknown") for p in question.get("presentations", [])}
        if not question.get("answers"):
            for kind in kinds:
                missing_answers[kind] += 1
        if not question.get("explanation"):
            missing_explanations += 1
    unexpected_answer_gaps = sum(count for kind, count in missing_answers.items() if kind not in {"ordering", "mapChoice"})
    repeated_identities = [values for values in presentation_identities.values() if len(values) > 1]
    cross_entry_duplicates = [values for values in repeated_identities
                              if len({question_id for question_id, _ in values}) > 1]
    grouped_format_variants = sum(len(values) - 1 for values in repeated_identities
                                  if len({question_id for question_id, _ in values}) == 1)
    question_subject_counts = Counter(subject_id for question in questions
                                      for subject_id in set(question.get("subjectIds", [])))
    shared_subjects = sum(count > 1 for count in question_subject_counts.values())
    questions_on_shared_subjects = sum(
        any(question_subject_counts[subject_id] > 1 for subject_id in question.get("subjectIds", []))
        for question in questions)

    # Repeated exact labels among unresolved anchors are candidate identity
    # links only. The source prompts are retained to aid conservative review.
    duplicate_anchors: dict[str, list[dict]] = defaultdict(list)
    for subject in question_anchors:
        label = normalize(subject.get("label", ""))
        if label:
            duplicate_anchors[label].append(subject)
    duplicate_anchors = {label: values for label, values in duplicate_anchors.items()
                         if len(values) > 1 and label not in {"a", "b", "c", "d", "5", "6", "trois"}}

    ambiguous = [subject for subject in subjects if subject.get("identityStatus") == "ambiguous"]
    unresolved = [subject for subject in subjects if subject.get("identityStatus") == "legacy-item-unresolved"]
    comic_pilot_id = "lib-chronologie-bd-premieres-20261012"
    comic_pilot_checks = []
    for question in questions:
        item_years: dict[str, int] = {}
        for subject_id in question.get("subjectIds", []):
            subject = subject_by_id[subject_id]
            fact = next((value for value in subject.get("chronologyFacts", [])
                         if value.get("contextId") == "comics.first_appearance"), None)
            if fact is None:
                continue
            for evidence in subject.get("chronologyEvidence", []):
                if evidence.get("sourceQuestionId") == question["id"] and evidence.get("sourceSetId") == comic_pilot_id:
                    item_years[evidence["itemId"]] = fact["earliestYear"]
        if item_years:
            actual = sorted(item_years, key=item_years.get)
            comic_pilot_checks.append((question, len(actual) == len(question["content"].get("items", []))
                                       and actual == question["content"].get("correctOrderIds", [])))
    used_tags = {tag["id"]: tag["label"] for tag in bank.get("taxonomy", [])}
    lines = [
        "# Question bank cleanup audit",
        "",
        "Generated from `questions.json` by `build/audit-question-bank-cleanup.py`.",
        "Subject and chronology identity are reviewed separately from play format.",
        "",
        "## Current inventory",
        "",
        f"- Schema: {bank['schemaVersion']}",
        f"- Authored questions: {len(questions)}; ordering presentations: {len(ordering)} across {len(ordering_pools)} legacy pools.",
        f"- Subjects: {len(subjects)}; unlinked ordinary subjects: {len(ordinary_orphaned)}; chronology-only subjects used by dynamic generation: {len(chronology_only)}.",
        f"- Question-scoped anchors: {len(question_anchors)}.",
        f"- Questions linked to a subject used by multiple questions: {questions_on_shared_subjects}; shared subjects: {shared_subjects}.",
        f"- Exact cross-entry question duplicates: {len(cross_entry_duplicates)}; identical format variants already grouped within a question entry: {grouped_format_variants}.",
        f"- Identity statuses: {', '.join(f'{key} {value}' for key, value in sorted(identity_counts.items()))}.",
        f"- Taxonomy tags: {len(bank.get('taxonomy', []))}; unused tags: {len(unused_tags)}.",
        f"- Empty accepted-answer lists by presentation type: {', '.join(f'{key} {value}' for key, value in sorted(missing_answers.items())) or 'none'}.",
        f"- Questions without explanations: {missing_explanations} (optional field; review for quality, not a structural error).",
        f"- Missing answers on non-ordering/non-map formats: {unexpected_answer_gaps}.",
        "",
        "Empty answer lists on ordering and map-choice questions are expected: their correct response is represented in structured content.",
        "",
        "## Sourced chronology coverage",
        "",
        "| Comparison context | Subjects | Precision counts | Strict non-overlapping triples |",
        "|---|---:|---|---:|",
    ]
    for context_id, values in sorted(contexts.items()):
        precision = Counter(fact.get("precision", "unknown") for _, fact in values)
        label = " (painting subjects)" if context_id == "artwork.creation" else ""
        lines.append(f"| `{context_id}`{label} | {len(values)} | "
                     f"{', '.join(f'{name}: {count}' for name, count in sorted(precision.items()))} | {safe_triples(values)} |")
    if not contexts:
        lines.append("| none | 0 | none | 0 |")
    lines.extend([
        "",
        "Only same-context, non-overlapping facts can be ordered automatically. Circa dates are currently excluded from generated sets; equal years and overlapping ranges are not guessed.",
        "",
        "## Unresolved chronology items",
        "",
        "| Identity status | Label | Candidate subjects | Source sets |",
        "|---|---|---|---|",
    ])
    for subject in sorted(ambiguous + unresolved, key=lambda item: (item["identityStatus"], normalize(item["label"]))):
        candidates = ", ".join(
            f"`{candidate}` ({subject_by_id.get(candidate, {}).get('label', 'missing')})"
            for candidate in subject.get("candidateSubjectIds", [])
        ) or "—"
        pools = ", ".join(sorted({e.get("sourceSetId", "") for e in subject.get("chronologyEvidence", []) if e.get("sourceSetId")}))
        lines.append(f"| {subject['identityStatus']} | {md(subject['label'])} | {md(candidates)} | {md(pools or '—')} |")
    if not ambiguous and not unresolved:
        lines.append("| — | none | — | — |")

    lines.extend([
        "",
        "## Chronology migration",
        "",
        f"Static ordering presentations active in the bank: {len(ordering)}. Legacy sets are archived separately. {sum(len(values) for values in contexts.values())} sourced subject facts remain available to the runtime generator.",
        "The repository generates only within a shared, sourced comparison context; current eligible pools are painting creation and comic first appearance.",
        "",
        "| Dynamic context | Sourced subjects | Strict non-overlapping triples |",
        "|---|---:|---:|",
    ])
    for context_id, values in sorted(contexts.items()):
        lines.append(f"| `{context_id}` | {len(values)} | {safe_triples(values)} |")
    if not contexts:
        lines.append("| none | 0 | 0 |")

    lines.extend([
        "",
        "## Repeated unresolved subject labels",
        "",
        "These exact normalized labels occur on multiple question-scoped anchors. A repeated answer can indicate the same entity, a shared concept, or a homonym; prompts are included for manual identity review.",
        "",
        "| Label | Question and prompt |",
        "|---|---|",
    ])
    for label, anchors in sorted(duplicate_anchors.items()):
        for anchor in anchors:
            q_ids = anchor.get("sourceQuestionIds", [])
            prompt_text = "; ".join(
                f"`{qid}`: {question_by_id.get(qid, {}).get('prompt', '(missing source question)')}"
                for qid in q_ids
            ) or "no source question recorded"
            lines.append(f"| {md(anchor['label'])} | {md(prompt_text)} |")
    if not duplicate_anchors:
        lines.append("| — | none |")

    lines.extend([
        "",
        "## Remaining audit work",
        "",
        f"1. Review the remaining {len(question_anchors)} question-scoped anchors by high-value subject groups; keep distinct entities separate and attach strong identity matches to one shared subject.",
        "2. Use the prepared data-only question review batch to rate clarity, interest, difficulty, answer variants, and source needs before making subjective removals.",
        "3. Add new chronology contexts only when individual subjects have comparable, sourced facts; unsupported fixed sets remain archived.",
        "4. The host setup already balances topics and formats; connect it to canonical subject queries as the registry gains verified links.",
        "",
        "## Taxonomy nodes without subjects",
        "",
    ])
    if unused_tags:
        lines.extend(f"- `{tag['id']}` — {tag['label']}" for tag in unused_tags)
    else:
        lines.append("None.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
