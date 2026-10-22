const fs=require('fs');let t=fs.readFileSync('cast-receiver/receiver.test.js','utf8');t=t.replace("assert.equal(feedback.textContent,'✕')","assert.equal(feedback.firstChild.className,'brush-mark')").replace("assert.equal(feedback.textContent,'✓')","assert.equal(feedback.firstChild.className,'brush-mark')").replace('/Type : Buzzer/','/Buzzer/').replace('/Type : Chronologie/','/Chronologie/');fs.writeFileSync('cast-receiver/receiver.test.js',t);
let p=fs.readFileSync('build/preview-tv-layout.cjs','utf8');p=p.replace("origin+'/tv'","origin+'/tv?screen=1'").replace("['QUESTION_ACTIVE','REVEAL_ANSWER','WAGER_RESULTS']","['CATEGORY_INTRO','WAGER_OPEN','GAME_ENDED','QUESTION_ACTIVE','REVEAL_ANSWER']").replace("const state={...base,phase,question:","const state={...base,phase,categoryQuestionCount:10,categoryQuestionTypes:['Buzzer'],categoryAnswerMode:'BUZZER',question:");
p=p.replace("if(layout.scroll>layout.width", "if(layout.scroll>layout.width");
p=p.replace("await send('Browser.close');",`for(const sound of ['bad','good']) {
 await send('Runtime.evaluate',{expression:'window.renderPreview('+JSON.stringify({...base,answerSoundId:1,answerSound:'bad',answerSoundClip:null})+')'},sessionId);
 await send('Runtime.evaluate',{expression:"document.getElementById('answer-feedback').className='answer-feedback "+sound+"';document.getElementById('answer-feedback').style.display='flex'"},sessionId);
 const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(output,'tv-feedback-'+sound+'.png'),Buffer.from(png.data,'base64'));
}
await send('Browser.close');`);fs.writeFileSync('build/preview-tv-emphasis.cjs',p);
