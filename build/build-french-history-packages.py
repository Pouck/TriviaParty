from pathlib import Path
import csv, json, zipfile
from collections import Counter
from quiz_choice_order import randomize_choices

root = Path('package-examples/histoire-france-2026-10-10')
packages = {
 'moyen-age-reperes': ('Moyen Âge — Repères', [
  ('Quel nom les Romains donnaient-ils à un territoire comprenant une grande partie de la France actuelle ?', ['Lusitanie', 'Gaule', 'Bretagne romaine', 'Helvétie'], 1, 'La Gaule dépassait les frontières de la France actuelle. Cette question sert de prélude antique au Moyen Âge.'),
  ('Laquelle de ces villes a été assiégée en 1209 lors de la croisade contre les Albigeois ?', ['Paris', 'Carcassonne', 'Bordeaux', 'Lyon'], 1, 'Carcassonne fut assiégée en 1209. La croisade ne visait pas une seule ville.'),
  ('Dans quel style architectural Notre-Dame de Paris, dont la construction commence en 1163, est-elle bâtie ?', ['Roman', 'Baroque', 'Gothique', 'Renaissance'], 2, 'Notre-Dame est une cathédrale gothique ; elle n’est pas le premier édifice de ce style.'),
  ('Quel collège de l’Université de Paris doit son nom à Robert de Sorbon ?', ['La Sorbonne', 'Le Louvre', 'La Bastille', 'Versailles'], 0, 'Le collège de Sorbonne et l’Université de Paris ne désignent pas la même fondation.'),
  ('Qu’appelle-t-on une épée bâtarde, ou épée à une main et demie ?', ['Une épée réservée aux cavaliers', 'Une épée pouvant être maniée à une ou deux mains', 'Une arme de siège pour briser les portes', 'Une dague empoisonnée'], 1, 'La poignée permet une prise à une ou deux mains. L’interdiction générale dans les duels avancée dans le texte fourni n’est pas retenue.'),
  ('Sur quel fleuve se trouve Orléans, dont Jeanne d’Arc contribua à lever le siège en 1429 ?', ['La Seine', 'Le Rhône', 'La Loire', 'Le Rhin'], 2, 'Orléans se trouve sur la Loire. Le siège fut levé en mai 1429.'),
 ]),
 'moyen-age-vie-quotidienne': ('Moyen Âge — Vie quotidienne', [
  ('En France médiévale, quels êtres pouvaient parfois être jugés pour avoir blessé ou tué une personne ?', ['Des murs de château', 'Des rivières', 'Des animaux', 'Des vêtements'], 2, 'Des procès d’animaux sont attestés. Il ne faut pas confondre les procès de bétail et les procédures ecclésiastiques contre des nuisibles.'),
  ('Quelle grande épidémie ravage la France au milieu du XIVe siècle, notamment en 1348 ?', ['La Grande Famine', 'La peste noire', 'La Jacquerie', 'Le Grand Schisme'], 1, 'La peste noire frappe l’Europe à partir de 1347. Ses conséquences démographiques et économiques varient selon les régions.'),
  ('Comment appelle-t-on les règles limitant le luxe et certains vêtements selon le statut social ?', ['Les lois somptuaires', 'Les codes de chevalerie', 'La loi salique', 'Les chartes de métiers'], 0, 'Les lois somptuaires encadrent notamment les dépenses de luxe et les signes vestimentaires du rang social.'),
  ('Quel palais de l’île de la Cité fut une résidence des rois de France au Moyen Âge ?', ['Le palais de la Cité', 'Le château de Vincennes', 'La Bastille', 'Le palais du Luxembourg'], 0, 'Le palais de la Cité était une résidence royale et un centre du pouvoir. Le passage à d’autres résidences ne se résume pas à un déménagement direct au Louvre.'),
  ('Quelles organisations réglementaient l’apprentissage et l’exercice de nombreux métiers dans les villes médiévales ?', ['Les fiefs féodaux', 'Les ordres monastiques', 'Les communautés de métiers', 'Les communes'], 2, 'Ces communautés sont souvent appelées corporations dans les présentations historiques. Elles ne contrôlaient pas toute l’économie.'),
  ('Quel prélèvement ecclésiastique portait sur les récoltes et est traditionnellement associé au dixième ?', ['La corvée', 'La gabelle', 'La taille', 'La dîme'], 3, 'La dîme est un prélèvement destiné à l’Église. Son taux réel n’était pas partout exactement de 10 %.'),
 ]),
 'renaissance-chronologie': ('Renaissance — Chronologie', []),
 'renaissance-rois-et-arts': ('Renaissance — Rois et arts', [
  ('Quel artiste italien François Ier accueillit-il au Clos Lucé, où il passa ses dernières années ?', ['Michel-Ange', 'Raphaël', 'Léonard de Vinci', 'Sandro Botticelli'], 2, 'Léonard de Vinci s’installe en France en 1516 et meurt à Amboise en 1519.'),
  ('Quelle reine, épouse d’Henri II, fut la mère de François II, Charles IX et Henri III ?', ['Lucrèce Borgia', 'Catherine de Médicis', 'Isabelle d’Este', 'Marie de Médicis'], 1, 'Catherine de Médicis joua un rôle politique majeur. Les affirmations culinaires et l’idée qu’elle aurait régné seule pendant les trois règnes sont écartées.'),
  ('Quel château possède une célèbre galerie construite sur un pont qui enjambe le Cher ?', ['Chambord', 'Amboise', 'Chenonceau', 'Fontainebleau'], 2, 'C’est la galerie de Chenonceau qui enjambe le Cher, et non tout le château.'),
  ('Quel musée parisien occupe l’ancien palais que François Ier fit transformer dans le style Renaissance ?', ['Le musée d’Orsay', 'Le Louvre', 'Le Centre Pompidou', 'Le musée de l’Orangerie'], 1, 'François Ier fait démolir le donjon médiéval en 1528 et confie le chantier Renaissance à Pierre Lescot en 1546.'),
 ]),
 'renaissance-lettres-et-savoirs': ('Renaissance — Lettres et savoirs', [
  ('Quel chirurgien de la Renaissance est célèbre pour ses soins aux blessés de guerre et l’emploi de ligatures lors des amputations ?', ['Ambroise Paré', 'René Descartes', 'Nostradamus', 'Michel de Montaigne'], 0, 'Paré distingue le traitement des plaies par armes à feu et la ligature des vaisseaux après amputation. Il n’est pas le premier auteur de toute technique de ligature.'),
  ('Quel écrivain publia la première édition de ses Essais en 1580 ?', ['Pierre de Ronsard', 'François Rabelais', 'Michel de Montaigne', 'Jean Calvin'], 2, 'Les deux premiers livres des Essais paraissent en 1580 ; un troisième s’ajoute en 1588.'),
  ('Quelle mesure linguistique célèbre figure dans l’ordonnance de Villers-Cotterêts de 1539 ?', ['L’interdiction de tous les textes protestants', 'L’emploi du français dans les actes judiciaires à la place du latin', 'L’autorisation du théâtre public', 'La création d’universités publiques'], 1, 'Les articles 110 et 111 concernent les actes de justice. Ils ne signifient pas que toute la population se met alors à parler français.'),
  ('Comment appelle-t-on la pratique consistant à acheter certains offices publics sous l’Ancien Régime ?', ['La levée féodale', 'La vénalité des offices', 'La gabelle', 'Les chartes de monopole'], 1, 'La vente des offices fournit des ressources à la monarchie. Tous les offices achetés ne confèrent pas automatiquement la noblesse.'),
 ]),
}

def timeline(topic, events, short, permutations, explanation):
    prompt = f'Quel est l’ordre chronologique, du plus ancien au plus récent, pour {topic} ?\n' + '\n'.join('• '+e for e in events)
    return prompt, [' → '.join(short[i] for i in order) for order in permutations], permutations.index((0,1,2)), explanation

packages['renaissance-chronologie'][1].extend([
 timeline('ces étapes royales et architecturales', ['Début de la construction de Chambord', 'Avènement de François Ier', 'Arrivée de Léonard de Vinci en France'], ['François Ier', 'Arrivée de Léonard', 'Chambord'], [(0,1,2),(1,0,2),(0,2,1),(2,0,1)], 'Avènement : 1515 ; arrivée de Léonard : 1516 ; chantier de Chambord : 1519.'),
 timeline('ces événements littéraires et linguistiques', ['Ordonnance de Villers-Cotterêts', 'Publication de Défense et illustration de la langue française', 'Publication de Gargantua'], ['Gargantua', 'Villers-Cotterêts', 'Défense et illustration'], [(1,0,2),(0,1,2),(0,2,1),(2,0,1)], 'Gargantua : vers 1534–1535 ; ordonnance : 1539 ; ouvrage de Du Bellay : 1549. Une publication datée remplace la formation imprécise de la Pléiade.'),
 timeline('ces épisodes des guerres de Religion', ['Massacre de la Saint-Barthélemy', 'Édit d’Amboise', 'Massacre de Wassy'], ['Wassy', 'Amboise', 'Saint-Barthélemy'], [(0,1,2),(1,0,2),(0,2,1),(2,1,0)], 'Wassy : 1562 ; Amboise : 1563 ; Saint-Barthélemy : 1572.'),
 timeline('ces événements politiques et militaires', ['Édit de Nantes', 'Victoire française à Marignan', 'Assassinat d’Henri III'], ['Marignan', 'Assassinat d’Henri III', 'Édit de Nantes'], [(0,2,1),(1,0,2),(0,1,2),(2,0,1)], 'Marignan : septembre 1515 ; assassinat d’Henri III : 1589 ; édit de Nantes : 1598.'),
])

rows, distribution = [], Counter()
for slug, (title, entries) in packages.items():
    package_id = f'histoire-france-{slug}-20261010'
    category_name = 'Histoire de France — '+title
    source = root/'sources'/package_id
    game = dict(id=package_id, name=category_name, description=f'{len(entries)} questions en français. 15 secondes ; 15, 10 puis 5 points.', categoryPackages=[package_id], answerTimeSeconds=10, timingConfig=dict(secondsPerFlip=5, decayPercentagePerFlip=0.0, maxFlips=2, pointsDecayPerFlip=5))
    questions = [dict(kind='multipleChoice', id=f'fr-{slug}-20261010-{n:02d}', category=category_name, prompt=prompt, basePoints=15, penaltyPoints=0, options=options, correctOptionIndex=answer) for n,(prompt,options,answer,_) in enumerate(entries,1)]
    extra = (0,2) if slug=='moyen-age-reperes' else (1,3) if slug=='moyen-age-vie-quotidienne' else ()
    for q in questions:
        q['options'] = [f'{letter} — {text}' for letter,text in zip('ABCD',q['options'])]
    randomize_choices(questions, package_id, extra_positions=extra)
    for n,(q,entry) in enumerate(zip(questions,entries),1):
        distribution[q['correctOptionIndex']] += 1
        rows.append([category_name,n,q['prompt'],*q['options'],q['options'][q['correctOptionIndex']],entry[3]])
    category = dict(category=category_name, answerMode='SIMULTANEOUS', questionTypes=['Choix multiples'], questions=questions)
    for relative,data in [('game.json',game),(f'question-bank/{package_id}.json',category)]:
        target=source/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    archive=root/f'histoire-france-{slug}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(source.rglob('*.json')): z.write(file,file.relative_to(source).as_posix())
    with zipfile.ZipFile(archive) as z: assert z.testzip() is None
    print(archive.resolve())
assert distribution == Counter({0:6,1:6,2:6,3:6}), distribution
with (root/'QUESTIONS-ET-CORRIGE.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f,delimiter=';')
    writer.writerow(['Catégorie','Question','Texte','A','B','C','D','Bonne réponse','Explication'])
    writer.writerows(rows)
print('24 questions ; réponses correctes :',dict(distribution))
