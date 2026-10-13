# Question bank

The host now loads imported ZIP packages. Original bundled sets are seeded once as removable packages; editing the legacy asset JSON does not update an already imported package. Use **Mettre à jour** with the same package ID to replace content. A ZIP contains `game.json` at its root, category JSON files in `question-bank/`, and optional images in `images/`. The category string in every question must match the file's `category`, and question IDs must be unique across all selected content.

At game preparation, whole categories are automatically arranged to vary both subject and question format (QCM, buzzer, Qui suis-je ?, chronology, speed race). The sequence is chosen once and remains stable throughout that game. Each category keeps its package timing and scoring rules, and shared categories still appear only once. When the selection is uneven, the scheduler minimizes repeated subjects/formats and long runs, then spreads the selection proportionally; perfect alternation is not always possible. Equal-quality sequences can differ between games.

Subject names are inferred from existing category/package names. A category JSON may optionally declare `"subject": "Architecture"` (or another consistent subject label) to override that inference. Existing archives without this field remain compatible. This field only describes the category; it does not change its answer mode, question format or rules.

```json
{
  "category": "Géographie mondiale",
  "answerMode": "SIMULTANEOUS",
  "questionTypes": ["Choix multiples"],
  "questions": [
    {
      "kind": "multipleChoice",
      "id": "geo-capital-001",
      "category": "Géographie mondiale",
      "prompt": "Quelle est la capitale du Canada ?",
      "basePoints": 100,
      "penaltyPoints": 0,
      "options": ["Toronto", "Ottawa", "Montréal", "Vancouver"],
      "correctOptionIndex": 1
    }
  ]
}
```

Supported `kind` values are `multipleChoice`, `ordering`, `textAnswer`, `guessWho`, `mapChoice`, `wager`, and `speedRace`. Each category contains one format and declares one `questionTypes` label; a package may combine several categories. Points and penalties belong to each question. `timingConfig` and `answerTimeSeconds` belong to the game package, not individual questions. `mapChoice` uses `imageUrl`, labeled options with normalized `xRatio`/`yRatio`, and `correctOptionIndex`. `textAnswer` uses the oral buzzer flow.

`guessWho` is **Qui suis-je ?** in `BUZZER` mode. Its `clues` array contains exactly `timingConfig.maxFlips + 1` nonempty strings: one immediately, then one per scoring interval. Earlier clues stay visible. Buzzing or manually pausing freezes progression. `acceptableAnswers` supplies the revealed solution; the host judges the spoken answer. Players see score and buzzer, with no clues or solution transmitted to web phones. See [the complete demo and format guide](../package-examples/qui-suis-je-demo/README.md).
