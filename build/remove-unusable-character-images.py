from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank"
QUESTIONS = BANK / "questions.json"
BACKUPS = ROOT / "review-backups"
REVISION = "2026-10-26-remove-last-cosplay-images"
DROP_PRESENTATIONS = {
    "image-qsj-personnages-de-manga-totoro",
}
DROP_QUESTIONS = {
    "image-qsj-personnages-de-dessins-animes-shaggy-rogers",
    "image-qsj-personnages-pixar-green-army-men-toy-story",
}


def main() -> None:
    bank = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    if any(row.get("id") == REVISION for row in bank.get("revisionHistory", [])):
        print("The remaining unsuitable character image entries are already removed.")
        return
    found = {p["id"] for q in bank["questions"] for p in q.get("presentations", [])}
    if not (DROP_PRESENTATIONS | DROP_QUESTIONS).issubset(found):
        raise ValueError("A presentation to remove is missing from the canonical bank.")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / "question-bank-before-removing-last-cosplay-images-2026-10-26.json"
    if not backup.exists():
        shutil.copyfile(QUESTIONS, backup)
    removed = []
    retained = []
    questions = []
    for question in bank["questions"]:
        if question.get("id") in DROP_QUESTIONS:
            removed.extend(p["id"] for p in question.get("presentations", []))
            continue
        presentations = question.get("presentations", [])
        keep = [p for p in presentations if p.get("id") not in DROP_PRESENTATIONS]
        removed.extend(p["id"] for p in presentations if p.get("id") in DROP_PRESENTATIONS)
        if len(keep) != len(presentations):
            retained.append(question.get("id"))
        if keep:
            question["presentations"] = keep
            questions.append(question)
        elif not presentations:
            questions.append(question)
    bank["questions"] = questions
    bank.setdefault("revisionHistory", []).append({
        "id": REVISION,
        "note": "Removed the remaining cosplay-only character images; preserved Totoro's other quiz formats.",
        "removedPresentationIds": removed,
        "retainedQuestionsWithoutImage": retained,
    })
    QUESTIONS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"removedPresentations": removed, "retainedQuestionsWithoutImage": retained, "backup": str(backup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
