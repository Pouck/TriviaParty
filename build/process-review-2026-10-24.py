"""Prepare durable review patches and a processed copy; preserve the original export."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = Path.home() / 'Downloads/question-review-feedback (2).json'
data = json.loads(source.read_text(encoding='utf-8-sig'))
backup = ROOT / 'review-backups'
backup.mkdir(exist_ok=True)
shutil.copyfile(source, backup / 'question-review-feedback-2026-10-24-raw.json')
patches = {}
handled = set()
previous = json.loads((backup / 'question-review-feedback-2026-10-23-raw.json').read_text(encoding='utf-8-sig'))
previous_processed = json.loads((backup / 'question-review-feedback-2026-10-23-processed.json').read_text(encoding='utf-8-sig'))
old_comments = {r['questionId']: r.get('modification') for r in previous['reviews']}
cleared_before = {r['questionId'] for r in previous_processed['reviews'] if not r.get('modification')}
for review in data['reviews']:
    qid, comment = review['questionId'], review.get('modification', '').strip()
    if not comment:
        continue
    if qid in cleared_before and comment == (old_comments.get(qid) or '').strip():
        handled.add(qid)
    elif 'picture' in comment.lower() or 'image' in comment.lower():
        patches[qid] = {'_removeImage': True}
        handled.add(qid)
    elif comment == 'too easy':
        # Keep easy material; the planner already limits each package to one rating 1.
        if review.get('rating') in (None, 0):
            review['rating'] = 1
        handled.add(qid)

edits = {
    'lib-buzzer-jeux-video-20261012-03': {'prompt': 'Comment s’appelle le frère de Mario ?'},
    'lib-buzzer-jeux-video-20261012-05': {'prompt': 'Dans quelle série de jeux de course peut-on lancer des carapaces et des peaux de banane sur ses adversaires ?'},
    'lib-buzzer-legendes-france-20261012-04': {'prompt': 'Quel nom donne-t-on à l’animal mystérieux tenu pour responsable d’attaques meurtrières dans le sud de la France entre 1764 et 1767 ?'},
    'lib-buzzer-recits-autochtones-20261012-01': {'prompt': 'Dans le récit oneida, d’où tombe la femme que des oiseaux portent jusqu’à une tortue ?'},
    'lib-qcm-explorateurs-20261012-05': {'prompt': 'Quel navigateur lance l’expédition qui accomplit le premier tour du monde, achevé par Elcano en 1522 ?', 'options': ['A — Jacques Cartier', 'B — Fernand de Magellan', 'C — James Cook', 'D — John Franklin'], 'correctOptionIndex': 1},
    'lib-qcm-geographie-monde-20261012-04': {'prompt': 'Quel pays abrite le mont Fuji ?'},
    'lib-qcm-devinettes-20261012-01': {'prompt': 'Trois boîtes contiennent respectivement uniquement des pommes, uniquement des oranges, et un mélange des deux. Leurs étiquettes « pommes », « oranges » et « mélange » sont toutes fausses. Dans quelle boîte faut-il tirer un seul fruit, sans regarder à l’intérieur, pour identifier le contenu des trois boîtes ?', 'explanation': 'La boîte étiquetée « mélange » contient un seul type de fruit, puisque son étiquette est fausse. Le fruit tiré révèle ce type. Les deux autres contenus se déduisent alors en gardant leurs étiquettes fausses.'},
    'lib-qcm-devinettes-20261012-03': {'explanation': 'Les écarts sont +4, +6, +8, +10, puis +12 : 30 + 12 = 42. Chaque terme est le produit de deux entiers consécutifs : 1×2, 2×3, …, 6×7.'},
    'lib-qcm-devinettes-20261012-05': {'prompt': 'Dans une famille, cinq garçons ont chacun une sœur. Il n’y a qu’une seule fille. Combien d’enfants compte cette famille ?', 'explanation': 'Les cinq garçons ont tous pour sœur l’unique fille de la famille : 5 + 1 = 6 enfants.'},
}
for qid, patch in edits.items():
    patches.setdefault(qid, {}).update(patch)
    handled.add(qid)

# Curated identities: equivalent knowledge across topics and authored formats.
# Equal answers alone are insufficient (e.g. London/Buckingham vs London/Thames).
groups = [
    ['architecture-buzzer-europe-20261011-04', 'lib-qcm-histoire-france-generale-20261012-01', 'test-20261012-buzzer-complement-4'],
    ['architecture-buzzer-monde-20261011-03', 'lib-qcm-histoire-mondiale-generale-20261012-03'],
    ['canada-buzzer-premieres-20261011-08', 'canada-inventions-medical-20261011-01', 'lib-qcm-inventions-canada-20261012-02'],
    ['canada-inventions-quotidien-20261011-01', 'lib-buzzer-inventions-canada-20261012-04', 'lib-qcm-inventions-canada-20261012-01'],
    ['canada-inventions-quotidien-20261011-04', 'lib-buzzer-inventions-canada-20261012-02'],
    ['canada-inventions-quotidien-20261011-05', 'lib-buzzer-inventions-canada-20261012-01'],
    ['canada-inventions-technologie-20261011-04', 'lib-buzzer-inventions-canada-20261012-03'],
    ['cinema-buzzer-titres-heros-20261011-07', 'q15'],
    ['cinema-buzzer-univers-20261011-03', 'lib-buzzer-dc-20261012-01'],
    ['cinema-qcm-coulisses-20261011-01', 'lib-qcm-musique-ecran-20261012-01'],
    ['culture-qcm-americaine-oeuvres-20261010-07', 'lib-buzzer-litterature-americaine-20261012-04'],
    ['culture-qcm-anglophone-personnages-20261010-01', 'lib-buzzer-litterature-anglaise-20261012-03'],
    ['culture-qcm-anglophone-personnages-20261010-03', 'lib-buzzer-litterature-anglaise-20261012-01'],
    ['culture-qcm-anglophone-personnages-20261010-05', 'lib-buzzer-litterature-anglaise-20261012-04'],
    ['culture-qcm-anglophone-personnages-20261010-10', 'lib-buzzer-litterature-anglaise-20261012-02'],
    ['culture-qcm-francaise-personnages-20261010-01', 'lib-buzzer-litterature-france-20261012-03'],
    ['us-societe-crises-et-culture-20261010-04', 'lib-buzzer-histoire-etats-unis-20261012-03'],
    ['lib-buzzer-explorateurs-20261012-03', 'lib-qcm-explorateurs-20261012-01'],
    ['lib-buzzer-explorateurs-20261012-04', 'lib-qcm-explorateurs-20261012-02'],
    ['lib-buzzer-histoire-etats-unis-20261012-04', 'lib-buzzer-histoire-mondiale-generale-20261012-03'],
    ['lib-buzzer-histoire-france-generale-20261012-04', 'lib-qcm-histoire-france-generale-20261012-03'],
    ['lib-buzzer-inventions-canada-20261012-05', 'lib-qcm-inventions-canada-20261012-05'],
    ['lib-buzzer-legendes-france-20261012-01', 'lib-qcm-legendes-france-20261012-01'],
    ['lib-buzzer-litterature-quebec-20261012-01', 'lib-qcm-litterature-quebec-20261012-01'],
    ['lib-buzzer-litterature-quebec-20261012-03', 'lib-qcm-litterature-quebec-20261012-04'],
    ['lib-buzzer-musique-quebec-20261012-01', 'lib-qcm-musique-ecran-20261012-02'],
    ['lib-buzzer-recits-autochtones-20261012-03', 'lib-qcm-recits-autochtones-20261012-02'],
    ['lib-buzzer-devinettes-20261012-01', 'lib-buzzer-logique-20261012-03'],
    ['lib-qcm-jeux-video-20261012-02', 'q21'],
    ['q6', 'lib-qcm-jeux-video-20261012-05'],
]
for group in groups:
    for qid in group:
        patches.setdefault(qid, {})['conceptId'] = group[0]
handled.add('lib-buzzer-logique-20261012-03')

(ROOT / 'build/question-review-revisions-2026-10-24.json').write_text(json.dumps(patches, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for review in data['reviews']:
    if review['questionId'] in handled:
        review['modification'] = ''
        if review.get('rating') == 0:
            review['rating'] = None
processed = backup / 'question-review-feedback-2026-10-24-processed.json'
processed.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Handled {len(handled)} comments; {len(groups)} duplicate groups; pending:')
for review in data['reviews']:
    if review.get('modification'):
        print(review['questionId'], review['modification'])
