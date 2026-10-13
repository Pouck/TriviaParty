from pathlib import Path
import csv, hashlib, json, random, zipfile
from quiz_choice_order import randomize_choices

root = Path('package-examples/histoire-antique-2026-10-10')
# Each event list is chronological; dates appear only in the separate correction sheet.
sets = {
    'grece-antique': ('Grèce antique', [
        ('les débuts de la Grèce antique', ['Premiers Jeux olympiques antiques traditionnellement datés', 'Lois écrites de Dracon à Athènes', 'Réformes démocratiques de Clisthène'], ['Jeux olympiques', 'Lois de Dracon', 'Réformes de Clisthène'], ['776 av. J.-C. (date traditionnelle)', 'vers 621 av. J.-C.', '508–507 av. J.-C.']),
        ('les batailles des guerres médiques', ['Bataille de Marathon', 'Bataille des Thermopyles', 'Bataille navale de Salamine'], ['Marathon', 'Thermopyles', 'Salamine'], ['490 av. J.-C.', '480 av. J.-C. (été)', '480 av. J.-C. (après les Thermopyles)']),
        ('la guerre du Péloponnèse', ['Début de l’épidémie dite « peste d’Athènes »', 'Défaite de l’expédition athénienne en Sicile', 'Capitulation d’Athènes face à Sparte'], ['Peste d’Athènes', 'Défaite en Sicile', 'Capitulation d’Athènes'], ['430 av. J.-C.', '413 av. J.-C.', '404 av. J.-C.']),
        ('la naissance des philosophes (du premier né au dernier né)', ['Naissance de Socrate', 'Naissance de Platon', 'Naissance d’Aristote'], ['Socrate', 'Platon', 'Aristote'], ['vers 470–469 av. J.-C.', 'vers 428–427 av. J.-C.', '384 av. J.-C.']),
        ('les conquêtes d’Alexandre le Grand', ['Traversée de l’Hellespont vers l’Asie', 'Conquête de l’Égypte', 'Bataille de Gaugamèles contre Darius III'], ['Hellespont', 'Conquête de l’Égypte', 'Gaugamèles'], ['334 av. J.-C.', '332 av. J.-C.', '331 av. J.-C.']),
    ]),
    'rome-antique': ('Rome antique', [
        ('le passage de la République au principat', ['Jules César franchit le Rubicon', 'Assassinat de Jules César', 'Octavien reçoit le titre d’Auguste'], ['Rubicon', 'Assassinat de César', 'Titre d’Auguste'], ['49 av. J.-C.', '44 av. J.-C.', '27 av. J.-C.']),
        ('les grands conflits de la République romaine', ['Hannibal traverse les Alpes', 'Destruction de Carthage à la fin de la troisième guerre punique', 'Début de la révolte de Spartacus'], ['Hannibal dans les Alpes', 'Destruction de Carthage', 'Révolte de Spartacus'], ['218 av. J.-C.', '146 av. J.-C.', '73 av. J.-C.']),
        ('les événements du début de l’Empire romain', ['Grand incendie de Rome sous Néron', 'Éruption du Vésuve qui ensevelit Pompéi', 'Inauguration du Colisée par Titus'], ['Incendie de Rome', 'Éruption du Vésuve', 'Inauguration du Colisée'], ['64 apr. J.-C.', '79 apr. J.-C.', '80 apr. J.-C.']),
        ('les réformes de l’Empire romain tardif', ['Mise en place de la tétrarchie par Dioclétien', 'Accord de Milan sur la liberté religieuse, appelé « édit de Milan »', 'Inauguration de Constantinople par Constantin'], ['Tétrarchie', 'Édit de Milan', 'Constantinople'], ['293 apr. J.-C.', '313 apr. J.-C.', '330 apr. J.-C.']),
        ('les dernières décennies de l’Empire romain d’Occident', ['Sac de Rome par les Wisigoths d’Alaric', 'Sac de Rome par les Vandales', 'Déposition de Romulus Augustule'], ['Wisigoths à Rome', 'Vandales à Rome', 'Déposition de Romulus Augustule'], ['410 apr. J.-C.', '455 apr. J.-C.', '476 apr. J.-C.']),
    ]),
}
rows = []
for set_index, (slug, (title, items)) in enumerate(sets.items()):
    package_id = f'histoire-chronologie-{slug}-20261010'
    name = f'Histoire - Chronologie de la {title}'
    source = root/'sources'/package_id
    questions = []
    for index, (topic, events, labels, dates) in enumerate(items, 1):
        prompt = f'Quel est l’ordre chronologique, du plus ancien au plus récent, pour {topic} ?\n' + '\n'.join('• '+events[i] for i in (1,2,0))
        question_id = f'antique-{slug}-20261010-{index:02d}'
        cards = [dict(id='event-'+hashlib.sha256((question_id+event).encode()).hexdigest()[:12], text=event) for event in events]
        correct = [card['id'] for card in cards]
        random.Random(question_id).shuffle(cards)
        if [card['id'] for card in cards] == correct:
            cards = cards[1:] + cards[:1]
        orders = [(0,1,2),(1,0,2),(0,2,1),(2,1,0)]
        questions.append(dict(kind='multipleChoice', id=question_id, category=name,
            prompt=prompt, basePoints=15, penaltyPoints=0,
            options=[f'{letter} — '+ ' → '.join(events[i] for i in order) for letter,order in zip('ABCD',orders)],correctOptionIndex=0))
    randomize_choices(questions,package_id,extra_positions=(set_index,))
    game = dict(id=package_id, name=name, description='5 chronologies à choix multiples. Lecture libre, puis départ du chrono par l’hôte. 15 secondes ; 15, 10 puis 5 points.',
        categoryPackages=[package_id], answerTimeSeconds=10,
        timingConfig=dict(secondsPerFlip=5, decayPercentagePerFlip=0.0, maxFlips=2, pointsDecayPerFlip=5))
    category = dict(category=name, answerMode='SIMULTANEOUS', questionTypes=['Choix multiples'], questions=questions)
    for relative, data in [('game.json', game), (f'question-bank/{package_id}.json', category)]:
        target = source/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    archive = root/f'histoire-chronologie-{slug}.zip'
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
    writer.writerow(['Catégorie', 'Question', 'Texte', 'A','B','C','D', 'Bonne réponse', 'Chronologie expliquée'])
    writer.writerows(rows)
