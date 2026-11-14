# CURRENT SESSION HANDOFF — 2026-10-31 (Trivia Party Chromecast launch failure)

Workspace: `C:\Users\pierr\AndroidStudioProjects\TriviaParty`

## Active task: replace temporary Cast receiver hosting with a viable setup

- User reports the latest cast attempt still leaves the TV showing Google's **“Something went wrong”** page. The user's most recent correction: **Tailscale was already agreed to be non-viable; do not return to relying on Tailscale/Funnel or a computer-side relay.** User expects normal casting to work from the phone without Android Studio or a computer acting as infrastructure.
- I acknowledged that I had backslid to the Tailscale relay and committed to investigate a durable receiver host independent of Tailscale. Do not ask the user to retry casting until there is a concrete change.
- Important platform constraint to verify/communicate: a custom Google Cast Web Receiver is loaded by the TV from the receiver URL registered to the Cast app ID. The sender APK and the Cast receiver page have separate delivery paths. Current receiver code sends game state over Cast messages, but receiver page/assets are not in the APK served directly to the TV. A static HTTPS host may be required; daily use can still be phone-only if that static host is independently deployed and media/data delivery is addressed. Do not claim the system is self-contained until tested.
- `gradle.properties` configures `castReceiverApplicationId=6CA3BAF3`.
- `cast-receiver/README.md` currently says this ID is Published/unlisted, but explicitly ties its receiver URL to a Tailscale Funnel hostname and describes keeping the computer/local relay running. This is only temporary setup and is not acceptable as the final architecture. README should be corrected once the permanent hosting decision is implemented.
- Another app ID `DFCF5F96` is unpublished and unused. Sender package is `com.example.triviaparty`. Registered device serial recorded in notes: Vizio Cast serial `LTMWXHKU4252953`, Console Ready for Testing.
- Cast launch logs on Pixel: `launchApplicationWithOptions` for `6CA3BAF3`, then `onApplicationConnectionFailed` with sender status `2472` ~0.8 seconds later. No app crash. Status code not mapped to an authoritative cause.
- Temporary Tailscale URL previously used: `https://desktop-pierre.tail0f0cb5.ts.net`, Funnel to loopback `127.0.0.1:18081`, with local relay forwarding selected phone media URLs from `http://192.168.2.13:8080`. Receiver assets returned HTTP 200, but Cast still failed with 2472. This is evidence that merely making this relay reachable did not fix the issue.
- Current browser UI was on Tailscale Machines, not Google Cast Console. Do not conflate that with the user authorizing Tailscale as the solution.
- Potential next investigation: inspect Cast Console's exact Web Receiver URL and deployment/registration settings, then choose durable public HTTPS hosting (e.g. repo-backed static hosting or an already configured hosting project) and point the same published app ID there. Assess whether the repo's private GitHub remote can support the desired hosting and what credentials/host configuration exist. Do not push unrelated existing workspace modifications while deploying; the working tree contains extensive outstanding app and question-bank edits.
- Preserve user's preference to drive this task without repeatedly asking for authorizations or sending them through Android Studio. No permission is needed for read-only diagnosis or local implementation. Before any public deployment, make the concrete URL/configuration reviewable and follow applicable service/credential constraints.

### 2026-10-31 continuation

- Google Cast's official registration guide confirms that a published Custom Web Receiver URL must use HTTPS, while resources loaded by the receiver may use HTTP. This makes a static HTTPS receiver plus direct LAN media from the phone a plausible computer-free design. Source: https://developers.google.com/cast/docs/registration.
- Updated `app/src/main/assets/tv/receiver.js` so receiver image URLs retain the phone's LAN HTTP origin and receiver audio uses the `joinUrl` origin. This removes the receiver-side dependency on an HTTPS relay for game media. This is an implementation hypothesis only; it has not been built or tested on the Vizio. Do not ask the user to retry yet.
- The registered Cast Console URL and publishing settings remain unverified. Read-only browser inspection could not start because the computer-use approval timed out. No Firebase, GitHub CLI, or Wrangler deployment tool/configuration was found, and a read-only `git ls-remote` attempt failed at DNS/network startup. Do not assume a hosting account, repo visibility, or Pages entitlement.
- `cast-receiver/README.md` now marks the Tailscale/Funnel setup as deprecated and says a durable HTTPS URL must be configured before retrying. No public deployment, Cast Console edit, build, device install, or test was performed.
- Next: get the exact current receiver URL/plan access and select a host that can publish only the receiver bundle (never the full private game library). Then review the resulting URL and static asset list, update the Cast Console registration for `6CA3BAF3`, build/install the sender as needed, and physically verify launch plus direct phone media. Preserve unrelated working-tree changes; don't deploy/push the whole repository.

## Current workspace changes / relevant files

- Modified Cast files include `app/src/main/assets/tv/receiver.js`, `app/src/main/java/com/example/triviaparty/MainActivity.kt`, `app/src/main/java/com/example/triviaparty/cast/GoogleCastController.kt`, `app/src/main/java/com/example/triviaparty/ui/cast/GoogleCastDeviceList.kt`, `app/src/main/res/values/themes.xml`, `gradle/libs.versions.toml`, and `cast-receiver/README.md`.
- Other modified/untracked files are from ongoing question-bank cleanup and reviews. Do not revert or include those in a Cast-only commit/deployment.
- Project Git remote: `https://github.com/Pouck/TriviaParty.git`.
- ADB device noted in prior workflow: Pixel 7 Pro, serial `adb-2B021FDH300B81-JSzzEA._adb-tls-connect._tcp`; Android package `com.example.triviaparty`.
- The 2026-10-31 continuation changed `app/src/main/assets/tv/receiver.js` to try direct phone-LAN image/audio delivery. This remains unverified on-device. An older attempt to start a logging copy of the relay found port 18081 occupied; do not assume that second process started. Avoid restarting Funnel or asking the user to use the relay.

## Previous session handoff — 2026-10-29 (Trivia Party TV audio / image reveal)

Workspace: `C:\Users\pierr\AndroidStudioProjects\TriviaParty`

## Immediate state

- User reported on the previously installed build: Cast startup error is gone, but in-game music stops/plays only on alternating questions and the TV repeatedly shows a “son désactivé” notice; validation sounds after the first question do not play, while final-page music does. Image pixelation became choppy, flashes black, reveals too quickly, and degrades further across successive questions.
- New receiver/layout changes are in the workspace and the latest debug APK built successfully, but **the latest APK was not installed on the Pixel**. The attempted elevated ADB install was not executed because automatic approval review failed with: `Selected model is at capacity. Please try a different model.` This is a review-service capacity issue, not an unsafe-action rejection. Do not bypass that review. Retry the approved ADB workflow when review is available.
- ADB discovery succeeded immediately before the install attempt. Connected device: `adb-2B021FDH300B81-JSzzEA._adb-tls-connect._tcp` (Pixel 7 Pro, wireless ADB).
- Latest APK: `C:\Users\pierr\AndroidStudioProjects\TriviaParty\app\build\outputs\apk\debug\app-debug.apk` (617,125,674 bytes; built 2026-10-29 around 11:35).
- User is restarting this long thread because typing into the thread input is laggy. This note is the current task state; historical bank work below is retained for context but is not the active task.

## Changes included in the latest build (not yet installed/tested on device)

- `app/src/main/assets/tv/receiver.js`
  - Separated answer-sound stopping from soundtrack stopping so validation cues no longer tear down music.
  - Reuses soundtrack `Audio` players across questions; primes Anitra's Dance and Cat's Theme when the Cast sound check runs; initializes the audio origin before the first game-state message; uses explicit MP3 URLs for sound check and musical validation cues.
  - Kept musical answer chimes independent of the global setting that silences dialogue clips. Dialogue clips remain governed by that setting.
  - Music playback errors no longer clear the queued answer-sound sequence or globally disable playback.
  - Pixelate rendering now uses the sampler-sized 1,000-pixel canvas and its approved curve (start sample width 4; transition at 65%; sample limit 60; same eased tail); it uses a fixed offscreen buffer, avoids per-frame clears/resizing, and caps resolution below full until explicit answer reveal.
  - Prevents images that finish loading after their question is replaced from starting detached reveal animation loops. Immediate cache-hit rendering now starts only after its wrapper is attached.
- `app/src/main/assets/tv/receiver.css`: compact image-QSJ layout (80% image / 20% details), tight image-to-prompt and prompt-to-answer spacing, bottom room under answer, and body/panel shifted upward. Preserve these unless user reports otherwise.
- `cast.html` and `display.html` use cache-busting query `cast-audio-layout-7` so a new Cast receiver loads updated assets.

## Verification and next actions

- `node --check app/src/main/assets/tv/receiver.js` passed.
- `git diff --check` passed (only line-ending notices).
- `.\gradlew.bat :app:assembleDebug --offline` succeeded. No automated tests were run.
- Next: when the ADB install approval review is available, install the APK with the project device skill workflow (`.agents/skills/triviaparty-android-device/SKILL.md`), force-stop and relaunch `com.example.triviaparty/.MainActivity`, restore `adb forward tcp:18080 tcp:8080`, then have user start a game and reconnect/refresh Cast. User's browser already has `http://127.0.0.1:18080/play` and `/tv` open. Debug server pages respond only once the app is hosting a game.
- After user tests, focus first on whether music plays on every question and validation chimes after the first. Then check the reveal on a longer run for black flashes/late-load regressions and rate against the sampler. Do not claim the Cast startup issue is resolved until tested on TV.
- Related skill: `.agents/skills/triviaparty-android-device/SKILL.md`. Use terminal + ADB; no phone mirroring or IDE menu driving.
- Preserve unrelated existing modifications and historical notes. Do not reset/revert the working tree.

---
# Session handoff - 2026-10-27 (latest update)

## Latest work - BD and manga image expansion

- Expanded the canonical image-QSJ bank to **415 presentations** and **399 unique images**. BD is now **17**, manga **53**; cartoon remains empty and the wider art/architecture coverage work remains incomplete.
- Added single-character official character art from Tintin.com (Tintin cast), Asterix.com (Astérix, Obélix, Idéfix, Panoramix, Falbala), ONE PIECE.com (Straw Hat crew), and Dragon Ball Super’s official site. Visually reviewed selections contain no title text or second character. Rejected the Thomson and Thompson pair portrait and the Lucky Luke publisher group art for individual-character prompts.
- Attached the suitable images to existing entries for Tintin, Milou, Captain Haddock, Astérix, Obélix, Panoramix, Luffy, and Son Goku. Added new canonical entries for remaining targets while retaining previous reviews and IDs.
- Added verified image facts/explanations where available and preserved official-source pages/direct image URLs in `game-library/bank/IMAGE-QSJ-MEDIA-CREDITS.json`. Rights-reserved images are marked for private local gameplay only; do not redistribute.
- Updated `game-library/bank/IMAGE-QSJ-COVERAGE.md`. Sampler regenerated at `build/image-qsj-sampler/sampler.html` (full path: `C:\Users\pierr\AndroidStudioProjects\TriviaParty\build\image-qsj-sampler\sampler.html`). Refresh the already-open sampler tab to see the new set.
- No automated tests were run. No commits or pushes. The wider image-bank cleanup and category expansion are still in progress.

- Follow-up: added 15 visually reviewed Detective Conan portraits from the official Shogakukan portal plus one Billy the Kid portrait from Dargaud. Excluded the Detective Boys group portrait, Calamity Jane art with a second silhouette, and Sailor Moon character cards because the prominent text would spoil reveals. Current sampler path remains `build/image-qsj-sampler/sampler.html`; refresh the existing browser tab to see the additions. Credits and private-local-use-only terms are recorded. New-entry media and credit checks passed; no automated test suite was run.
- Follow-up: added nine single-character full-body portraits from the official Jujutsu Kaisen site, raising manga coverage to 53 and sampler size to 415 presentations / 399 unique images. No test suite was run.
- Follow-up: replaced the five black-and-white Astérix character images with full-color portraits (Astérix and Falbala from Salvat; Obélix, Idéfix and Panoramix from reviewed full-color comic art). Checkerboard preview backgrounds were removed from the latter assets while retaining the character art. This addresses the white-until-late blur reveal. Sampler counts remain 415 / 399. Refresh `build/image-qsj-sampler/sampler.html`; no test suite was run.

---

## Latest work - image sampler cleanup and Plus usage question

- Workspace: `C:\Users\pierr\AndroidStudioProjects\TriviaParty`. Do not assume the older handoff sections below describe current bank counts; check current files/status.
- User asked to complete the full image-bank overhaul without waiting for further approvals. Visually audited the original 272-image contact sheets and updated canonical `game-library/bank/questions.json`.
- Added `build/revise-image-bank-visual-audit.py`. It uses already-downloaded official Disney art to replace 7 Disney character images and removes 60 unsuitable image presentations (cosplay, statues, parade/theme-park depictions, unrelated subjects, etc.). Where questions had other presentations, those were kept. 43 image-only questions were retired. Revision history and backups are present.
- Rebuilt sampler and contact sheets. Current sampler: `build/image-qsj-sampler/sampler.html` (full path: `C:\Users\pierr\AndroidStudioProjects\TriviaParty\build\image-qsj-sampler\sampler.html`). Current: 210 unique sampler images, 219 image-reveal presentations, all four modes (BLUR, PIXELATE, SHUFFLE, UNCOVER), continuous reveal at 12/16/24 seconds. Do not alter the user-approved pixelate curve or reveal timing without request.
- Structural audit: 1,300 questions, 1,627 presentations, 210 unique sampler images; no missing sampler image files/credits or duplicate presentation IDs. 19 missing credit entries belong to non-image-reveal legacy presentations and are outside the sampler.
- Confirmed directly that the Eiffel Tower source includes base and spire, and Abraham Lincoln portrait includes his full head and face. Some apparent blank webp tiles in contact sheets are a contact-sheet rendering limitation; e.g. Iron Man's actual webp is a clear movie still. Do not remove remaining Marvel items based only on a blank contact-sheet tile.
- User flagged DC/Marvel choices as sometimes obscure or non-iconic. Latest cleanup removed Green Lantern cosplay but did not comprehensively revise the remaining secondary-hero choices. Possible follow-up if user asks. Keep broad policy: recognizable canonical character/movie/comic image, no cosplay or third-party rendition.
- Eiffel/Lincoln complaint may have referred to reveal state or an earlier sampler; source images themselves are complete. Contact sheets are `build/image-qsj-sampler/audit/sheet-01.jpg` through `sheet-14.jpg`.
- Answered user's Plus usage question for Codex in Android Studio: no automatic quality degradation from session duration; Plus usage is limited and shared across local IDE and cloud Codex/Work, and consumption varies with model/task/context/tools. Limits may reset on a schedule. Current usage dashboard is authoritative. Official source: `https://learn.chatgpt.com/docs/pricing`. I cannot inspect the user's account quota.
- No tests were run for this image-only work. No commits or pushes. Many unrelated files are modified/untracked; do not reset/revert them. Check `git status --short` before continuing.

---

﻿# Session handoff — 2026-10-24

Project: `C:\Users\pierr\AndroidStudioProjects\TriviaParty`
Baseline Git commit: `6872482` (`Checkpoint current project before question bank redesign`). No new changes have been committed or pushed.

## Latest state — canonical storage redesign (supersedes package-storage notes below)

- User corrected the earlier approach: one stored question must own multiple play presentations; old source packages must not remain the database. Implemented this change, rather than only hiding gameplay duplicates.
- Authoritative source is now `game-library/bank/questions.json` (schemaVersion 2). It contains **1189 unique entries**, preserving all **1408 legacy IDs/authored presentations** and **1106 historical reviews**. Shared content is stored once; format-specific overrides are nested under each entry. Shared images live in content-addressed `game-library/bank/media/` (232 files).
- Migrated 43 exact/curated duplicates plus 176 further audited identification variants. Keep homonyms separate (e.g. Notre-Dame cathedral/novel and Mars planet/god). Do not apply a universal same-answer merge.
- Legacy `game-library/current` ZIPs/source trees are now historical compatibility artifacts. Do not edit them to change the bank. Read `game-library/bank/README.md` for authoring/schema details. The one-time importer refuses to overwrite the canonical file.
- Sampler generator now reads ONLY the canonical bank. Output path remains `build/question-review-sampler/sampler.html`. Header is “Question bank review”; count is **1189 unique questions**. Each card has a presentation selector; changing it keeps the same entry/review. Buzzer/written projections are created dynamically. Total selectable projections: 3151, nested under the 1189 entries.
- Sampler exports `question-review-sampler-v2`, accepts old v1 review IDs, preserves presentation review history and conflicting old ratings, and persists shared reviews. Different historical ratings are not silently collapsed into one new rating. General deferred comments and Odyssey category note remain pending.
- Android embeds the canonical bank directly via an assets source set. `CanonicalQuestionBank.kt` creates transient category views; `QuestionBankRepository.installCanonicalBank` and `GamePackageRepository.installBankViews` overlay legacy compatibility catalogs. Old packages no longer provide the built-in question content. New media is copied to `files/game-packages/canonical-bank/images` and served through the existing safe media route.
- Canonical bank loaded successfully on connected Pixel 7 Pro. Latest debug APK installed; cold launch, random draw, game preparation into host lobby, player/TV HTTP pages and canonical media HTTP endpoint passed. Phone is in a prepared test lobby.
- Verification: all **140 Android unit tests** passed; all **69 Node browser/judge/TV tests** passed; debug APK built. `python build/verify-canonical-bank.py` audits every preserved source field/media/review. `node build/verify-canonical-sampler.cjs` performs real headless Chrome checks of count, QCM/direct/clue switching, shared review persistence, legacy import/export (including conflicting ratings), and actual 390px layout. Both passed.
- Relevant new sources: `build/canonical_question_bank.py`, `build/consolidate-question-presentations.py`, `build/question-review-sampler.cjs`, `build/verify-canonical-bank.py`, `build/verify-canonical-sampler.cjs`, and `CanonicalQuestionBankTest.kt`. Existing sampler generator, repository, MainActivity, Gradle asset config and README were updated.
- No commits or pushes. `.gradle-task/` remains local diagnostic cache, not for committing.

### Follow-up: repeated sampler formats

- User found duplicate “Réponses écrites” choices on question 15. Audit found 57 entries with repeated format labels caused by historical wording variants and QCM-to-text projections.
- Sampler now groups choices by question kind + answer mode, with one choice per play format. Prefer authored free-response wording over QCM-derived wording. Authored alternatives and all reviews remain unchanged in canonical storage.
- Question 15 now has only Buzzer, Choix multiples, Réponses écrites. All 1189 entries have zero repeated kind/mode choices; total selectable sampler formats is now 3021 (supersedes 3151 above).
- Regenerated sampler; migration preservation audit passed. No Android code changed in this follow-up.

### Follow-up: retry message after “Préparer la partie”

- User clarified the error was the host preparation connection/retry screen. Fixed premature failure display: initial DISCONNECTED during setup now shows loading; retry appears on actual error/timeout.
- Fixed GameClient reconnect ownership: each attempt cancels/replaces the old connection, clears stale snapshots, and old socket cleanup cannot clear a replacement. Disconnect captures/closes only its own socket. Cancellation is not reported as a connection error.
- Added `HostConnectionTest`: 12 immediate disconnect/reconnect cycles remain usable through HostStartGame and category introduction; an in-flight failed connection can be replaced by a working one.
- All **142 Android unit tests passed**; debug APK built and installed on Pixel 7 Pro. Live draw and Prepare reached host lobby successfully. Player/TV HTTP endpoints return 200. No user review/package data cleared.
- Current phone state: prepared test lobby with no teams. Start Game is intentionally disabled until a team joins (`PrivateHostDashboard.kt`, unlike the unused old LobbyPanel). Earlier automated taps on the disabled button did not indicate a networking failure. Do not claim the native Start button was verified to advance without a team.
- No commits or pushes.

### Latest review (export (3), 2026-10-24 13:06), maps and clue totals

- Applied `Downloads/question-review-feedback (3).json` (v2, 1189 canonical reviews, 31 comments) directly to canonical storage with `build/process-canonical-review-2026-10-24-1306.py`.
- Processed 30 individual comments; the existing Odyssey category difficulty/repetition note and three general deferred notes remain pending. Corrected requested prompts/distractors and four specific clue sets; removed flagged irrelevant/revealing pictures. Siren clues verified against Homer Odyssey 12 and Met Museum Greek depictions; URLs saved on the bank entry.
- Combined 10 more overlapping groups: five remaining identification pairs and five obsolete speed-race wrappers that now use ordinary multiple-choice presentations. Canonical count is **1179**, preserving all **1408 authored presentation IDs**. Speed-race presentations remaining in canonical data: zero. Do not merge the mythological Great Turtle with a marine turtle or other equal-answer homonyms.
- Full pre-edit canonical bank snapshot and raw review are in `review-backups/*2026-10-24-1306*`. `revisionHistory` in canonical JSON points to that snapshot; audit script now verifies original source preservation through that archive and checks latest positive ratings against reviewHistory. Historical legacyReviews are unchanged; current canonical `review` and `reviewHistory` preserve new annotations/ratings.
- Processed export: `Downloads/question-review-feedback-processed-2026-10-24-1306.json` and workspace backup. Sampler review-state refreshed. It now has **1179 unique questions / 3016 format choices**.
- Fixed missing sampler maps: the five mapChoice diagnostic questions use procedural diagrams instead of image files. Sampler now renders the map and all A–D markers, highlights the correct marker, and lists correct labels instead of raw coordinate objects. Screenshot verified at `build/question-review-sampler/canonical-sampler-map.png`.
- Added total clue counts to sampler clue sections, native private host dashboard, TV category intro and active question. TvState exports only clueCount, without future clues. Both TV receiver copies updated; remote Cast hosting not published.
- Added consumed-review acknowledgement to sampler loading: notes matching the processed download are cleared on refresh, while notes edited after that export remain saved. v1/v2 import/export and conflicting historical ratings still work.
- Verification: **142 Android unit tests** and **70 Node player/judge/TV tests** pass; debug APK built. Real headless Chrome sampler checks pass (maps, total unique count, no duplicate formats, review persistence/import/export and processed-note reconciliation). `python build/verify-canonical-bank.py` passes.
- Latest APK installation is still unconfirmed: wireless ADB transfer and package status checks stopped responding. Asked user to keep phone awake/unlocked on same Wi-Fi. Running exec sessions: install/relaunch `62817`, package status `6476`. Resume/poll those before starting another install. APK is ~307 MB because the embedded canonical offline images total ~263 MB. Do not report installed without success. No commits or pushes.

## User's active product direction

- Replace static 5–7 question source packages with game-time packages randomly assembled from the larger bank, selected by topic as before.
- Host can choose package question count (currently implemented with default 6).
- Announce one format per package, and balance formats across packages. Buzzer and written response should be interchangeable where the question supports it; multiple choice need not mean first response wins.
- Avoid semantic duplicates when different formats/package organization mask the same question.
- A generated package may contain at most one rating-1 (very easy) and at most one rating-5 (very hard) question. Either can be absent; do not exclude them from the bank.
- User also requested processing the newest sampler export, clearing processed individual comments and rating 0 while preserving all other ratings. Deferred general review comments should remain pending until the full review is submitted.

## Current local implementation and review edits

There are uncommitted changes to `DynamicPackagePlanner.kt`, `QuestionBankRepository.kt`, `GameSetupScreen.kt`, `GameServer.kt`, `MainActivity.kt`, `GameEvent.kt`, `HostScreen.kt`, a test, and question review revision scripts/data. Recent edits add a dynamic package planner, flexible response formats, semantic de-duplication, per-package difficulty-1/5 limits, and apply 16 specific sampler comments to question sources and generated archives.

Processed export saved at:
- `C:\Users\pierr\Downloads\question-review-feedback-processed-2026-10-23.json`
- Workspace copies: `review-backups/question-review-feedback-2026-10-23-processed.json` and `review-backups/question-review-feedback-2026-10-23-raw.json`

The 16 handled comments are cleared with their rating 0 flags; other ratings and deferred general comments are preserved. Earlier exports and review details are in the conversation history.

## Gradle diagnosis

- `gradle/gradle-daemon-jvm.properties` in the baseline explicitly has `toolchainVersion=25` and a Foojay URL for downloading JDK 25.
- Windows PATH resolves `java` to Oracle Java 8 (`1.8.0_511`). `JAVA_HOME` is unset.
- Android Studio 2026.1.4 has a registered JetBrains Runtime JDK 17 at `C:\Users\pierr\.jdks\jbr-17.0.14`.
- Gradle hangs during the JDK 25 download (the `.part` file remained 0 bytes). With daemon JVM criteria temporarily bypassed and JDK 17, Gradle starts, but offline setup fails because `org.gradle.toolchains.foojay-resolver-convention:1.0.0` is not cached. An online diagnostic also stalled on remote resolution in this environment.
- The diagnostic temporarily moved `gradle/gradle-daemon-jvm.properties`; it was restored. Confirmed tracked project settings are not modified by the diagnostic. No JDK 25 has been installed.
- Gradle tests/build are therefore not verified. Continue by deciding whether the project should keep JDK 25 and download it in the user's normal Android Studio/network environment, or change the project to use an installed JDK and remove/replace the Foojay dependency. Do not silently alter the checked-in runtime requirement.
- `.gradle-task/` is a local Gradle cache created for diagnostics; it appears untracked and should not be committed.

## Next steps

### Review update — 2026-10-24, later

- Read newest Downloads export `question-review-feedback (2).json` (1106 reviews, 95 comments). Original backed up in `review-backups/question-review-feedback-2026-10-24-raw.json`.
- Processed 94 comments (including 16 previously handled comments carried forward by the export). Removed irrelevant/revealing pictures, revised requested wording/logic, added host-visible explanations for deduction questions. Converted unrated/rating-0 “too easy” feedback to difficulty 1; preserved all existing 1–5 ratings and all general comments.
- One category-level Odyssey difficulty/repetition comment stays pending alongside deferred general review notes.
- Processed file in Downloads: `question-review-feedback-processed-2026-10-24.json`; workspace mirror in review-backups. Refreshed `build/question-review-sampler/sampler.html` using processed state; 1408 questions, no missing images.
- Added 30 curated shared concept groups (cross-topic and QCM/free-response duplicates). Sources and current ZIPs retain authored variants under shared conceptId. Planner deduplicates by concept across the entire game, ignores response class/choice labels for exact duplicates, and can hide authored QCM choices for buzzer/written presentation. Choice-dependent prompts and random-answer variants stay QCM-only. Equal answers alone do not imply duplicate facts.
- Fixed fallback package filling to prefer the largest remaining pool before balancing formats. Fixed voting integration test isolation to restore generated repository state.
- All 137 Android unit tests and 69 Node browser/judge/TV tests passed; debug APK built. Latest review/planner changes have NOT been installed on the phone. Existing phone package data also requires updated library import to gain concept IDs/content revisions.
- Durable edits: `build/process-review-2026-10-24.py`, `build/question-review-revisions-2026-10-24.json`, and existing revision application pipeline. No commits or pushes.

### Testing resumed — 2026-10-24

- Updated Android Studio at `C:\Program Files\Android\Android Studio2` bundles Java 25.0.3. Explicitly setting `JAVA_HOME` to its `jbr` folder allows Gradle to run with the checked-in Java 25 requirement unchanged.
- User `JAVA_HOME` and both Windows PowerShell/PowerShell startup profiles now select this Java. System Path still contains Oracle Java 8.
- Fixed `DynamicPackagePlanner.kt` compilation: GuessWho semantic key uses `acceptableAnswers.firstOrNull().orEmpty()` rather than nonexistent `answer`.
- `:app:testDebugUnitTest :app:assembleDebug` completed successfully. All unit test suites passed, including the five dynamic planner tests.
- Browser player, judge browser and Cast receiver Node tests: 69 passed, zero failures.
- Debug APK: `app/build/outputs/apk/debug/app-debug.apk`.
- Pixel 7 Pro subsequently connected via wireless ADB. Installed debug APK successfully and launched app. Live smoke test: generated six six-question packages, inspected varied announced formats, and prepared game successfully into host lobby. Player/TV pages and scripts returned HTTP 200 via ADB forward on localhost:8080. App remains in host lobby; multiplayer gameplay and audio/Cast validation remain pending.
- No commits or pushes performed.

1. Resume by reading this note and checking `git status` before making further changes.
2. Check planner/repository integration for compile issues, especially difficulty callbacks and semantic fingerprint behavior; current test run did not complete.
3. Resolve Gradle runtime/network setup or ask the user before changing the checked-in Java 25 requirement.
4. Once Gradle works, run the relevant build/tests and report verified status. Do not commit or push unless requested.

### Continuation — Pixel smoke test and permissions, 2026-10-24

- User resumed the on-device validation and confirmed the Pixel was connected. Normal sandbox `adb devices -l` could see the TLS device (`adb-2B021FDH300B81-JSzzEA._adb-tls-connect._tcp`), but `adb shell` failed with `adb_utils.cpp:315 Cannot mkdir '\\.android': Permission denied` because the managed sandbox could not access the ADB home directory.
- Elevated ADB wireless discovery found the Pixel at `192.168.2.13:40261`. Running `adb connect 192.168.2.13:40261` in that same elevated context restored shell access. Use the explicit serial `192.168.2.13:40261` for commands while that connection remains active. The host app's join sheet showed `http://192.168.2.13:8080/play`.
- Drew six packages and prepared a host lobby. Forwarded host port 8080; `/play`, `/play/player.js`, `/tv`, `/tv/display.js`, `/play/sound-sampler`, and `/tv/audio-credits` each returned HTTP 200.
- Opened the player page in Chrome on the Pixel. It displayed `Connecté à l’hôte`; submitted temporary team `CodexTest`, and the page changed to `En attente…` with 0 points. Host/player synchronization was not conclusively verified. After switching back, tapping the host start control showed `Partie terminée`, so gameplay was not verified. Audio playback and physical Cast remain unverified.
- Browser/app task navigation became confusing during the test and the Pixel ended on the launcher/home screen. No intentional repository files or personal data were changed during the device test. Nothing committed or pushed.
- User noted the machine setup is unchanged and the model changed; agree that the phone was connected. Do not ask the user to reconnect by default. Recheck `adb devices -l`; if sandbox ADB shell again fails on `.android`, use `adb mdns services` and the discovered `ip:port` in the same elevated context, then continue. The approval issue was due the managed sandbox boundary, not a changed phone setup.
- User asked about avoiding authorization prompts. Explained that “Approve for me” is only shown in some desktop/configuration surfaces and may be absent in this managed session; do not imply the option is universally available. Official guide: `https://learn.chatgpt.com/docs/sandboxing`. User is moving to another session; this note records context only.

## 2026-10-27 — image-bank expansion resumed

- The earlier assistant stopped after partial status updates; user challenged this. Continue the active image-bank overhaul instead of treating intermediate progress as completion.
- Replaced the Hong Kong flag image and group photos for ostrich, giraffe, horse, and pig in canonical `game-library/bank/questions.json`. Candidates were checked visually; the first ostrich candidate was a turkey and was rejected. Final sources and licenses are in `IMAGE-QSJ-MEDIA-CREDITS.json`.
- Downloaded and parsed Art & See’s 100 most famous paintings page. Its page describes a 100-entry fame ranking using pageviews, searches, language coverage, and museum attendance. Of the candidates with a Commons PD/CC source, 54 new image presentations passed contact-sheet review and were added. Excluded duplicate Impression, Sunrise, a Rhinoceros print with answer-bearing lettering, and explicit erotic works. Painting presentations now total 70 (16 prior + 54 added); this does not meet the user's desired 100 yet. 24 benchmark entries have no cleared image source in that list.
- The reviewed 60-image candidate set is under `build/image-qsj-sampler/candidates/quality-pass/`; contact sheets are in `build/image-qsj-sampler/audit/paintings-top100/`. Approved IDs are recorded in `build/image-qsj-sampler/candidates/painting-approved-keys.json`. Importer: `build/add-reviewed-image-qsj-paintings.py`.
- Regenerated sampler and contact sheets. Sampler currently has 264 unique images and 13 categories. Full path: `C:\Users\pierr\AndroidStudioProjects\TriviaParty\build\image-qsj-sampler\sampler.html`.
- Coverage table was updated. Sculptures and buildings remain at 20 each and require continued expansion to 100. Sculpture benchmark HTML/list extracted to `build/image-qsj-sampler/candidates/sculpture-top100-source.html`, `sculpture-top100-list.json`, and `sculpture-captions.json`. A Commons image-search fetcher is in progress; ensure its search results are image MIME and license-compatible before accepting. The first attempt incorrectly requested `giprop`; corrected to `iiprop`. Candidate downloader now checkpoints metadata after each image and skips already-downloaded files.
- Do not change approved image-reveal progression or pixelate curve. No tests/build/phone install or commit was performed.

## 2026-10-27 — image-bank expansion continued

- Continued the public-license image-bank cleanup/expansion. Canonical bank now contains 349 image-QSJ presentations, 333 unique image files, and 13 represented categories. Current main counts: paintings 82, sculptures 37, buildings/sites 67, animals 25, landscapes 19, cities 20, politicians 20, Disney 19, Pixar 15, Marvel 19, DC 19, manga 5, and BD characters 2. Cartoon images remain 0.
- Added 12 visually reviewed paintings from Art & See’s top-100 discovery list. Media credits record source/license/creator. The bank now covers 65 distinct positions from that list; 35 remain unrepresented or uncleared. Same-title Venus works are disambiguated by artist; corrected “Surrender of Brea” to “Surrender of Breda”.
- Added 8 reviewed sculpture image questions from the Sculptura top-100 discovery set. Sculpture questions total 37, but exact rank coverage for all prior bank works is not yet reconciled.
- Reviewed all 80 new building targets and imported 47 images after visual review. The building/site category totals 67 including the previous 20. Several weak Commons matches were rejected; the rejected files remain only as local review candidates and are not in the canonical bank. The Commons fetcher now requests MIME metadata and ranks matches using both target and refined query terms. Building importer license whitelist includes CC BY 2.0 and CC BY-SA 2.0.
- Normalized building category paths so the expanded entries share the existing architecture category. Rebuilt sampler: `build/image-qsj-sampler/sampler.html`; it contains 331 unique images, 13 categories, displays one image at a time, and retains the four reveal modes.
- Coverage reference: `game-library/bank/IMAGE-QSJ-COVERAGE.md`. These counts do not mean the requested expansion is complete: 65/100 Art & See painting positions are covered, sculptures have 37 presentations (rank reconciliation remains), and the curated building set has 67 presentations. BD/cartoon/manga and additional category visual audits remain incomplete. Continue work instead of treating these interim counts as complete.
- New candidate-review artifacts and approval lists are under `build/image-qsj-sampler/candidates/`; do not import pending candidates without visual and license review. No build, tests, device install, or commits were performed.


### Image bank continuation — structured facts and image cleanup, 2026-10-27

- Continued the image-QSJ bank work from the prior handoff. The Bécassine title-cover image is replaced by the public-domain Pinchon panel `media/06eb6b3faca17a792e6e364f.jpg`; Bécassine is dominant and recognizable with no answer lettering, but another character is partly visible at right. Keep searching for a single-character replacement. The media credit and review note are recorded in `IMAGE-QSJ-MEDIA-CREDITS.json`.
- Added structured `imageFacts` on 352 image-question presentations / 336 unique images. Fields preserve subject type, work/subject title, franchise and typed source-linked facts. Media creators remain distinct from subject creators. The Android model can deserialize these fields and the host reveal renders the question explanation.
- Added curated painter/sculptor/architect/country/depicted-person/character-author facts and an actor fact for Iron Man: Robert Downey Jr. in the Marvel Cinematic Universe films, sourced to Marvel. These are supplementary, not yet used to generate new alternate question prompts.
- Added three visually reviewed, complete painting images from Art & See’s list: The Dog (rank 30), Medusa (51), and The Massacre at Chios (71). The existing Great Wave question now records rank 7 rather than getting a duplicate. Painting coverage is 69/100 benchmark positions (31 still unrepresented/uncleared). Total image QSJs: 352 presentations, 336 unique images, 13 represented categories.
- Refreshed sampler: `C:\Users\pierr\AndroidStudioProjects\TriviaParty\build\image-qsj-sampler\sampler.html`. Answer reveal includes supplementary facts. Coverage and schema notes are in `game-library/bank/IMAGE-QSJ-COVERAGE.md` and `game-library/bank/README.md`.
- Reproducible scripts: `build/enrich-image-qsj-facts.py`; image import and review metadata are under `build/image-qsj-sampler/candidates/`.
- Remaining work is substantial: 31 painting benchmark positions, sculptures/buildings below 100 and sculpture rank reconciliation, and image quantity/quality audits for BD, cartoon, manga, and the other categories (including multi-subject, text-bearing and noncanonical depictions). Continue working; do not call the requested bank complete. No tests, build, phone install, or commit were run/performed this turn.


### Image bank continuation — painting rank reconciliation, 2026-10-27

- Resumed per user request. Reconciled nine more already-present canonical painting images to Art & See ranks by exact title and media record (Mona Lisa 1, Starry Night 2, Last Supper 4, Scream 6, Las Meninas 15, American Gothic 20, Olympia 26, Bal du moulin de la Galette 33, Impression, Sunrise 42). Reused existing images without duplicate questions. Benchmark coverage is now 78/100 (22 missing/unresolved); presentation/image totals remain 352/336.
- Reviewed the outstanding candidate ranks from the available painting folder. Most potentially applicable images were already in the bank under canonical rank IDs and are now mapped; Wedding at Cana rank 68 is a cropped detail and remains rejected. Other remaining ranks have no downloaded candidate in the local review set.
- Audited Bécassine alternates from the same Gallica album. Several apparent panels depict other characters or groups; rejected them. The current text-free panel has Bécassine dominant but another character partly visible, so continue looking for a better single-character source. Commons discovery category is at https://commons.wikimedia.org/wiki/Category:B%C3%A9cassine_chez_les_Turcs_(illustrations); do not assume a page title identifies the depicted character. Current Bécassine asset remains `media/06eb6b3faca17a792e6e364f.jpg` pending a stricter replacement.
- Regenerated facts v8 and sampler. Corrected Iron Man actor explanation punctuation. Structured facts and individual painting creator facts remain in the bank. No new image-question presentations added this continuation; current categories and asset-quality audits still have substantial gaps. No tests/build/device installation or commits performed.
