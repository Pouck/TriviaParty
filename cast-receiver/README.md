# Local TV display

## Registered Google Cast test receiver

**Deprecated temporary setup — do not use for normal casting.** The phone build still references receiver ID `6CA3BAF3` in `gradle.properties`. Its registered URL was temporarily served through Tailscale Funnel and a computer-side relay; this is not a viable daily setup and the latest TV attempt showed Google's “Something went wrong” page. The registered URL must be replaced with a durable HTTPS host before asking the user to retry. Android sender package details are `com.example.triviaparty`. The second app ID `DFCF5F96` remains unpublished and unused. The Vizio Cast serial `LTMWXHKU4252953` was marked `Ready For Testing`. Launch failures were logged as sender status 2472 for `6CA3BAF3` and 2474 for `DFCF5F96`; neither code has been mapped to an authoritative cause.

Legacy implementation details only: `build/cast-receiver-relay.mjs` served the receiver through Tailscale Funnel on port 18081 and forwarded selected phone media requests. It required the computer and relay to stay online, so it is retired and must not be used as the daily Cast setup. The receiver now keeps allowed phone-LAN media URLs direct; see the active work in `SESSION-HANDOFF.md`.

The receiver receives public `TvState` snapshots, not the host screen. Once the dedicated Cast connection is active, **RÉPONSE** on the host opens the expected oral answer privately. The regular good/wrong answer controls remain on the Pixel. Do not enable screen mirroring for this workflow.

The latest debug APK, including HTTPS media handling, was rebuilt and installed on the Pixel. The public HTTPS receiver page returns HTTP 200; the unrelated `/play` route returns 404 through the relay. Physical launch on the Vizio after publication remains to be verified. Casting uses the TV's Cast system; a TV browser is not required.

Trivia Party serves its TV display from the host phone over the same local Wi-Fi network as the game. The host app starts the web server on port 8080; it does not upload game state or the display page to an external site.

1. Connect the host phone, players and TV to the same Wi-Fi network.
2. Start a host game and leave the host app open.
3. On the TV, open its web browser and visit `http://<host-phone-ip>:8080/tv`. The host screen shows the correct local URL in **TV Display**.
4. The TV page reconnects to the host and updates as the game progresses.

Android 17 requires Trivia Party's **Nearby devices** permission for local network connections. If the TV does not offer a web browser, a computer or tablet on the same network can open the page, or the computer can connect to the TV over HDMI.

Local browser display does not need a Cast Developer Console account, a registered receiver application ID or public website hosting. The page and game-state connection work locally; question images supplied as external URLs still need their original source to be reachable. External-site deployment has not been performed.


## Buzzer audition and response time

The player sends an oral buzz on pointer contact, with click retained for keyboard activation, and immediately plays the preloaded category sound locally. TV and debug receivers do not play buzzer audio. Refresh player pages after updating the app, and reconnect Cast so its receiver reloads.

Twenty original buzzer candidates and twenty correct-answer effects can be compared at `/tv/buzzer-sampler`; the standalone page and local preview instructions are in [BUZZERS.md](../audio-bank/BUZZERS.md). Auditioning does not change the live buzzer.


The debug `/tv/ws` stream retains a small public `buzzer` cue for protocol compatibility, independently of queued full snapshots. The display deduplicates it without playing sound. Cast uses state snapshots for its visual updates; phone buzzer playback does not wait for either transport.

## Phone buzzer playback and ordered turns

Buzzer sounds now play immediately on the phone that presses, including phones that enter the queue after the first player. The TV and debug monitor do not echo buzzer audio. One of eight bundled clips is selected at each category introduction and kept for that category, avoiding an immediate repeat from the previous category. Joining and pressing unlock phone audio; the clip is fetched and decoded before the press, with preloaded HTML audio as a fallback.

The server records each player's first buzz per question/clue in arrival order. Only the active player has a locked oral submission and answer timer. A wrong answer or timeout promotes the next connected queued player, retaining their original buzz time and points timing. The host sees the ordered log. Duplicate presses, out-of-turn judgements, closed questions and reading phases cannot steal a turn. A correct answer closes the question. Queues reset with a new question/clue.

Audition the eight files at `/play/sound-sampler`, or open `audio-bank/phone-buzzer-preview.html` for an offline preview. Credits are linked on player pages and at `/play/sound-credits`; exact source URLs, licenses and processing are recorded in `audio-bank/phone-buzzers.json`. The wolf, coyote, boat and train clips use recordings; owl, rooster, dog and bell clips use CC0 SFXMint effects (generated or synthesized). All clips are bundled locally and trimmed for prompt attacks.

TV feedback uses SVG-contained image masks and explicit positional/sizing fallbacks for older Cast browsers. Local Cast-page renders verify centering and the visible stroke animations; physical TV verification remains necessary after reinstalling the debug build and reconnecting Cast. Refresh all player pages after updating the app.

## Audio activation and diagnostics

Player pages include **Activer / tester le son**. Use it after refreshing or restoring a player page; it plays the selected category clip and reports failures visibly. Touch contact still sends the buzz immediately. If mobile autoplay blocks the first sound, touch release retries activation and plays that pending buzz once. Once unlocked, later buzzes start at contact. Audio and player-script responses disable caching so updated files are fetched from the host.

In the host's **TV** dialog, **Tester le son TV** requests an audible receiver test and displays the receiver's playback result. A playing status means the receiver started playback; if it is still inaudible, check the TV's volume/output. Blocked or unavailable status distinguishes autoplay or file-loading trouble. The TV buzzer remains intentionally silent; correct/wrong voices and the game-end sound remain TV audio.

Validation: `build/test-phone-audio-autoplay.cjs` uses touch emulation and normal document-activation autoplay policy to cover restored identity, touch-release recovery, explicit sound test, and immediate subsequent playback. `build/test-debug-tv-autoplay.cjs` verifies TV ping/voice/end playback with normal autoplay restrictions and explicit activation. Physical Galaxy/TV verification remains outstanding.

## Rotating winner music

Each new game selects one of seven classical 24-second endings on the host. All seven are used in random order before the cycle repeats, with no immediate repeat across cycles. The selected file travels in `TvState.gameEndSoundClip`, so local displays and Cast use the same ending. Single and tied winners share the same behavior. Repeated final-state updates and late connections do not replay the music. Recording credits and licenses are available at `/tv/winner-music-credits` and in `audio-bank/game-ending-sounds.json`.

Category-intro edition numbers stay attached to the preceding title line, including titles with a dash before the number.
