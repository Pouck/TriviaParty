# Dynamic question selection and chronology

## Intended model

The bank separates canonical subjects from authored questions. A subject entry
represents an entity, work, event, person, place, or concept, and owns its
hierarchical tags, relationships, aliases, and structured facts. Authored
questions reference one or more subject IDs and keep their own prompts, accepted
answers, explanations, and play presentations. One subject can therefore be
asked about from several angles without duplicating its identity or facts. A
package is generated from a subject query and selected format; format does not
create a separate subject entry.

For chronology, subjects need comparable, structured values and a comparison
context. A context distinguishes, for example, an artwork's creation from its
first public exhibition, or a person's birth from a work's publication. The
generator selects a compatible affinity group, draws distinct subjects from it,
and constructs an ordering question. It must not combine values that only look
comparable because they share a broad tag such as `Arts` or `History`.

One entity can support several angles: a painting subject may be linked to image
identification and title/artist questions, as well as a creation-date chronology
fact. A historical event may have buzzer or written questions and a chronological
fact. The subject is stored once; genuinely different authored question content
remains as separate questions associated with that subject.

## Initial inventory (2026-10-29)

- Canonical bank before subject migration: 1,580 authored question entries.
- Ordering presentations: 124 entries across 23 legacy categories.
- Those orderings contain 357 distinct normalized item labels.
- 88 item labels already exactly match answers in other entries (97 occurrences,
  pointing to 101 non-ordering entries before duplicate-entity consolidation).
- Several labels point to multiple existing entries. Examples include *Les
  Époux Arnolfini*, *La Naissance de Vénus*, *La Jeune Fille à la perle*, and
  *Le Baiser*. These need entity-level consolidation and presentation/review
  preservation, not another chronology-specific copy. An exact title is only a
  textual collision: *La Naissance de Vénus* can refer to distinct paintings by
  Botticelli, Bouguereau, or Cabanel. Resolution must use canonical subject IDs,
  creator/relationship facts, and chronology context rather than title alone.
- Chronology entries currently store their entire ordering item list as one
  `ordering` question. They have no structured date or comparison context, so
  automatic cross-question combinations cannot yet be generated safely.

The paintings chronology alone has six authored three-item sets covering 18
distinct work labels. If those works are linked to canonical entries and
verified as comparable by creation date, the pool can produce up to
`C(18, 3) = 816` distinct three-work selections instead of only the six authored
sets. This is an upper bound before excluding reused presentations, repeats,
uncertain dates, or sets that are too easy or too hard; it illustrates why the
affinity and date checks are essential.

These figures are a discovery audit, not a merge instruction. Matching answer
text is a candidate link; homonyms and similarly named works must remain
separate unless the underlying entity is verified.

## Subject registry migration

The canonical bank now uses schema version 4. At the initial subject migration checkpoint, it contained 1,540 subject records
and all 1,444 authored question entries then active referenced at least one subject. The
first pass created subjects from verified image facts and creator/franchise
relationships, plus question-scoped anchors where identity was not confidently
resolved. Seventeen question anchors that duplicated an existing person or the
Montreal city record now share the canonical subject, with aliases and question
provenance retained. All existing question text, presentations and reviews are
preserved.

Twenty painting subjects now have source-backed `artwork.creation` facts with
year bounds and precision, including three distinct paintings titled *The
Birth of Venus*. Seventeen legacy painting chronology labels now reference
canonical work subjects. The old unqualified *La Naissance de Vénus* item stays
ambiguous because its label does not identify the artist. One bad inherited
creator role was corrected: Raimond Spekking remains the photograph credit, and
Alexandre Cabanel is the painter. The Franco-Belgian comics chronology is now a
pilot affinity pool: all 15 distinct series or character subjects have sourced
`comics.first_appearance` facts, and four unresolved chronology stubs were
replaced by canonical series identities. A further 24 comic, superhero, and
architecture chronology occurrences were linked to existing subjects. The
repository generator selects verified subjects by taxonomy and comparison
context, rejects overlapping dates, and can produce the appropriate chronology
prompt. Two demo video-game ordering questions had inherited the comic chronology
package ID; they now have separate console and video-game pool IDs and `gaming`
subject tags. The host setup flow does not yet expose subject-first package selection.

The repository generates orderings only from structured, comparable chronology
facts. All 119 authored ordering presentations have been removed from active
play and preserved in `review-backups/chronology-static-sets-archived-2026-10-29.json`.
The 35 verified subject facts currently support two dynamic contexts: painting
creation (20 works) and comic first appearance (15 series). Unsupported static
sets and 295 unresolved chronology stubs were archived or pruned rather than
left as fixed questions without standalone sourced components.

The content-audit cleanup merged six exact duplicate painting-identification
pairs, removed 11 demo-only questions, retired 30 test-labelled presentations,
consolidated 33 duplicate question anchors and linked 12 more to verified
subjects, and pruned 13 unreachable subjects. Their source
records, answers, explanations, IDs and retired presentations are preserved in
`review-backups/questions-excluded-and-merged-2026-10-29.json`; the pre-change
bank is snapshotted alongside it. Fourteen test presentation IDs remain only as
legacy aliases on playable records.

## Migration sequence

1. Continue resolving question-scoped subject anchors and chronology labels into
   canonical identities. Keep historical categories as provenance, not as the
   live taxonomy. The current taxonomy is a first-pass hierarchy from existing
   topic labels plus verified subject type and relationship data.
2. Add sourced chronology facts to the remaining affinity pools, each with its
   own comparison context. Never infer absolute dates from an old order alone.
3. Review additional entity merges while preserving aliases, question content,
   presentations, accepted answers, media and review history.
4. Add dynamic subject-first package selection to host setup. Select a subject
   query first, then one compatible format for the package, then distinct
   eligible questions. Random format means one format chosen once per package.
5. Keep old package/category identifiers as import and review aliases until
   migration checks show they are no longer needed.

## Guardrails

- Subject filters support both broad tags and specific descendants, and entries
  may match multiple branches.
- Chronology pools require a shared comparison context and enough distinct
  entries. Broad tags alone never make a pool comparable.
- If a pool is too small for the requested package, report the available count
  or choose a different compatible pool; never duplicate entries or silently
  mix formats.
- Migration is repeatable and writes a pre-change bank snapshot before editing.
- Preserve provenance so each migrated fact can be traced to an authored source
  list or a verified source.


## User-reviewed subject batch 01 (2026-10-30)

The first 16 candidate pairs were reviewed in the existing Drive spreadsheet. Eight same-entity pairs were consolidated under their verified subject entries: the Nile, Bird in Space, Mount Fuji, Van Gogh’s *Sunflowers* entry point, Versailles, Professor Tournesol, the Pantheon in Rome, and Michelangelo. All question content and presentations were retained. For *Sunflowers*, the flower-identification prompt and artwork-identification prompt both remain available under the shared entry point.

The Medusa mythological figure and Caravaggio painting, and Victor Hugo’s *Notre-Dame de Paris* and the cathedral, remain distinct subjects with explicit relationship links. A Cairo/Nile fact repeated in two question records was consolidated into one record; both multiple-choice presentations, alternate wording, review records, and legacy IDs were retained. No question presentations were deleted. The bank now has 1,443 authored question records, 1,532 subjects, and 854 question-scoped anchors. Backup: `review-backups/questions-before-subject-review-batch-01-2026-10-30.json`.


## Broader question-duplicate pass (2026-10-30)

The initial indexed screen included all 1,443 question records as input, but compared only 9,234 candidate pairs. A reproducible follow-up scored every pair in the then-current 1,442-question bank and flagged 116 high-signal candidates. Following the media review below, the current 1,441-question bank was rescanned across all 1,037,520 pairs and flagged 114 candidates using shared answers (after article normalization), shared subjects, or very high prompt overlap. Every pair is screened under those signals, but candidates still need semantic adjudication; generic image prompts without informative written clues remain a limitation. Gotham remains one canonical written-answer question after its redundant multiple-choice presentation was removed, and its legacy ID/review history remain for traceability. The user's reviewed rows 5–11 remain classified as related. A Frodo pair with film and book contexts is related, not an image duplicate. The full current candidate screen is reproducible with `build/audit-question-duplicate-all-pairs.py` and saved to `QUESTION-ALL-PAIRS-CANDIDATES.csv`.

The active bank now contains 1,441 questions, 1,531 subjects, and 853 question-scoped anchors. The full Gotham source records are archived in `review-backups/questions-gotham-duplicate-pair-archived-2026-10-30.json`; snapshots before the Gotham and Ottawa edits are stored in `review-backups/questions-before-gotham-presentation-prune-2026-10-30.json` and `review-backups/questions-before-ottawa-image-duplicate-merge-2026-10-31.json`.

## Image-based duplicate check (2026-10-31)

The reviewer had marked seven pairs as duplicates based on text alone. The source export's `Image` field and the canonical presentation data show that only Ottawa's two charade/rebus records both have image assets. The user asked to keep the goose image; the goose is in `geo-capitales-20261010-06-v2` (`ottawa.png`). That entry remains active, while `cv-354c48d6502bb8ccd12c` is archived and removed from the canonical bank. The other six pairs—Nile, Rapa Nui, Frodo, Nymphéas, Versailles, and the Pantheon—include a text-based question on at least one side, so they are classified as related and both questions remain. The source rows and media determinations are documented in the Drive review sheet and `migration.json`.
