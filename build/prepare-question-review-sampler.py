from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
OUT = ROOT / "build" / "question-review-sampler"


def collect():
    from canonical_question_bank import BANK, sampler_questions
    import shutil
    questions = sampler_questions()
    copied = 0
    for image in (BANK / 'media').iterdir():
        target = OUT / 'assets/media' / image.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(image, target)
            copied += 1
    return questions, copied, []


OUT.mkdir(parents=True, exist_ok=True)
questions, images_copied, missing_images = collect()
assert questions, "Canonical question bank is empty"
if len({q["id"] for q in questions}) != len(questions):
    raise SystemExit("Question IDs are not unique; refusing to create an ambiguous review sampler.")

manifest = {
    "createdAt": datetime.now().astimezone().isoformat(),
    "questionCount": len(questions),
    "presentationCount": sum(len(q["presentations"]) for q in questions),
    "storageSchema": "canonical-question-bank-v2",
    "imagesCopied": images_copied,
    "missingImages": missing_images,
    "ratingScale": {"0": "Needs review", "1-5": "Difficulty"},
    "questions": questions,
}
(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

data = json.dumps(questions, ensure_ascii=False).replace("</", "<\\/")
state_path = OUT / "review-state.json"
review_state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"reviews": [], "generalComments": []}
rows = {r['questionId']: r for r in review_state.get('reviews', [])}
initial_reviews, history = {}, {}
from canonical_question_bank import read_bank
bank_metadata = read_bank()
consumed_rows = {}
if bank_metadata.get('revisionHistory'):
    consumed_path = ROOT / ('review-backups/question-review-feedback-' + bank_metadata['revisionHistory'][-1]['id'] + '-raw.json')
    if consumed_path.exists():
        consumed_rows = {r['questionId']: r for r in json.loads(consumed_path.read_text(encoding='utf-8'))['reviews']}
consumed = {}
for q in questions:
    consumed[q['id']] = [{'rating': '' if consumed_rows[alias].get('rating') is None else str(consumed_rows[alias]['rating']),
        'modification': consumed_rows[alias].get('modification', '')} for alias in q['legacyIds'] if alias in consumed_rows]
    previous = [rows.get(alias, r) for alias in q['legacyIds'] for r in q['legacyReviews'] if r['questionId'] == alias]
    previous.extend(rows[alias] for alias in q['legacyIds'] if alias in rows and not any(r['questionId'] == alias for r in previous))
    history[q['id']] = {r['questionId']: r for r in previous}
    if review_state.get('sampler') == 'question-review-sampler-v2' and q['id'] in rows:
        review = rows[q['id']]
        history[q['id']].update({r['questionId']: r for r in review.get('presentationReviews', [])})
        initial_reviews[q['id']] = {'rating': '' if review.get('rating') is None else str(review['rating']),
            'modification': review.get('modification', '')}
        continue
    ratings = {r['rating'] for r in previous if r.get('rating') is not None}
    comments = list(dict.fromkeys(r.get('modification', '') for r in previous if r.get('modification')))
    if previous:
        initial_reviews[q['id']] = {'rating': str(next(iter(ratings))) if len(ratings) == 1 else '', 'modification': '\n'.join(comments)}
initial = json.dumps({'reviews': initial_reviews, 'history': history, 'consumed': consumed,
    'generalComments': review_state.get('generalComments', [])}, ensure_ascii=False).replace('</', '<\\/')
page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Question review sampler</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101725;color:#eef3ff;font:17px system-ui,sans-serif;max-width:1150px;padding:20px;margin-inline:auto}button,input,select,textarea{font:inherit;color:inherit;background:#202f44;border:1px solid #526780;border-radius:9px;padding:10px}button{cursor:pointer}.top{position:sticky;top:0;background:#101725ee;backdrop-filter:blur(10px);z-index:3;padding:10px 0}.filters,.nav{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}.filters input{flex:1;min-width:230px}.counter{margin-left:auto;color:#c6d6eb}.card{background:#1b293c;border:1px solid #405674;border-radius:16px;padding:clamp(16px,3vw,30px);margin-top:18px}.meta{color:#b9c9dc;font-size:14px}.meta span{display:inline-block;margin:0 10px 8px 0}.question{font-size:clamp(22px,3.2vw,34px);line-height:1.3;margin:18px 0;font-weight:700;white-space:pre-wrap}.sub{font-size:20px;color:#d4e1f3;white-space:pre-wrap}.prompt-image{display:block;max-width:min(100%,650px);max-height:420px;object-fit:contain;background:#0e1723;border-radius:10px;margin:18px auto}.section{background:#24354a;border-radius:11px;padding:14px 18px;margin:12px 0}.section h3{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:#9fcfff;margin:0 0 8px}.section p,.section li{line-height:1.5;white-space:pre-wrap}.option{padding:9px 12px;border-radius:8px;background:#1a2637;margin:6px 0}.correct{border:2px solid #65d99b;background:#16382e}.controls{border-top:1px solid #405674;margin-top:22px;padding-top:20px;display:grid;grid-template-columns:minmax(250px,1fr) minmax(300px,2fr);gap:18px}.rating-options{display:flex;gap:8px;flex-wrap:wrap}.rating-options label{display:flex;align-items:center;gap:5px;background:#24354a;padding:10px 13px;border-radius:9px;cursor:pointer}.rating-options input{accent-color:#65d99b}.rating-help{color:#b9c9dc;font-size:13px;margin-top:8px}.controls textarea{width:100%;min-height:125px;resize:vertical}.buttons{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}.status{color:#8fe5b0;align-self:center}.empty{padding:40px;text-align:center;color:#c3d2e4}
.meta span{max-width:100%;overflow-wrap:anywhere}.section li{overflow-wrap:anywhere}@media(max-width:700px){.top{position:static}.controls{grid-template-columns:1fr}body{padding:14px}h1{font-size:26px}}
.review-map{position:relative;width:100%;max-width:650px;margin:18px auto}.review-map svg,.review-map img{display:block;width:100%;height:auto}.map-marker{position:absolute;transform:translate(-50%,-50%);background:#172b42;border:2px solid white;border-radius:50%;width:36px;height:36px;display:grid;place-items:center;font-weight:700}.map-marker.correct{background:#176842;border-color:#8af0ad}
</style><div class="top"><h1>Question bank review</h1><p>One entry per question. Choose its play presentation within the card.</p><div class="filters"><input id="search" type="search" placeholder="Search topic, question, answer…"><select id="category"><option value="">All topics</option></select><select id="status"><option value="all">All questions</option><option value="unreviewed">Not reviewed</option><option value="reviewed">Reviewed</option><option value="needs">Rated 0 · Needs review</option><option value="modified">Has modification note</option></select><select id="ratingFilter"><option value="all">Any rating</option><option value="unrated">Unrated</option><option value="0">Rating 0 · Needs review</option><option value="1">Rating 1 · Very easy</option><option value="2">Rating 2 · Easy</option><option value="3">Rating 3 · Moderate</option><option value="4">Rating 4 · Difficult</option><option value="5">Rating 5 · Very difficult</option></select><span class="counter" id="counter"></span></div><details class="general"><summary>General review notes</summary><p>These reminders stay with the exported feedback. Edit them if needed.</p><textarea id="generalNotes"></textarea></details><div class="nav"><button id="prev">← Previous</button><button id="next">Next →</button><button id="nextTodo">Next unreviewed</button><button id="export">Export review</button><button id="import">Load review JSON</button><input id="file" type="file" accept="application/json" hidden><span class="status" id="saved"></span></div></div><main id="main"></main>
<script>
SAMPLER_SCRIPT
</script></html>'''.replace("SAMPLER_SCRIPT", (ROOT / "build/question-review-sampler.cjs").read_text(encoding="utf-8").replace("QUESTION_DATA", data).replace("INITIAL_STATE", initial))
(OUT / "sampler.html").write_text(page, encoding="utf-8")

print(json.dumps({
    "questions": len(questions),
    "presentations": sum(len(q["presentations"]) for q in questions),
    "questionsWithImages": sum(bool(q["image"]) for q in questions),
    "imagesCopied": images_copied,
    "missingImages": len(missing_images),
    "sampler": str(OUT / "sampler.html"),
    "manifest": str(OUT / "manifest.json"),
}, ensure_ascii=False, indent=2))
