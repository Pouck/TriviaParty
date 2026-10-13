"""Report repeated chronology events and event pairs across the playable catalogue."""
import itertools,json,re,unicodedata,runpy
from collections import defaultdict
from pathlib import Path
def normalize(text):
    text=''.join(c for c in unicodedata.normalize('NFD',text.casefold()) if unicodedata.category(c)!='Mn')
    text=re.sub(r'^(ouverture de |ouverture du |inauguration de |installation de |arrivee chez |sejour chez )','',text)
    return re.sub(r'[^a-z0-9]+',' ',text).strip()
events=defaultdict(list);pairs=defaultdict(list);questions={};package_events=defaultdict(list)
for path in Path('game-library/current/sources').glob('*/question-bank/*.json'):
    bank=json.loads(path.read_text(encoding='utf8'))
    if bank['subject']=='Tests':continue
    for question in bank['questions']:
        if question['kind']!='ordering':continue
        questions[question['id']]=question
        values=[normalize(item['text']) for item in question['items']]
        package_events[path.parent.parent.name].extend(values)
        for item in values:events[item].append(question['id'])
        for pair in itertools.combinations(sorted(values),2):pairs[pair].append(question['id'])
revisions=runpy.run_path('build/chronology-revisions.py')['REVISIONS']
assert set(revisions)<=set(questions)
for qid,revision in revisions.items():
    question=questions[qid]
    ordered=[next(i['text'] for i in question['items'] if i['id']==item) for item in question['correctOrderIds']]
    assert ordered==[event for event,date in revision['events']],qid
    assert [date for event,date in revision['events']]==sorted(date for event,date in revision['events']),qid
for pid in ['lib-chronologie-architecture-reperes-20261012','lib-chronologie-bd-premieres-20261012','lib-chronologie-superheros-premieres-20261012','lib-chronologie-ghibli-sorties-20261012']:
    assert len(package_events[pid])==len(set(package_events[pid])),f'Repeated event in {pid}'
duplicates=[dict(events=list(pair),questions=ids) for pair,ids in pairs.items() if len(ids)>1]
report=dict(chronologyQuestions=len(questions),revisedQuestions=len(revisions),repeatedPairs=duplicates,
    repeatedSingleEvents=[dict(event=event,questions=ids) for event,ids in events.items() if len(ids)>1])
Path('game-library/current/CHRONOLOGY-AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'{len(revisions)} revised questions; {len(questions)} chronology questions audited; {len(duplicates)} repeated event pairs.')
if duplicates:print(json.dumps(duplicates,ensure_ascii=True,indent=2))
