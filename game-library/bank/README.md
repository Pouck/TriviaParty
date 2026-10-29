# Question bank

`questions.json` is the authoritative question bank (schema version 3). It
separates canonical subjects from authored questions, independent of game
packages. Do not rebuild it from package ZIPs.

The root `subjects` collection stores reusable subject identities: works,
characters, people, places, events, concepts, and chronology items. Each subject
can have aliases, hierarchical `tagIds`, typed relationships, verified facts,
chronology evidence, and source/provenance links. `taxonomy` defines the tag
hierarchy and labels.

Each authored question owns:

- A stable `id` and all historical `legacyIds`.
- `subjectIds`, linking the question to one or more canonical subjects. The old
  `topics` strings remain as migration provenance and compatibility metadata. Questions
  about the same subject from different angles can share a subject ID while
  retaining their distinct authored wording and reviews.
- Shared prompt, accepted answers, explanation and common content fields.
- `presentations`: authored play variants, such as multiple choice, direct answer,
  picture identification or progressive clues. Presentation content contains only
  its format and overrides of shared content. Buzzer/written projections of a
  suitable direct question are generated at play time.
- `legacyReviews`: the original reviews, including different presentation ratings.
  Ratings that disagree are retained separately instead of being overwritten.

`media/` contains images addressed by content hash; shared images are stored once.
`migration.json` records the consolidation and original IDs. No original IDs or
presentations were discarded. Homonyms such as the novel and cathedral named
Notre-Dame de Paris remain separate questions.

Progressive image-identification presentations authored from the existing photo
collections are listed in `IMAGE-QSJ-MEDIA-CREDITS.json`; their present coverage
and remaining image needs are tracked in `IMAGE-QSJ-COVERAGE.md`.

Image-identification questions retain their source `imageFacts`; the subject
registry also stores those facts for cross-format selection. Facts use explicit
roles such as `painter`, `sculptor`, `architect`,
`depicted_person`, `actor`, `location`, or `media_creator`. A media creator is the credited maker of
the image file and must not be assumed to be the creator of the depicted work.
Only verified facts are copied into the subject registry; unknown architect,
actor, country, and date fields are left absent for later enrichment. A media
creator remains distinct from the creator of the depicted work. `identityStatus`
marks question-local anchors and unresolved chronology labels so they are not
mistaken for verified subject identities.

Legacy chronology questions are still retained for compatibility. Their
`subjectIds` reference reusable chronology subjects, and each subject retains
`chronologyEvidence` from the authored ordering lists. Ambiguous title matches
remain unresolved with candidate IDs. The data does not yet invent absolute
dates or combine incompatible comparison contexts; chronology pools can grow
once subjects have verified sortable facts such as creation, publication, or
event dates.

## Authoring and review

When adding content, identify the canonical subject first. Attach an authored
question to that subject using `subjectIds`; preserve multiple question angles
as separate question records where their wording or answer differs. Do not
merge subjects by answer/title text alone. Distinct works with the same title
remain separate when their creators or identities differ. Use chronology facts
only with an explicit comparison context and a verified source.

Run `python build/prepare-question-review-sampler.py` from the project root. The
sampler reads only this bank and shows one review card per entry, with a play
presentation selector. Review exports use `question-review-sampler-v2`, preserve
legacy reviews, and accept older v1 exports through the legacy ID mapping.

The Android APK embeds this bank directly. At runtime the app creates category
views in memory for browsing and assembles packages for games. Legacy package
metadata is retained as a compatibility view, not the question source.

`game-library/current/`, its ZIPs, source mirrors and old inventory are historical
import/export artifacts. They remain available for compatibility and migration
verification; they no longer feed the sampler or bundled question storage.
The old package builders/review revision scripts operate only on those artifacts.
They must not be used to author the canonical bank.

The one-time import is `build/canonical_question_bank.py`; it refuses to overwrite
an existing canonical database. `build/consolidate-question-presentations.py`
contains the reviewed identification merges. Future merges must preserve aliases,
all presentation content, and all review history in the surviving entry.
