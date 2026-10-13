const fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{spawn}=require('node:child_process');
const assets=path.resolve('app/src/main/assets/tv'),out=path.resolve('build/reaction-preview');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
 const mapping={'/tv/display.css':['receiver.css','text/css'],'/tv/receiver.js':['receiver.js','application/javascript']};
 if(mapping[req.url]){res.setHeader('Content-Type',mapping[req.url][1]);return res.end(fs.readFileSync(path.join(assets,mapping[req.url][0])));}
 if(/^\/tv\/sounds\/((good|bad)-(\d{2}|ping)\.(wav|mp3)|(buzzer|enabled|game-end)\.wav)$/.test(req.url)){res.setHeader('Content-Type',req.url.endsWith('mp3')?'audio/mpeg':'audio/wav');return res.end(fs.readFileSync(path.join(assets,'sounds',path.basename(req.url))));}
 res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(assets,'display.html'),'utf8').replace('<script src="/tv/display.js"></script>',''));
});
server.listen(0,'127.0.0.1',async()=>{
 let chrome,ws;
 try {
  chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--no-first-run','--autoplay-policy=no-user-gesture-required','--remote-debugging-port=0','--user-data-dir='+path.join(out,'profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
  const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',d=>{log+=d;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1]);});chrome.once('error',reject);});
  ws=new WebSocket(endpoint);await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map();
  ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result);}};
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'}),{sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  await send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false},sessionId);
  const origin='http://127.0.0.1:'+server.address().port;await send('Page.navigate',{url:origin+'/tv?screen=1'},sessionId);await new Promise(r=>setTimeout(r,300));
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  const base={type:'state',version:1,roomId:'preview',phase:'QUESTION_ACTIVE',category:'Architecture — Chronologie',categories:[],round:1,totalRounds:5,teams:[{name:'Les bâtisseurs',score:30,connected:true},{name:'Les architectes',score:15,connected:true}],flip:0,secondsRemaining:10,points:15,joinUrl:origin+'/play',answerSoundId:0};
  const bank=JSON.parse(fs.readFileSync('game-library/current/sources/lib-chronologie-architecture-reperes-20261012/question-bank/lib-chronologie-architecture-reperes-20261012.json','utf8'));
  for(const q of bank.questions) {
    const question={id:q.id,kind:'ordering',prompt:q.prompt,options:q.items.map(i=>i.text),orderItems:q.items,correctOrderIds:null,answer:null};
    await evaluate('window.renderFeedback ||= TriviaReceiver.makeRenderer(document);window.renderFeedback('+JSON.stringify({...base,question})+')');
    const layout=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,details:document.querySelector(".question-details").scrollHeight,height:document.querySelector(".question-details").clientHeight})');
    if(layout.scroll>layout.width||layout.details>layout.height+1)throw new Error('Chronology overflow '+q.id+JSON.stringify(layout));
  }
  const question={id:'feedback',prompt:'Quel monument se trouve à Paris ?',options:['Tour Eiffel','Colisée','Tower Bridge','Burj Khalifa'],answer:null};
  await evaluate('window.renderFeedback('+JSON.stringify({...base,question})+');window.questionBefore=document.getElementById("scene").firstChild');
  for(const [id,outcome,file] of [[1,'bad','bad-04.wav'],[2,'good','good-03.wav']]) {
    await evaluate('window.renderFeedback('+JSON.stringify({...base,question,answerSoundId:id,answerSound:outcome,answerSoundClip:file})+')');
    const result=await evaluate('({stable:window.questionBefore===document.getElementById("scene").firstChild,visible:getComputedStyle(document.getElementById("answer-feedback")).display,height:document.getElementById("answer-feedback").getBoundingClientRect().height,scroll:document.documentElement.scrollWidth})');
    if(!result.stable||result.visible!=='flex'||result.height<500||result.scroll>1920)throw new Error(JSON.stringify(result));
    const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(out,outcome+'.png'),Buffer.from(png.data,'base64'));
  }
  await new Promise(r=>setTimeout(r,2300));if(await evaluate('getComputedStyle(document.getElementById("answer-feedback")).display')!=='none')throw new Error('Feedback did not expire');
  const clips=JSON.parse(fs.readFileSync(path.join(assets,'sounds/reactions.json'),'utf8').replace(/^\uFEFF/,''));
  const decoded=await evaluate('(async()=>{const ctx=new AudioContext();const results=[];for(const clip of '+JSON.stringify(clips)+'){const response=await fetch("/tv/sounds/"+clip.file);const decoded=await ctx.decodeAudioData(await response.arrayBuffer());let peak=0,lead=0;const samples=decoded.getChannelData(0);for(let i=0;i<samples.length;i++){peak=Math.max(peak,Math.abs(samples[i]));if(i<decoded.sampleRate*.18)lead=Math.max(lead,Math.abs(samples[i]));}if(decoded.duration<.2||peak<.01||lead>.005)throw Error("Missing protected speech lead-in "+clip.file);results.push({file:clip.file,duration:decoded.duration,peak,lead});}await ctx.close();return results;})()');
  fs.writeFileSync(path.join(out,'audio-validation.json'),JSON.stringify(decoded,null,2));
  const teams=Array.from({length:8},(_,i)=>({name:'Équipe '+(i+1),score:60-i*5,connected:true,colorIndex:i}));
  const clues={id:'ready-layout',prompt:'Qui suis-je ?\n\n1. Je suis un monument de pierre célèbre depuis l’Antiquité.\n\n2. Des foules venaient assister à des spectacles dans mes gradins.\n\n3. Je suis un grand amphithéâtre situé dans la capitale italienne.',options:[],answer:null,answerMode:'WRITTEN'};
  for(const [name,extra] of [
   ['ready',{questionReading:true,playersReadyReading:true,readyCount:3,connectedCount:8}],
   ['answering',{answeringTeam:'Équipe 3',answerSecondsRemaining:8,answerTimeSeconds:10}],
   ['written-review',{phase:'ANSWER_REVIEW',submittedAnswer:'Le Colisée de Rome',categoryAnswerMode:'WRITTEN',answeringTeam:'Équipe 3'}]
  ]) {
    await evaluate('window.renderFeedback('+JSON.stringify({...base,question:clues,category:'Architecture — Qui suis-je ? écrit',teams,answerSoundId:2,...extra})+')');
    const measured=await evaluate('({scroll:document.documentElement.scrollWidth,width:innerWidth,details:document.querySelector(".question-details").scrollHeight,height:document.querySelector(".question-details").clientHeight,scoreWidth:document.getElementById("scores").scrollWidth,scoreClient:document.getElementById("scores").clientWidth,nameSize:parseFloat(getComputedStyle(document.querySelector("#scores .team span")).fontSize),answeringSize:parseFloat(getComputedStyle(document.getElementById("answering")).fontSize),colors:Array.from(document.querySelectorAll("#scores .team")).map(e=>getComputedStyle(e).backgroundColor)})');
    if(measured.scroll>measured.width||measured.details>measured.height+1||measured.scoreWidth>measured.scoreClient+1||measured.nameSize<30||measured.answeringSize<45||new Set(measured.colors).size<7)throw new Error(name+JSON.stringify(measured));
    const shot=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(shot.data,'base64'));
  }
  console.log('TV layouts fit at 1920×1080 with larger colored player names, readiness, selected-team and written-review states; all 46 speech clips decode and retain their protected lead-ins.');
  await send('Browser.close');
 }catch(e){console.error(e);process.exitCode=1;}finally{ws?.close();chrome?.kill();server.close();}
});
