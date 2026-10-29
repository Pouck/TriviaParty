"""Canonical question storage. Legacy packages are import/export artifacts only."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'game-library/bank'
PATH = BANK / 'questions.json'


def normalize(value):
    value = re.sub(r'^[A-Z]\s*[—–:.)-]\s*', '', value.strip())
    value = ''.join(c for c in unicodedata.normalize('NFD', value.casefold()) if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[a-z0-9]+', value))


def answers(question):
    if question['kind'] in ('multipleChoice', 'mapChoice'):
        index = question.get('correctOptionIndex', -1)
        if not 0 <= index < len(question.get('options', [])):
            return []
        answer = question['options'][index]
        return [answer['label']] if isinstance(answer, dict) else [re.sub(r'^[A-Z]\s*[—–:.)-]\s*', '', answer)]
    return question.get('acceptableAnswers', [])


def identity(question):
    if question.get('conceptId'):
        return 'concept:' + question['conceptId']
    kind = question['kind']
    if kind in ('multipleChoice', 'textAnswer'):
        return ('direct', normalize(question['prompt']), normalize(next(iter(answers(question)), '')))
    # No answer-only merging: different facts may have the same answer.
    content = {k: v for k, v in question.items() if k not in ('id', 'category', 'basePoints', 'penaltyPoints', 'imageUrl')}
    return (kind, json.dumps(content, sort_keys=True, ensure_ascii=False))


def read_bank():
    bank = json.loads(PATH.read_text(encoding='utf-8'))
    validate(bank)
    return bank


def sampler_questions():
    """One review card per entry, with playable projections nested under it."""
    bank = read_bank()
    output = []
    for entry in bank['questions']:
        presentations = []
        for p in entry['presentations']:
            q = materialize(entry, p)
            items = q.get('items', [])
            by_id = {str(i['id']): i for i in items}
            presentations.append({'presentationId': p['id'], 'label': p['label'],
                'kind': q['kind'], 'answerMode': p['answerMode'], 'prompt': q['prompt'],
                'subQuestion': q.get('subQuestion', ''),
                'options': [o['label'] if isinstance(o, dict) else o for o in q.get('options', [])],
                'mapOptions': q.get('options', []) if q['kind'] == 'mapChoice' else [],
                'correctOptionIndex': q.get('correctOptionIndex'), 'answers': answers(q),
                'explanation': q.get('explanation', ''), 'clues': q.get('clues', []), 'clueCount': len(q.get('clues', [])), 'items': items,
                'correctOrder': [by_id[str(i)] for i in q.get('correctOrderIds', [])],
                'randomVariants': q.get('randomVariants', []),
                'image': 'assets/' + q['imageUrl'] if q.get('imageUrl') else '',
                'imageSource': q.get('imageUrl', '')})
        # The free-response projections are gameplay choices, not stored entries.
        for p in list(presentations):
            if p['kind'] == 'textAnswer':
                for mode, label in [('BUZZER', 'Buzzer'), ('WRITTEN', 'Réponses écrites')]:
                    if not any(x['answerMode'] == mode and x['kind'] == 'textAnswer' and x['prompt'] == p['prompt'] for x in presentations):
                        presentations.append(dict(p, presentationId=p['presentationId'] + ':' + mode, answerMode=mode, label=label))
            if p['kind'] == 'multipleChoice' and not p['randomVariants'] and not re.search(r'parmi|suivant|ci-dessous|lequel|laquelle', p['prompt'], re.I):
                for mode, label in [('BUZZER', 'Buzzer'), ('WRITTEN', 'Réponses écrites')]:
                    if not any(x['kind'] == 'textAnswer' and x['answerMode'] == mode and x['prompt'] == p['prompt'] for x in presentations):
                        presentations.append(dict(p, presentationId=p['presentationId'] + ':' + mode,
                            kind='textAnswer', options=[], correctOptionIndex=None, answerMode=mode, label=label))
            if p['kind'] == 'guessWho':
                mode = 'WRITTEN' if p['answerMode'] == 'BUZZER' else 'BUZZER'
                if not any(x['kind'] == 'guessWho' and x['answerMode'] == mode and x['clues'] == p['clues'] for x in presentations):
                    presentations.append(dict(p, presentationId=p['presentationId'] + ':' + mode,
                        answerMode=mode, label='Qui suis-je ? écrit' if mode == 'WRITTEN' else 'Qui suis-je ?'))
        # A play format is one choice, regardless of historical wording. Prefer
        # authored free-response content to a projection generated from QCM.
        # All authored alternatives remain losslessly stored in the bank.
        groups = {}
        for p in presentations:
            groups.setdefault((p['kind'], p['answerMode']), []).append(p)
        unique = []
        for (kind, mode), variants in groups.items():
            selected = next((p for p in variants if ':' not in p['presentationId']), variants[0])
            # A converted authored text answer is preferable to converted QCM.
            if kind == 'textAnswer' and ':' in selected['presentationId']:
                authored_text_ids = {p['id'] for p in entry['presentations'] if p['content']['kind'] == 'textAnswer'}
                selected = next((p for p in variants if p['presentationId'].split(':')[0] in authored_text_ids), selected)
            selected = dict(selected)
            if kind == 'textAnswer':
                selected['label'] = 'Réponses écrites' if mode == 'WRITTEN' else 'Buzzer'
                selected['answers'] = list(dict.fromkeys(a for p in variants for a in p['answers']))
            elif kind == 'multipleChoice':
                selected['label'] = 'Choix multiples'
            elif kind == 'guessWho':
                selected['label'] = 'Qui suis-je ? écrit' if mode == 'WRITTEN' else 'Qui suis-je ?'
            unique.append(selected)
        output.append(dict(unique[0], id=entry['id'], category=' · '.join(entry['topics']),
            topics=entry['topics'], legacyIds=entry['legacyIds'], presentations=unique,
            legacyReviews=entry.get('legacyReviews', []), packageId='', packageName=''))
    return output


def validate(bank):
    assert bank['schemaVersion'] == 2
    entries = bank['questions']
    ids, aliases = set(), set()
    for entry in entries:
        assert entry['id'] not in ids, entry['id']
        ids.add(entry['id'])
        assert entry['topics'] and entry['presentations']
        assert entry['id'] in entry['legacyIds']
        for alias in entry['legacyIds']:
            assert alias not in aliases, alias
            aliases.add(alias)
        assert {p['id'] for p in entry['presentations']} == set(entry['legacyIds'])
        for presentation in entry['presentations']:
            q = materialize(entry, presentation)
            assert q['kind'] and q['prompt']
            image = q.get('imageUrl')
            if image:
                assert not Path(image).is_absolute() and '..' not in Path(image).parts
                assert (BANK / image).is_file(), image
    return bank


def materialize(entry, presentation):
    """Create an ephemeral game question; storage retains a single shared record."""
    q = dict(entry.get('content', {}))
    q.update(presentation['content'])
    q.update(id=entry['id'], category=presentation['legacyCategory'])
    q.setdefault('prompt', entry['prompt'])
    if q['kind'] in ('textAnswer', 'guessWho'):
        q.setdefault('acceptableAnswers', entry['answers'])
    if q['kind'] in ('textAnswer', 'multipleChoice', 'guessWho'):
        q['conceptId'] = entry['id']
    if entry.get('explanation'):
        q.setdefault('explanation', entry['explanation'])
    return q


def migrate_legacy():
    """One-time import; refuse to overwrite an authored canonical bank."""
    assert not PATH.exists(), 'Canonical bank already exists. Edit it directly; do not rebuild it from old packages.'
    reviews_path = ROOT / 'review-backups/question-review-feedback-2026-10-24-processed.json'
    review_data = json.loads(reviews_path.read_text(encoding='utf-8'))
    reviews = {r['questionId']: r for r in review_data['reviews']}
    records = []
    for bank_path in sorted((ROOT / 'game-library/current/sources').glob('*/question-bank/*.json')):
        source = json.loads(bank_path.read_text(encoding='utf-8'))
        package = bank_path.parent.parent
        for original in source['questions']:
            question = copy.deepcopy(original)
            for q in [question, question.get('subQuestion', {})]:
                image = q.get('imageUrl')
                if image:
                    payload = (package / image).read_bytes()
                    filename = hashlib.sha256(payload).hexdigest()[:24] + Path(image).suffix.lower()
                    destination = BANK / 'media' / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if not destination.exists():
                        destination.write_bytes(payload)
                    q['imageUrl'] = 'media/' + filename
            records.append((question, source, package.name))

    # Union explicit concept mappings with exact cross-format duplicates, including
    # copies in historical test sets. Preserve every alias and presentation.
    parent = {q['id']: q['id'] for q, _, _ in records}
    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key
    seen = {}
    for q, _, _ in records:
        keys = [identity(q)]
        plain = dict(q)
        plain.pop('conceptId', None)
        keys.append(identity(plain))
        for key in keys:
            if key in seen:
                parent[root(q['id'])] = root(seen[key])
            seen[key] = q['id']
    groups = {}
    for record in records:
        groups.setdefault(root(record[0]['id']), []).append(record)
    entries = []
    for group in groups.values():
        # Stable curated IDs take precedence; keep historical IDs as aliases.
        preferred = next((q.get('conceptId') for q, _, _ in group if q.get('conceptId')), group[0][0]['id'])
        first, first_source, _ = next((r for r in group if r[0]['id'] == preferred), group[0])
        canonical_answers = list(dict.fromkeys(a for q, _, _ in group for a in answers(q)))
        # Store only fields shared by every presentation at the entry level.
        excluded = {'id', 'category', 'kind', 'conceptId', 'prompt', 'acceptableAnswers', 'explanation'}
        common = {k: v for k, v in first.items() if k not in excluded and all(q.get(k) == v for q, _, _ in group)}
        entry = {'id': preferred, 'legacyIds': [q['id'] for q, _, _ in group],
                 'topics': list(dict.fromkeys(s.get('subject') or s['category'].split(' — ')[0] for _, s, _ in group)),
                 'prompt': first['prompt'], 'answers': canonical_answers, 'content': common,
                 'presentations': [], 'legacyReviews': [reviews[q['id']] for q, _, _ in group if q['id'] in reviews]}
        if first.get('explanation'):
            entry['explanation'] = first['explanation']
        for q, source, package_id in group:
            content = {k: v for k, v in q.items() if k not in ('id', 'category', 'conceptId') and (k not in common or common[k] != v)}
            if content.get('prompt') == entry['prompt']:
                content.pop('prompt')
            if content.get('acceptableAnswers') == canonical_answers:
                content.pop('acceptableAnswers')
            if content.get('explanation') == entry.get('explanation'):
                content.pop('explanation', None)
            entry['presentations'].append({'id': q['id'], 'label': source['questionTypes'][0],
                'answerMode': source.get('answerMode', 'SIMULTANEOUS'), 'topic': source.get('subject') or entry['topics'][0],
                'legacyCategory': source['category'], 'legacyPackageId': package_id, 'content': content})
        entries.append(entry)
    result = {'schemaVersion': 2, 'questions': entries, 'generalComments': review_data.get('generalComments', [])}
    validate(result)
    PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = {'legacyQuestionCount': len(records), 'questionCount': len(entries),
              'mergedEntries': len(records) - len(entries),
              'groups': [{'id': e['id'], 'legacyIds': e['legacyIds']} for e in entries if len(e['legacyIds']) > 1]}
    (BANK / 'migration.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'groups'}, indent=2))


def merge_entries(entries):
    base = entries[0]
    projected = [(materialize(e, p), p) for e in entries for p in e['presentations']]
    excluded = {'id', 'category', 'kind', 'conceptId', 'prompt', 'acceptableAnswers', 'explanation'}
    first = projected[0][0]
    common = {k: v for k, v in first.items() if k not in excluded and all(q.get(k) == v for q, _ in projected)}
    result = dict(base, legacyIds=list(dict.fromkeys(i for e in entries for i in e['legacyIds'])),
                  topics=list(dict.fromkeys(t for e in entries for t in e['topics'])), content=common,
                  answers=list(dict.fromkeys(a for e in entries for a in e['answers'])),
                  legacyReviews=[r for e in entries for r in e.get('legacyReviews', [])], presentations=[])
    for q, presentation in projected:
        content = {k: v for k, v in q.items() if k not in ('id', 'category', 'conceptId') and (k not in common or common[k] != v)}
        if content.get('prompt') == result['prompt']:
            content.pop('prompt')
        if content.get('acceptableAnswers') == result['answers']:
            content.pop('acceptableAnswers')
        if content.get('explanation') == result.get('explanation'):
            content.pop('explanation', None)
        result['presentations'].append(dict(presentation, content=content))
    return result


if __name__ == '__main__':
    migrate_legacy()
