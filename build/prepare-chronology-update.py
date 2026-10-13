"""Stage only packages containing the editorial chronology revisions."""
import json,runpy,shutil
from pathlib import Path
root=Path('game-library/current')
revisions=runpy.run_path('build/chronology-revisions.py')['REVISIONS']
mapping=json.loads((root/'MIGRATION.json').read_text(encoding='utf8'))['questionMap']
packages={mapping[q]['packageId'] for q in revisions}
destination=Path('build/chronology-update-20261012');destination.mkdir(exist_ok=True)
for pid in packages:shutil.copy2(root/f'{pid}.zip',destination/f'{pid}.zip')
assert {p.stem for p in destination.glob('*.zip')}==packages
print(f'Staged {len(packages)} packages containing {len(revisions)} revised questions.')
