# Category packages

These legacy assets are retained as source examples. The app now loads imported packages, with original sets seeded once into removable packages. For new content, create or update an importable ZIP.

Store one category per JSON file in this directory. Each file has category-level rules and a question list:

```json
{
  "category": "Geographie mondiale",
  "answerMode": "SIMULTANEOUS",
  "questionTypes": ["Choix multiples"],
  "questions": []
}
```

`answerMode` is either `SIMULTANEOUS` or `BUZZER`. Every question in one category file must use the same format, and `questionTypes` must name that single format. The app rejects mixed-format category files. Individual questions contain their content, answer structure, and scoring values.

Set `answerTimeSeconds` in the game package (`game.json`), rather than in a category. It defaults to 10 seconds and starts automatically on a buzz while the question timer pauses. Legacy category-level values are accepted for compatibility but the game package determines the countdown.

For an imported ZIP, put image files under `images/` and set `imageUrl` to a relative path such as `images/nun-ace.png`. The ZIP importer supports PNG, JPEG, and WebP. Imported images are hosted by the host phone for the duration of the local game; no public image URL is required.

For **Qui suis-je ?**, use `kind: "guessWho"`, `answerMode: "BUZZER"`, `questionTypes: ["Qui suis-je ?"]`, a `clues` array, and `acceptableAnswers`. Include exactly `game.json`'s `maxFlips + 1` clues: the first is immediate, each later clue appears with the next point interval. Buzzing pauses progression while the oral answer countdown runs. See `package-examples/qui-suis-je-demo/` for editable sources and an importable example.
