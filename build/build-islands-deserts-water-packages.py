from pathlib import Path
import csv, json, zipfile
from quiz_choice_order import randomize_choices

root = Path('package-examples/geographie-2026-10-10')
packages = {
    'iles-et-archipels': ('Îles et archipels', [
        ('Sur quelle île se trouve le cœur de Tokyo, la capitale du Japon ?',
         ['Hokkaido', 'Honshu', 'Kyushu', 'Shikoku'], 1),
        ('Sur quelle île de l’archipel d’Hawaï se trouve Honolulu ?',
         ['Maui', 'Hawaï (la Grande Île)', 'Oahu', 'Kauai'], 2),
        ('Quelle grande île se situe au sud-est de l’Inde ?',
         ['Maldives', 'Madagascar', 'Sri Lanka', 'Sumatra'], 2),
        ('Sur quelle île méditerranéenne se trouve Palerme ?',
         ['Sardaigne', 'Sicile', 'Corse', 'Chypre'], 1),
    ]),
    'deserts-et-paysages-arides': ('Déserts et paysages arides', [
        ('Dans quel désert se trouve Las Vegas, au Nevada ?',
         ['Désert de Sonora', 'Désert des Mojaves', 'Désert de Chihuahua', 'Désert du Grand Bassin'], 1),
        ('Quel désert côtier du nord du Chili est réputé être le désert non polaire le plus aride du monde ?',
         ['Désert de Patagonie', 'Désert d’Atacama', 'Désert de Sechura', 'Désert du Monte'], 1),
        ('Quel désert s’étend dans le sud de la Mongolie et le nord de la Chine, le long d’anciennes routes commerciales de la soie ?',
         ['Désert du Taklamakan', 'Désert de Gobi', 'Désert du Karakoum', 'Désert du Kyzylkoum'], 1),
        ('Quel désert de la péninsule Arabique comprend le Rub al-Khali, surnommé le « Quart Vide » ?',
         ['Désert de Syrie', 'Désert d’Arabie', 'Désert du Néguev', 'Désert du Thar'], 1),
    ]),
    'lacs-mers-et-golfes': ('Lacs, mers et golfes', [
        ('Quelle mer sépare la côte est de la Grande-Bretagne de l’Europe continentale ?',
         ['Mer Celtique', 'Mer du Nord', 'Mer Baltique', 'Manche'], 1),
        ('Quel grand lac africain est partagé entre la Tanzanie, l’Ouganda et le Kenya ?',
         ['Lac Tanganyika', 'Lac Victoria', 'Lac Malawi', 'Lac Turkana'], 1),
        ('Quelle vaste étendue d’eau salée, sans débouché sur l’océan, est bordée notamment par la Russie, l’Iran et le Kazakhstan ?',
         ['Mer Noire', 'Mer Caspienne', 'Mer d’Aral', 'Mer Morte'], 1),
        ('Sur la rive sud-ouest de quel Grand Lac se trouve Chicago, dans l’Illinois ?',
         ['Lac Supérieur', 'Lac Michigan', 'Lac Huron', 'Lac Érié'], 1),
    ]),
}
rows = []
for slug, (title, items) in packages.items():
    package_id = f'geographie-{slug}-20261010'
    category_name = f'Géographie - {title}'
    source = root/'sources'/package_id
    game = dict(id=package_id, name=category_name,
        description=f'{title} du monde. 4 questions à choix multiples. 15 secondes par question ; 15, 10 puis 5 points.',
        categoryPackages=[package_id], answerTimeSeconds=10,
        timingConfig=dict(secondsPerFlip=5, decayPercentagePerFlip=0.0, maxFlips=2, pointsDecayPerFlip=5))
    questions = []
    for i, (prompt, options, correct) in enumerate(items, 1):
        questions.append(dict(kind='multipleChoice', id=f'geo-{slug}-20261010-{i:02d}',
            category=category_name, prompt=prompt, basePoints=15, penaltyPoints=0,
            options=[f'{letter} — {name}' for letter, name in zip('ABCD', options)], correctOptionIndex=correct))
    randomize_choices(questions, package_id)
    for i, q in enumerate(questions, 1):
        rows.append([category_name, i, q['prompt'], *[option.split(' — ', 1)[1] for option in q['options']],
            q['options'][q['correctOptionIndex']]])
    category = dict(category=category_name, answerMode='SIMULTANEOUS', questionTypes=['Choix multiples'], questions=questions)
    for relative, data in [('game.json', game), (f'question-bank/{package_id}.json', category)]:
        target = source/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    archive = root/f'geographie-{slug}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in sorted(source.rglob('*.json')):
            z.write(file, file.relative_to(source).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {'game.json', f'question-bank/{package_id}.json'}
    assert len(questions) == 4
    print(archive.resolve())
with (root/'ILES-DESERTS-EAUX-QUESTIONS-ET-REPONSES.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Catégorie', 'Question', 'Texte', 'A', 'B', 'C', 'D', 'Bonne réponse'])
    writer.writerows(rows)
