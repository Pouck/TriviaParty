const fs=require('fs');let s=fs.readFileSync('build/verify-winner-music-sampler.cjs','utf8');
s=s.replace("path.resolve('build/winner-music')","path.resolve('build/dialogue-extracts/X1PiR7WfuWs')").replace("path.join(dir,'sampler.html')","path.join(dir,'index.html')");
const start=s.indexOf('const decoded=');const end=s.indexOf("console.log('PASS:");
s=s.slice(0,start)+`
const expected=JSON.parse(fs.readFileSync(path.join(dir,'dialogues.json'),'utf8'));
const decoded=await evaluate('(async()=>{const ctx=new AudioContext(),results=[];for(const a of document.querySelectorAll("audio")){const b=await ctx.decodeAudioData(await(await fetch(a.src)).arrayBuffer());const x=b.getChannelData(0);let peak=0,lead=0;for(let i=0;i<x.length;i++){peak=Math.max(peak,Math.abs(x[i]));if(i<b.sampleRate*.18)lead=Math.max(lead,Math.abs(x[i]))}results.push({number:a.dataset.number||"context",duration:b.duration,peak,lead})}await ctx.close();return results})()');
if(decoded.length!==8)throw Error('Expected seven extracts and one context clip');
for(const r of expected){const a=decoded.find(a=>a.number===String(expected.indexOf(r)+1));if(!a||Math.abs(a.duration-r.durationSeconds)>.12||a.peak<.01||a.lead>.005)throw Error('Invalid excerpt '+r.id)}
fs.writeFileSync(path.join(out,'audio-validation.json'),JSON.stringify(decoded,null,2));
await evaluate('document.querySelector("#all").click()');await new Promise(r=>setTimeout(r,100));if(!await evaluate('sequence&&!clips[0].paused'))throw Error('Playlist failed');
await evaluate('clips[0].dispatchEvent(new Event("ended"))');await new Promise(r=>setTimeout(r,100));if(!await evaluate('!clips[1].paused&&clips[0].paused'))throw Error('Next clip/overlap failed');
await evaluate('stop()');if(await evaluate('all.some(a=>!a.paused)'))throw Error('Stop failed');
fs.writeFileSync(path.join(out,'desktop.png'),Buffer.from((await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId)).data,'base64'));
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true},sessionId);if(await evaluate('document.documentElement.scrollWidth>innerWidth'))throw Error('Mobile overflow');
`+s.slice(end);
s=s.replace(/console\.log\('PASS:[^']*'\)/,"console.log('PASS: seven extracts and context decode; durations and protected beginnings verified; playlist, exclusivity and stop work; phone layout fits.')");
fs.writeFileSync('build/verify-requested-dialogues.cjs',s);
