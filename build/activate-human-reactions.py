"""Explicitly activate the auditioned 100-clip bank, preserving the existing bank in Git history."""
from pathlib import Path
import json,shutil,html
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'audio-bank';TARGET=ROOT/'app/src/main/assets/tv/sounds'
records=json.loads((BANK/'reactions.json').read_text(encoding='utf8'))
assert len(records)==100 and all(r['license'] and r['sourceUrl'] for r in records)
assert all((BANK/'clips'/r['file']).is_file() for r in records)
for r in records:shutil.copy2(BANK/'clips'/r['file'],TARGET/r['file'])
(TARGET/'reactions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
shutil.copy2(BANK/'ATTRIBUTION.md',TARGET/'ATTRIBUTION.md')
if (BANK/'credits.html').exists():shutil.copy2(BANK/'credits.html',TARGET.parent/'audio-credits.html')
lines=['package com.example.triviaparty.model','','/** Generated from the bundled reaction manifest. */','internal object ReactionCatalogue {','    val clips = listOf(']
for i,r in enumerate(records):lines.append('        ReactionClip('+','.join(json.dumps(r[k],ensure_ascii=True) for k in ['file','outcome','voice','text'])+')'+(',' if i<len(records)-1 else ''))
lines+=['    )','}']
(ROOT/'app/src/main/java/com/example/triviaparty/model/ReactionCatalogue.kt').write_text('\n'.join(lines)+'\n',encoding='utf8')
print('Activated 100 human clips; rebuild and test before installing. This bank contains pronunciation recordings plus five acted game reactions, not film dialogue.')
