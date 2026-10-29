"""Apply reviewed identification-question merges to the canonical bank, once.

The allowlist refers to audited named targets, not a general answer-only heuristic.
Homonyms and facts that merely share a short answer are deliberately excluded.
"""
import json
import re
from collections import defaultdict
from canonical_question_bank import PATH, BANK, read_bank, materialize, normalize, validate, merge_entries

TARGETS = '''tour eiffel|louis xiv|colisee|grande pyramide de kheops|versailles|guernica|statue de la liberte|insuline|imax|samuel de champlain|miserables|orgueil et prejuges|istanbul|iron man|elsa|john williams|hamlet|candide|alexandre le grand|moby dick|the great gatsby|atticus finch|frankenstein|animal farm|dracula|petit prince|comte de monte cristo|victor hugo|dionysos|athena|meduse|janus|enee|neptune|andes|george washington|abraham lincoln|tortue marine|edith piaf|tchaikovski|ludwig van beethoven|boucle d or|jack|petit poucet|tiramisu|couscous|macaron|mochi|aquaman|wonder woman|cendrillon|vasco de gama|jacques cartier|antarctique|rome|totoro|kiki|neil armstrong|martin luther king jr|marie antoinette|napoleon bonaparte|charles de gaulle|nelson mandela|phasme|accordeon|canadarm|louis armstrong|duke ellington|b king|pikachu|pac man|tarasque|melusine|bete du gevaudan|korrigans|michel tremblay|gabrielle roy|emile nelligan|felix leclerc|son goku|sailor moon|naruto|ennio morricone|celine dion|gilles vigneault|penelope|polypheme|circe|autruche|beatles|michael jackson|bob marley|corbeau|lune|albert einstein|excalibur|pieuvre|baleine bleue|hippocampe|kangourou|ornithorynque|jacques brel|georges brassens|charles aznavour|antonio vivaldi|mozart|robin des bois|humpty dumpty|barbe bleue|pizza|poutine|sushi|croissant|taco|marco polo|roald amundsen|sahara|japon|tokyo|jeanne d arc|francois ier|coccinelle|abeille|violon|harpe|joseph armand bombardier|miles davis|ella fitzgerald|anne hebert|monkey d luffy|hulk|joe hisaishi|leonard cohen|robert charlebois|colibri|paon|manchot|pic|freddie mercury|elvis presley|glooscap|microscope|arthur|merlin|graal|lancelot|mario|sonic|minecraft'''.split('|')




bank = read_bank()
before = len(bank['questions'])
merges = []
for target in TARGETS:
    candidates = [e for e in bank['questions'] if any(re.sub(r'^(le |la |les |l |un |une |des )', '', normalize(a)) == target for a in e['answers'])]
    if len(candidates) < 2 or not any(any(p['content']['kind'] == 'guessWho' for p in e['presentations']) for e in candidates):
        continue
    replacement = merge_entries(candidates)
    ids = {e['id'] for e in candidates}
    bank['questions'] = [replacement if e['id'] == replacement['id'] else e for e in bank['questions'] if e['id'] not in ids or e['id'] == replacement['id']]
    merges.append({'target': target, 'id': replacement['id'], 'mergedIds': sorted(ids)})

# Explicit disambiguated groups where a generic answer also names another entity.
for ids in [
    ['lib-buzzer-instruments-20261012-02', 'lib-qsj-instruments-20261012-03'],
    ['lib-qcm-instruments-20261012-02', 'lib-qsj-instruments-20261012-01'],
    ['lib-buzzer-animaux-terrestres-20261012-02', 'lib-qsj-animaux-terrestres-20261012-05'],
    ['lib-buzzer-animaux-terrestres-20261012-04', 'lib-qsj-animaux-terrestres-20261012-01'],
    ['lib-qcm-science-generale-20261012-01', 'lib-qsj-science-generale-20261012-03', 'test-03-qui-suis-je-q1'],
    ['culture-qsj-mythologie-romaine-divinites-20261010-02', 'lib-qcm-mythologie-romaine-20261012-03'],
]:
    candidates = [e for e in bank['questions'] if set(e['legacyIds']) & set(ids)]
    if len(candidates) < 2:
        continue
    replacement = merge_entries(candidates)
    chosen = {e['id'] for e in candidates}
    bank['questions'] = [replacement if e['id'] == replacement['id'] else e for e in bank['questions'] if e['id'] not in chosen or e['id'] == replacement['id']]
    merges.append({'id': replacement['id'], 'mergedIds': sorted(chosen)})

validate(bank)
PATH.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
report_path = BANK / 'migration.json'
report = json.loads(report_path.read_text(encoding='utf-8'))
report['questionCount'] = len(bank['questions'])
report['mergedEntries'] = report['legacyQuestionCount'] - report['questionCount']
report.setdefault('reviewedIdentificationMerges', []).extend(merges)
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Consolidated {before - len(bank["questions"])} more records; {len(bank["questions"])} unique entries remain.')
