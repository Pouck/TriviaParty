# TriviaParty

Android quiz host with browser-based players and a separate Chromecast/debug TV display. Player phones need no app installation. The host privately validates oral and written answers; TV and player views receive only the appropriate public information.

## Contents

- `app/`: Android host, local web server, browser player, bundled TV assets and tests.
- `cast-receiver/`: Chromecast receiver sources and browser tests. The configured receiver application ID is `6CA3BAF3`.
- `game-library/bank/`: authoritative question database: one entry per question with multiple play presentations, shared media and preserved reviews. See [bank documentation](game-library/bank/README.md).
- `game-library/current/`: legacy package ZIPs, source mirrors and inventory, retained for import/export compatibility and migration checks. Gameplay packages are assembled from the canonical bank.
- `game-library/history/` and `package-examples/`: historical authoring materials and package versions.
- `build/*.py`, `build/*.cjs`, `build/*.ps1`: package generators, audits, audio tools, previews and device helpers. Although located in `build/`, these files are source code and are versioned.
- `review-backups/`: a dated backup of question annotations, ratings and usage statistics. The app's live review file remains on the host device.

## Build and check

Open this directory in Android Studio and configure an Android SDK. Local SDK paths, IDE caches, APKs and temporary previews are excluded from Git.

```powershell
.\gradlew.bat :app:assembleDebug :app:testDebugUnitTest
node --test cast-receiver/receiver.test.js app/src/test/browser-player.test.cjs app/src/test/judge-browser.test.cjs
python build/build-playable-library.py
python build/audit-chronology.py
```

Package authoring tools use Python; browser preview tools use Node.js and Chrome. Some image and audio generation tools require network access. Device helpers currently contain the development machine's SDK/device paths; adapt them for another machine.

## Playing and reviewing

See [browser players](BROWSER-PLAYERS.md), [host review and selection](HOST-REVIEW-AND-SELECTION.md), and [written answers and chronology readiness](game-library/WRITTEN-AND-READY.md). Current packages contain 5–7 questions each. Chronology players confirm **PRÊT** before the timer starts; Qui suis-je starts each clue automatically. Written responses are reviewed one player at a time, with that player’s submission shown on TV during validation.

The debug TV is served at `/tv` and players at `/play` on the host's port 8080. The debug TV requires one click on **Activer le son** after reloading. USB/wireless ADB forwarding can expose the host locally: `adb forward tcp:18080 tcp:8080`.

## Backup scope

This private repository preserves project sources, packaged media, current and historical question content, and the dated review backup. Downloaded images and other third-party material retain their source rights; source/verification records accompany the packages. Credentials and signing keys must not be committed.

## Human voice reaction bank

The bundled bank now contains 100 original-language human recordings: 50 per outcome, 70 French, 20 English, 5 Spanish and 5 German, with 57 speakers and 60 distinct language/outcome expressions. It contains 95 short pronunciation expressions and five acted English game reactions. See [audition page](audio-bank/index.html), [bank details](audio-bank/README.md), and [attribution](audio-bank/ATTRIBUTION.md). These are human recordings rather than a completed commercial-film dialogue bank; film candidates remain separately documented in [MOVIE-REACTIONS.md](MOVIE-REACTIONS.md).

Audio credits are accessible at `/tv/audio-credits`. Per-game shuffle bags exhaust clips by outcome before repeating and prefer available speaker/phrase variety. Updated bank URLs carry a version to avoid stale cached speech.
