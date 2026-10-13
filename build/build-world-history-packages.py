from pathlib import Path
from collections import Counter
import csv, json, zipfile
from quiz_choice_order import randomize_choices

root = Path('package-examples/histoire-mondiale-2026-10-10')

def timeline(topic, events, explanation):
    permutations = [(0,1,2),(1,0,2),(0,2,1),(2,1,0)]
    return ('Quel est l’ordre chronologique, du plus ancien au plus récent, pour '+topic+' ?\n'+'\n'.join('• '+events[i] for i in (1,2,0)), [' → '.join(events[i] for i in p) for p in permutations], 0, explanation)

packages = {
 'chronologie-1': ('Histoire mondiale — XIXe et XXe siècles : chronologie 1', [
  timeline('ces transformations politiques', ['Bataille de Waterloo','Restauration de Meiji','Proclamation de l’Empire allemand'], 'Waterloo : 1815 ; restauration de Meiji : 1868 ; proclamation de l’Empire allemand : 1871.'),
  timeline('ces événements du début du XXe siècle', ['Naufrage du Titanic','Début de la Première Guerre mondiale','Abdication de Nicolas II'], 'Titanic : 1912 ; début de la guerre : 1914 ; abdication du tsar pendant la révolution de Février : 1917 (mars dans le calendrier grégorien).'),
  timeline('ces événements de la guerre froide', ['Lancement de Spoutnik 1','Début de la construction du mur de Berlin','Crise des missiles de Cuba'], 'Spoutnik 1 : 1957 ; construction du mur : 1961 ; crise des missiles : 1962.'),
  timeline('ces bouleversements de la fin du XXe siècle', ['Chute du mur de Berlin','Libération de Nelson Mandela','Dissolution de l’Union soviétique'], 'Chute du mur : novembre 1989 ; libération de Mandela : février 1990 ; dissolution de l’URSS : décembre 1991.'),
 ]),
 'xixe-empires-et-industrie': ('Histoire mondiale — XIXe siècle : empires et industrie', [
  ('Quel congrès réorganisa l’Europe en 1814–1815 après les guerres napoléoniennes ?', ['Le traité de Versailles','Le congrès de Vienne','La conférence de Berlin','La paix de Westphalie'], 1, 'Le congrès de Vienne cherche à rétablir un équilibre entre puissances. Des guerres européennes surviennent ensuite : il n’instaure pas un siècle sans guerre.'),
  ('Quel territoire passe de l’administration de la Compagnie des Indes orientales à celle de la Couronne britannique en 1858 ?', ['L’Afrique du Sud','L’Australie','L’Inde','Le Canada'], 2, 'La Couronne reprend l’administration de l’Inde britannique en 1858. Les États princiers conservent des souverains sous tutelle britannique ; tout le sous-continent n’est pas administré directement.'),
  ('Quel canal, ouvert en 1869, relie la mer Méditerranée à la mer Rouge ?', ['Le canal de Panama','Le canal de Suez','Le canal de Kiel','Le canal Érié'], 1, 'Le canal de Suez ouvre en novembre 1869 et permet d’éviter le contournement de l’Afrique pour certaines liaisons Europe–Asie.'),
  ('Quel enjeu était notamment au cœur de la conférence de Berlin de 1884–1885 ?', ['Créer une monnaie européenne commune','Fixer des règles entre puissances pour l’expansion coloniale en Afrique','Restreindre collectivement le commerce avec la Chine','Former une alliance militaire contre l’Empire ottoman'], 1, 'La conférence fixe notamment des règles concernant les revendications coloniales et le commerce en Afrique. Elle accélère la colonisation sans tracer à elle seule toutes les frontières du continent.'),
 ]),
 'xxe-conflits-et-transformations': ('Histoire mondiale — XXe siècle : conflits et transformations', [
  ('Quelle organisation internationale commence ses activités en 1920 pour favoriser la paix après la Première Guerre mondiale ?', ['L’Organisation des Nations unies','La Société des Nations','L’OTAN','Le pacte de Varsovie'], 1, 'Le pacte de la Société des Nations entre en vigueur le 10 janvier 1920. Les États-Unis ne deviennent pas membres.'),
  ('Quel projet dirigé par les États-Unis développa les premières armes nucléaires pendant la Seconde Guerre mondiale ?', ['Le projet Manhattan','Le programme Apollo','Le programme V-2','Le programme britannique de radar'], 0, 'Le projet Manhattan associe notamment les États-Unis, le Royaume-Uni et le Canada. Leslie Groves dirige le projet ; Robert Oppenheimer dirige le laboratoire de Los Alamos. Le premier essai, Trinity, a lieu en 1945.'),
  ('Comment appelle-t-on la division de l’Inde britannique en 1947, qui donne naissance à l’Inde et au Pakistan indépendants ?', ['Le Grand Réalignement','La partition de l’Inde','L’accord de décolonisation','La rupture de Lahore'], 1, 'La partition s’accompagne de déplacements massifs de population et de violences. Le Pakistan comprend alors deux parties géographiquement séparées ; le Bangladesh devient indépendant en 1971.'),
  ('Quel dirigeant du mouvement Solidarność devint président de la Pologne en 1990 ?', ['Lech Wałęsa','Václav Havel','Wojciech Jaruzelski','Imre Nagy'], 0, 'Lech Wałęsa, électricien et dirigeant syndical, joue un rôle majeur dans Solidarność et est élu président en 1990.'),
 ]),
 'chronologie-2': ('Histoire mondiale — XIXe et XXe siècles : chronologie 2', [
  timeline('ces événements politiques et scientifiques', ['Campagne de Russie de Napoléon','Convention de Seneca Falls','Publication de L’Origine des espèces'], 'Campagne de Russie : 1812 ; Seneca Falls : 1848 ; publication de l’ouvrage de Darwin : 1859.'),
  timeline('ces innovations et cette crise sanitaire', ['Ouverture du central téléphonique commercial de New Haven','Premier vol motorisé et contrôlé des frères Wright','Pandémie de grippe dite « espagnole »'], 'Central commercial de New Haven : 1878 ; vol des frères Wright : 1903 ; pandémie grippale : 1918. Le surnom ne démontre pas une origine espagnole.'),
  timeline('ces événements de guerre et d’après-guerre', ['Attaque de Pearl Harbor','Début de la bataille de Stalingrad','Adoption de la Déclaration universelle des droits de l’homme'], 'Pearl Harbor : 1941 ; début de Stalingrad : 1942 ; adoption de la Déclaration par l’Assemblée générale de l’ONU : 1948. Il s’agit d’une adoption, et non de la signature d’un traité.'),
  timeline('ces événements de la seconde moitié du XXe siècle', ['Premier alunissage humain, avec Apollo 11','Chute de la monarchie en Iran','Catastrophe nucléaire de Tchernobyl'], 'Alunissage d’Apollo 11 : juillet 1969 ; chute de la monarchie iranienne : février 1979 ; catastrophe de Tchernobyl : avril 1986.'),
 ]),
 'xixe-revoltes-et-unifications': ('Histoire mondiale — XIXe siècle : révoltes et unifications', [
  ('Quel nom portent les deux guerres du XIXe siècle opposant notamment le Royaume-Uni à la Chine des Qing, dont la première entraîne la cession de l’île de Hong Kong ?', ['La révolte des Boxers','Les guerres de l’opium','La révolte des Taiping','La guerre sino-japonaise'], 1, 'Première guerre : 1839–1842 ; seconde : 1856–1860. L’île de Hong Kong est cédée en 1842 ; les autres extensions du territoire britannique relèvent d’accords ultérieurs.'),
  ('Quel officier américain arriva avec ses « navires noirs » dans la baie d’Edo, près de l’actuelle Tokyo, en 1853 ?', ['Matthew Perry','George Dewey','John Paul Jones','William Bainbridge'], 0, 'Perry obtient l’ouverture de ports par le traité de Kanagawa de 1854. Le Japon avait auparavant des échanges extérieurs limités : il n’était pas totalement isolé.'),
  ('Quelle révolte chinoise fut menée par Hong Xiuquan, qui affirmait être le frère cadet de Jésus ?', ['La révolte du Lotus blanc','La révolte des Taiping','La révolte des Dounganes','La révolte d’An Lushan'], 1, 'La révolte des Taiping, généralement datée de 1851 à 1864, dévaste une partie de la Chine. Ses origines remontent à 1850 et son bilan humain reste estimatif.'),
  ('Quel chef italien mena les « Chemises rouges » lors de l’expédition des Mille en 1860 ?', ['Camillo Benso, comte de Cavour','Giuseppe Garibaldi','Giuseppe Mazzini','Victor-Emmanuel II'], 1, 'Garibaldi conquiert la Sicile et le sud de la péninsule. Le royaume d’Italie est proclamé en 1861 ; l’intégration de Venise et de Rome intervient plus tard.'),
 ]),
 'xxe-guerres-et-reformes': ('Histoire mondiale — XXe siècle : guerres et réformes', [
  ('Quelle bataille opposa les armées française et allemande de février à décembre 1916 ?', ['La bataille de la Somme','La bataille de Verdun','La bataille de Gallipoli','La bataille de Passchendaele'], 1, 'Verdun dure près de dix mois et cause des centaines de milliers de morts et de blessés. Ce n’est pas la plus longue bataille de toute l’histoire moderne.'),
  ('Quel programme américain finança la reconstruction de l’Europe occidentale à partir de 1948 ?', ['La doctrine Truman','Le plan Marshall','La doctrine Eisenhower','Le programme de prêt-bail'], 1, 'Le plan Marshall, ou Programme de rétablissement européen, apporte une aide économique majeure pendant quatre ans. Le prêt-bail appartient à la période de la Seconde Guerre mondiale.'),
  ('Qui fut le premier être humain à voyager dans l’espace et à effectuer une orbite terrestre, en 1961 ?', ['Alan Shepard','Iouri Gagarine','John Glenn','Alexeï Leonov'], 1, 'Iouri Gagarine accomplit son vol à bord de Vostok 1 le 12 avril 1961.'),
  ('Quelle politique de Gorbatchev, dont le nom signifie « transparence » ou « ouverture », favorisa le débat public en URSS ?', ['La perestroïka','La glasnost','La démocratisation','Le Gosplan'], 1, 'La glasnost développe l’ouverture du débat et de l’information à partir des années 1980. La perestroïka désigne les réformes de restructuration ; le Gosplan est l’organisme de planification.'),
 ]),
}

rows, counts = [], Counter()
for slug,(name,entries) in packages.items():
    package_id = f'histoire-mondiale-{slug}-20261010'
    assert len(package_id) <= 64
    source = root/'sources'/package_id
    game = dict(id=package_id,name=name,description='4 questions en français. 15 secondes ; 15, 10 puis 5 points.',categoryPackages=[package_id],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=5,decayPercentagePerFlip=0.0,maxFlips=2,pointsDecayPerFlip=5))
    questions = [dict(kind='multipleChoice',id=f'monde-{slug}-{i:02d}-20261010',category=name,prompt=p,basePoints=15,penaltyPoints=0,options=[f'{letter} — {o}' for letter,o in zip('ABCD',options)],correctOptionIndex=c) for i,(p,options,c,_) in enumerate(entries,1)]
    randomize_choices(questions,package_id)
    assert Counter(q['correctOptionIndex'] for q in questions) == Counter({0:1,1:1,2:1,3:1})
    for i,(q,e) in enumerate(zip(questions,entries),1):
        counts[q['correctOptionIndex']] += 1
        rows.append([name,i,q['prompt'],*q['options'],q['options'][q['correctOptionIndex']],e[3]])
    category = dict(category=name,answerMode='SIMULTANEOUS',questionTypes=['Choix multiples'],questions=questions)
    for relative,data in [('game.json',game),(f'question-bank/{package_id}.json',category)]:
        file = source/relative
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    archive = root/f'histoire-mondiale-{slug}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(source.rglob('*.json')): z.write(file,file.relative_to(source).as_posix())
    with zipfile.ZipFile(archive) as z: assert z.testzip() is None
    print(archive.resolve())
with (root/'QUESTIONS-ET-CORRIGE.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f,delimiter=';')
    writer.writerow(['Catégorie','Question','Texte','A','B','C','D','Bonne réponse','Explication'])
    writer.writerows(rows)
assert counts == Counter({0:6,1:6,2:6,3:6})
print('24 questions ; six bonnes réponses à chaque position A–D.')
