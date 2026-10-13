"""Verify active device catalogue and preserved review records after migration."""
import argparse,base64,io,json,subprocess,tarfile
from pathlib import Path
adb=['H:/Android/Sdk/platform-tools/adb.exe','-s','adb-2B021FDH300B81-JSzzEA._adb-tls-connect._tcp']
parser=argparse.ArgumentParser();parser.add_argument('--baseline',default='build/pixel-reviews-before-resize.json');args=parser.parse_args()
raw=subprocess.check_output(adb+['shell','-T','run-as','com.example.triviaparty','sh','-c',"'tar -cf - files/game-packages/*/game.json files/game-packages/*/question-bank/*.json | base64'"])
packages={}
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(raw))) as archive:
    for member in archive:
        if not member.isfile():continue
        parts=member.name.split('/'); entry=packages.setdefault(parts[2],{'banks':{}})
        data=json.loads(archive.extractfile(member).read())
        if parts[-1]=='game.json':entry['game']=data
        else:entry['banks'][parts[-1]]=data
catalog=json.loads(Path('game-library/current/CATALOGUE.json').read_text(encoding='utf8'))
assert set(packages)=={p['id'] for p in catalog},'Active package IDs differ'
ids=set()
for package in packages.values():
    questions=[q for bank in package['banks'].values() for q in bank['questions']]
    assert 5<=len(questions)<=7
    assert len({q['kind'] for q in questions})==1
    ids.update(q['id'] for q in questions)
reviews=json.loads(subprocess.check_output(adb+['shell','run-as','com.example.triviaparty','cat','files/host-review.json']))
baseline=json.loads(Path(args.baseline).read_text(encoding='utf8'))
assert reviews['reviews']==baseline['reviews'],'Saved reviews changed'
assert all(q in ids for q in reviews['reviews']),'Reviewed question missing'
Path('build/pixel-library-after-resize.json').write_text(json.dumps(packages,ensure_ascii=False,indent=2),encoding='utf8')
Path('build/pixel-reviews-after-resize.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf8')
print(f'Verified {len(packages)} active packages, {len(ids)} questions, and {len(reviews["reviews"])} unchanged reviews.')
