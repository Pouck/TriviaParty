#!/usr/bin/env python3
"""Score every question pair for likely duplicate or same-subject overlap.

This is a candidate screen, not an automatic duplicate classifier. Generic
image and charade stems without clues are excluded from text comparisons.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank/questions.json"
OUT = ROOT / "game-library/bank/QUESTION-ALL-PAIRS-CANDIDATES.csv"
STOP = set("a an the le la les un une des de du d l au aux et ou en dans sur par pour avec quel quelle quels quelles qui que quoi est sont a-t-il a-t-elle comment pourquoi quand ou dont je suis vous mon ma mes leur leurs ce cet cette".split())
GENERIC_ANSWERS = {"oui", "non", "vrai", "faux", "a", "b", "c", "d", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}


def norm(value):
    value = unicodedata.normalize("NFKD", (value or "").casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", value))


def answer_key(value):
    value = norm(value)
    return re.sub(r"^(?:[a-d]\s+)?(?:le|la|les|l|un|une|des|the|a|an)\s+", "", value)


def bits(values, vocabulary):
    result = 0
    for value in values:
        result |= 1 << vocabulary.setdefault(value, len(vocabulary))
    return result


def main():
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    subjects = {s["id"]: s for s in bank["subjects"]}
    token_vocab = {}
    items = []
    for q in bank["questions"]:
        clues = []
        for p in q.get("presentations", []):
            clues.extend(p.get("content", {}).get("clues", []))
        prompt = norm(q.get("prompt", ""))
        generic_prompt = prompt == "qui suis je" or "se cache dans cette" in prompt or prompt in {
            "quelle expression se cache dans cette image", "quel personnage se cache dans cette image"
        }
        text = norm(" ".join(clues)) if generic_prompt and clues else ("" if generic_prompt else norm(" ".join([q.get("prompt", ""), *clues])))
        tokens = {t for t in text.split() if len(t) > 2 and t not in STOP}
        answers = {answer_key(a) for a in q.get("answers", [])}
        answers = {a for a in answers if len(a) >= 3 and a not in GENERIC_ANSWERS}
        items.append({
            "q": q,
            "text": text,
            "tokens": bits(tokens, token_vocab),
            "token_count": len(tokens),
            "answers": answers,
            "subjects": set(q.get("subjectIds", [])),
        })

    candidates = []
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            common_answers = a["answers"] & b["answers"]
            common_subjects = a["subjects"] & b["subjects"]
            token_intersection = (a["tokens"] & b["tokens"]).bit_count()
            token_union = (a["tokens"] | b["tokens"]).bit_count()
            token_jaccard = token_intersection / max(1, token_union)
            if not (common_answers or common_subjects or (a["text"] and b["text"] and token_jaccard >= .75)):
                continue
            qa, qb = a["q"], b["q"]
            candidates.append({
                "same_accepted_answer": bool(common_answers),
                "shared_subject": bool(common_subjects),
                "common_answers": " / ".join(sorted(common_answers)),
                "candidate_reason": "shared accepted answer" if common_answers else ("shared subject" if common_subjects else "very high prompt token overlap"),
                "subject_a": " | ".join(subjects.get(sid, {}).get("label", "") for sid in qa.get("subjectIds", [])),
                "question_a": qa["id"],
                "prompt_a": qa.get("prompt", ""),
                "answers_a": " / ".join(qa.get("answers", [])),
                "subject_b": " | ".join(subjects.get(sid, {}).get("label", "") for sid in qb.get("subjectIds", [])),
                "question_b": qb["id"],
                "prompt_b": qb.get("prompt", ""),
                "answers_b": " / ".join(qb.get("answers", [])),
                "token_jaccard": round(token_jaccard, 3),
                "review_outcome": "",
                "review_notes": "",
            })

    candidates.sort(key=lambda x: (
        -int(x["same_accepted_answer"]), -int(x["shared_subject"]),
        -x["token_jaccard"],
        x["question_a"], x["question_b"],
    ))
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(candidates[0]) if candidates else [])
        writer.writeheader()
        writer.writerows(candidates)
    n = len(bank["questions"])
    print(f"Scored all {n * (n - 1) // 2:,} pairs across {n:,} questions.")
    print(f"Flagged {len(candidates):,} candidates using shared answers, shared subjects, or very high prompt overlap.")
    print(f"Wrote {OUT.relative_to(ROOT)}; candidates still require semantic review.")


if __name__ == "__main__":
    main()
