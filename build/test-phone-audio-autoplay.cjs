const fs=require('fs'),http=require('http'),path=require('path'),{spawn}=require('child_process');
const root=path.resolve('app/src/main/assets'),output=path.resolve('build/phone-audio-autoplay');fs.mkdirSync(output,{recursive:true});
const fixture=`<script>
window.testContexts=[];window.testStarts=0;window.testMessages=[];
const NativeContext=window.AudioContext;
window.AudioContext=class extends NativeContext {constructor(...args){super(...args);testContexts.push(this);}createBufferSource(){const source=super.createBufferSource(),start=source.start.bind(source);source.start=(...args)=>{if(this.state==='running')testStarts++;return start(...args);};return source;}};
window.fixtureState={roomId:'sound-room',state:'QUESTION_ACTIVE',categoryBuzzerSound:'owl',currentCategoryAnswerMode:'BUZZER',currentQuestion:{id:'q1',type:'textAnswer'},teams:[{id:'a',name:'Audio',score:0}],submissions:{},buzzQueue:[],textBuzzedTeamIds:[]};
sessionStorage.setItem('trivia-player:'+location.host,JSON.stringify({teamName:'Audio',roomId:'sound-room',sessionToken:'audio-test'}));
window.WebSocket=class {constructor(){window.testSocket=this;this.readyState=0;setTimeout(()=>{this.readyState=1;this.onopen();this.update();},10);}update(){this.onmessage({data:JSON.stringify({type:'com.example.triviaparty.network.GameEvent.RoomStateBroadcast',session:fixtureState})});}send(raw){const event=JSON.parse(raw);testMessages.push(event);if(event.type.endsWith('.JoinRoom'))this.onmessage({data:JSON.stringify({type:'com.example.triviaparty.network.GameEvent.JoinResponse',success:true,teamId:'a',message:'Joined'})});}};
</script>`;
const server=http.createServer((req,res)=>{
 const name=req.url.split('?')[0];let file,type;
 if(name==='/play'){res.setHeader('Content-Type','text/html');return res.end(fs.readFileSync(path.join(root,'player/index.html'),'utf8').replace('<script src=',fixture+'<script src='));}
 if(name.startsWith('/play/sounds/')){file=path.join(root,'tv/phone-sounds',path.basename(name));type='audio/mpeg';}
 else if(name==='/play/player.js'){file=path.join(root,'player/player.js');type='application/javascript';}
 else if(name==='/play/player.css'){file=path.join(root,'player/player.css');type='text/css';}
 if(!file||!fs.existsSync(file)){res.statusCode=404;return res.end();}res.setHeader('Content-Type',type);res.end(fs.readFileSync(file));
});
server.listen(0,'127.0.0.1',async()=>{let chrome,ws;
try {
 chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--no-first-run','--autoplay-policy=document-user-activation-required','--remote-debugging-port=0','--user-data-dir='+path.join(output,'profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
 const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',d=>{log+=d;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1]);});chrome.on('error',reject);});
 ws=new WebSocket(endpoint);await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map();
 ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result);}};
 const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));});
 const {targetId}=await send('Target.createTarget',{url:'about:blank'}),{sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true},sessionId);if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
 await send('Emulation.setDeviceMetricsOverride',{width:430,height:900,deviceScaleFactor:1,mobile:true},sessionId);await send('Emulation.setTouchEmulationEnabled',{enabled:true},sessionId);
 await send('Page.navigate',{url:'http://127.0.0.1:'+server.address().port+'/play'},sessionId);await new Promise(r=>setTimeout(r,700));
 const initial=await evaluate('({contexts:testContexts.map(c=>c.state),started:testStarts,buzz:!!document.querySelector(".buzz.ready")})');
 if(!initial.buzz||initial.started||initial.contexts[0]!=='suspended')throw Error('Expected a restored session with blocked autoplay: '+JSON.stringify(initial));
 async function contact(selector,phase){const point=await evaluate('(()=>{const r=document.querySelector('+JSON.stringify(selector)+').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()');await send('Input.dispatchTouchEvent',{type:phase,touchPoints:phase==='touchEnd'?[]:[point]},sessionId);}
 await contact('.buzz.ready','touchStart');const sentOnContact=await evaluate('testMessages.filter(m=>m.type.endsWith(".LockAnswer")).length');if(sentOnContact!==1)throw Error('Buzz did not send at contact');
 await contact('.buzz','touchEnd');await new Promise(r=>setTimeout(r,200));
 const after=await evaluate('({contexts:testContexts.map(c=>c.state),started:testStarts,status:document.getElementById("sound-status").textContent})');
 if(after.contexts[0]!=='running'||after.started!==1)throw Error('Touch release did not recover audio: '+JSON.stringify(after));
 await contact('#sound-button','touchStart');await contact('#sound-button','touchEnd');await new Promise(r=>setTimeout(r,100));
 if(await evaluate('testStarts')!==2)throw Error('Sound test did not play');
 await evaluate("fixtureState.currentQuestion.id='q2';testSocket.update()");await contact('.buzz.ready','touchStart');
 if(await evaluate('testStarts')!==3)throw Error('Unlocked buzz did not play immediately on contact');await contact('.buzz','touchEnd');
 const result={initial,sentOnContact,after,immediateStarts:await evaluate('testStarts')};fs.writeFileSync(path.join(output,'result.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result));const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(output,'player.png'),Buffer.from(png.data,'base64'));
 await send('Browser.close');
}catch(error){console.error(error);process.exitCode=1;}finally{ws?.close();chrome?.kill();server.close();}});
