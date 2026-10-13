"""Use the publisher's actual character illustration, retaining its copyright credit."""
from pathlib import Path
import json, urllib.request
out=Path('package-examples/library-2026-10-12')
url='https://www.dargaud.com/sites/dargaud.com/files/2020-03/lucky_luke_personnages_jolly_jumper_0.png'
metadata=dict(slug='bd-character-03',title='Jolly Jumper — illustration officielle',file='bd-character-03.png',
    commons='https://www.dargaud.com/bd/lucky-luke',download=url,artist='Morris / Dargaud',
    license='Illustration protégée — droits réservés à ses ayants droit',licenseUrl='https://www.dargaud.com/bd/lucky-luke',
    credit='Jolly Jumper, Lucky Luke — Morris / Dargaud. Illustration de la page personnages de l’éditeur.',
    changes='Aucune modification')
(out/'assets'/metadata['file']).write_bytes(urllib.request.urlopen(url).read())
(out/'assets/bd-character-03.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
