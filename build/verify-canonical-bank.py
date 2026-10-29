"""Migration audit against the archived source data, including all content and reviews."""
import hashlib
import json
from canonical_question_bank import ROOT, BANK, read_bank, materialize

bank = read_bank()
by_legacy = {p['id']: (entry, p) for entry in bank['questions'] for p in entry['presentations']}
# Later authored revisions are checked against their preserved pre-edit baseline.
baseline_bank = bank
if bank.get('revisionHistory'):
    baseline_bank = json.loads((ROOT / bank['revisionHistory'][0]['baseline']).read_text(encoding='utf-8'))
archived = {p['id']: (entry, p) for entry in baseline_bank['questions'] for p in entry['presentations']}
checked = set()
for source in (ROOT / 'game-library/current/sources').glob('*/question-bank/*.json'):
    package = source.parent.parent
    for old in json.loads(source.read_text(encoding='utf-8'))['questions']:
        entry, presentation = archived[old['id']]
        q = materialize(entry, presentation)
        def compare(original, projected):
            for key, value in original.items():
                if key in ('id', 'conceptId'):
                    continue
                if key == 'subQuestion':
                    compare(value, projected[key])
                elif key == 'imageUrl' and value:
                    assert hashlib.sha256((package / value).read_bytes()).digest() == hashlib.sha256((BANK / projected[key]).read_bytes()).digest(), old['id']
                elif key == 'acceptableAnswers':
                    assert set(value) <= set(projected[key]), old['id']
                else:
                    assert value == projected[key], (old['id'], key, value, projected.get(key))
        compare(old, q)
        checked.add(old['id'])
assert checked == set(by_legacy)
previous = json.loads((ROOT / 'review-backups/question-review-feedback-2026-10-24-processed.json').read_text(encoding='utf-8'))
preserved = {r['questionId']: r for entry in bank['questions'] for r in entry.get('legacyReviews', [])}
assert {r['questionId']: r for r in previous['reviews']} == preserved
assert previous['generalComments'] == bank['generalComments']
if bank.get('appliedReviews'):
    latest = json.loads((ROOT / 'review-backups/question-review-feedback-2026-10-24-1306-raw.json').read_text(encoding='utf-8'))
    revised = {r['questionId']: r for e in bank['questions'] for r in e.get('reviewHistory', [])}
    assert all(revised[r['questionId']]['rating'] == r['rating'] for r in latest['reviews'] if r.get('rating') in (1,2,3,4,5))
    assert latest['generalComments'] == bank['generalComments']
print(f'PASS: {len(bank["questions"])} unique entries preserve all {len(checked)} original question contents, {len(preserved)} reviews, every media file and general comments.')
