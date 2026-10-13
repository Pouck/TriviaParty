# Play from an iPhone, Android phone, tablet, or computer

1. Open the Android app directly to host setup and start a game.
2. Connect the host and players to the same Wi-Fi network. The host can also supply a hotspot if its network allows clients to reach the phone.
3. Scan the QR code in the lobby with the phone camera, or type the displayed address into Safari, Chrome, or another browser.
4. Enter a team name and join; no room code is required. If host approval is enabled, wait for acceptance.
5. Keep the page open during play. Players see their centered team name and score, with “En attente…” until a question is ready. Multiple-choice questions (including speed races) show only answer choices: one tap submits and locks the answer immediately, with no Validate button or buzzer. Choices stay visible after submission and during the reveal. Buzzer questions show the colored buzzer, labeled only “BUZZER”, or “Reconnexion…” while disconnected. Question prompts and illustrations stay on the TV and host screens. The host selects categories and judges spoken answers.

The host's **JOINDRE** button shows the QR code again during the game. The URL is `http://<host-ip>:8080/play?room=<room-code>`; the port follows the host server configuration.

No player installation or external buzzer service is needed. The page and its assets are served by the Android phone, so internet access is not needed for joining and buzzing. Question images hosted externally still require internet access. Guest Wi-Fi that isolates devices can block connections; use a network that allows devices to communicate.

The browser automatically reconnects after a temporary connection loss and remembers the team within the current browser tab, including a refresh. If the host starts a new game, join again. Closing the tab can lose the saved identity; reusing a team name then requires host approval.

The Android app is host-only; native player screens, debug player buttons, and local player discovery have been removed. The room ID remains internal to distinguish game sessions and restore connections automatically. Browser connections use `/play/ws` and accept only player events; their snapshots omit question content, answer keys, team session tokens, and other teams' submissions.

## Verification

Run `node --test app/src/test/browser-player.test.cjs` for browser interaction checks and `gradlew.bat :app:testDebugUnitTest :app:assembleDebug` for network integration tests and the APK build. Before a live game, check a real iPhone on the same Wi-Fi: scan, join, buzz, refresh, and temporarily switch away and return. Mobile operating systems can suspend background tabs; keeping the page visible is best for buzzing.

Buzzer colors: yellow = ready, blue = pressed / your turn to answer, red = disabled after an incorrect answer, green = correct, gray = waiting / another team answering / disconnected / game ended. The buzzer is hidden for non-buzzer questions.

At game end, teams tied for the highest positive score see “Gagnant!” and the other teams see “Bel effort!”. Buzzer presses automatically pause the question timer and start the package’s `answerTimeSeconds` countdown (10 seconds by default). Wrong answers and timeouts lock out that team and resume the question timer.

Select one or more packages on host setup, then press **PRÉPARER LA PARTIE**. The combined game includes each shared category once and retains per-category package timing, scoring, and answer duration. If shared categories have conflicting rules, the first package selected takes precedence; setup lists those conflicts.
