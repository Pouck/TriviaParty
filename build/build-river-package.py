from pathlib import Path
import csv, json, zipfile
from quiz_choice_order import randomize_choices

root = Path('package-examples/geographie-2026-10-10')
package_id = 'geographie-fleuves-et-rivieres-20261010'
category_name = 'Géographie - Fleuves et rivières'
source = root/'sources'/package_id
items = [
    ('Quel cours d’eau traverse Bagdad, en Irak ?', ['Euphrate', 'Tigre', 'Jourdain', 'Karoun'], 1),
    ('Quel fleuve traverse Le Caire, en Égypte ?', ['Congo', 'Nil', 'Zambèze', 'Niger'], 1),
    ('Quel fleuve traverse Paris, en France ?', ['Loire', 'Rhône', 'Seine', 'Garonne'], 2),
    ('Quel fleuve traverse Rome, en Italie ?', ['Arno', 'Pô', 'Tibre', 'Rubicon'], 2),
    ('Quel fleuve traverse Londres, au Royaume-Uni ?', ['Severn', 'Tamise', 'Mersey', 'Clyde'], 1),
    ('Quel fleuve traverse à la fois Vienne, en Autriche, et Budapest, en Hongrie ?', ['Rhin', 'Elbe', 'Danube', 'Oder'], 2),
    ('Quel fleuve traverse Saint-Pétersbourg, en Russie ?', ['Volga', 'Neva', 'Don', 'Ob'], 1),
    ('Quel cours d’eau traverse Dublin, en Irlande ?', ['Shannon', 'Liffey', 'Lee', 'Boyne'], 1),
    ('Au bord de quel cours d’eau se trouve Perth, en Australie ?', ['Yarra', 'Murray', 'Swan', 'Darling'], 2),
    ('Quel cours d’eau traverse le centre de Shanghai, en Chine ?', ['Huang He (fleuve Jaune)', 'Yangzi Jiang (fleuve Bleu)', 'Zhu Jiang (rivière des Perles)', 'Huangpu'], 3),
    ('Quel fleuve borde Lisbonne, au Portugal ?', ['Douro', 'Èbre', 'Tage', 'Guadalquivir'], 2),
    ('Quel fleuve borde Kinshasa, en République démocratique du Congo ?', ['Nil', 'Niger', 'Congo', 'Orange'], 2),
]
questions = [dict(kind='multipleChoice', id=f'geo-fleuves-20261010-{i:02d}', category=category_name,
    prompt=prompt, basePoints=15, penaltyPoints=0,
    options=[f'{letter} — {name}' for letter, name in zip('ABCD', options)], correctOptionIndex=correct)
    for i, (prompt, options, correct) in enumerate(items, 1)]
game = dict(id=package_id, name=category_name,
    description='Identifiez les cours d’eau des grandes villes du monde. 12 questions à choix multiples. 15 secondes par question ; 15, 10 puis 5 points.',
    categoryPackages=[package_id], answerTimeSeconds=10,
    timingConfig=dict(secondsPerFlip=5, decayPercentagePerFlip=0.0, maxFlips=2, pointsDecayPerFlip=5))
randomize_choices(questions, package_id)
category = dict(category=category_name, answerMode='SIMULTANEOUS',
    questionTypes=['Choix multiples'], questions=questions)
for relative, data in [('game.json', game), (f'question-bank/{package_id}.json', category)]:
    target = source/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
archive = root/'geographie-fleuves-et-rivieres.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in sorted(source.rglob('*.json')):
        z.write(file, file.relative_to(source).as_posix())
with (root/'FLEUVES-QUESTIONS-ET-REPONSES.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Question', 'Texte', 'A', 'B', 'C', 'D', 'Bonne réponse'])
    for i, q in enumerate(questions, 1):
        writer.writerow([i, q['prompt'], *[option.split(' — ', 1)[1] for option in q['options']],
            q['options'][q['correctOptionIndex']]])
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert set(z.namelist()) == {'game.json', f'question-bank/{package_id}.json'}
assert len(questions) == 12 and len({q['id'] for q in questions}) == 12
print(archive.resolve())
