from pathlib import Path
from collections import Counter
import csv, json, zipfile
from quiz_choice_order import randomize_choices

root=Path('package-examples/histoire-etats-unis-2026-10-10')

def chronology(topic, events, permutations, explanation):
    prompt=f'Quel est l’ordre chronologique, du plus ancien au plus récent, pour {topic} ?\n'+'\n'.join('• '+events[i] for i in (1,2,0))
    return prompt, [' → '.join(events[i] for i in order) for order in permutations], permutations.index((0,1,2)), explanation

packages={
 'chronologie': ('Histoire des États-Unis — Chronologie', [
    chronology('ces événements de la Révolution américaine', ['Massacre de Boston', 'Boston Tea Party', 'Adoption de la Déclaration d’indépendance'], [(0,1,2),(1,0,2),(0,2,1),(1,2,0)], 'Massacre de Boston : 5 mars 1770 ; Boston Tea Party : 16 décembre 1773 ; adoption de la Déclaration : 4 juillet 1776. La plupart des signatures sur le parchemin datent du 2 août, et non du 4 juillet.'),
    chronology('ces étapes constitutionnelles', ['Adoption des Articles de la Confédération', 'Ratification de la Constitution', 'Ratification de la Déclaration des droits'], [(1,0,2),(0,1,2),(0,2,1),(1,2,0)], 'Articles adoptés par le Congrès : 15 novembre 1777, ratification achevée en 1781 ; seuil de neuf États pour la Constitution atteint le 21 juin 1788 ; Déclaration des droits (Bill of Rights) : 15 décembre 1791.'),
    chronology('ces événements de l’expansion vers l’ouest', ['Achat de la Louisiane', 'Loi sur le déplacement des peuples autochtones', 'Début de la ruée vers l’or en Californie'], [(0,2,1),(1,0,2),(0,1,2),(2,0,1)], 'Achat de la Louisiane : 1803 ; Indian Removal Act : 28 mai 1830 ; découverte d’or à Sutter’s Mill : 24 janvier 1848, suivie de la ruée vers l’or. Les arrivées massives des forty-niners ont lieu en 1849.'),
    chronology('ces étapes de la guerre de Sécession', ['Attaque de Fort Sumter', 'Bataille de Gettysburg', 'Reddition de Lee à Appomattox'], [(0,1,2),(1,0,2),(0,2,1),(1,2,0)], 'Fort Sumter : 12 avril 1861 ; Gettysburg : 1er–3 juillet 1863 ; reddition de l’armée de Lee : 9 avril 1865. Toutes les forces confédérées ne se rendent pas ce même jour.'),
 ]),
 'politique-et-grandes-figures': ('Histoire des États-Unis — Politique et grandes figures', [
    ('Qui fut le principal rédacteur de la Déclaration d’indépendance, puis le troisième président des États-Unis ?', ['Benjamin Franklin', 'John Adams', 'Thomas Jefferson', 'Alexander Hamilton'], 2, 'Jefferson rédige le projet en 1776 ; le texte est ensuite discuté et modifié. Il est président de 1801 à 1809.'),
    ('Qui participa à l’expédition de Lewis et Clark en facilitant notamment les échanges avec les Shoshones ?', ['Pocahontas', 'Sacagawea', 'Squanto', 'Geronimo'], 1, 'Sacagawea joue un rôle d’interprète et de médiation. Son mari Toussaint Charbonneau est engagé comme interprète ; la présenter simplement comme une guide recrutée par Lewis et Clark est trompeur.'),
    ('Après quelle bataille Lincoln annonça-t-il la proclamation préliminaire d’émancipation en septembre 1862 ?', ['Bull Run', 'Antietam', 'Shiloh', 'Fredericksburg'], 1, 'La bataille d’Antietam a lieu le 17 septembre 1862 ; la proclamation préliminaire suit le 22 septembre. La proclamation définitive prend effet le 1er janvier 1863 et concerne les territoires en rébellion.'),
    ('Quel arrêt de 1803 affirma le pouvoir de la Cour suprême de déclarer une loi fédérale contraire à la Constitution ?', ['Marbury c. Madison', 'McCulloch c. Maryland', 'Gibbons c. Ogden', 'Dred Scott c. Sandford'], 0, 'Marbury v. Madison est l’arrêt de référence sur le contrôle de constitutionnalité. Il ne s’agit pas d’un pouvoir arbitraire et illimité d’annuler toutes les lois.'),
 ]),
 'societe-crises-et-culture': ('Histoire des États-Unis — Société, crises et culture', [
    ('Quel réseau clandestin aidait des personnes réduites en esclavage à gagner des territoires libres, notamment le Canada ?', ['L’Express abolitionniste', 'Le Freedom Trail', 'Le Chemin de fer clandestin', 'La Ligne de la liberté'], 2, 'Le Chemin de fer clandestin, ou Underground Railroad, est un réseau d’entraide et d’itinéraires de fuite, pas une ligne ferroviaire unique. Harriet Tubman est l’une de ses figures majeures.'),
    ('Quelle interdiction le 18e amendement, ratifié en 1919, établissait-il aux États-Unis ?', ['La fabrication et la vente de boissons alcoolisées destinées à la consommation', 'Le vote des femmes aux élections fédérales', 'La perception de l’impôt fédéral sur le revenu', 'La semaine de travail de 40 heures'], 0, 'Proposé par le Congrès en 1917, ratifié en 1919 et entré en vigueur en 1920, cet amendement instaure la prohibition. Il vise aussi le transport, l’importation et l’exportation, sans interdire expressément la consommation. Il est abrogé en 1933.'),
    ('Quelle convention tenue dans l’État de New York en 1848 marqua une étape majeure du mouvement pour les droits des femmes ?', ['La conférence des ouvrières de Lowell', 'La convention de Seneca Falls', 'L’assemblée d’Albany', 'Le sommet de Saratoga Springs'], 1, 'La convention de Seneca Falls se tient les 19 et 20 juillet 1848 et adopte la Déclaration de sentiments. Elle s’inscrit dans des mobilisations antérieures, plutôt que de créer tous les mouvements pour les droits des femmes.'),
    ('Quelle grande crise économique des années 1930 est associée au krach boursier de 1929 et à un chômage massif ?', ['La panique de 1893', 'La Grande Dépression', 'La crise du Dust Bowl', 'La crise de la stagflation'], 1, 'L’activité économique américaine recule dès l’été 1929. Le krach d’octobre et les crises bancaires aggravent la dépression ; le krach n’en est pas l’unique cause.'),
 ]),
}

rows,counts=[],Counter()
for slug,(name,entries) in packages.items():
    package_id=f'histoire-etats-unis-{slug}-20261010'
    source=root/'sources'/package_id
    game=dict(id=package_id,name=name,description='4 questions en français. 15 secondes ; 15, 10 puis 5 points.',categoryPackages=[package_id],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=5,decayPercentagePerFlip=0.0,maxFlips=2,pointsDecayPerFlip=5))
    questions=[dict(kind='multipleChoice',id=f'us-{slug}-20261010-{i:02d}',category=name,prompt=prompt,basePoints=15,penaltyPoints=0,options=[f'{letter} — {option}' for letter,option in zip('ABCD',options)],correctOptionIndex=correct) for i,(prompt,options,correct,_) in enumerate(entries,1)]
    randomize_choices(questions,package_id)
    for i,(q,entry) in enumerate(zip(questions,entries),1):
        counts[q['correctOptionIndex']]+=1
        rows.append([name,i,q['prompt'],*q['options'],q['options'][q['correctOptionIndex']],entry[3]])
    category=dict(category=name,answerMode='SIMULTANEOUS',questionTypes=['Choix multiples'],questions=questions)
    for relative,data in [('game.json',game),(f'question-bank/{package_id}.json',category)]:
        file=source/relative
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    archive=root/f'histoire-etats-unis-{slug}.zip'
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
