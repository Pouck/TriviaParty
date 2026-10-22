const fs=require('fs');
let t=fs.readFileSync('cast-receiver/receiver.test.js','utf8');t+=`
test('category titles break at separators and keep repeated formats out of headings', () => {
 for (const renderer of [receiver,currentReceiver]) {
  const doc=documentStub(),render=renderer.makeRenderer(doc);
  render(state({phase:'CATEGORY_INTRO',category:'Manga - Grands classiques - QCM',categoryQuestionTypes:['Choix multiples'],categoryAnswerMode:'SIMULTANEOUS'}));
  const scene=doc.getElementById('scene');
  assert.deepEqual(scene.firstChild.children.map(line=>line.textContent),['Manga','Grands classiques']);
  assert.equal((scene.textContent.match(/Choix multiples/g)||[]).length,1);
  assert.equal(doc.getElementById('category').textContent,'Manga · Grands classiques');
  render(state({phase:'CATEGORY_INTRO',category:'Culture - Qui suis-je ? - Buzzer',categoryQuestionTypes:['Qui suis-je ?','Buzzer'],categoryAnswerMode:'BUZZER'}));
  assert.equal(doc.getElementById('scene').firstChild.textContent,'Culture');
  assert.equal((scene.textContent.match(/Buzzer/g)||[]).length,1);
  assert.equal((scene.textContent.match(/Qui suis-je/g)||[]).length,1);
  render(state({phase:'CATEGORY_INTRO',category:'Histoire — Chronologie',categoryQuestionTypes:['Chronologie'],categoryAnswerMode:'SIMULTANEOUS'}));
  assert.equal(scene.firstChild.textContent,'Histoire');
  assert.equal((scene.textContent.match(/Chronologie/g)||[]).length,1);
 }
});
`;fs.writeFileSync('cast-receiver/receiver.test.js',t);
let p=fs.readFileSync('build/preview-tv-emphasis.cjs','utf8');
p=p.replace("if(files[url])", "if (/^\\/tv\\/feedback-(good|bad)\\.png$/.test(url)) { res.setHeader('Content-Type','image/png'); return res.end(fs.readFileSync(path.join(assets,path.basename(url)))); }\n  if(files[url])");
p=p.replace("category:'Géographie - Afrique'","category:'Manga - Grands classiques - QCM'").replace("categoryQuestionTypes:['Buzzer'],categoryAnswerMode:'BUZZER'","categoryQuestionTypes:['Choix multiples'],categoryAnswerMode:'SIMULTANEOUS'");
p=p.replace("const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync", "await new Promise(r=>setTimeout(r,250));\n const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync");
fs.writeFileSync('build/preview-tv-emphasis.cjs',p);
