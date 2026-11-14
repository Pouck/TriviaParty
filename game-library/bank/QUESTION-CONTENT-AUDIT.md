# Question-bank content audit

## Scope and review method

The active canonical bank now has 1,441 authored question records after high-confidence duplicate cleanup, subject consolidation, and retirement of static chronology sets. The initial diagnostic pass covered the
pre-cleanup bank of 1,580 records. This audit counts each active record once
and inspects its shared prompt, accepted answer, and relevant question data. It
does not expand every presentation or display image files. Image presence and
references are checked as metadata only.

Use **general adult trivia players** as the audience. For each question, review:

- **Difficulty:** 1 = trivial, 2 = easy, 3 = moderate, 4 = challenging, 5 = specialist-level or obscure. Flag 1 and 5 for possible removal or revision; do not treat difficulty as a fact about the question.
- **Interest:** 1 = low, 2 = serviceable, 3 = engaging or memorable.
- **Clarity:** clear, revise, or ambiguous. Check that the prompt supplies the necessary context and asks one thing.
- **Answer:** confirm the answer, identify other defensible answers, and check that accepted variants are neither too strict nor too broad.
- **Evidence:** attach a reliable source when the answer could be disputed, changes over time, or depends on a specific date, ranking, attribution, or interpretation.
- **Duplication:** compare the underlying fact and intended reasoning. A shared subject, answer, or generic prompt alone does not make two questions duplicates.
- **Coverage:** use canonical subject tags and distinct concepts. A large count alone is not a flaw without a target distribution.

Ratings already present in the bank are legacy quality reviews, not difficulty
scores. Use them as context, not as the adult-audience difficulty rating.

## First-pass findings

### Duplicate cleanup completed

Six exact image-question duplicates shared the same subject, prompt, answer, and image asset. All six pairs are merged under the existing canonical question IDs. The reviewed Nile/Cairo pair was consolidated into one question entry; both multiple-choice presentations, prompt wording, IDs, and review records were preserved. An initial indexed screen compared 9,234 candidate pairs drawn from 1,443 records. A follow-up scored all 1,038,961 pairs in the 1,442-question bank and flagged 116 high-signal candidates. After media review, Ottawa's duplicate image-charade pair was consolidated, retaining the image with a goose; the alternate image question was archived. Gotham remains one written-answer question after its redundant multiple-choice presentation was removed. The user-marked Nile, Rapa Nui, Frodo, Nymphéas, Versailles, and Pantheon pairs were reclassified as related because one or both source questions were text-based; both questions remain in each case. Candidate-sheet rows 5–11 remain related and retained. The current 1,441-question bank was rescanned and the 114 resulting candidates still need semantic adjudication. Generic visual prompts without informative clues remain a text-screening limitation.
All historical IDs and answer variants remain in the active canonical record;
the removed source records and duplicate presentations are preserved in the
archive. The merged records retain the fuller explanation when it adds a date
and French title.

| Candidate A | Candidate B | Subject |
|---|---|---|
| `image-qsj-arts-baiser` | `image-qsj-painting-rank-011` | The Kiss / Le Baiser |
| `image-qsj-arts-radeau` | `image-qsj-painting-rank-025` | The Raft of the Medusa |
| `image-qsj-arts-ronde` | `image-qsj-painting-rank-027` | The Night Watch / La Ronde de nuit |
| `arts-buzzer-tableaux-celebres-20261011-05` | `image-qsj-painting-rank-021` | Liberty Leading the People / La Liberté guidant le peuple |
| `arts-qcm-peintures-classiques-20261011-03` | `image-qsj-painting-rank-014` | The Birth of Venus / La Naissance de Vénus (Botticelli) |
| `arts-qcm-peintures-classiques-20261011-07` | `image-qsj-painting-rank-012` | Girl with a Pearl Earring / La Jeune Fille à la perle |

Repeated chronology wording was not treated as duplication. The 119 fixed ordering entries are now archived, and chronology questions are generated from individual sourced subject facts in supported contexts. Questions that share an answer but ask different things (for example, identifying a city from a charade versus asking which city hosted an event) remain separate.

### Coverage snapshot

The counts below are current question membership by top-level canonical
taxonomy tag. Questions with multiple subjects may count in more than one
branch. Counts describe the bank; they are not quality targets.

| Canonical branch | Questions |
|---|---:|
| Arts | 276 |
| Literature | 238 |
| History | 203 |
| Geography | 169 |
| Nature | 94 |
| Culture | 91 |
| Cinema | 89 |
| Music | 69 |
| Languages | 57 |
| Puzzles | 53 |
| Folklore | 52 |
| Mythology | 44 |
| Science | 37 |
| People | 23 |
| Food | 20 |
| Gaming | 17 |

Some leaf topics remain small; compare their breadth against the intended game audience rather than treating low counts as automatic defects. Arts, literature, and history remain the largest areas, while gaming and food are relatively small.

### Completeness and maintenance signals

- 1,092 questions (75.7%) have no explanation. Explanations are optional, so
  this is a review opportunity rather than a failure count.
- 545 questions have an explicit source either on the question, its image
  facts, or a linked subject; 897 have no such source reference. Easy,
  stable common facts do not all need citations, but disputed, date-sensitive,
  attribution, and ranking questions should be sourced before approval.
- The 11 test/demo-only records and all 30 test-labelled presentations have
  been removed from active play data and retained in the archive. Fourteen
  historical test presentation IDs remain as non-playable legacy aliases on
  surviving canonical questions.
- All 517 unique media references exist in `media/` (542 references total).
  No image was opened or rendered for this review.
- 853 subjects remain question-scoped anchors after merging repeated entity anchors, linking 12 additional anchors to verified subjects, and resolving the Sistine Chapel and Creation of Adam subjects. They are not orphaned, but they
  limit cross-question coverage and duplicate analysis until identities are
  reviewed.

### Diagnostic sample

One question was sampled from each of 24 legacy topic groups (excluding
test-only content). This is a diagnostic sweep, not a statistical estimate or a
full fact-check. Early difficulty candidates for an adult general audience are
the iPhone creator (`q18`), Zelda's central kingdom (`q22`), Louis XVI's queen
(`lib-buzzer-histoire-france-generale-20261012-01`), the dolphin's animal group
(`lib-qcm-animaux-marins-20261012-03`), Bob Marley and “No Woman, No Cry”
(`lib-buzzer-pop-rock-20261012-05`), and Poseidon's pursuit of Odysseus
(`lib-qcm-odyssee-20261012-02`). These look like possible warm-up-level items;
they should be rated in a wider batch before being removed.

One wording candidate is “Quel fruit sec forme la base habituelle de la pâte
de massepain ?” (`lib-qcm-cuisine-saveurs-20261012-01`). “Fruit sec” can be read
broadly; “fruit à coque” would make the intended answer less ambiguous.

Image-based questions with an empty clue list may still be complete when the
image itself is the intended prompt. Since this review is data-only, their
visual difficulty and legibility remain unscored; the asset references are
present.

## Recommended audit sequence

1. Review questions in batches by canonical subject branch, assigning
   difficulty, interest, clarity, answer quality, and evidence status.
2. Continue resolving the 853 question-scoped anchors in data-only batches, prioritizing repeated entities and coverage gaps.
3. Fact-check disputed and time-sensitive answers from the prepared review batches; add chronology facts only with a clear comparison context and source.

The excluded and merged records are preserved at
`review-backups/questions-excluded-and-merged-2026-10-29.json`; the full
pre-cleanup snapshot is at
`review-backups/questions-before-content-audit-cleanup-2026-10-29.json`.
Difficulty and interest judgments from the diagnostic sample need wider batch
calibration before any subjective edits.
