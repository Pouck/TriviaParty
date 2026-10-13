from pathlib import Path
from collections import Counter
import csv, json, zipfile
from quiz_choice_order import randomize_choices

root = Path('package-examples/revolution-francaise-2026-10-10')

def chronology(topic, events, permutations, explanation):
    # List the events in a different order from the answer, without date spoilers.
    prompt = f'Quel est l’ordre chronologique, du plus ancien au plus récent, pour {topic} ?\n' + '\n'.join('• '+events[i] for i in (1,2,0))
    return (prompt, [' → '.join(events[i] for i in order) for order in permutations], permutations.index((0,1,2)), explanation)

packages = {
 'chronologie': ('Révolution française — Chronologie', [
    chronology('ces journées de 1789', ['Serment du Jeu de paume', 'Prise de la Bastille', 'Marche des femmes sur Versailles'], [(1,0,2),(0,1,2),(0,2,1),(1,2,0)], '20 juin 1789 : serment du Jeu de paume ; 14 juillet : prise de la Bastille ; 5–6 octobre : journées de Versailles, la marche commençant le 5.'),
    chronology('ces crises de la monarchie', ['Fuite à Varennes', 'Abolition de la royauté', 'Exécution de Louis XVI'], [(0,1,2),(1,0,2),(0,2,1),(2,0,1)], '20–21 juin 1791 : fuite à Varennes ; 21 septembre 1792 : abolition de la royauté ; 21 janvier 1793 : exécution de Louis XVI. L’an I de la République commence le 22 septembre 1792.'),
    chronology('ces exécutions de la période révolutionnaire', ['Marie-Antoinette', 'Danton', 'Robespierre'], [(0,1,2),(1,0,2),(0,2,1),(1,2,0)], 'Marie-Antoinette : 16 octobre 1793 ; Danton : 5 avril 1794 ; Robespierre : 28 juillet 1794, après sa chute le 27 juillet (9 Thermidor).'),
    chronology('la transition vers l’époque napoléonienne', ['Mise en place du Directoire', 'Coup d’État du 18 Brumaire', 'Sacre de Napoléon'], [(1,0,2),(0,1,2),(0,2,1),(1,2,0)], 'Directoire : 1795 ; coup d’État des 18–19 Brumaire : 9–10 novembre 1799 ; sacre : 2 décembre 1804. Napoléon est proclamé empereur dès mai 1804, avant son sacre.'),
 ]),
 'politique-et-personnages': ('Révolution française — Politique et personnages', [
    ('Sous l’Ancien Régime, quel groupe appartient au tiers état ?', ['Le clergé catholique', 'La noblesse', 'Les paysans, les artisans et les bourgeois non nobles', 'Les membres de la famille royale'], 2, 'Le tiers état rassemble ceux qui ne relèvent ni du clergé ni de la noblesse. Il est très divers socialement ; les conseillers et militaires ne constituent pas un quatrième ordre.'),
    ('À quel célèbre club politique Robespierre appartient-il pendant la Révolution ?', ['Le club des Feuillants', 'Le club des Jacobins', 'Le club des Cordeliers', 'Le club de Clichy'], 1, 'Robespierre est une figure majeure des Jacobins. Le club ne doit pas être confondu avec la Montagne, groupe de députés à la Convention.'),
    ('Qui assassina Jean-Paul Marat dans sa baignoire en 1793 ?', ['Charlotte Corday', 'Madame Roland', 'Olympe de Gouges', 'Lucile Desmoulins'], 0, 'Charlotte Corday tue Marat le 13 juillet 1793. La question évite d’imposer une interprétation unique de ses motivations.'),
    ('Quel comité créé en 1793 joua un rôle central dans le gouvernement révolutionnaire pendant la Terreur ?', ['Le Comité de constitution', 'Les États généraux', 'Le Directoire', 'Le Comité de salut public'], 3, 'Créé par la Convention le 6 avril 1793, le Comité de salut public exerce des pouvoirs gouvernementaux étendus. Il n’est pas la seule institution du gouvernement révolutionnaire.'),
 ]),
 'culture-et-mobilisation': ('Révolution française — Culture et mobilisation', [
    ('Dans le nom « sans-culottes », que désigne le mot « culottes » ?', ['Des chemises', 'Des pantalons courts s’arrêtant au genou', 'Des coiffes militaires', 'Des chaussures à boucles'], 1, 'Il s’agit de la culotte masculine portée notamment par les élites, par opposition au pantalon long. Le terme ne désigne pas les sous-vêtements modernes.'),
    ('Dans le calendrier républicain, combien de jours compte une décade ?', ['5 jours', '7 jours', '10 jours', '12 jours'], 2, 'Chaque mois de trente jours comprend trois décades de dix jours. Des jours complémentaires sont ajoutés en fin d’année.'),
    ('Quel chant composé par Rouget de Lisle en 1792 devient un hymne national en 1795 ?', ['La Marseillaise', 'Vive le roi', 'Ça ira', 'Le Chant du départ'], 0, 'Composé à Strasbourg comme Chant de guerre pour l’armée du Rhin, il est popularisé par les volontaires marseillais. Il n’a pas été écrit spécialement pour eux.'),
    ('Quel principe est au cœur de la levée en masse décrétée en 1793 ?', ['Le recours exclusif à la guérilla', 'La mobilisation de la population pour soutenir l’effort de guerre', 'L’interdiction permanente des mercenaires', 'L’emploi exclusif de la cavalerie'], 1, 'Le décret du 23 août mobilise la population et répartit les tâches. Le départ au combat concerne d’abord les jeunes hommes célibataires ou veufs sans enfants de 18 à 25 ans, pas tous les citoyens indistinctement.'),
 ]),
}

rows, counts = [], Counter()
for slug, (name, entries) in packages.items():
    package_id = f'revolution-francaise-{slug}-20261010'
    source = root/'sources'/package_id
    game = dict(id=package_id,name=name,description='4 questions en français. 15 secondes ; 15, 10 puis 5 points.',categoryPackages=[package_id],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=5,decayPercentagePerFlip=0.0,maxFlips=2,pointsDecayPerFlip=5))
    questions = [dict(kind='multipleChoice',id=f'revolution-{slug}-20261010-{i:02d}',category=name,prompt=prompt,basePoints=15,penaltyPoints=0,options=[f'{letter} — {option}' for letter,option in zip('ABCD',options)],correctOptionIndex=correct) for i,(prompt,options,correct,_) in enumerate(entries,1)]
    randomize_choices(questions,package_id)
    for i,(q,entry) in enumerate(zip(questions,entries),1):
        counts[q['correctOptionIndex']]+=1
        rows.append([name,i,q['prompt'],*q['options'],q['options'][q['correctOptionIndex']],entry[3]])
    category=dict(category=name,answerMode='SIMULTANEOUS',questionTypes=['Choix multiples'],questions=questions)
    for relative,data in [('game.json',game),(f'question-bank/{package_id}.json',category)]:
        file=source/relative
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    archive=root/f'revolution-francaise-{slug}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(source.rglob('*.json')): z.write(file,file.relative_to(source).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={'game.json',f'question-bank/{package_id}.json'}
    print(archive.resolve())
assert counts==Counter({0:3,1:3,2:3,3:3})
with (root/'QUESTIONS-ET-CORRIGE.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f,delimiter=';')
    writer.writerow(['Catégorie','Question','Texte','A','B','C','D','Bonne réponse','Explication'])
    writer.writerows(rows)
print('12 questions ; trois bonnes réponses à chaque position A–D.')
