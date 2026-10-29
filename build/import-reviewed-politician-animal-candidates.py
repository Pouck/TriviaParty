"""Import only the candidate images visually approved in the contact sheet."""
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'game-library/bank'
CANDIDATES = ROOT / 'build/image-qsj-sampler/candidates/politicians-animals-more'
QUESTIONS = BANK / 'questions.json'
CREDITS = BANK / 'IMAGE-QSJ-MEDIA-CREDITS.json'
REVISION = 'image-qsj-politician-exotic-animal-additions-2026-10-27'

# Pangolin is a three-panel comparison and the flamingo photo contains two birds;
# both are excluded because this bank expects one clean, complete target subject.
APPROVED = {
 'louis-riel': ('politician','Louis Riel','Louis Riel','Figure politique canadienne'),
 'rene-levesque': ('politician','René Lévesque','René Lévesque','Figure politique québécoise'),
 'robert-borden': ('politician','Robert Borden','Robert Borden','Premier ministre du Canada'),
 'jean-chretien': ('politician','Jean Chrétien','Jean Chrétien','Premier ministre du Canada'),
 'angela-merkel': ('politician','Angela Merkel','Angela Merkel','Chancelière allemande'),
 'jawaharlal-nehru': ('politician','Jawaharlal Nehru','Jawaharlal Nehru','Premier ministre indien'),
 'golda-meir': ('politician','Golda Meir','Golda Meir','Première ministre israélienne'),
 'okapi': ('animal','Okapi','Okapi','Mammifère africain'),
 'giant-anteater': ('animal','Giant anteater','Tamanoir','Mammifère d’Amérique centrale et du Sud'),
 'wombat': ('animal','Wombat','Wombat','Marsupial australien'),
}

def main() -> None:
    questions = json.loads(QUESTIONS.read_text(encoding='utf-8'))
    credits = json.loads(CREDITS.read_text(encoding='utf-8'))
    if any(x.get('id') == REVISION for x in questions.get('revisionHistory', [])):
        print('Revision already applied.'); return
    meta = json.loads((CANDIDATES/'candidate-metadata.json').read_text(encoding='utf-8'))
    known = {a.casefold() for q in questions['questions'] for a in q.get('answers', [])}
    created = []
    for key, (kind, original, french, description) in APPROVED.items():
        row = meta[key]
        source_path = ROOT / row['candidate']
        blob = source_path.read_bytes()
        suffix = source_path.suffix.lower()
        filename = hashlib.sha256(blob).hexdigest()[:24] + suffix
        target = BANK/'media'/filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target)
        category = 'Histoire — Personnalités politiques — Qui suis-je ?' if kind == 'politician' else 'Nature — Animaux — Qui suis-je ?'
        qid = f'image-qsj-{kind}-{key}'
        answers = [original]
        if french.casefold() != original.casefold(): answers.append(french)
        title_kind = 'political_figure' if kind == 'politician' else 'animal'
        source = row['source']
        existing = next((q for q in questions['questions'] if any(a.casefold() == original.casefold() for a in q.get('answers', []))), None)
        presentation = {
                'id': qid, 'label': 'Qui suis-je ? — image', 'answerMode': 'BUZZER',
                'topic': 'Histoire' if kind == 'politician' else 'Nature', 'legacyCategory': category,
                'legacyPackageId': 'image-qsj-figures-politiques' if kind == 'politician' else 'image-qsj-animaux',
                'content': {'kind':'guessWho','prompt':'Qui suis-je ?','clues':[],'imageRevealMode':'BLUR',
                            'imageRevealSteps':6,'imageUrl':'media/'+filename,'basePoints':30,'penaltyPoints':0}
        }
        q = {
            'id': qid, 'legacyIds': [qid], 'topics': ['Histoire' if kind == 'politician' else 'Nature'],
            'prompt': 'Qui suis-je ?', 'answers': answers, 'content': {},
            'presentations': [presentation],
            'explanation': f'{original} — {description}.',
            'legacyReviews': [],
            'imageFacts': {'subjectType':title_kind,'subjectTitle':original,'frenchTitle':french,
                           'facts':[{'kind':'subject_title','value':original,'sourceUrl':source}], 'sources':[source]}
        }
        if existing:
            existing['presentations'].append(presentation)
            if qid not in existing['legacyIds']:
                existing['legacyIds'].append(qid)
            if not existing.get('imageFacts'):
                existing['imageFacts'] = q['imageFacts']
            existing['explanation'] = existing.get('explanation') or q['explanation']
        else:
            questions['questions'].append(q)
        known.update(a.casefold() for a in answers)
        credits[filename] = {
            'filename':row['commonsFile'].removeprefix('File:'), 'title':original,
            'creator':row.get('creator',''), 'credit':row.get('credit',''),
            'license':row.get('license',''), 'licenseUrl':row.get('licenseUrl',''),
            'source':source, 'downloadedFrom':row['downloadedFrom'], 'localSource':row['candidate'],
            'question':original,'category':category,
            'visualReview':'Approved: single-subject, recognizable portrait/photo with no overlay text.'
        }
        created.append({'id':qid,'answer':original,'media':filename})
    questions.setdefault('revisionHistory', []).append({'id':REVISION,
        'note':'Added visually reviewed single-subject political portraits and exotic animal photos. Rejected the three-panel pangolin comparison and two-bird flamingo photo.',
        'createdQuestions':[x['id'] for x in created]})
    QUESTIONS.write_text(json.dumps(questions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    CREDITS.write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'created':created,'excluded':['pangolin','greater-flamingo']},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
