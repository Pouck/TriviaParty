# Local TV display

## Registered Google Cast test receiver

The unpublished receiver application ID is `6CA3BAF3` (configured in `gradle.properties`). The registered Vizio P55-F1 loads `http://192.168.86.47:8080/tv/cast` from the Pixel host. Start a host session before tapping **TV** and selecting the television. Keep the Pixel and TV on the same network. This URL must be updated in the Cast console if the Pixel's Wi-Fi address changes.

The receiver receives public `TvState` snapshots, not the host screen. Once the dedicated Cast connection is active, **RÉPONSE** on the host opens the expected oral answer privately. The regular good/wrong answer controls remain on the Pixel. Do not enable screen mirroring for this workflow.

The local Cast receiver route and sender controls are implemented and built; physical receiver launch still requires testing on the registered television. Public HTTPS hosting and publishing have not been performed.

Trivia Party serves its TV display from the host phone over the same local Wi-Fi network as the game. The host app starts the web server on port 8080; it does not upload game state or the display page to an external site.

1. Connect the host phone, players and TV to the same Wi-Fi network.
2. Start a host game and leave the host app open.
3. On the TV, open its web browser and visit `http://<host-phone-ip>:8080/tv`. The host screen shows the correct local URL in **TV Display**.
4. The TV page reconnects to the host and updates as the game progresses.

Android 17 requires Trivia Party's **Nearby devices** permission for local network connections. If the TV does not offer a web browser, a computer or tablet on the same network can open the page, or the computer can connect to the TV over HDMI.

Local browser display does not need a Cast Developer Console account, a registered receiver application ID or public website hosting. The page and game-state connection work locally; question images supplied as external URLs still need their original source to be reachable. External-site deployment has not been performed.


## Buzzer audition and response time

The player sends an oral buzz on pointer contact, with click retained for keyboard activation. The receiver predecodes `buzzer.wav` while the room is open and uses a low-latency Web Audio buffer when available; HTML audio remains the fallback. Refresh debug player/TV pages after updating the app, or reconnect the Cast session so the receiver reloads.

Ten original sound candidates can be compared at `/tv/buzzer-sampler`; the standalone page and local preview instructions are in [BUZZERS.md](../audio-bank/BUZZERS.md). Auditioning does not change the live buzzer.
