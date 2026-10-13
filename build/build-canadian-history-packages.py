from pathlib import Path
import csv, json, zipfile
from quiz_choice_order import randomize_choices

root = Path('package-examples/histoire-canada-2026-10-10')
# Events are stored in chronological order. Options retain the supplied permutations.
sets = {
    'facile': [
        ('les explorations et la fondation de Québec', ['Voyage de Jean Cabot en Amérique du Nord', 'Premier voyage de Jacques Cartier', 'Fondation de Québec par Champlain'], ['Cabot', 'Cartier', 'Champlain'], ['1497', '1534', '1608'], [(1,0,2),(0,1,2),(2,0,1),(0,2,1)]),
        ('les conflits et traités du XVIIIe siècle', ['Début de la Déportation des Acadiens', 'Bataille des plaines d’Abraham', 'Signature du traité de Paris'], ['Déportation des Acadiens', 'Plaines d’Abraham', 'Traité de Paris'], ['1755', '1759', '1763'], [(0,1,2),(1,0,2),(0,2,1),(2,0,1)]),
        ('les étapes vers la Confédération', ['Rébellions du Haut et du Bas-Canada', 'Conférence de Charlottetown', 'Entrée en vigueur de l’Acte de l’Amérique du Nord britannique'], ['Rébellions', 'Charlottetown', 'Confédération'], ['1837–1838', '1864', '1867'], [(1,0,2),(0,2,1),(0,1,2),(1,2,0)]),
        ('l’expansion vers l’Ouest', ['Résistance de la Rivière-Rouge', 'Pose du dernier crampon du chemin de fer Canadien Pacifique', 'Découverte d’or au Klondike'], ['Rivière-Rouge', 'Dernier crampon', 'Or au Klondike'], ['1869–1870', '1885', '1896'], [(0,1,2),(1,0,2),(0,2,1),(2,0,1)]),
        ('les symboles et institutions du Canada', ['Entrée en vigueur de la Loi sur la citoyenneté canadienne', 'Inauguration du drapeau à la feuille d’érable', 'Rapatriement de la Constitution et entrée en vigueur de la Charte'], ['Citoyenneté canadienne', 'Drapeau à la feuille d’érable', 'Rapatriement'], ['1947', '1965', '1982'], [(1,0,2),(0,1,2),(0,2,1),(2,0,1)]),
    ],
    'moins-facile': [
        ('le début du XXe siècle', ['Création des provinces de l’Alberta et de la Saskatchewan', 'Naufrage de l’Empress of Ireland', 'Bataille de la crête de Vimy'], ['Alberta et Saskatchewan', 'Empress of Ireland', 'Vimy'], ['1905', '1914', '1917'], [(0,1,2),(2,0,1),(0,2,1),(1,0,2)]),
        ('la participation canadienne à la Seconde Guerre mondiale', ['Bataille de Hong Kong', 'Raid de Dieppe', 'Débarquement à Juno Beach'], ['Hong Kong', 'Dieppe', 'Juno Beach'], ['1941', '1942', '1944'], [(1,0,2),(0,1,2),(0,2,1),(1,2,0)]),
        ('les grands jalons de l’après-guerre', ['Entrée de Terre-Neuve dans la Confédération', 'Inauguration de la Voie maritime du Saint-Laurent', 'Ouverture d’Expo 67 à Montréal'], ['Terre-Neuve', 'Voie maritime', 'Expo 67'], ['1949', '1959', '1967'], [(0,2,1),(1,0,2),(0,1,2),(2,0,1)]),
        ('les crises et attentats', ['Crise d’Octobre', 'Attentat contre le vol 182 d’Air India', 'Crise d’Oka'], ['Crise d’Octobre', 'Attentat d’Air India', 'Crise d’Oka'], ['1970', '1985', '1990'], [(0,1,2),(1,0,2),(0,2,1),(2,0,1)]),
        ('les changements politiques et territoriaux', ['Échec de l’accord du lac Meech', 'Deuxième référendum québécois sur la souveraineté', 'Création du territoire du Nunavut'], ['Échec de Meech', 'Référendum québécois', 'Nunavut'], ['1990', '1995', '1999'], [(1,0,2),(0,1,2),(0,2,1),(2,0,1)]),
    ],
}
rows = []
for set_index, (slug, items) in enumerate(sets.items()):
    package_id = f'histoire-canada-chronologie-{slug}-20261010'
    name = 'Histoire du Canada - Chronologie ' + ('facile' if slug == 'facile' else 'moins facile')
    source = root/'sources'/package_id
    questions = []
    for index, (topic, events, labels, dates, permutations) in enumerate(items, 1):
        # List events in a non-chronological order in the host prompt.
        prompt = f'Quel ordre va du plus ancien au plus récent pour {topic} ?\n' + '\n'.join('• '+events[i] for i in (2,0,1))
        choices = [' → '.join(labels[i] for i in p) for p in permutations]
        questions.append(dict(kind='multipleChoice', id=f'canada-{slug}-20261010-{index:02d}', category=name,
            prompt=prompt, basePoints=15, penaltyPoints=0,
            options=[f'{letter} — {choice}' for letter, choice in zip('ABCD', choices)],
            correctOptionIndex=permutations.index((0,1,2))))
    expected = [q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in questions]
    randomize_choices(questions, package_id, extra_positions=(set_index*2,))
    assert expected == [q['options'][q['correctOptionIndex']].split(' — ',1)[1] for q in questions]
    assert max([sum(q['correctOptionIndex']==i for q in questions) for i in range(4)]) == 2
    game = dict(id=package_id, name=name,
        description='5 questions de chronologie à choix multiples. Du plus ancien au plus récent. 15 secondes ; 15, 10 puis 5 points.',
        categoryPackages=[package_id], answerTimeSeconds=10,
        timingConfig=dict(secondsPerFlip=5, decayPercentagePerFlip=0.0, maxFlips=2, pointsDecayPerFlip=5))
    category = dict(category=name, answerMode='SIMULTANEOUS', questionTypes=['Choix multiples'], questions=questions)
    for relative, data in [('game.json', game), (f'question-bank/{package_id}.json', category)]:
        target = source/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    archive = root/f'histoire-canada-chronologie-{slug}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in sorted(source.rglob('*.json')):
            z.write(file, file.relative_to(source).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == 2
    for i, (q, item) in enumerate(zip(questions, items), 1):
        rows.append([name, i, q['prompt'], *q['options'], q['options'][q['correctOptionIndex']],
            ' → '.join(f'{event} ({date})' for event, date in zip(item[1], item[3]))])
    print(archive.resolve())
with (root/'QUESTIONS-ET-CORRIGE.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Catégorie', 'Question', 'Texte', 'A', 'B', 'C', 'D', 'Bonne réponse', 'Chronologie expliquée'])
    writer.writerows(rows)
