from pathlib import Path
import json
source=Path('build/preview-tv-layout.cjs').read_text(encoding='utf-8')
q=json.loads(Path('package-examples/qui-suis-je-demo/sources/question-bank/qui-suis-je-demo.json').read_text(encoding='utf-8'))['questions'][0]
prompt=q['prompt']+'\n\n'+'\n\n'.join(f'{i+1}. {clue}' for i,clue in enumerate(q['clues']))
base=dict(type='state',version=1,roomId='1234',phase='QUESTION_ACTIVE',category=q['category'],categories=[],round=1,totalRounds=1,flip=2,secondsRemaining=5,points=5,question=dict(prompt=prompt,imageUrl=None,options=[],answer=None),teams=[dict(name='Les étoiles',score=15,connected=True)])
start=source.index('    const base=')
end=source.index('    for(const phase',start)
source=source[:start]+'    const base='+json.dumps(base,ensure_ascii=False)+';\n'+source[end:]
source=source.replace("['QUESTION_ACTIVE','REVEAL_ANSWER','WAGER_RESULTS']","['QUESTION_ACTIVE','REVEAL_ANSWER']")
source=source.replace("prompt:'Quel pays fallait-il identifier ?',imageUrl:null,options:[],answer:'B — Égypte'","prompt:'Qui suis-je ?',imageUrl:null,options:[],answer:'Un sablier'")
source=source.replace("tv-layout-preview-profile","progressive-preview-profile")
source=source.replace("if(phase==='QUESTION_ACTIVE'&&layout.image/layout.scene<.6)throw new Error('Map pane too narrow');", "")
source=source.replace("'tv-layout-'","'qui-suis-je-'")
source=source.replace('scene:document.getElementById("scene").getBoundingClientRect().width,','scene:document.getElementById("scene").getBoundingClientRect().width,detailsScroll:document.querySelector(".question-details").scrollHeight,detailsHeight:document.querySelector(".question-details").clientHeight,')
source=source.replace("const png=await send", "if(layout.detailsScroll>layout.detailsHeight+1)throw new Error('Clues require scrolling');\n      const png=await send")
Path('build/preview-qui-suis-je.cjs').write_text(source,encoding='utf-8')
