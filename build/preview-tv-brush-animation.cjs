const fs=require('node:fs'), http=require('node:http'), path=require('node:path');
const {spawn}=require('node:child_process');
const output=path.resolve('build'), assets=path.resolve('app/src/main/assets/tv');
const server=http.createServer((req,res)=>{
  const url=req.url.split('?')[0];
  const files={'/tv/display.css':[path.join(assets,'receiver.css'),'text/css'], '/tv/receiver.js':[path.join(assets,'receiver.js'),'application/javascript'], '/map.png':[path.join(output,'map-preview.png'),'image/png']};
  if (/^\/tv\/feedback-(good|bad|red-stroke)\.png$/.test(url)) { res.setHeader('Content-Type','image/png'); return res.end(fs.readFileSync(path.join(assets,path.basename(url)))); }
  if(files[url]) {res.setHeader('Content-Type',files[url][1]);res.end(fs.readFileSync(files[url][0]));}
  else {res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(assets,'display.html'),'utf8').replace('<script src="/tv/display.js"></script>',''));}
});
server.listen(0,'127.0.0.1',async()=>{
  let chrome,ws;
  try {
    chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(output,'tv-layout-preview-profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
    const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',data=>{log+=data;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1]);});chrome.once('error',reject);});
    ws=new WebSocket(endpoint);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
    let sequence=0;const pending=new Map();
    ws.onmessage=event=>{const r=JSON.parse(event.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(new Error(JSON.stringify(r.error))):p.resolve(r.result);}};
    const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));});
    const {targetId}=await send('Target.createTarget',{url:'about:blank'});
    const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
    await send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false},sessionId);
    await send('Page.enable',{},sessionId);
    const origin='http://127.0.0.1:'+server.address().port;
    await send('Page.navigate',{url:origin+'/tv?screen=1'},sessionId);await new Promise(resolve=>setTimeout(resolve,400));
    const base={type:'state',version:1,roomId:'1234',phase:'QUESTION_ACTIVE',category:'Légendes de France — Régions et créatures — Qui suis-je écrit',categories:[],round:1,totalRounds:5,flip:0,secondsRemaining:12,points:15,
      question:{prompt:'Quel repère correspond à ce pays ?',imageUrl:origin+'/map.png',options:['A','B','C','D'],answer:null},
      teams:[{name:'Les étoiles',score:45,connected:true},{name:'Les voyageurs',score:30,connected:true},{name:'Les érudits',score:15,connected:true},{name:'Les explorateurs',score:15,connected:true}]};
    for(const phase of ['CATEGORY_INTRO','WAGER_OPEN','GAME_ENDED','QUESTION_ACTIVE','REVEAL_ANSWER']) {
      const state={...base,phase,categoryQuestionCount:10,categoryQuestionTypes:['Qui suis-je ? — réponse écrite'],categoryAnswerMode:'WRITTEN',question:phase==='QUESTION_ACTIVE'?base.question:{prompt:'Quel pays fallait-il identifier ?',imageUrl:null,options:[],answer:'B — Égypte'},
        wagerResults:base.teams.map((team,index)=>({teamName:team.name,amount:15,correct:index<2,delta:index<2?15:-15}))};
      await send('Runtime.evaluate',{expression:'window.renderPreview ||= TriviaReceiver.makeRenderer(document);window.renderPreview('+JSON.stringify(state)+')'},sessionId);
      await new Promise(resolve=>setTimeout(resolve,300));
      const measured=await send('Runtime.evaluate',{expression:'JSON.stringify({width:innerWidth,height:innerHeight,scroll:document.documentElement.scrollWidth,image:document.querySelector(".image-panel")?.getBoundingClientRect().width,scene:document.getElementById("scene").getBoundingClientRect().width,scores:document.getElementById("scores").getBoundingClientRect().bottom})',returnByValue:true},sessionId);
      const layout=JSON.parse(measured.result.value);
      if(layout.scroll>layout.width||layout.scores>layout.height+1)throw new Error('TV overflow: '+measured.result.value);
      if(phase==='QUESTION_ACTIVE'&&layout.image/layout.scene<.6)throw new Error('Map pane too narrow');
      const png=await send('Page.captureScreenshot',{format:'png'},sessionId);
      const file=path.join(output,'tv-layout-'+phase.toLowerCase()+'.png');fs.writeFileSync(file,Buffer.from(png.data,'base64'));console.log(file);
    }
    let cueId=0;
for(const sound of ['bad','good']) {
 await send('Runtime.evaluate',{expression:'window.renderPreview('+JSON.stringify({...base,answerSoundId:++cueId,answerSound:sound,answerSoundClip:null})+')'},sessionId);
 for(const moment of [200,550,1000]) {
  await send('Runtime.evaluate',{expression:'document.getAnimations().forEach(a=>{a.pause();a.currentTime='+moment+'})'},sessionId);
  await new Promise(r=>setTimeout(r,120));
  const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(output,'tv-brush-'+sound+'-'+moment+'.png'),Buffer.from(png.data,'base64'));
 }
}
await send('Browser.close');
  }catch(error){console.error(error);process.exitCode=1;}
  finally{ws?.close();chrome?.kill();server.close();}
});
