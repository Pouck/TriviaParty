const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),{spawn}=require('node:child_process');
const dir=path.resolve('build/dialogue-extracts/vadrouille-tea-for-two'),out=path.join(dir,'checks');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(dir,'index.html')))});
server.listen(0,'127.0.0.1',async()=>{let chrome,ws;try{
chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--mute-audio','--no-first-run','--autoplay-policy=no-user-gesture-required','--remote-debugging-port=0','--user-data-dir='+path.join(out,'profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',d=>{log+=d;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1])});chrome.once('error',reject)});
ws=new WebSocket(endpoint);await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map();ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result)}};
const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}))});
const {targetId}=await send('Target.createTarget',{url:'about:blank'}),{sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false},sessionId);await send('Page.navigate',{url:'http://127.0.0.1:'+server.address().port},sessionId);await new Promise(r=>setTimeout(r,400));

const expected=JSON.parse(fs.readFileSync(path.join(dir,'dialogues.json'),'utf8'));
const decoded=await evaluate('(async()=>{const ctx=new AudioContext(),results=[];for(const a of document.querySelectorAll("audio")){const b=await ctx.decodeAudioData(await(await fetch(a.src)).arrayBuffer());const x=b.getChannelData(0);let peak=0,lead=0;for(let i=0;i<x.length;i++){peak=Math.max(peak,Math.abs(x[i]));if(i<b.sampleRate*.18)lead=Math.max(lead,Math.abs(x[i]))}results.push({number:a.dataset.number||"context",duration:b.duration,peak,lead})}await ctx.close();return results})()');
if(decoded.length!==expected.length)throw Error('Expected two extracts');
for(const r of expected){const a=decoded.find(a=>a.number===String(expected.indexOf(r)+1));if(!a||Math.abs(a.duration-r.durationSeconds)>.12||a.peak<.01||a.lead>.005)throw Error('Invalid excerpt '+r.id)}
fs.writeFileSync(path.join(out,'audio-validation.json'),JSON.stringify(decoded,null,2));
await evaluate('document.querySelector("#all").click()');await new Promise(r=>setTimeout(r,100));if(!await evaluate('sequence&&!clips[0].paused'))throw Error('Playlist failed');
await evaluate('clips[0].dispatchEvent(new Event("ended"))');await new Promise(r=>setTimeout(r,100));if(!await evaluate('!clips[1].paused&&clips[0].paused'))throw Error('Next clip/overlap failed');
await evaluate('stop()');if(await evaluate('clips.some(a=>!a.paused)'))throw Error('Stop failed');
fs.writeFileSync(path.join(out,'desktop.png'),Buffer.from((await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId)).data,'base64'));
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true},sessionId);if(await evaluate('document.documentElement.scrollWidth>innerWidth'))throw Error('Mobile overflow');
console.log('PASS: both extracts decode; durations and protected beginnings verified; playlist and stop work; phone layout fits.');await send('Browser.close');
}catch(e){console.error(e);process.exitCode=1}finally{ws?.close();chrome?.kill();server.close()}});
