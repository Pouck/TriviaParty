const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { spawn } = require('node:child_process');
const assets = path.resolve('app/src/main/assets/player');
const output = path.resolve('build');
const mock = `<script>
window.WebSocket = class {
  constructor() { this.readyState = 0; setTimeout(() => { this.readyState = 1; this.onopen(); this.state(); }, 10); }
  state(active) { this.onmessage({data: JSON.stringify({type:'com.example.triviaparty.network.GameEvent.RoomStateBroadcast',session:{roomId:'4821',state:active?(location.search.includes('wager=1')?'WAGER_OPEN':location.search.includes('ended=1')?'GAME_ENDED':'QUESTION_ACTIVE'):'LOBBY',teams:[{id:'a',name:'Les étoiles',score:location.search.includes('zero=1')?0:120}],categoryWagerQuestionId:'q',categoryWagerLimits:{a:location.search.includes('zero=1')?15:120},categoryWagers:{},submissions:{},textBuzzedTeamIds:[],currentFlipNumber:0,elapsedSecondsInFlip:3,timingConfig:{secondsPerFlip:10},currentQuestion:active?(location.search.includes('choices=1')?{type:'multipleChoice',id:'choice',options:['Océan Atlantique','Océan Pacifique','Océan Indien','Océan Arctique']}:{type:'textAnswer',id:'q'}):null}})}); }
  send(text) { const event=JSON.parse(text); if(event.type.endsWith('.JoinRoom')) { this.onmessage({data:JSON.stringify({type:'com.example.triviaparty.network.GameEvent.JoinResponse',success:true,teamId:'a',message:'Joined'})}); this.state(!location.search.includes('waiting=1')); } }
};
</script>`;
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/play/player.css')) { res.setHeader('Content-Type','text/css'); res.end(fs.readFileSync(path.join(assets,'player.css'))); }
  else if (req.url.startsWith('/play/player.js')) { res.setHeader('Content-Type','application/javascript'); res.end(fs.readFileSync(path.join(assets,'player.js'))); }
  else {
    const autoJoin = req.url.includes('active=1') ? `<script>setTimeout(()=>{document.getElementById('name').value='Les étoiles';document.getElementById('join-form').requestSubmit()},100)</script>` : '';
    res.setHeader('Content-Type','text/html; charset=utf-8');
    res.end(fs.readFileSync(path.join(assets,'index.html'),'utf8').replace('<script src="/play/player.js">',mock+'<script src="/play/player.js">').replace('</body>',autoJoin+'</body>'));
  }
});
server.listen(0,'127.0.0.1',async()=>{
  let chrome, ws;
  try {
    chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',[
      '--headless','--disable-gpu','--no-first-run','--remote-debugging-port=0',
      '--user-data-dir='+path.join(output,'wager-preview-profile'),'about:blank'
    ],{windowsHide:true,stdio:['ignore','ignore','pipe']});
    const endpoint=await new Promise((resolve,reject)=>{
      let log=''; chrome.stderr.on('data',data=>{log+=data; const match=log.match(/DevTools listening on (ws:\/\/\S+)/); if(match) resolve(match[1]);});
      chrome.once('error',reject); chrome.once('exit',code=>reject(new Error('Chrome exited '+code)));
    });
    ws=new WebSocket(endpoint);
    await new Promise((resolve,reject)=>{ws.onopen=resolve; ws.onerror=reject;});
    let sequence=0; const requests=new Map();
    ws.onmessage=message=>{const result=JSON.parse(message.data); if(result.id) {const pending=requests.get(result.id); requests.delete(result.id); result.error?pending.reject(new Error(JSON.stringify(result.error))):pending.resolve(result.result);}};
    const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++sequence; requests.set(id,{resolve,reject}); ws.send(JSON.stringify({id,method,params,sessionId}));});
    const {targetId}=await send('Target.createTarget',{url:'about:blank'});
    const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
    await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true},sessionId);
    await send('Page.enable',{},sessionId);
    for(const mode of ['wager','wager-zero']) {
      const active=mode!=='join';
      const file=path.join(output,'browser-player-'+mode+'.png');
      await send('Page.navigate',{url:'http://127.0.0.1:'+server.address().port+'/play?room=4821'+(active?'&active=1':'')+(mode==='choices'?'&choices=1':'' )+(mode==='waiting'?'&waiting=1':'')+'&wager=1'+(mode==='wager-zero'?'&zero=1':'')},sessionId);
      await new Promise(resolve=>setTimeout(resolve,700));
      const {result}=await send('Runtime.evaluate',{expression:'JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,game:!document.getElementById("game").hidden})',returnByValue:true},sessionId);
      const dimensions=JSON.parse(result.value);
      if(dimensions.width!==390||dimensions.scroll>390||dimensions.game!==active) throw new Error('Unexpected mobile layout: '+result.value);
      const screenshot=await send('Page.captureScreenshot',{format:'png'},sessionId);
      fs.writeFileSync(file,Buffer.from(screenshot.data,'base64'));
      console.log(file);
    }
    await send('Browser.close');
  } catch(error) { console.error(error); process.exitCode=1; }
  finally {ws?.close(); chrome?.kill(); server.close();}
});
