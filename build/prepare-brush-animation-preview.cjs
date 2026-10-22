const fs=require('fs');let p=fs.readFileSync('build/preview-tv-emphasis.cjs','utf8');
p=p.replace("category:'Manga - Grands classiques - QCM'","category:'Légendes de France — Régions et créatures — Qui suis-je écrit'").replace("categoryQuestionTypes:['Choix multiples'],categoryAnswerMode:'SIMULTANEOUS'","categoryQuestionTypes:['Qui suis-je ? — réponse écrite'],categoryAnswerMode:'WRITTEN'");
const a=p.indexOf("for(const sound of ['bad','good'])"),b=p.indexOf("await send('Browser.close');",a);
p=p.slice(0,a)+`let cueId=0;
for(const sound of ['bad','good']) {
 await send('Runtime.evaluate',{expression:'window.renderPreview('+JSON.stringify({...base,answerSoundId:++cueId,answerSound:sound,answerSoundClip:null})+')'},sessionId);
 for(const moment of [200,550,1000]) {
  await send('Runtime.evaluate',{expression:'document.getAnimations().forEach(a=>{a.pause();a.currentTime='+moment+'})'},sessionId);
  await new Promise(r=>setTimeout(r,120));
  const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(output,'tv-brush-'+sound+'-'+moment+'.png'),Buffer.from(png.data,'base64'));
 }
}
`+p.slice(b);
fs.writeFileSync('build/preview-tv-brush-animation.cjs',p);
for(const name of ['cast-receiver/index.html','app/src/main/assets/tv/display.html']) {
 let html=fs.readFileSync(name,'utf8');const base=name.startsWith('cast')?'':'/tv/';
 html=html.replace('</head>', '<link rel="preload" as="image" href="'+base+'feedback-bad.png">\n  <link rel="preload" as="image" href="'+base+'feedback-good.png">\n</head>');fs.writeFileSync(name,html);
}
