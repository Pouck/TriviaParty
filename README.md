# TriviaParty

Android quiz host with browser-based players and a separate Chromecast/debug TV display. Player phones need no app installation. The host privately validates oral and written answers; TV and player views receive only the appropriate public information.

## Contents

- `app/`: Android host, local web server, browser player, bundled TV assets and tests.
- `cast-receiver/`: Chromecast receiver sources and browser tests. The configured receiver application ID is `6CA3BAF3`.
- `game-library/current/`: current playable catalogue, ZIP packages, editable JSON/image sources, audits and migration metadata. It contains 248 packages and 1,303 questions, including six diagnostic packages excluded from normal draws.
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

See [browser players](BROWSER-PLAYERS.md), [host review and selection](HOST-REVIEW-AND-SELECTION.md), and [written answers and chronology readiness](game-library/WRITTEN-AND-READY.md). Current packages contain 5–7 questions each. Chronology players confirm **PRÊT** before the timer starts; Qui suis-je uses a host-controlled reading phase. Written responses are reviewed privately one player at a time.

The debug TV is served at `/tv` and players at `/play` on the host's port 8080. The debug TV requires one click on **Activer le son** after reloading. USB/wireless ADB forwarding can expose the host locally: `adb forward tcp:18080 tcp:8080`.

## Backup scope

This private repository preserves project sources, packaged media, current and historical question content, and the dated review backup. Downloaded images and other third-party material retain their source rights; source/verification records accompany the packages. Credentials and signing keys must not be committed.
