"""Apply the latest v2 review directly to canonical storage; preserve historical data."""
import copy
import json
import shutil
from canonical_question_bank import ROOT, PATH, BANK, read_bank, materialize, merge_entries, answers, validate, identity

tag = '2026-10-24-1306'
backup = ROOT / 'review-backups'
source = ROOT.parent.parent / 'Downloads/question-review-feedback (3).json'
if not source.exists():
    from pathlib import Path
    source = Path.home() / 'Downloads/question-review-feedback (3).json'
data = json.loads(source.read_text(encoding='utf-8-sig'))
assert data['sampler'] == 'question-review-sampler-v2'
shutil.copyfile(source, backup / f'question-review-feedback-{tag}-raw.json')
bank = read_bank()
baseline = backup / f'question-bank-before-review-{tag}.json'
if not baseline.exists():
    shutil.copyfile(PATH, baseline)
if tag in bank.get('appliedReviews', []):
    raise SystemExit('This review has already been applied; refusing to overwrite later authoring.')
rows = {r['questionId']: copy.deepcopy(r) for r in data['reviews']}
handled = set()
pending = {'lib-chronologie-odyssee-episodes-20261012-05'}
patches = {
    'us-societe-crises-et-culture-20261010-01': {'options': ['A — L’Express abolitionniste', 'B — Le Chemin de fer clandestin (Underground Railroad)', 'C — Le Freedom Trail', 'D — L’American Colonization Society'], 'correctOptionIndex': 1},
    'lib-qcm-devinettes-20261012-01': {'prompt': 'Trois boîtes contiennent respectivement seulement des pommes, seulement des oranges et un mélange des deux. Leurs étiquettes « pommes », « oranges » et « mélange » sont toutes fausses. Quelle boîte faut-il ouvrir en premier, en regardant un seul fruit, pour déduire le contenu des trois boîtes ?'},
    'lib-qcm-devinettes-20261012-05': {'prompt': 'Dans une famille, cinq garçons ont chacun une sœur. Combien d’enfants cette famille compte-t-elle au minimum ?'},
    'lib-qcm-explorateurs-20261012-05': {'prompt': 'Je lance l’expédition qui accomplit le premier tour du monde et qui est menée à terme par Elcano en 1522. Qui suis-je ?'},
    'lib-qsj-logique-20261012-01': {'clues': ['Je suis un nombre entier.', 'M’ajouter à un nombre ne le change pas.', 'Je représente l’absence de quantité.', 'Je ne suis ni positif ni négatif.']},
    'lib-qsj-logique-20261012-03': {'clues': ['Je suis un nombre entier.', 'Je peux être partagé en deux groupes égaux sans reste.', '2, 4 et 6 sont des exemples de moi.', 'En écriture décimale, mon chiffre des unités est 0, 2, 4, 6 ou 8.']},
    'lib-qsj-marvel-20261012-05': {'clues': ['Je voyage avec les Gardiens de la Galaxie.', 'Rocket est mon compagnon.', 'Mon corps ressemble à un arbre.', 'Mon vocabulaire se réduit habituellement à une seule phrase.']},
    'lib-qsj-odyssee-20261012-05': {'clues': ['Dans l’art grec, nous avons un corps d’oiseau et une tête de femme.', 'Homère nous situe dans un pré entouré d’ossements de marins.', 'Notre chant attire les navigateurs vers leur perte.', 'Ulysse nous écoute attaché au mât, pendant que ses compagnons ont les oreilles bouchées avec de la cire.']},
    'revolution-culture-et-mobilisation-20261010-01': {'options': ['A — Des pantalons courts s’arrêtant au genou', 'B — Des pantalons longs descendant aux chevilles', 'C — Des sous-vêtements portés sous le pantalon', 'D — Des bandes de tissu enroulées autour des jambes'], 'correctOptionIndex': 0},
    'test-04-chronologie-q1': {'prompt': 'Classez ces étapes de l’exploration et de la colonisation européennes du Canada, de la plus ancienne à la plus récente.', 'items': [{'id': 'item-0', 'text': 'Voyage de Jean Cabot vers les côtes de l’Amérique du Nord'}, {'id': 'item-1', 'text': 'Fondation de Québec par Samuel de Champlain'}, {'id': 'item-2', 'text': 'Premier voyage de Jacques Cartier au Canada'}]},
}
for e in bank['questions']:
    row = rows.get(e['id'], {})
    comment = row.get('modification', '')
    if not comment or e['id'] in pending:
        continue
    image_edit = 'picture' in comment.lower()
    explicit = patches.get(e['id'], {})
    obsolete = 'obsolete format' in comment.lower()
    if not (image_edit or explicit or obsolete):
        continue
    projected = []
    for p in e['presentations']:
        q = materialize(e, p)
        if image_edit:
            q.pop('imageUrl', None)
            if isinstance(q.get('subQuestion'), dict):
                q['subQuestion'].pop('imageUrl', None)
        patch = dict(explicit)
        if 'clues' in patch and q['kind'] != 'guessWho':
            patch.pop('clues')
        if 'options' in patch and q['kind'] != 'multipleChoice':
            patch.pop('options')
            patch.pop('correctOptionIndex', None)
        q.update(patch)
        if obsolete and q['kind'] == 'speedRace':
            sub = q.pop('subQuestion')
            q.update({k: v for k, v in sub.items() if k not in ('id', 'category', 'basePoints', 'penaltyPoints')})
            q['kind'] = 'multipleChoice'
            p = dict(p, label='Choix multiples', answerMode='SIMULTANEOUS')
        projected.append((q, p))
    # Recompose the shared record, keeping all authored presentation IDs.
    shared = dict(e)
    first = projected[0][0]
    shared['prompt'] = first['prompt']
    shared['answers'] = list(dict.fromkeys(a for q, _ in projected for a in answers(q)))
    shared['content'] = {}
    shared['presentations'] = [dict(p, content={k: v for k, v in q.items() if k not in ('id', 'category', 'conceptId')}) for q, p in projected]
    e.clear(); e.update(merge_entries([shared]))
    handled.add(e['id'])

# Audited remaining named-target identification overlaps. Marine turtles and the
# mythological Great Turtle remain distinct, as do planet/deity homonyms.
groups = [
    ['lib-buzzer-geographie-villes-20261012-04', 'lib-qsj-geographie-villes-20261012-03'],
    ['test-02-buzzer-q1', 'lib-qsj-geographie-villes-20261012-01'],
    ['cinema-buzzer-univers-20261011-07', 'lib-qsj-animaux-marins-20261012-05'],
    ['lib-buzzer-legendes-france-20261012-02', 'lib-qsj-legendes-france-20261012-03'],
    ['lib-qcm-recits-autochtones-20261012-01', 'lib-qsj-recits-autochtones-20261012-05'],
]
# Speed-race wrappers are ordinary authored MC presentations of existing facts.
seen = {}
for e in bank['questions']:
    for p in e['presentations']:
        q = materialize(e, p)
        if q['kind'] != 'multipleChoice':
            continue
        plain = dict(q); plain.pop('conceptId', None)
        key = identity(plain)
        if key in seen and seen[key] != e['id']:
            groups.append([seen[key], e['id']])
        seen[key] = e['id']
groups.append(['lib-qcm-science-generale-20261012-01', 'test-08-speed-race-q1'])
merged = []
for ids in groups:
    candidates = [e for e in bank['questions'] if set(ids) & set(e['legacyIds'])]
    if len(candidates) < 2:
        continue
    combined = merge_entries(candidates)
    chosen = {e['id'] for e in candidates}
    bank['questions'] = [combined if e['id'] == combined['id'] else e for e in bank['questions'] if e['id'] not in chosen or e['id'] == combined['id']]
    merged.append(sorted(chosen))

for id in handled:
    rows[id]['modification'] = ''
    if rows[id].get('rating') == 0:
        rows[id]['rating'] = None
processed = dict(data, reviews=[])
for e in bank['questions']:
    old = [rows[id] for id in e['legacyIds'] if id in rows]
    if not old:
        continue
    ratings = {r['rating'] for r in old if r.get('rating') is not None}
    history = {r['questionId']: r for r0 in old for r in r0.get('presentationReviews', [])}
    if len(old) > 1:
        for r in old:
            history[r['questionId']] = {k: v for k, v in r.items() if k != 'presentationReviews'}
    review = {'questionId': e['id'], 'legacyIds': e['legacyIds'], 'topics': e['topics'], 'prompt': e['prompt'],
        'rating': next(iter(ratings)) if len(ratings) == 1 else None,
        'modification': '\n'.join(dict.fromkeys(r.get('modification', '') for r in old if r.get('modification'))),
        'presentationReviews': list(history.values())}
    e['review'] = {k: v for k, v in review.items() if k not in ('presentationReviews', 'legacyIds', 'topics')}
    e['reviewHistory'] = [{k: v for k, v in r.items() if k != 'presentationReviews'} for r in old]
    processed['reviews'].append(review)
    if e['id'] == 'lib-qsj-odyssee-20261012-05':
        e['sources'] = ['https://www.metmuseum.org/art/collection/search/254674', 'https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0218%3Abook%3D12']
bank.setdefault('appliedReviews', []).append(tag)
bank.setdefault('revisionHistory', []).append({'id': tag, 'baseline': f'review-backups/question-bank-before-review-{tag}.json',
    'handledComments': sorted(handled), 'mergedGroups': merged})
validate(bank)
PATH.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
output = backup / f'question-review-feedback-{tag}-processed.json'
output.write_text(json.dumps(processed, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
shutil.copyfile(output, ROOT / 'build/question-review-sampler/review-state.json')
print(f'Handled {len(handled)} comments; merged {len(merged)} groups; {len(bank["questions"])} unique questions.')
print('Pending:', [(r['questionId'], r['modification']) for r in processed['reviews'] if r.get('modification')])
