from pathlib import Path
import json,hashlib,collections
R=Path.cwd();D=R/'build/movie-audition';rows=json.loads((D/'reactions.json').read_text(encoding='utf8'));before=json.loads((D/'pre-classic-integration-hashes.json').read_text(encoding='utf8'))
assert len(rows)==100 and collections.Counter(r['outcome'] for r in rows)=={'good':50,'bad':50}
assert len({r['sha256'] for r in rows})==100
assert all(hashlib.sha256((D/f).read_bytes()).hexdigest()==h for f,h in before.items())
short=[r for r in rows if r.get('preparedAsset')];assert len(short)==10
page=(D/'credits.html').read_text(encoding='utf8')
for r in short:
 assert hashlib.sha256((R/r['preparedAsset']).read_bytes()).hexdigest()==r['sha256']
 assert r['licenseUrl'] in page and r['attribution'].replace('&','&amp;') in page
assert all(r['audience']=='all' for r in short)
print('100 unique clips; balanced 50/50; 88 original files unchanged; 10 short recordings retain audio hashes, licenses and displayed attribution.')
