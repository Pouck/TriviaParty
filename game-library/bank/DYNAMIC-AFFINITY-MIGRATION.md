# Dynamic question selection and chronology

## Intended model

The bank stores reusable subject entries. Each entry can have hierarchical subject
tags, links to related entries, structured facts, and one or more authored play
presentations. A package is generated from a subject query and a selected format;
the format does not create a separate subject or duplicate entry.

For chronology, entries need a comparable, structured value and a comparison
context. A comparison context distinguishes, for example, an artwork's creation
from its first public exhibition, or a person's birth from a work's publication.
The generator selects a compatible affinity group, draws distinct entries from
it, and constructs an ordering question. It must not combine values that only
look comparable because they share a broad tag such as `Arts` or `History`.

One entity can therefore support several angles: a painting may have image
identification, title/artist questions, and a creation-date chronology fact. A
historical event may have a buzzer or written question and a chronological fact.
The entity is stored once; format-specific prompt content remains attached as a
presentation where the question wording or mechanics truly differ.

## Initial inventory (2026-10-29)

- Canonical bank: 1,580 entries.
- Ordering presentations: 124 entries across 23 legacy categories.
- Those orderings contain 357 distinct normalized item labels.
- 88 item labels already exactly match answers in other entries (97 occurrences,
  pointing to 101 non-ordering entries before duplicate-entity consolidation).
- Several labels point to multiple existing entries. Examples include *Les
  Époux Arnolfini*, *La Naissance de Vénus*, *La Jeune Fille à la perle*, and
  *Le Baiser*. These need entity-level consolidation and presentation/review
  preservation, not another chronology-specific copy.
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

## Migration sequence

1. Define canonical hierarchical tags, aliases, and typed relationships (for
   example, `creator_of`, `member_of_franchise`, and `depicts`). Keep historical
   categories as provenance during migration, not as the live taxonomy.
2. Define typed chronology facts with a comparison-context key, sortable value,
   precision, and source/provenance. Link each ordering item to a canonical entry
   or create a reusable entry when no matching subject exists.
3. Review candidate entity merges, preserving all stable IDs, authored
   presentations, accepted answers, media, and review history.
4. Convert legacy ordering lists into affinity constraints and chronology facts.
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
