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

The canonical bank now uses schema version 3. It contains 1,899 subject records
and all 1,580 authored question entries reference at least one subject. The
first pass created 643 subjects from verified image facts and creator/franchise
relationships, 943 question-scoped anchors for records without a confidently
resolved entity, and 313 chronology-item subjects. Six repeated image-fact
identities now share a subject record while their authored questions and review
history remain intact. Four chronology labels have multiple candidate paintings
and are explicitly marked ambiguous; 309 more labels remain unresolved pending
identity/source enrichment. This does not yet generate larger chronology sets.

## Migration sequence

1. Continue resolving question-scoped subject anchors and chronology labels into
   canonical identities. Keep historical categories as provenance, not as the
   live taxonomy. The current taxonomy is a first-pass hierarchy from existing
   topic labels plus verified subject type and relationship data.
2. Add typed chronology facts with a comparison-context key, sortable value,
   precision, and source/provenance. Never infer absolute dates from order alone.
3. Review entity merges, preserving stable aliases, all authored questions,
   presentations, accepted answers, media, and review history.
4. Convert legacy ordering lists into affinity constraints and subject facts.
   Where an exact date is not available, preserve only verified relative order
   inside its compatible context; do not invent dates.
5. Generate packages dynamically: subject query first, then a compatible
   package format, then a set of distinct eligible entries. Random format means
   choose one compatible format per package and keep it constant for that
   package.
6. Keep old package/category identifiers as import and review aliases until
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
