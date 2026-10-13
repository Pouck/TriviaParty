const fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const {spawn}=require('node:child_process');
const root=path.resolve(process.argv[2]||'package-examples/architecture-2026-10-11'),assets=path.resolve('app/src/main/assets/tv'),out=path.resolve('build/'+(process.argv[2]?path.basename(root).replace(/-2026-.*/, '')+'-preview':'architecture-preview'));
fs.mkdirSync(out,{recursive:true});
const photos=fs.existsSync(path.join(root,'PHOTOS.json'))?JSON.parse(fs.readFileSync(path.join(root,'PHOTOS.json'),'utf8')):[];
const sheetFor=page=>{
 const subset=photos.slice(page*24,(page+1)*24),rows=Math.max(1,Math.ceil(subset.length/6)),rowHeight=1080/rows;
 return '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#111;color:white;font:18px Arial;display:grid;grid-template-columns:repeat(6,1fr);grid-template-rows:repeat('+rows+','+rowHeight+'px)}figure{margin:8px;display:flex;flex-direction:column;align-items:center}img{width:100%;height:'+(rowHeight-40)+'px;object-fit:contain}figcaption{padding:4px}</style>'+subset.map(p=>'<figure><img src="/photo/'+p.file+'"><figcaption>'+p.slug+'</figcaption></figure>').join('');
};
const server=http.createServer((req,res)=>{
 const url=req.url.split('?')[0];
 if(url.startsWith('/photo/')) {const file=photos.find(p=>'/photo/'+p.file===url);if(!file){res.writeHead(404);return res.end();}res.setHeader('Content-Type',file.file.endsWith('.png')?'image/png':file.file.endsWith('.webp')?'image/webp':'image/jpeg');return res.end(fs.readFileSync(path.join(root,'assets',file.file)));}
 const files={'/tv/hourglass.svg':['hourglass.svg','image/svg+xml'],'/tv/display.css':['receiver.css','text/css'],'/tv/receiver.js':['receiver.js','application/javascript']};
 if(files[url]) {res.setHeader('Content-Type',files[url][1]);return res.end(fs.readFileSync(path.join(assets,files[url][0])));}
 res.setHeader('Content-Type','text/html; charset=utf-8');res.end(url==='/photos'?sheetFor(Number(new URL(req.url,'http://localhost').searchParams.get('page')||0)):fs.readFileSync(path.join(assets,'display.html'),'utf8').replace('<script src="/tv/display.js"></script>',''));
});
server.listen(0,'127.0.0.1',async()=>{
 let chrome,ws;
 try {
  chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(out,'profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
  const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',d=>{log+=d;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1]);});chrome.once('error',reject);});
  ws=new WebSocket(endpoint);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
  let sequence=0;const pending=new Map();
  ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(new Error(JSON.stringify(r.error))):p.resolve(r.result);}};
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  await send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false},sessionId);
  await send('Page.enable',{},sessionId);
  const origin='http://127.0.0.1:'+server.address().port;
  const evaluate=async expression=>(await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId));
  const loaded='Promise.all(Array.from(document.images).map(img=>img.complete?Promise.resolve():new Promise(resolve=>{img.onload=resolve;img.onerror=resolve;})))';
  const capture=async name=>{const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(png.data,'base64'));};
  for(let page=0;page<Math.ceil(photos.length/24);page++){await send('Page.navigate',{url:origin+'/photos?page='+page},sessionId);await new Promise(r=>setTimeout(r,300));await evaluate(loaded);await capture(page===0?'photos':'photos-'+page);}
  await send('Page.navigate',{url:origin+'/tv?screen=1'},sessionId);await new Promise(r=>setTimeout(r,300));
  const base={type:'state',version:1,roomId:'1234',phase:'QUESTION_ACTIVE',category:'Architecture',categories:[],round:1,totalRounds:6,flip:0,secondsRemaining:15,secondsPerFlip:5,points:15,categoryAnswerTimeSeconds:10,answerTimeSeconds:10,teams:[{name:'Les bâtisseurs',score:35,connected:true},{name:'Les voyageurs',score:30,connected:true},{name:'Les architectes',score:20,connected:true},{name:'Les curieux',score:15,connected:true},{name:'Les rêveurs',score:10,connected:true},{name:'Les explorateurs',score:0,connected:true}]};
  const cases=[];
  for(const folder of fs.readdirSync(path.join(root,'sources'))) {
   const bank=JSON.parse(fs.readFileSync(path.join(root,'sources',folder,'question-bank',folder+'.json'),'utf8'));
   const game=JSON.parse(fs.readFileSync(path.join(root,'sources',folder,'game.json'),'utf8'));
   for(const q of bank.questions) {
    if(process.argv[3]&&!process.argv[3].split(',').some(key=>q.imageUrl?.includes(key)))continue;
    const answer=q.kind==='multipleChoice'?q.options[q.correctOptionIndex]:q.kind==='ordering'?q.correctOrderIds.map(id=>q.items.find(i=>i.id===id).text).join(' → '):q.acceptableAnswers[0];
    const chronology=q.kind==='ordering'||q.kind==='multipleChoice'&&q.options.every(o=>o.includes('→'));
    const make=(flip=0)=>({id:q.id,prompt:q.prompt+(q.items?'\n'+q.items.map(i=>'• '+i.text).join('\n'):'')+(q.clues?'\n\n'+q.clues.slice(0,flip+1).map((clue,i)=>(i+1)+'. '+clue).join('\n'):''),imageUrl:q.imageUrl?origin+'/photo/'+path.basename(q.imageUrl):null,options:chronology?[]:q.options||[],answer:null,answerMode:bank.answerMode});
    if(chronology)cases.push({...base,category:bank.category,categoryAnswerMode:bank.answerMode,questionReading:true,question:make()});
    for(let flip=0;flip<(q.clues?4:1);flip++)cases.push({...base,category:bank.category,categoryAnswerMode:bank.answerMode,flip,secondsPerFlip:game.timingConfig.secondsPerFlip,secondsRemaining:game.timingConfig.secondsPerFlip,points:q.clues?20-5*flip:15,question:make(flip)});
    cases.push({...base,category:bank.category,categoryAnswerMode:bank.answerMode,phase:'REVEAL_ANSWER',question:{...make(3),answer,...(q.kind==='multipleChoice'?{correctOptionIndex:q.correctOptionIndex}:{})}});
    if(q.kind==='textAnswer')cases.push({...base,category:bank.category,categoryAnswerMode:bank.answerMode,answeringTeam:'Les voyageurs',answerSecondsRemaining:8,question:make()});
   }
  }
  if(photos.some(p=>p.file==='pisa.jpg')&&photos.some(p=>p.file==='alhambra.jpg')){
  const longAnswer='La cathédrale Notre-Dame de Paris, située sur l’île de la Cité, célèbre pour ses grandes roses de vitraux, ses arcs-boutants et ses deux tours.';
  const longQuestion={id:'typography-long-answer',prompt:'Quelle cathédrale parisienne est décrite par ces éléments architecturaux ?',options:[],answer:longAnswer,answerMode:'BUZZER'};
  cases.push({...base,category:'Typographie — réponse longue',phase:'REVEAL_ANSWER',question:longQuestion});
  cases.push({...base,category:'Typographie — réponse sous image',phase:'REVEAL_ANSWER',question:{...longQuestion,id:'typography-image-answer',imageUrl:origin+'/photo/pisa.jpg'}});
  const beside={id:'typography-beside',prompt:'Dans quelle ville française se trouve cet édifice architectural ?',options:['A — Une ville avec un patrimoine architectural particulièrement remarquable','B — Une autre ville réputée pour ses grands monuments historiques','C — La ville où se trouve cet ensemble de bâtiments','D — Une ville connue pour son architecture et ses jardins'],imageUrl:origin+'/photo/alhambra.jpg',answer:null};
  cases.push({...base,category:'Typographie — question et choix longs',question:beside});
  cases.push({...base,category:'Typographie — question et choix longs',phase:'REVEAL_ANSWER',question:{...beside,correctOptionIndex:2,answer:beside.options[2]}});
  cases.push({...base,category:'Typographie — anciennes TV',question:{...beside,id:'typography-fallback'}});
  }
  let checked=0;const captures=new Set();
  for(const state of cases) {
   if(state.question.id==='typography-fallback')await evaluate('CSS.supports=()=>false;var legacy=document.createElement("style");legacy.textContent="h1,.clue-text,.options li,.chronology-line,.answer-text,.choice-text{text-wrap:wrap!important}";document.head.appendChild(legacy)');
   if(state.phase==='REVEAL_ANSWER')state.teams=state.teams.map((team,i)=>({...team,correct:i===0||i===2}));
   await evaluate('window.renderPreview ||= TriviaReceiver.makeRenderer(document);window.renderPreview('+JSON.stringify(state)+')');
   await evaluate(loaded);await new Promise(r=>setTimeout(r,25));
   if(state.category.includes('Chronologie')&&state.phase==='REVEAL_ANSWER'){
    await new Promise(r=>setTimeout(r,1100));
    const ranked=await evaluate('JSON.stringify(Array.from(document.querySelectorAll(".chronology-line.ranked")).sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top).map(el=>parseInt(el.textContent,10)))');
    if(ranked.result.value!=='[1,2,3]')throw new Error('Chronology did not settle into correct rank order: '+state.question.id+' '+ranked.result.value);
   }
   const measured=await evaluate('JSON.stringify({width:innerWidth,height:innerHeight,scroll:document.documentElement.scrollWidth,sceneScroll:document.getElementById("scene").scrollHeight,sceneHeight:document.getElementById("scene").clientHeight,detailsScroll:document.querySelector(".question-details")?.scrollHeight||0,detailsHeight:document.querySelector(".question-details")?.clientHeight||0,answerScroll:document.querySelector(".answer-slot")?.scrollHeight||0,answerHeight:document.querySelector(".answer-slot")?.clientHeight||0,answerWidth:document.querySelector(".answer-slot")?.scrollWidth||0,answerClientWidth:document.querySelector(".answer-slot")?.clientWidth||0,scores:document.getElementById("scores").getBoundingClientRect().bottom,images:Array.from(document.images).filter(i=>i.src.includes("/photo/")).every(i=>i.complete&&i.naturalWidth>0)})');
   const l=JSON.parse(measured.result.value);
   if(l.scroll>l.width||l.scores>l.height+1||l.detailsScroll>l.detailsHeight+1||l.sceneScroll>l.sceneHeight+1||l.answerScroll>l.answerHeight+1||l.answerWidth>l.answerClientWidth+1||!l.images)throw new Error('TV layout/image failure '+state.question.id+' '+state.phase+': '+JSON.stringify(l));
   if(state.question.id.startsWith('typography-'))await capture(state.question.id+'-'+state.phase);
   const key=state.category.includes('Chronologie')?'chronologie':state.category.includes('QCM')?(state.question.imageUrl?'qcm-image':'qcm'):state.category.includes('Buzzer')?(state.question.imageUrl?'buzzer-image':'buzzer'):state.category.includes('Qui suis-je')&&(state.flip===3||state.phase==='REVEAL_ANSWER')?'clues':null;
   if(key&&(!captures.has(key+'-'+state.phase))){await capture(key+'-'+state.phase);captures.add(key+'-'+state.phase);}
   checked++;
  }
  console.log(checked+' TV states fit at 1920×1080; all available embedded pictures loaded.');
  await send('Browser.close');
 }catch(error){console.error(error);process.exitCode=1;}
 finally{ws?.close();chrome?.kill();server.close();}
});
