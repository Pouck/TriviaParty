const fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{spawn}=require('node:child_process');
const assets=path.resolve('app/src/main/assets/tv'),out=path.resolve('build/movie-audition/browser-check');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
 if(req.url==='/audition'){res.setHeader('Content-Type','text/html; charset=utf-8');return res.end(fs.readFileSync(path.resolve('build/movie-audition/credits.html')));}
 const mapping={'/tv/display.css':['receiver.css','text/css'],'/tv/receiver.js':['receiver.js','application/javascript']};
 if(mapping[req.url]){res.setHeader('Content-Type',mapping[req.url][1]);return res.end(fs.readFileSync(path.join(assets,mapping[req.url][0])));}
 if(/^\/tv\/sounds\/((good|bad)-(\d{2}|ping)\.(wav|mp3)|(buzzer|enabled|game-end)\.wav)$/.test(req.url)){res.setHeader('Content-Type',req.url.endsWith('mp3')?'audio/mpeg':'audio/wav');return res.end(fs.readFileSync(path.resolve('build/movie-audition',path.basename(req.url))));}
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
  const clips=JSON.parse(fs.readFileSync(path.resolve('build/movie-audition/reactions.json'),'utf8').replace(/^\uFEFF/,''));
  const decoded=await evaluate('(async()=>{const ctx=new AudioContext();const results=[];for(const clip of '+JSON.stringify(clips)+'){const response=await fetch("/tv/sounds/"+clip.file);const decoded=await ctx.decodeAudioData(await response.arrayBuffer());let peak=0,lead=0;const samples=decoded.getChannelData(0);for(let i=0;i<samples.length;i++){peak=Math.max(peak,Math.abs(samples[i]));if(i<decoded.sampleRate*.18)lead=Math.max(lead,Math.abs(samples[i]));}if(decoded.duration<.2||peak<.01||lead>.005)throw Error("Missing protected speech lead-in "+clip.file);results.push({file:clip.file,duration:decoded.duration,peak,lead});}await ctx.close();return results;})()');
  fs.writeFileSync(path.join(out,'audio-validation.json'),JSON.stringify(decoded,null,2));
  console.log('All '+clips.length+' film clips decode in Chrome with protected speech lead-ins.');
  await send('Page.navigate',{url:origin+'/audition'},sessionId);await new Promise(r=>setTimeout(r,300));
  const count=await evaluate('document.querySelectorAll("article").length');if(count!==clips.length)throw Error('Incomplete audition page');
  const good=await evaluate('document.getElementById("outcome").value="good";document.getElementById("outcome").dispatchEvent(new Event("input"));document.querySelectorAll("article:not([hidden])").length');if(good!==clips.filter(c=>c.outcome==='good').length)throw Error('Outcome filtering failed');
  const search=await evaluate('document.getElementById("search").value="magie";document.getElementById("search").dispatchEvent(new Event("input"));document.querySelectorAll("article:not([hidden])").length');if(search!==1)throw Error('Corrected Kaamelott clip not searchable');
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true},sessionId);
  const overflow=await evaluate('document.documentElement.scrollWidth>innerWidth');if(overflow)throw Error('Audition page overflows phone width');
  console.log('Audition filters work and the page fits a phone screen.');
  await send('Browser.close');
 }catch(e){console.error(e);process.exitCode=1;}finally{ws?.close();chrome?.kill();server.close();}
});
