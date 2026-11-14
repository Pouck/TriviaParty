# Question bank cleanup audit

Generated from `questions.json` by `build/audit-question-bank-cleanup.py`.
Subject and chronology identity are reviewed separately from play format.

## Current inventory

- Schema: 4
- Authored questions: 1441; ordering presentations: 0 across 0 legacy pools.
- Subjects: 1531; unlinked ordinary subjects: 0; chronology-only subjects used by dynamic generation: 5.
- Question-scoped anchors: 853.
- Questions linked to a subject used by multiple questions: 76; shared subjects: 37.
- Exact cross-entry question duplicates: 0; identical format variants already grouped within a question entry: 325.
- Identity statuses: question-scoped 853, verified 678.
- Taxonomy tags: 32; unused tags: 0.
- Empty accepted-answer lists by presentation type: none.
- Questions without explanations: 1091 (optional field; review for quality, not a structural error).
- Missing answers on non-ordering/non-map formats: 0.

Empty answer lists on ordering and map-choice questions are expected: their correct response is represented in structured content.

## Sourced chronology coverage

| Comparison context | Subjects | Precision counts | Strict non-overlapping triples |
|---|---:|---|---:|
| `artwork.creation` (painting subjects) | 20 | circa-year: 2, year: 16, year-range: 2 | 800 |
| `comics.first_appearance` | 15 | year: 15 | 429 |

Only same-context, non-overlapping facts can be ordered automatically. Circa dates are currently excluded from generated sets; equal years and overlapping ranges are not guessed.

## Unresolved chronology items

| Identity status | Label | Candidate subjects | Source sets |
|---|---|---|---|
| — | none | — | — |

## Chronology migration

Static ordering presentations active in the bank: 0. Legacy sets are archived separately. 35 sourced subject facts remain available to the runtime generator.
The repository generates only within a shared, sourced comparison context; current eligible pools are painting creation and comic first appearance.

| Dynamic context | Sourced subjects | Strict non-overlapping triples |
|---|---:|---:|
| `artwork.creation` | 20 | 800 |
| `comics.first_appearance` | 15 | 429 |

## Repeated unresolved subject labels

These exact normalized labels occur on multiple question-scoped anchors. A repeated answer can indicate the same entity, a shared concept, or a homonym; prompts are included for manual identity review.

| Label | Question and prompt |
|---|---|
| — | none |

## Remaining audit work

1. Review the remaining 853 question-scoped anchors by high-value subject groups; keep distinct entities separate and attach strong identity matches to one shared subject.
2. Use the prepared data-only question review batch to rate clarity, interest, difficulty, answer variants, and source needs before making subjective removals.
3. Add new chronology contexts only when individual subjects have comparable, sourced facts; unsupported fixed sets remain archived.
4. The host setup already balances topics and formats; connect it to canonical subject queries as the registry gains verified links.

## Taxonomy nodes without subjects

None.
