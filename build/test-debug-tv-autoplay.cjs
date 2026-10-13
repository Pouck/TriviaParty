const fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{spawn}=require('node:child_process');
const assets=path.resolve('app/src/main/assets/tv'),out=path.resolve('build/autoplay-preview');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
 const mapping={'/tv/display.css':['receiver.css','text/css'],'/tv/receiver.js':['receiver.js','application/javascript']};
 if(mapping[req.url]){res.setHeader('Content-Type',mapping[req.url][1]);return res.end(fs.readFileSync(path.join(assets,mapping[req.url][0])));}
 if(/^\/tv\/sounds\/((good|bad)-(\d{2}|ping)\.(wav|mp3)|(buzzer|enabled|game-end)\.wav)$/.test(req.url)){res.setHeader('Content-Type',req.url.endsWith('mp3')?'audio/mpeg':'audio/wav');return res.end(fs.readFileSync(path.join(assets,'sounds',path.basename(req.url))));}
 res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(assets,'display.html'),'utf8').replace('<script src="/tv/display.js"></script>',''));
});
server.listen(0,'127.0.0.1',async()=>{
 let chrome,ws;
 try {
  chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--no-first-run','--autoplay-policy=document-user-activation-required','--remote-debugging-port=0','--user-data-dir='+path.join(out,'profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
  const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',d=>{log+=d;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1]);});chrome.once('error',reject);});
  ws=new WebSocket(endpoint);await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map();
  ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result);}};
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'}),{sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  await send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false},sessionId);
  const origin='http://127.0.0.1:'+server.address().port;await send('Page.navigate',{url:origin+'/tv'},sessionId);await new Promise(r=>setTimeout(r,400));
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  const inFrame=expression=>evaluate('document.querySelector("iframe").contentWindow.eval('+JSON.stringify(expression)+')');
  await inFrame('window.playingClips=[];window.audioErrors=[];const OriginalAudio=window.Audio;window.Audio=function(url){const audio=new OriginalAudio(url);audio.addEventListener("playing",()=>playingClips.push(audio.src.split("/").pop()));audio.addEventListener("error",()=>audioErrors.push(audio.src));return audio;};window.renderAudio=TriviaReceiver.makeRenderer(document,{localAudio:true})');
  const base={type:'state',version:1,roomId:'audio-preview',phase:'QUESTION_ACTIVE',category:'Audio',categories:[],round:1,totalRounds:5,teams:[{name:'A',score:0,connected:true}],flip:0,secondsRemaining:10,points:15,joinUrl:'http://unreachable-host:8080/play',answerSoundId:0,buzzerSoundId:0,question:{id:'audio',prompt:'Question au buzzer',options:[],answer:null}};
  await inFrame('renderAudio('+JSON.stringify(base)+')');
  await inFrame('renderAudio('+JSON.stringify({...base,answerSoundId:1,answerSound:'good',answerSoundClip:'good-01.wav'})+')');await new Promise(r=>setTimeout(r,200));
  const blocked=await inFrame('({played:playingClips,display:getComputedStyle(document.getElementById("tv-audio-control")).display,text:document.getElementById("tv-audio-control").textContent,active:navigator.userActivation.hasBeenActive})');
  if(blocked.played.length||blocked.display==='none'||blocked.active)throw new Error('Did not reproduce blocked autoplay '+JSON.stringify(blocked));
  const box=await inFrame('(()=>{const r=document.getElementById("tv-audio-control").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()');
  for(const type of ['mousePressed','mouseReleased'])await send('Input.dispatchMouseEvent',{type,x:box.x,y:box.y,button:'left',clickCount:1},sessionId);
  for(let attempt=0;attempt<30;attempt++) { if(await inFrame('getComputedStyle(document.getElementById("tv-audio-control")).display')==='none') break; await new Promise(r=>setTimeout(r,100)); }
  if(await inFrame('getComputedStyle(document.getElementById("tv-audio-control")).display')!=='none')throw new Error('Trusted activation click did not unlock audio');
  for(const state of [
   {...base,answerSoundId:1,buzzerSoundId:1,answeringTeam:'A'},
   {...base,answerSoundId:2,buzzerSoundId:1,answerSound:'bad',answerSoundClip:'bad-04.wav'},
   {...base,answerSoundId:3,buzzerSoundId:1,answerSound:'good',answerSoundClip:'good-03.wav'}
  ]) {
    await inFrame('renderAudio('+JSON.stringify(state)+')');
    const file=state.answerSoundClip||'buzzer.wav';
    for(let attempt=0;attempt<60;attempt++) {
      if(await inFrame('playingClips.includes('+JSON.stringify(file)+')'))break;
      await new Promise(r=>setTimeout(r,100));
    }
  }
  const submitted={...base,answerSoundId:3,buzzerSoundId:1,teams:[{name:'Right',score:0,answerResult:true},{name:'Wrong',score:0,answerResult:false},{name:'Waiting',score:0,answerResult:null}]};
  await inFrame('renderAudio('+JSON.stringify(submitted)+')');
  const colors=await inFrame('Array.from(document.getElementById("scores").children).map(card=>({name:card.textContent,classes:card.className,color:getComputedStyle(card).backgroundColor}))');
  if(!colors[0].classes.includes('correct-team')||!colors[1].classes.includes('incorrect-team')||colors[2].classes!=='team'||colors[0].color===colors[1].color)throw new Error('Card feedback failed '+JSON.stringify(colors));
  const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(out,'submitted-cards.png'),Buffer.from(png.data,'base64'));
  await inFrame('renderAudio('+JSON.stringify({...submitted,phase:'GAME_ENDED',question:null})+')');await new Promise(r=>setTimeout(r,300));
  await inFrame('renderAudio('+JSON.stringify({...submitted,phase:'GAME_ENDED',question:null})+')');
  const result=await inFrame('({played:playingClips,errors:audioErrors,activated:navigator.userActivation.hasBeenActive})');
  if(JSON.stringify(result.played)!==JSON.stringify(['enabled.wav','buzzer.wav','bad-ping.wav','bad-04.wav','good-ping.wav','good-03.wav','game-end.wav'])||result.errors.length)throw new Error('Playback failed '+JSON.stringify(result));
  fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({blocked,result,colors},null,2));
  console.log('Normal autoplay restrictions: activation, buzzer, negative ping then voice, positive ping then voice, and one end fanfare all play; submitted cards turn green/red immediately at TV resolution.');
  await send('Browser.close');
 }catch(e){console.error(e);process.exitCode=1;}finally{ws?.close();chrome?.kill();server.close();}
});
