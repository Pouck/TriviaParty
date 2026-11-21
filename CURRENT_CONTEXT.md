# Trivia Party — Session Status & Complete Context Handoff

Date: November 21, 2026  
Workspace: `H:\AndroidStudioProjects\TriviaParty`

---

## 1. Summary of Session Accomplishments

### A. Environment & Workspace Migration (C: to H:)
- Project successfully relocated to `H:\AndroidStudioProjects\TriviaParty`.
- Reconfigured Android SDK path to `H:\Android\Sdk` in `local.properties`.
- Repaired environment variables: permanently added `H:\Android\Sdk\platform-tools` to User `PATH`.
- Cleared conflicting legacy variables (`ANDROID_PREFS_ROOT` and `ANDROID_USER_HOME`) that were causing Gradle build crashes.
- Re-established wireless ADB connectivity with Pixel 7 Pro (`adb-2B021FDH300B81-JSzzEA._adb-tls-connect._tcp`).

### B. Canonical Question Bank & 3-Tier Taxonomy Architecture
- Established the 3-tier Directed Acyclic Graph (DAG) taxonomy model:
  - **Tier 1 (Selectable Categories / Grand Domaine)**: High-level setup nodes (*Arts*, *History*, *Geography*, *Science*, etc.).
  - **Tier 2 (Internal Keywords & Facets)**: Deterministic attributes, synonyms, periods, museums, and materials.
  - **Tier 3 (Compact Leaf Entities & Facet-Based Question Derivation)**: Single-source-of-truth entities (*Le Radeau de la Méduse*, *Tour Eiffel*) from which multiple non-repetitive questions are derived.
- Documented in `taxonomy_graph_architecture.artifact.md` and `taxonomy_proposal.artifact.md`.

### C. GameSetupScreen UI Refactoring & Performance
- Replaced flat category chips with a collapsible hierarchical tree explorer (`TaxonomyNodeView`).
- Solved initial performance/freeze issues by implementing thread-safe memoized caching in `QuestionBankRepository`.
- Enforced strict branch-vs-leaf separation: intermediate nodes (*Arts*, *Painting*, *Sculpture*) only expand into sub-categories, preventing premature dumping of leaf entities.
- Redesigned bottom action bar:
  - Full-width "Tout sélectionner" / "Tout désélectionner" buttons.
  - Collapsible "Paramètres de jeu" banner with distinct color differentiation.
  - Clean three-action bar: **Paramètres**, **Révision Solo**, and **Commencer**.
  - Count badge bubbles protected with `softWrap = false` to prevent numbers wrapping across rows.
  - Selection defaults to unselected so players choose categories deliberately.

### D. Leaf Inventory Review & Normalization
- Generated complete inventory: `leaf_subjects_inventory.artifact.md`.
- Normalized entries according to user directives:
  - Converted foreign/English landmark and artwork labels strictly to French (*Sistine Chapel* -> *Chapelle Sixtine*, *Fallingwater* -> *Maison sur la cascade*, *The Matrix* -> *Matrix*, *The Scream* -> *Cri*, etc.).
  - Stripped leading articles (*Le*, *La*, *Un*, *Une*) and elisions (*L’*, *d’*) from general category labels.
  - Preserved creator/artist details in aliases/notes rather than cluttering titles (e.g. *David* instead of *David en bronze de Donatello*).

---

## 2. Root Cause Analysis: Google Cast Failure (Status 2472 / 2475)

### Historical Working Mechanism:
On drive `C:`, casting worked because a local background relay (`build/cast-receiver-relay.mjs`) was running on port 18081 through a **Tailscale Funnel** tunnel (`https://desktop-pierre.tail0f0cb5.ts.net`). The Cast Application ID `6CA3BAF3` in the Google Cast Developer Console was pointing directly to that Tailscale URL.

### Why it Broke on H::
1. When the workspace moved to `H:`, the Tailscale Funnel / computer relay was no longer running.
2. When the phone sends `launchApplicationWithOptions: 6CA3BAF3`, the Chromecast contacts Google's Cast server, receives the old Tailscale URL (`https://desktop-pierre.tail0f0cb5.ts.net`), and tries to load it over HTTPS.
3. Because that Tailscale URL is dead and unreachable, the TV receiver fails to load and drops the connection ~0.8s later with status codes **`2472` / `2475`**, leaving the TV on Google's "Something went wrong" screen.

---

## 3. Permanent Solution: GitHub Pages Hosting

### Strategy:
Deploy the static Cast Web Receiver directly to **GitHub Pages** on your repository (`https://github.com/Pouck/TriviaParty`), resulting in a permanent, free, 100% independent HTTPS endpoint:
```text
https://pouck.github.io/TriviaParty/
```

### Benefits:
- **No computer needed**: The phone casts directly to the TV without requiring your PC, Android Studio, or Tailscale to be running.
- **Direct LAN media**: The receiver on the TV loads over HTTPS from GitHub Pages, and once connected, loads local game state and images directly from the phone host over your home Wi-Fi (`http://<phone-ip>:8080`), complying with Google Cast's mixed-content policies.
- **100% Free**: Operates permanently well within GitHub Pages' free tier limits.

### Bundle Contents Prepared for GitHub Pages:
The static bundle located in `build/cast-site/public/` (or `gh-pages` branch) requires only:
1. `index.html` (the receiver entrypoint)
2. `receiver.js` (incorporating all latest direct phone-LAN HTTP origin resolution fixes)
3. `receiver.css` (display styles and animations)
4. Assets: `feedback-good.png`, `feedback-bad.png`, `feedback-red-stroke.png`, `hourglass.svg`
*(Note: Never deploy the private question bank JSON to GitHub Pages; only the static UI receiver shell).*
