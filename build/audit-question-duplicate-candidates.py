#!/usr/bin/env python3
"""Find question-level near-duplicate candidates across the whole canonical bank."""
import csv
import itertools
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library/bank/questions.json"
OUT = ROOT / "game-library/bank/QUESTION-DUPLICATE-CANDIDATES.csv"
STOP = set("a an the le la les un une des de du d l au aux et ou en dans sur par pour avec quel quelle quels quelles qui que quoi est sont a-t-il a-t-elle comment pourquoi quand ou dont je suis vous mon ma mes leur leurs ce cet cette ces on y".split())
GENERIC = {"oui", "non", "vrai", "faux", "a", "b", "c", "d", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}
GENERIC_PROMPTS = {
    "qui suis je", "quelle capitale se cache dans cette charade visuelle",
    "quel objet ou quelle chose se cache dans cette charade visuelle",
    "quelle expression se cache dans cette image", "quel titre de livre se cache dans cette charade visuelle",
    "quel mot se cache dans cette charade visuelle", "quelle ville se cache dans cette charade visuelle",
    "quelle ville se cache dans cette charade", "quel personnage se cache dans cette image",
}

def norm(value):
    value = unicodedata.normalize("NFKD", (value or "").casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", value))

def norm_answer(value):
    value = norm(value)
    value = re.sub(r"^[a-d]\s+", "", value)
    value = re.sub(r"^(le|la|les|l|un|une|des|the|a|an)\s+", "", value)
    return value

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    questions = bank["questions"]
    subjects = {s["id"]: s for s in bank["subjects"]}
    items = []
    answer_index, subject_index, token_index, exact_index = (defaultdict(set) for _ in range(4))
    for ix, q in enumerate(questions):
        extra = []
        for p in q.get("presentations", []):
            c = p.get("content", {})
            if c.get("clues"):
                extra.extend(c["clues"])
        prompt = norm(q.get("prompt", ""))
        # Generic image/charade stems are not evidence of duplicate content.
        # Only compare them when the record also has informative written clues.
        generic_prompt = prompt in GENERIC_PROMPTS or "se cache dans cette" in prompt or prompt == "qui suis je"
        text = " ".join(extra) if generic_prompt and extra else ("" if generic_prompt else " ".join([q.get("prompt", ""), *extra]))
        normalized = norm(text)
        tokens = {t for t in normalized.split() if len(t) > 2 and t not in STOP}
        answers = {norm_answer(a) for a in q.get("answers", []) if norm_answer(a) not in GENERIC and len(norm_answer(a)) >= 3}
        item = {"q": q, "text": normalized, "tokens": tokens, "answers": answers, "subjects": set(q.get("subjectIds", []))}
        items.append(item)
        if normalized:
            exact_index[normalized].add(ix)
        for answer in answers:
            answer_index[answer].add(ix)
        for sid in item["subjects"]:
            subject_index[sid].add(ix)
        for token in tokens:
            token_index[token].add(ix)

    pairs = set()
    for groups, max_size in ((exact_index, 80), (answer_index, 40), (subject_index, 25), (token_index, 18)):
        for members in groups.values():
            if len(members) < 2 or len(members) > max_size:
                continue
            pairs.update(tuple(pair) for pair in itertools.combinations(sorted(members), 2))

    candidates = []
    for i, j in pairs:
        a, b = items[i], items[j]
        if not a["tokens"] & b["tokens"]:
            continue
        jac = len(a["tokens"] & b["tokens"]) / max(1, len(a["tokens"] | b["tokens"]))
        seq = SequenceMatcher(None, a["text"], b["text"]).ratio() if a["text"] and b["text"] else 0
        same_answer = bool(a["answers"] & b["answers"])
        same_subject = bool(a["subjects"] & b["subjects"])
        if same_answer and (seq >= .50 or jac >= .33):
            reason = "same accepted answer plus wording overlap"
        elif same_subject and (seq >= .52 or jac >= .30):
            reason = "same subject plus similar wording"
        elif same_subject and seq >= .82 and jac >= .58:
            reason = "very similar prompts; check answer/context"
        else:
            continue
        score = round(.50 * seq + .50 * jac + (.12 if same_answer else 0) + (.05 if same_subject else 0), 3)
        qa, qb = a["q"], b["q"]
        sa = " | ".join(subjects.get(sid, {}).get("label", "") for sid in qa.get("subjectIds", []))
        sb = " | ".join(subjects.get(sid, {}).get("label", "") for sid in qb.get("subjectIds", []))
        candidates.append({"score": score, "prompt_similarity": round(seq, 3), "token_overlap": round(jac, 3),
          "same_accepted_answer": same_answer, "shared_subject": same_subject, "candidate_reason": reason,
          "question_a": qa["id"], "subject_a": sa, "prompt_a": qa.get("prompt", ""), "answers_a": " / ".join(qa.get("answers", [])),
          "question_b": qb["id"], "subject_b": sb, "prompt_b": qb.get("prompt", ""), "answers_b": " / ".join(qb.get("answers", [])),
          "review_outcome": "", "review_notes": ""})
    candidates.sort(key=lambda x: (-x["score"], x["question_a"], x["question_b"]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(candidates[0].keys()) if candidates else ["question_a", "question_b"])
        writer.writeheader()
        writer.writerows(candidates)
    print(f"Scanned {len(questions)} question records; examined {len(pairs)} candidate pairs; retained {len(candidates)} possible overlaps.")
    for row in candidates[:100]:
        print(f"{row['score']:.3f} ans={row['same_accepted_answer']} sub={row['shared_subject']} | {row['question_a']} [{row['subject_a']}] {row['prompt_a']} => {row['answers_a']} || {row['question_b']} [{row['subject_b']}] {row['prompt_b']} => {row['answers_b']}")
    print(f"Wrote {OUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
