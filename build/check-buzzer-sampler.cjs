const fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{spawn}=require('node:child_process');
const assets=path.resolve('app/src/main/assets/tv'),out=path.resolve('build/buzzer-browser-check');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');
 if(url.pathname==='/sampler' || url.pathname==='/success-sampler.html'){res.setHeader('Content-Type','text/html; charset=utf-8');return res.end(fs.readFileSync(path.join(assets,url.pathname==='/sampler'?'buzzer-sampler.html':'success-sampler.html')));}
 if(url.pathname==='/tv/receiver.js'){res.setHeader('Content-Type','application/javascript');return res.end(fs.readFileSync(path.join(assets,'receiver.js')));}
 if(/^\/tv\/sounds\/(buzzer(-\d{2})?|success-\d{2})\.wav$/.test(url.pathname)){res.setHeader('Content-Type','audio/wav');return res.end(fs.readFileSync(path.join(assets,'sounds',path.basename(url.pathname))));}
 res.writeHead(404);res.end();
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
  const origin='http://127.0.0.1:'+server.address().port;await send('Page.navigate',{url:origin+'/sampler'},sessionId);await new Promise(r=>setTimeout(r,300));
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  const checked=await evaluate(`(async()=>{
    if(document.querySelectorAll('article').length!==20)throw Error('Expected twenty choices');
    const ctx=new AudioContext();const result=[];
    for(const prefix of ['buzzer-','success-'])for(let n=1;n<=20;n++){
      const name=prefix+String(n).padStart(2,'0')+'.wav';const bytes=await (await fetch('/tv/sounds/'+name)).arrayBuffer();const decoded=await ctx.decodeAudioData(bytes);
      const data=decoded.getChannelData(0);let onset=0;while(onset<data.length && Math.abs(data[onset])<.01)onset++;
      if(onset/decoded.sampleRate>.01)throw Error('Delayed attack: '+name);
      result.push({file:name,duration:decoded.duration,onsetMs:1000*onset/decoded.sampleRate});
    }
    await ctx.close();
    document.querySelectorAll('article button')[0].click();document.querySelectorAll('article button')[4].click();
    if(document.querySelectorAll('article.playing').length!==1 || !document.getElementById('status').textContent.includes('plateau'))throw Error('Exclusive audition failed');
    document.getElementById('stop').click();if(document.querySelectorAll('.playing').length)throw Error('Stop failed');
    return result;
  })()`);
  fs.writeFileSync(path.join(out,'audio-validation.json'),JSON.stringify(checked,null,2));
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true},sessionId);
  if(await evaluate('document.documentElement.scrollWidth>innerWidth'))throw Error('Sampler overflows phone width');
  await evaluate(`(async()=>{await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='/tv/receiver.js';script.onload=resolve;script.onerror=reject;document.head.append(script);});
    let decodedResolve;const decoded=new Promise(r=>decodedResolve=r);const original=AudioContext.prototype.decodeAudioData;
    AudioContext.prototype.decodeAudioData=function(bytes){return original.call(this,bytes).then(buffer=>{decodedResolve();return buffer;});};
    let started=null;const create=AudioContext.prototype.createBufferSource;AudioContext.prototype.createBufferSource=function(){const source=create.call(this);const start=source.start.bind(source);source.start=(...args)=>{started=performance.now();start(...args);};return source;};
    const player=TriviaReceiver.makeSoundPlayer(document);player.setOrigin(location.origin+'/play');player.setVersion('sampler');await decoded;await new Promise(r=>setTimeout(r,20));const press=performance.now();player.play('buzzer.wav');
    if(started===null || started-press>50)throw Error('Buzzer did not start from decoded memory');window.buzzerStartMs=started-press;player.stop();
  })()`);
  console.log('Forty buzzer and success sounds decode, begin within 10 ms, play exclusively and fit a phone screen.');
  console.log('Preloaded Web Audio start scheduling: '+await evaluate('window.buzzerStartMs')+' ms after the playback call (network/TV output latency excluded).');
  await send('Page.navigate',{url:origin+'/success-sampler.html'},sessionId);await new Promise(r=>setTimeout(r,300));
  if(await evaluate('document.querySelectorAll(\"article\").length')!==20)throw Error('Missing success samples');
  if(await evaluate('document.documentElement.scrollWidth>innerWidth'))throw Error('Success sampler overflows');
  const shot=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(out,'sampler-phone.png'),Buffer.from(shot.data,'base64'));
  await send('Browser.close');
 }catch(e){console.error(e);process.exitCode=1;}finally{ws?.close();chrome?.kill();server.close();}
});
