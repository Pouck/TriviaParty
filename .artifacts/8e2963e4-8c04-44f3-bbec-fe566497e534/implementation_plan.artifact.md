# Implementation Plan — Trivia Party Enhancements (Cast Duplicates, Winner Music Sync, Random Image Reveal, & Multi-Mode Roadmap)

This plan outlines targeted improvements for Cast device deduplication, winner music synchronization, randomized image reveal modes for Image-QSJ questions, and a roadmap for multi-mode question authoring (artist vs. painting, city vs. country).

## User Review Required

> [!NOTE]
> No breaking changes are introduced. All existing unit tests and Node browser tests will be maintained and kept green.

## Proposed Changes

### Cast & Network Layer

#### [MODIFY] [GoogleCastController.kt](file:///C:/Users/pierr/AndroidStudioProjects/TriviaParty/app/src/main/java/com/example/triviaparty/cast/GoogleCastController.kt)
- Filter MediaRouter route discovery to deduplicate identical physical TV devices (matching by device name or ID) so the living room TV appears only once.

### TV Receiver & Display

#### [MODIFY] [receiver.js](file:///C:/Users/pierr/AndroidStudioProjects/TriviaParty/app/src/main/assets/tv/receiver.js) & [receiver.css](file:///C:/Users/pierr/AndroidStudioProjects/TriviaParty/app/src/main/assets/tv/receiver.css)
- For `GAME_ENDED`, trigger winner audio immediately and add a subtle CSS fade-in delay (approx. 500ms) on winner text display so the music begins before the winner names appear.

### Question Bank & Reveal Logic

#### [MODIFY] [CanonicalQuestionBank.kt](file:///C:/Users/pierr/AndroidStudioProjects/TriviaParty/app/src/main/java/com/example/triviaparty/data/CanonicalQuestionBank.kt) / [QuestionBankRepository.kt](file:///C:/Users/pierr/AndroidStudioProjects/TriviaParty/app/src/main/java/com/example/triviaparty/data/QuestionBankRepository.kt)
- When materializing Image-QSJ (`GuessWho`) questions, randomize the active image reveal mode (`PIXELATE`, `BLUR`, `SHUFFLE`, `UNCOVER`) per session/draw rather than keeping it static.

## Verification Plan

### Automated Tests
- Run `:app:testDebugUnitTest` to verify all Kotlin unit tests pass.
- Run node tests `node --test app/src/test/browser-player.test.cjs app/src/test/judge-browser.test.cjs cast-receiver/receiver.test.js` to verify TV display and player behavior.

### Manual Verification
- Deploy to Pixel 7 Pro and verify:
  1. Cast device list shows each TV uniquely without duplicates.
  2. Winner page starts music before winner text appears.
  3. "Peintures célèbres" Image-QSJ questions pick a random reveal mode each session.
