from pathlib import Path
import csv, json, zipfile
from quiz_choice_order import randomize_choices

root = Path('package-examples/geographie-2026-10-10')
packages = {
    'sommets-et-volcans': ('Sommets et volcans', [
        ('Quel volcan, emblème du Japon, peut être aperçu depuis Tokyo par temps clair ?',
         ['Mont Kita', 'Mont Fuji', 'Mont Aso', 'Mont Ontake'], 1),
        ('Quel volcan actif se dresse près de Naples, en Italie ?',
         ['Etna', 'Stromboli', 'Vésuve', 'Vulcano'], 2),
        ('Quelle montagne au sommet plat domine Le Cap, en Afrique du Sud ?',
         ['Tête du Lion', 'Montagne de la Table', 'Drakensberg', 'Pic du Diable'], 1),
        ('Quel sommet andin s’élève à l’est de Santiago, sur la frontière entre le Chili et l’Argentine ?',
         ['Aconcagua', 'Tupungato', 'Huascarán', 'Chimborazo'], 1),
        ('Quel volcan emblématique, haut d’environ 4 400 m, est visible depuis Seattle, dans l’État de Washington ?',
         ['Mont Saint Helens', 'Mont Hood', 'Mont Rainier', 'Mont Adams'], 2),
        ('Quel sommet de Rio de Janeiro, au Brésil, porte la statue du Christ Rédempteur ?',
         ['Pain de Sucre', 'Corcovado', 'Pedra da Gávea', 'Pico da Bandeira'], 1),
    ]),
    'chaines-de-montagnes': ('Chaînes de montagnes', [
        ('Quelle chaîne montagneuse parcourt la péninsule italienne et en constitue la « colonne vertébrale » ?',
         ['Alpes', 'Apennins', 'Pyrénées', 'Dolomites'], 1),
        ('Quelle chaîne de montagnes forme une frontière naturelle entre la France et l’Espagne ?',
         ['Alpes', 'Massif central', 'Pyrénées', 'Vosges'], 2),
        ('Quelle chaîne montagneuse russe, située au nord de la mer Caspienne, marque traditionnellement la limite entre l’Europe et l’Asie ?',
         ['Caucase', 'Oural', 'Carpates', 'Altaï'], 1),
        ('Quelle chaîne de montagnes se dresse à l’ouest de Denver, dans le Colorado ?',
         ['Sierra Nevada', 'Chaîne des Cascades', 'Montagnes Rocheuses', 'Appalaches'], 2),
        ('Quelle cordillère longe l’ouest de l’Amérique du Sud et traverse notamment le Pérou et la Colombie ?',
         ['Andes', 'Sierras de Córdoba', 'Himalaya', 'Atlas'], 0),
        ('Dans quelle chaîne de montagnes se trouve le mont Blanc, visible depuis Genève par temps clair ?',
         ['Jura', 'Alpes', 'Vosges', 'Forêt-Noire'], 1),
    ]),
}
rows = []
for slug, (title, items) in packages.items():
    package_id = f'geographie-{slug}-20261010'
    category_name = f'Géographie - {title}'
    source = root/'sources'/package_id
    game = dict(id=package_id, name=category_name,
        description='Identifiez les montagnes du monde. 6 questions à choix multiples. 15 secondes par question ; 15, 10 puis 5 points.',
        categoryPackages=[package_id], answerTimeSeconds=10,
        timingConfig=dict(secondsPerFlip=5, decayPercentagePerFlip=0.0, maxFlips=2, pointsDecayPerFlip=5))
    questions = []
    for i, (prompt, options, correct) in enumerate(items, 1):
        questions.append(dict(kind='multipleChoice', id=f'geo-{slug}-20261010-{i:02d}',
            category=category_name, prompt=prompt, basePoints=15, penaltyPoints=0,
            options=[f'{letter} — {name}' for letter, name in zip('ABCD', options)], correctOptionIndex=correct))
    randomize_choices(questions, package_id, (0, 2) if slug == 'sommets-et-volcans' else (1, 3))
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
    assert len(questions) == 6
    print(archive.resolve())
with (root/'MONTAGNES-QUESTIONS-ET-REPONSES.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Catégorie', 'Question', 'Texte', 'A', 'B', 'C', 'D', 'Bonne réponse'])
    writer.writerows(rows)
