from pathlib import Path
import json

root=Path('package-examples/culture-2026-10-10/sources')
cases=[]
for file in sorted(root.glob('culture-qsj-*/question-bank/*.json')):
    for q in json.loads(file.read_text(encoding='utf-8'))['questions']:
        cases.append(dict(type='state',version=1,roomId='1234',phase='QUESTION_ACTIVE',category=q['category'],categories=[],round=1,totalRounds=4,flip=3,secondsRemaining=20,points=5,question=dict(prompt=q['prompt']+'\n\n'+'\n'.join(f'{i+1}. {clue}' for i,clue in enumerate(q['clues'])),imageUrl=None,options=[],answer=None),teams=[dict(name='Les étoiles',score=20,connected=True)]))
cases.sort(key=lambda c:len(c['question']['prompt']),reverse=True)
source=Path('build/preview-qui-suis-je.cjs').read_text(encoding='utf-8')
start=source.index('    const base=')
end=source.index("    await send('Browser.close');",start)
block='    const cases='+json.dumps(cases,ensure_ascii=False)+';\n'+'''    let checked=0;
    for(const state of cases) {
      await send('Runtime.evaluate',{expression:'window.renderPreview ||= TriviaReceiver.makeRenderer(document);window.renderPreview('+JSON.stringify(state)+')'},sessionId);
      await new Promise(resolve=>setTimeout(resolve,30));
      const measured=await send('Runtime.evaluate',{expression:'JSON.stringify({width:innerWidth,height:innerHeight,scroll:document.documentElement.scrollWidth,sceneScroll:document.getElementById("scene").scrollHeight,sceneHeight:document.getElementById("scene").clientHeight,detailsScroll:document.querySelector(".question-details").scrollHeight,detailsHeight:document.querySelector(".question-details").clientHeight,scores:document.getElementById("scores").getBoundingClientRect().bottom})',returnByValue:true},sessionId);
      const layout=JSON.parse(measured.result.value);
      if(layout.scroll>layout.width || layout.scores>layout.height+1 || layout.detailsScroll>layout.detailsHeight+1 || layout.sceneScroll>layout.sceneHeight+1)throw new Error('TV overflow for '+state.category+': '+measured.result.value);
      if(checked===0) {
        const png=await send('Page.captureScreenshot',{format:'png'},sessionId);
        fs.writeFileSync(path.join(output,'culture-four-clues.png'),Buffer.from(png.data,'base64'));
      }
      checked++;
    }
    console.log(checked+' questions: four clues fit at 1920×1080 without scrolling.');
'''
source=source[:start]+block+source[end:]
source=source.replace('progressive-preview-profile','culture-preview-profile')
Path('build/preview-culture.cjs').write_text(source,encoding='utf-8')
