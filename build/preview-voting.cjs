const fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{spawn}=require('node:child_process');
const assets=path.resolve('app/src/main/assets/tv'),out=path.resolve('build/voting-preview');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
 const files={'/tv/display.css':['receiver.css','text/css'],'/tv/receiver.js':['receiver.js','application/javascript']};
 if(files[req.url]){res.setHeader('Content-Type',files[req.url][1]);return res.end(fs.readFileSync(path.join(assets,files[req.url][0])));}
 res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(assets,'display.html'),'utf8').replace('<script src="/tv/display.js"></script>',''));
});
server.listen(0,'127.0.0.1',async()=>{
 let chrome,ws;
 try {
  chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(out,'profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
  const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',d=>{log+=d;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1]);});chrome.once('error',reject);});
  ws=new WebSocket(endpoint);await new Promise(r=>ws.onopen=r);
  let seq=0;const pending=new Map();ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result);}};
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'}),{sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  await send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false},sessionId);
  const origin='http://127.0.0.1:'+server.address().port;
  await send('Page.navigate',{url:origin+'/tv?screen=1'},sessionId);await new Promise(r=>setTimeout(r,300));
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  const subjects=['Architecture','Arts','BD et manga','Cinéma','Contes et légendes','Cuisine','Culture populaire','Géographie','Histoire','Jeux vidéo','Littérature','Logique et énigmes','Musique','Mythologie','Nature','Sciences','Super-héros'];
  const base={type:'state',version:1,roomId:'vote-preview',phase:'SUBJECT_VOTING',category:null,categories:[],round:0,totalRounds:0,question:null,teams:Array.from({length:8},(_,i)=>({name:'Équipe '+(i+1),score:0,connected:true})),flip:0,secondsRemaining:0,points:0,joinUrl:origin+'/play'};
  const vote={candidates:subjects,selected:[],totals:Object.fromEntries(subjects.map((s,i)=>[s,i%4])),round:1,slots:5,hostTieBreak:false,completed:false,ballots:8};
  for(const [name,state] of [
   ['vote-initial',{...base,subjectVote:vote}],
   ['vote-second',{...base,subjectVote:{...vote,candidates:subjects.slice(6,13),selected:subjects.slice(0,3),slots:2,round:2}}],
   ['vote-host-tie',{...base,subjectVote:{...vote,candidates:subjects.slice(6,10),selected:subjects.slice(0,3),slots:2,round:3,hostTieBreak:true}}]
  ]){
   await evaluate('window.renderVote ||= TriviaReceiver.makeRenderer(document);window.renderVote('+JSON.stringify(state)+')');
   const layout=JSON.parse(await evaluate('JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,height:document.getElementById("scene").clientHeight,content:document.getElementById("scene").scrollHeight,count:document.querySelectorAll(".subject-vote-card").length})'));
   if(layout.scroll>layout.width||layout.content>layout.height+1||layout.count!==state.subjectVote.candidates.length)throw new Error(name+': '+JSON.stringify(layout));
   const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(png.data,'base64'));
  }
  console.log('Three voting phases fit at 1920×1080, including all 17 initial subjects.');
  await send('Browser.close');
 }catch(e){console.error(e);process.exitCode=1;}finally{ws?.close();chrome?.kill();server.close();}
});
