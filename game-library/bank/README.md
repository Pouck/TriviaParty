# Question bank

`questions.json` is the authoritative question database. It contains one entry per
question, independent of game packages. Do not rebuild it from package ZIPs.

Each entry owns:

- A stable `id`, all historical `legacyIds`, and one or more topic tags.
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

Image-identification entries may also include `imageFacts`: a reusable subject
type, subject/work title, optional franchise, source-linked facts, and source
URLs. Facts use explicit roles such as `painter`, `sculptor`, `architect`,
`depicted_person`, `actor`, `location`, or `media_creator`. A media creator is the credited maker of
the image file and must not be assumed to be the creator of the depicted work.
Only verified facts are stored; unknown architect, actor, country, and date
fields are left absent for later enrichment. The Android model retains these
facts for future question-angle generation. A question's `explanation` can
provide verified supplementary information on the answer reveal.

## Authoring and review

Edit an existing entry or add a presentation under it when the same question can
be played with different amounts of information. Add a new entry only for a new
question. Equal answers alone do not imply equal questions.

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
