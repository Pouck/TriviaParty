"""Build the authoritative 5–7-question catalogue from historical authoring exports.

Question IDs and canonical answers are preserved. The manifest records where every
old package/question moves so deployment can retire obsolete sets without losing notes.
"""
from pathlib import Path
from collections import Counter,defaultdict
from copy import deepcopy
import csv,hashlib,json,random,re,runpy,unicodedata,zipfile
from quiz_choice_order import randomize_choices

ROOT=Path('package-examples'); OUT=Path('game-library/current'); OUT.mkdir(parents=True,exist_ok=True)
data=runpy.run_path('build/library-size-supplements.py'); EXTRA=data['ADDITIONS']
runpy_revisions=runpy.run_path('build/chronology-revisions.py')['REVISIONS']
written_manifest=Path('game-library/WRITTEN-PACKAGES.json')
written_packages=set(json.loads(written_manifest.read_text(encoding='utf8'))) if written_manifest.exists() else set()
inputs={}; records={}; output={}; claimed=set(); used=set(); actions=[]
def folded(text):return ''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn')
def is_test(game):return any(re.search(r'(^|[^a-z0-9])(tests?|demo|demonstration)([^a-z0-9]|$)',folded(game[k])) for k in ['id','name'])
def subject(name):
    text=folded(name)
    if re.search(r'\bdc\b',text):return 'Super-héros'
    if 'devinette' in text:return 'Logique et énigmes'
    if ('histoire' in text or 'antiqu' in text) and not any(term in text for term in ['musique','jeu','mytholog']):return 'Histoire'
    if 'culture populaire' in text or 'pop culture' in text:return 'Culture populaire'
    for terms,label in [(['musique','chanson','jazz'],'Musique'),(['super-heros','marvel'],'Super-héros'),(['bd ','manga'],'BD et manga'),
      (['logique','enigme','charade'],'Logique et énigmes'),(['conte','legende','table ronde'],'Contes et légendes'),(['cuisine'],'Cuisine'),
      (['nature','oiseaux','insectes','animaux'],'Nature'),(['mytholog','odyssee'],'Mythologie'),(['architecture'],'Architecture'),(['arts','peinture','sculpture'],'Arts'),
      (['cinema','disney','ghibli'],'Cinéma'),(['litterature'],'Littérature'),(['geograph'],'Géographie'),(['science','invention'],'Sciences'),
      (['jeu','gaming'],'Jeux vidéo'),(['histoire','antiquite','revolution','canada'],'Histoire')]:
        if any(term in text for term in terms):return label
    return 'Autres'
def unlabel(option):return re.sub(r'^[A-D]\s*[—.):\-]\s*','',option).strip()
def is_chrono(q):return q['kind']=='ordering' or q['kind']=='multipleChoice' and len(q['options'])==4 and all('→' in option for option in q['options'])
def canonical(q):
    if q['kind']=='multipleChoice':return unlabel(q['options'][q['correctOptionIndex']])
    if q['kind']=='ordering':return ' → '.join(next(i['text'] for i in q['items'] if i['id']==id) for id in q['correctOrderIds'])
    if q['kind']=='mapChoice':return q.get('options',[{}])[q.get('correctOptionIndex',0)].get('label','') if q.get('options') else str(q.get('target'))
    if q['kind'] in ['wager','speedRace']:return canonical(q['subQuestion'])
    return q['acceptableAnswers'][0]

for path in sorted(ROOT.rglob('*.zip')):
    # Some authoring drops are aggregate archives intended for humans, not importable packages.
    with zipfile.ZipFile(path) as archive:
        if 'game.json' not in archive.namelist():
            continue
    with zipfile.ZipFile(path) as z:
        game=json.loads(z.read('game.json')); pid=game['id'];assert pid not in inputs,pid
        banks=[json.loads(z.read(name)) for name in z.namelist() if name.startswith('question-bank/') and name.endswith('.json')]
        qs=[q for bank in banks for q in bank['questions']]
    reference_path=path.parent/'sources'/pid/'VERIFICATION.json'
    refs=json.loads(reference_path.read_text(encoding='utf-8-sig')) if reference_path.exists() else []
    inputs[pid]=dict(path=path,game=game,banks=banks,ids=[q['id'] for q in qs],count=len(qs),test=is_test(game))
    records[pid]=[]
    for n,q in enumerate(qs):
        records[pid].append(dict(q=deepcopy(q),owner=pid,reference=refs[n] if isinstance(refs,list) and n<len(refs) else {},new=False))

def take(pid):
    assert pid in inputs and pid not in claimed,pid
    claimed.add(pid);return deepcopy(records[pid])
def addition(key):
    q=deepcopy(EXTRA[key]);refs=q.pop('sources',[]);note=q.pop('verification','')
    return dict(q=q,owner=None,reference=dict(sources=refs,note=note),new=True)
def put(pid,name,qs,base=None):
    assert pid not in output and 5<=len(qs)<=7,(pid,len(qs))
    assert all(rec['q']['id'] not in used for rec in qs),pid
    used.update(rec['q']['id'] for rec in qs)
    output[pid]=dict(id=pid,name=name,records=qs,base=base or next((r['owner'] for r in qs if r['owner']),None),sources=sorted({r['owner'] for r in qs if r['owner']}))
def preserve(pid,qs,name=None):put(pid,name or inputs[pid]['game']['name'],qs,pid)
def split_id(pid):return pid[:54]+'-part-2'

# Five architecture clue sets of three become three coherent sets of five.
a=take('architecture-qsj-antiquite-20261011'); c=take('architecture-qsj-civilisations-20261011')
m=take('architecture-qsj-modernes-20261011'); p=take('architecture-qsj-palais-20261011'); s=take('architecture-qsj-sacre-20261011')
put('architecture-qsj-antiquite-20261011','Architecture — Merveilles historiques — Qui suis-je ?',a+[c[0],c[2]])
put('architecture-qsj-modernes-20261011','Architecture — Monuments emblématiques — Qui suis-je ?',m+[s[0],s[2]])
put('architecture-qsj-palais-20261011','Architecture — Palais et lieux d’exception — Qui suis-je ?',p+[c[1],s[1]])
actions.append('Architecture : cinq forfaits de trois indices regroupés en trois forfaits de cinq, sans ajouter ni supprimer de question.')

# Keep six themed questions from each eight-question film/art set; gather its
# two remaining questions into a fourth set. Photo/text alternation stays balanced.
for domain,roots in [('arts',{'qcm':['couleurs-mouvements','peintures-classiques','sculptures-iconiques'],
                            'buzzer':['marbre-bronze','regards-scenes','tableaux-celebres']}),
                     ('cinema',{'qcm':['coulisses','films-personnages','prix-classiques'],
                               'buzzer':['france-quebec','titres-heros','univers']})]:
    for mode,slugs in roots.items():
        remainder=[]
        for slug in slugs:
            pid=f'{domain}-{mode}-{slug}-20261011';qs=take(pid);preserve(pid,qs[:6]);remainder+=qs[6:]
        title='Arts — Œuvres et artistes' if domain=='arts' else 'Cinéma — Personnages et grands univers'
        put(f'{domain}-{mode}-selection-variee-20261012',title+' — '+('QCM' if mode=='qcm' else 'Buzzer'),remainder)
actions.append('Arts et cinéma : les séries de huit deviennent des séries de six ; les questions restantes forment quatre nouveaux forfaits de six.')

# Ten-question sets split naturally into two five-question sets.
for pid,entry in inputs.items():
    if entry['count']==10:
        qs=take(pid);name=entry['game']['name']
        preserve(pid,qs[:5],name+' — 1');put(split_id(pid),name+' — 2',qs[5:],pid)
actions.append('Canada et QCM littéraires : les onze forfaits de dix sont scindés en deux forfaits de cinq.')

# Map pools: the four-tag map variants and image answer keys are retained intact.
af=take('geographie-afrique-20261010'); asia=take('geographie-asie-20261010'); eu=take('geographie-europe-20261010')
put('geographie-afrique-20261010','Géographie — Cartes du monde — 1',af+asia[:2])
put('geographie-asie-20261010','Géographie — Cartes du monde — 2',asia[2:]+eu)
am=take('geographie-amerique-du-sud-20261010')+take('geographie-etats-unis-20261010')
put('geographie-amerique-du-sud-20261010','Géographie — Cartes des Amériques',am)
water=take('geographie-lacs-mers-et-golfes-20261010')
put('geographie-iles-et-archipels-20261010','Géographie — Îles et eaux du monde — QCM',take('geographie-iles-et-archipels-20261010')+water[:2])
put('geographie-deserts-et-paysages-arides-20261010','Géographie — Paysages et milieux naturels — QCM',take('geographie-deserts-et-paysages-arides-20261010')+water[2:])
capital_id='geographie-capitales-20261010-v2';capital=take(capital_id)
donor='lib-buzzer-geographie-villes-20261012'
preserve(capital_id,capital[:7]);preserve(donor,take(donor)+capital[7:])
river_id='geographie-fleuves-et-rivieres-20261010';river=take(river_id)
preserve(river_id,river[:6],'Géographie — Fleuves et rivières — 1');put(split_id(river_id),'Géographie — Fleuves et rivières — 2',river[6:],river_id)
actions.append('Géographie : regroupement des cartes régionales en 5/6/6 ; eaux et paysages en deux séries de six ; capitales en deux séries de sept ; fleuves en deux séries de six.')

# Historical figures stay separate from mythology.
for pid,key in [('culture-qsj-grece-figures-et-lieux-20261010','socrate'),('culture-qsj-grece-grandes-figures-20261010','aristote'),
                ('culture-qsj-rome-personnages-20261010','cesar'),('culture-qsj-rome-monuments-et-crises-20261010','auguste')]:
    preserve(pid,take(pid)+[addition(key)],inputs[pid]['game']['name'].replace('Monuments et crises','Monuments et pouvoirs'))

# Short older clue sets and newer sets of five form two sets of five per tradition.
for region,new_slug,new_key in [('francaise','france','hugo'),('anglophone','anglaise','hamlet'),('americaine','americaine','huck-finn')]:
    works=f'culture-qsj-litterature-{region}-oeuvres-20261010';characters=f'culture-qsj-litterature-{region}-personnages-20261010'
    old=take(works)+take(characters);new=take(f'lib-qsj-litterature-{new_slug}-20261012')+[addition(new_key)]
    # Avoid the same canonical work twice within a set: spread its two versions.
    first=old.copy();second=[]
    for rec in new:
        answer=folded(canonical(rec['q']))
        if len(first)<5 and answer not in [folded(canonical(r['q'])) for r in first]:first.append(rec)
        else:second.append(rec)
    assert len(first)==len(second)==5,(region,len(first),len(second))
    title={'francaise':'Littérature française','anglophone':'Littérature britannique et irlandaise','americaine':'Littérature américaine'}[region]
    put(works,title+' — Œuvres et personnages — Qui suis-je ? — 1',first)
    put(characters,title+' — Œuvres et personnages — Qui suis-je ? — 2',second)
greek_a='culture-qsj-mythologie-grecque-dieux-et-mortels-20261010';greek_b='culture-qsj-mythologie-grecque-monstres-et-objets-20261010'
g=take('lib-qsj-mythologie-grecque-20261012')
put(greek_a,'Mythologie grecque — Dieux et mortels — Qui suis-je ?',take(greek_a)+g[:2]+[addition('athena')])
put(greek_b,'Mythologie grecque — Héros et objets — Qui suis-je ?',take(greek_b)+g[2:])
roman_a='culture-qsj-mythologie-romaine-divinites-20261010';roman_b='culture-qsj-mythologie-romaine-fondations-20261010'
r=take('lib-qsj-mythologie-romaine-20261012')
put(roman_a,'Mythologie romaine — Dieux et héros — Qui suis-je ?',take(roman_a)+[r[0],r[1],r[4]])
put(roman_b,'Mythologie romaine — Dieux et fondations — Qui suis-je ?',take(roman_b)+[r[2],r[3],addition('neptune')])
actions.append('Antiquité, mythologie et littérature : regroupement par tradition et format, avec neuf nouveaux portraits accessibles ; les versions d’un même personnage sont réparties entre les forfaits.')

# Thirteen US questions become six and seven; 21 world questions become three sevens.
usa_a='histoire-etats-unis-politique-et-grandes-figures-20261010';usa_b='histoire-etats-unis-societe-crises-et-culture-20261010'
usa=take('lib-qcm-histoire-etats-unis-20261012')
put(usa_a,'Histoire des États-Unis — Figures et institutions — QCM',take(usa_a)+usa[:2])
put(usa_b,'Histoire des États-Unis — Société et repères — QCM',take(usa_b)+usa[2:])
chrono_usa='histoire-etats-unis-chronologie-20261010';preserve(chrono_usa,take(chrono_usa)+[addition('usa-xxe')])
world_ids=['histoire-mondiale-xixe-empires-et-industrie-20261010','histoire-mondiale-xixe-revoltes-et-unifications-20261010',
           'histoire-mondiale-xxe-conflits-et-transformations-20261010','histoire-mondiale-xxe-guerres-et-reformes-20261010']
world=sum((take(pid) for pid in world_ids),[])+take('lib-qcm-histoire-mondiale-generale-20261012')
for n,pid in enumerate(world_ids[:3]):put(pid,f'Histoire mondiale — Grands repères — QCM — {n+1}',world[n*7:(n+1)*7])
world_chrono=['histoire-mondiale-chronologie-1-20261010','histoire-mondiale-chronologie-2-20261010']
explorer=take('lib-chronologie-explorateurs-reperes-20261012')
put(world_chrono[0],'Histoire mondiale — Transformations et explorations — Chronologie — 1',take(world_chrono[0])+explorer[:2])
put(world_chrono[1],'Histoire mondiale — Transformations et explorations — Chronologie — 2',take(world_chrono[1])+explorer[2:])
for pid,key in [
 ('histoire-france-renaissance-rois-et-arts-20261010','marignan'),('histoire-france-renaissance-lettres-et-savoirs-20261010','pleiade'),
 ('histoire-france-renaissance-chronologie-20261010','rois-renaissance'),('revolution-francaise-politique-et-personnages-20261010','louis-xvi'),
 ('revolution-francaise-culture-et-mobilisation-20261010','guillotine'),('revolution-francaise-chronologie-20261010','jalons-1789')]:
    preserve(pid,take(pid)+[addition(key)])
actions.append('Histoire : regroupement des QCM mondiaux en trois séries de sept ; États-Unis en six/sept ; compléments courts pour Renaissance, Révolution et chronologie américaine.')

# Original mixed sets are made homogeneous too: games/BD timelines are grouped,
# while their ordinary multiple-choice questions retain two original package IDs.
pop=take('original-pop-culture'); games=take('original-video-game-maps')
ordinary_pop=[r for r in pop if not is_chrono(r['q'])]
ordinary_games=[r for r in games if not is_chrono(r['q'])]
game_questions=take('lib-qcm-jeux-video-20261012')
put('original-pop-culture','Culture populaire — QCM',ordinary_pop+game_questions[:2])
put('original-video-game-maps','Jeux vidéo — Univers et personnages — QCM',ordinary_games+game_questions[2:])
bd_timeline='lib-chronologie-bd-premieres-20261012'
put(bd_timeline,'Culture populaire — Jeux et BD — Chronologie',take(bd_timeline)+[r for r in pop+games if is_chrono(r['q'])])
actions.append('Les ensembles originaux deviennent homogènes : les chronologies de jeux rejoignent les repères BD ; les QCM restent dans deux ensembles distincts de six et sept.')

# The unused one-question charade example becomes a complete, readable set.
charades=take('charades');q=charades[0]['q'];q.pop('imageUrl',None)
replacement=deepcopy(data['CHARADE_REPLACEMENT']);charades[0]['reference']={'note':replacement.pop('verification')}
q.update(replacement);q['allowFuzzyMatch']=False
put('charades','Logique et énigmes — Charades — Buzzer',charades+[addition(key) for key in ['chapeau','radeau','pinceau','cartable']])

# Diagnostic packages remain one format each, with five examples per format.
diagnostics=sum((take(pid) for pid,entry in inputs.items() if entry['test']),[])
for rec in diagnostics:
    if rec['q']['id']=='qui-suis-je-demo-01':
        rec['q']['clues'].insert(2,'Deux réservoirs sont reliés par un passage étroit.')
    if rec['q']['kind']=='wager':
        old=rec['q'];rec['q']=dict(old['subQuestion'],id=old['id'],category=old['category'],basePoints=15,penaltyPoints=0)
diagnostic_groups=defaultdict(list)
for rec in diagnostics:diagnostic_groups['ordering' if is_chrono(rec['q']) else rec['q']['kind']].append(rec)
diagnostic_added=0
normal=[r for pid,qs in records.items() if not inputs[pid]['test'] for r in qs]
labels={'multipleChoice':('qcm','QCM et images'),'ordering':('chronologie','Chronologie'),'mapChoice':('carte','Cartes'),
        'textAnswer':('buzzer','Buzzer'),'guessWho':('indices','Qui suis-je ?'),'speedRace':('rapidite','Rapidité')}
for kind,group in diagnostic_groups.items():
    slug,label=labels[kind];needed=5-len(group)
    templates=[r for r in normal if ('ordering' if is_chrono(r['q']) else r['q']['kind'])==kind]
    if kind=='mapChoice':templates=[group[0]]*needed
    if kind=='speedRace':templates=[r for r in normal if r['q']['kind']=='multipleChoice' and not is_chrono(r['q']) and not r['q'].get('randomVariants')]
    if kind=='multipleChoice':templates=[r for r in templates if not r['q'].get('randomVariants')]
    for n,template in enumerate(templates[:needed],1):
        rec=deepcopy(template);rec['diagnosticClone']=True;rec['new']=True
        q=rec['q'];q['id']=f'test-20261012-{slug}-complement-{n}'
        if kind=='mapChoice':
            q['correctOptionIndex']=(n-1)%len(q['options'])
            q['prompt']='Test carte : sélectionnez le repère '+q['options'][q['correctOptionIndex']]['label']
        if kind=='speedRace':
            q=dict(kind='speedRace',id=q['id'],category=q['category'],prompt=q['prompt'],basePoints=15,penaltyPoints=0,subQuestion=q)
            rec['q']=q
        group.append(rec);diagnostic_added+=1
    assert len(group)==5,(kind,len(group))
    put('test-'+slug+'-20261012','TEST — '+label,group)
actions.append('Diagnostic : six forfaits homogènes de cinq exemples, toujours exclus des sélections automatiques ; les compléments de test sont des copies identifiées de questions existantes.')

for pid in inputs:
    if pid not in claimed:preserve(pid,take(pid))
assert claimed==set(inputs)
old_ids={q['id'] for entry in inputs.values() for bank in entry['banks'] for q in bank['questions']}
assert old_ids <= used,old_ids-used
assert len(used)==len(old_ids)+len(EXTRA)+diagnostic_added

def convert_order(q):
    if q['kind']!='multipleChoice' or not is_chrono(q):return q
    orders=[[part.strip() for part in unlabel(option).split('→')] for option in q['options']]
    correct=orders[q['correctOptionIndex']]
    assert len(set(correct))==len(correct) and all(set(order)==set(correct) for order in orders),q['id']
    display=correct.copy();random.Random(q['id']).shuffle(display)
    if display==correct:display=display[1:]+display[:1]
    items=[dict(id=f'item-{i}',text=text) for i,text in enumerate(display)]
    prompt=q['prompt'].split('\n')[0]
    if len(prompt)>85:prompt='Classez ces événements du plus ancien au plus récent'
    return {k:v for k,v in q.items() if k not in ['options','correctOptionIndex','randomVariants']} | dict(kind='ordering',prompt=prompt,items=items,
        correctOrderIds=[next(i['id'] for i in items if i['text']==text) for text in correct])

def assign_category(q,name):
    q['category']=name
    if 'subQuestion' in q:assign_category(q['subQuestion'],name)
def image_paths(q):
    paths=[q['imageUrl']] if q.get('imageUrl') else []
    if 'subQuestion' in q:paths+=image_paths(q['subQuestion'])
    return paths
def replace_images(q,mapping):
    if q.get('imageUrl'):q['imageUrl']=mapping[q['imageUrl']]
    if 'subQuestion' in q:replace_images(q['subQuestion'],mapping)

catalog=[];question_map={};rows=[];owner_destinations=defaultdict(set);checks=[]
for pid,entry in sorted(output.items()):
    name=entry['name'];qs=[];images={};refs=[];credits=[];kinds=[];credited_owners=set()
    if pid in written_packages:
        name=name.replace('Qui suis-je ?','Qui suis-je ? écrit').replace('Buzzer','Réponses écrites')
        if 'écrit' not in name:name+=' — Réponses écrites'
    for n,record in enumerate(entry['records'],1):
        original=record['q'];q=convert_order(deepcopy(original));assign_category(q,name)
        revision=runpy_revisions.get(q['id'])
        if revision:
            events=[text for text,date in revision['events']]
            display=list(events);random.Random(q['id']+'editorial-20261012').shuffle(display)
            if display==events:display=display[1:]+display[:1]
            q={**q,'kind':'ordering','prompt':revision['prompt'],'items':[dict(id=f'item-{i}',text=text) for i,text in enumerate(display)]}
            q['correctOrderIds']=[next(item['id'] for item in q['items'] if item['text']==text) for text in events]
        if q['kind']=='guessWho':q['basePoints']=len(q['clues'])*5;q['penaltyPoints']=5
        else:q['basePoints']=15;q['penaltyPoints']=0
        assert revision or canonical(q)==canonical(original),(q['id'],canonical(q),canonical(original))
        owner=record['owner'];mapping={}
        if owner:
            if not record.get('diagnosticClone'):owner_destinations[owner].add(pid)
            with zipfile.ZipFile(inputs[owner]['path']) as source:
                for old in image_paths(q):
                    assert old in source.namelist(),(owner,old)
                    new='images/'+owner+'/'+old.removeprefix('images/')
                    mapping[old]=new;images[new]=source.read(old)
                if mapping and owner not in credited_owners:
                    sidecar=inputs[owner]['path'].parent/'sources'/owner/'PHOTOS.json'
                    values=json.loads(source.read('images/credits.json')) if 'images/credits.json' in source.namelist() else json.loads(sidecar.read_text(encoding='utf-8-sig')) if sidecar.exists() else []
                    if isinstance(values,list):credits.extend(dict(item,originalPackage=owner) for item in values if isinstance(item,dict))
                    credited_owners.add(owner)
        replace_images(q,mapping);qs.append(q);kinds.append(q['kind'])
        refs.append(dict(question=n,questionId=q['id'],originalPackage=owner,reference=record['reference'],new=record['new'],
            **({'editorialRevision':dict(date='2026-10-12',reason='Réduire les événements et ordres répétés',**revision)} if revision else {})))
        question_map[q['id']]=dict(packageId=pid,category=name,originalPackage=owner)
    guesses=[q for q in qs if q['kind']=='guessWho']
    clue_count=max((len(q['clues']) for q in guesses),default=0)
    assert not guesses or all(len(q['clues'])==clue_count for q in guesses),pid
    chronology=all(q['kind']=='ordering' for q in qs)
    logic=subject(name)=='Logique et énigmes'
    segment=20 if len(guesses)==len(qs) else 15 if chronology else 10 if logic else 5
    if pid in written_packages and not guesses:segment=max(segment,10)
    flips=clue_count-1 if guesses else 2
    if flips<0:flips=2
    config=dict(secondsPerFlip=segment,decayPercentagePerFlip=0,maxFlips=flips,pointsDecayPerFlip=5)
    # Mixed diagnostic sets rely on the question-level clue/chronology timing rules.
    test=is_test(dict(id=pid,name=name))
    if test and guesses:config['maxFlips']=clue_count-1
    choices=[q for q in qs if q['kind']=='multipleChoice' and not q.get('randomVariants')]
    if len(choices)==len(qs):
        # Map letters are fixed physical labels and must not be reassigned.
        named=[q for q in choices if not all(re.fullmatch(r'[A-D]',option) for option in q['options'])]
        for q in named:q['options']=[f'{letter} — {unlabel(option)}' for letter,option in zip('ABCD',q['options'])]
        if named and all(len(q['options'])==4 and len(set(q['options']))==4 for q in named):
            randomize_choices(named,pid,extra_positions=range(len(named)%4))
    mode='BUZZER' if all(q['kind'] in ['textAnswer','guessWho'] for q in qs) else 'SIMULTANEOUS'
    if pid in written_packages:mode='WRITTEN'
    type_names={'multipleChoice':'Choix multiples','textAnswer':'Buzzer','guessWho':'Qui suis-je ?','ordering':'Chronologie','mapChoice':'Carte','speedRace':'Rapidité'}
    declared={bank.get('subject') for owner in entry['sources'] for bank in inputs[owner]['banks'] if bank.get('subject')}
    resolved_subject='Tests' if test else next(iter(declared)) if len(declared)==1 else subject(name)
    assert len(set(kinds))==1,(pid,kinds)
    bank=dict(category=name,subject=resolved_subject,answerMode=mode,questionTypes=list(dict.fromkeys(type_names.get(k,'Choix multiples') for k in kinds)),questions=qs)
    if mode=='WRITTEN':bank['questionTypes']=['Qui suis-je ? écrit' if guesses else 'Réponses écrites']
    duration=segment*(flips+1)
    one_glass=all(q['kind'] in ['multipleChoice','mapChoice','speedRace'] for q in qs)
    if one_glass:
        config=dict(secondsPerFlip=15,decayPercentagePerFlip=0,maxFlips=0,pointsDecayPerFlip=None,pointsDecayPerSecond=1)
        duration=15
    description=f'{len(qs)} questions en français. '+('4 indices de 20 secondes ; ' if guesses and clue_count==4 else f'{clue_count} indices de 20 secondes ; ' if guesses else 'Lecture libre puis 45 secondes ; ' if chronology else f'{duration} secondes ; ')+('5 points par palier. Réponse au buzzer : 10 secondes.' if guesses else '15 → 10 → 5 points. Réponse au buzzer : 10 secondes.')
    if guesses:description+=' Lecture confirmée par les joueurs avant chaque indice.'
    if mode=='WRITTEN':description=description.replace('Réponse au buzzer : 10 secondes.','')+' Réponses écrites, validées individuellement par l’hôte.'
    if one_glass:description=f'{len(qs)} questions en français. 15 points au départ ; −1 point par seconde. Sablier unique de 15 secondes.'
    game=dict(id=pid,name=name,description=description,categoryPackages=[pid],timingConfig=config,answerTimeSeconds=10)
    source_dir=OUT/'sources'/pid
    with zipfile.ZipFile(OUT/(pid+'.zip'),'w',zipfile.ZIP_DEFLATED) as zipout:
        for rel,value in [('game.json',game),(f'question-bank/{pid}.json',bank),*([('images/credits.json',credits)] if credits else [])]:
            text=json.dumps(value,ensure_ascii=False,indent=2)+'\n';target=source_dir/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8');zipout.writestr(rel,text)
        for rel,blob in images.items():
            target=source_dir/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);zipout.writestr(rel,blob)
    (source_dir/'VERIFICATION.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for q,ref in zip(qs,refs):
        rows.append([pid,name,q['id'],q['kind'],q['prompt'],q.get('imageUrl',''),' | '.join(q.get('clues',[])),
            ' | '.join(option if isinstance(option,str) else option.get('label','') for option in q.get('options',[])),canonical(q),ref['originalPackage'] or 'AJOUT'])
    catalog.append(dict(id=pid,name=name,count=len(qs),subject=bank['subject'],types=bank['questionTypes'],test=test,
        images=sum(bool(image_paths(q)) for q in qs),sources=entry['sources'],seconds=duration))

retired=sorted(set(inputs)-set(output))
migration=dict(minQuestions=5,maxQuestions=7,retiredPackageIds=retired,
    replacements={pid:sorted(owner_destinations[pid]) for pid in inputs},
    newPackageSources={pid:entry['sources'] for pid,entry in output.items() if pid not in inputs},questionMap=question_map)
(OUT/'CATALOGUE.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'MIGRATION.json').write_text(json.dumps(migration,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'QUESTIONS-ET-REPONSES.csv').open('w',encoding='utf-8-sig',newline='') as file:
    writer=csv.writer(file,delimiter=';');writer.writerow(['ID forfait','Forfait','ID question','Format','Question','Image','Indices','Choix','Réponse','Origine']);writer.writerows(rows)
with (OUT/'CHANGEMENTS.csv').open('w',encoding='utf-8-sig',newline='') as file:
    writer=csv.writer(file,delimiter=';');writer.writerow(['Ancien ID','Ancien forfait','Ancienne taille','Nouveaux IDs','Nouvelles tailles'])
    for pid,entry in sorted(inputs.items()):
        destinations=sorted(owner_destinations[pid])
        writer.writerow([pid,entry['game']['name'],entry['count'],' | '.join(destinations),' | '.join(str(len(output[d]['records'])) for d in destinations)])
distribution=Counter(c['count'] for c in catalog)
assert set(distribution)<=set(range(5,8))
for stale in OUT.glob('*.zip'):
    if stale.stem not in output and not stale.stem.startswith('charades-visuelles-'):
        history=Path('game-library/history/2026-10-12');history.mkdir(parents=True,exist_ok=True)
        target=history/stale.name
        assert stale.resolve().parent==OUT.resolve() and target.resolve().is_relative_to(Path.cwd().resolve())
        stale.replace(target)
        old_source=OUT/'sources'/stale.stem
        if old_source.exists():
            destination=history/'sources'/stale.stem;destination.parent.mkdir(parents=True,exist_ok=True)
            assert old_source.resolve().is_relative_to(OUT.resolve()) and destination.resolve().is_relative_to(Path.cwd().resolve())
            old_source.rename(destination)
assert len(catalog)==len([p for p in OUT.glob('*.zip') if not p.stem.startswith('charades-visuelles-')]),'Stale ZIPs in current catalogue'
(OUT/'README.md').write_text('# Bibliothèque actuelle — 5 à 7 questions par forfait\n\n'
    +f'{len(catalog)} forfaits ; {len(rows)} questions ; chaque forfait contient **5, 6 ou 7 questions**. '
    +'Les six forfaits de diagnostic ont cinq questions chacun et restent exclus des tirages automatiques.\n\n'
    +f'{len(written_packages & set(output))} forfaits à réponses écrites coexistent avec les versions orales. Les choix multiples utilisent 15 points, puis −1 point par seconde dans un seul sablier. Les joueurs confirment la lecture avant chaque indice de Qui suis-je.\n\n'
    +'Cette bibliothèque remplace les anciennes archives courtes ou longues de `package-examples`. Utiliser les ZIP de ce dossier pour importer ou mettre à jour. '
    +'Les anciennes archives sont conservées comme sources et références historiques ; elles ne représentent plus le catalogue proposé sur le Pixel.\n\n'
    +'## Réorganisation\n\n'+'\n'.join('- '+action for action in actions)
    +f'\n\n{len(EXTRA)} nouvelles questions courtes complètent les pools qui ne pouvaient pas être répartis proprement ; {diagnostic_added} copies supplémentaires servent uniquement aux diagnostics. Les {len(old_ids)} anciens identifiants de questions sont tous conservés. '
    +'Les notes restent liées aux questions, même lorsque leur forfait ou leur titre change. Les images et leurs clés sont déplacées avec les questions. '
    +'Les rébus incomplets de l’exemple Charades ont été remplacés par une charade textuelle complète, puis quatre charades accessibles ont été ajoutées.\n\n'
    +'## Sources modifiables et inventaire\n\n'
    +'[Questions et réponses](QUESTIONS-ET-REPONSES.csv) · [Répartition des anciennes séries](CHANGEMENTS.csv) · [Catalogue](CATALOGUE.json) · [Migration](MIGRATION.json).\n\n'
    +'Les JSON et images prêts à éditer sont dans `sources/<ID>/`. Les références propres à chaque question sont dans `VERIFICATION.json`. '
    +'Les ajouts sont rédigés dans `build/library-size-supplements.py`. Reconstituer le catalogue : `python build/build-playable-library.py`. '
    +'Ce script utilise les exports historiques comme entrées ; une correction durable doit aussi être reportée dans les données d’auteur correspondantes.\n\n'
    +'## Forfaits\n\n| Sujet | Forfait | Questions | Archive |\n|---|---|---:|---|\n'
    +'\n'.join(f"| {c['subject']} | {c['name']} | {c['count']} | [{c['id']}.zip]({c['id']}.zip) |" for c in catalog)+'\n',encoding='utf-8')
print(f'{len(catalog)} packages; {len(rows)} questions; sizes {dict(sorted(distribution.items()))}; {len(retired)} old package IDs retired; {len(EXTRA)} playable questions and {diagnostic_added} diagnostic examples added; every old question ID preserved.')

# Preserve and register the separately authored visual charades on every rebuild.
runpy.run_path('build/build-visual-charades.py')

# Keep reviewed question fixes durable when rebuilding the playable catalog.
runpy.run_path('build/apply-question-review-revisions.py')
