# Game packages

Each JSON file in this directory is a ready-to-play preset. `categoryPackages` lists filenames (without `.json`) from `question-bank/`, and `timingConfig` contains the preset's timer and scoring options.

## Importable ZIP format

On the host phone, choose **Importer un forfait (.ZIP)** and select an archive with this layout:

```text
game.json
question-bank/
  charades.json
images/
  nun-ace.png
```

`game.json` uses the `GamePackage` fields: `id`, `name`, `description`, `categoryPackages`, `timingConfig`, and `answerTimeSeconds` (default 10). For example:

```json
{
  "id": "charades",
  "name": "Charades",
  "description": "Mime et buzzer",
  "categoryPackages": ["charades"],
  "answerTimeSeconds": 10,
  "timingConfig": {
    "secondsPerFlip": 10,
    "decayPercentagePerFlip": 0.1,
    "maxFlips": 5,
    "pointsDecayPerFlip": 5
  }
}
```

Each category JSON follows the format in `question-bank/README.md`. Set an image question's `imageUrl` to a relative path such as `images/nun-ace.png`. Include that file in the ZIP. Supported local image types are PNG, JPEG, and WebP. The app stores imported packages on the host phone and shares images over the game's Wi-Fi connection. Do not use computer file paths or website URLs for imported images.

The importer accepts one package per ZIP, up to 150 MB total and 20 MB per image. Package ids and image paths may contain letters, numbers, `_`, and `-` (plus `.` in filenames).

`answerTimeSeconds` must be positive. It is the automatic countdown after a buzzer press for every category in the game. The question/scoring timer pauses while that team answers; a wrong answer or timeout locks out the team and resumes the question timer. A correct answer ends the question. This package setting replaces the legacy category-level answer timer.
