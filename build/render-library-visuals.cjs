// Render original visual clues and small logic diagrams to offline PNG assets.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve('package-examples/library-2026-10-12'),assets=path.join(root,'assets');
fs.mkdirSync(assets,{recursive:true});
const used=JSON.parse(fs.readFileSync('build/library-image-keys.json','utf8'));
const icons={
 stone:'🪨',bat:'🦇',lightning:'⚡',sea:'🌊',rope:'🪢',shield:'🛡️',hammer:'🔨',web:'🕸️',
 ship:'⛵',pumpkin:'🎃',snowman:'⛄',bus:'🚌',broom:'🧹',plane:'✈️',
 'winged-horse':'🐎 🪽',snakes:'🐍',phoenix:'🔥 🐦',fire:'🔥',slipper:'👠',mouse:'🐁',
 'three-houses':'🏠 🏠 🏠',beanstalk:'🌱 ☁️',cup:'🏆',sword:'⚔️',castle:'🏰',island:'🏝️',
 'one-eye':'👁️',space:'🚀',mask:'🎭','maple-leaf':'🍁','cowboy-hat':'🤠',crosswalk:'🚶 🚶 🚶 🚶',
 sunrise:'🌅',clock:'🕒',key:'🔑',umbrella:'☂️',mirror:'🪞',book:'📖',submarine:'🌊 ⚓',
 magnifier:'🔍',rabbit:'🐇',ghost:'👻',blocks:'🧱',hedgehog:'🦔',mars:'🔴',magnet:'🧲',snow:'❄️',battle:'⚔️',
 'round-table':'ROUND','seven-balls':'BALLS',sequence:'SEQUENCE','five-apples':'APPLES',fives:'FIVES',
 'four-squares':'SQUARES','four-seasons':'SEASONS',maze:'MAZE',dragon:'🐉',fairy:'🧚'
};
(async()=>{
 let chrome,ws;try{
  chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.resolve('build/library-visual-profile'),'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
  const endpoint=await new Promise((resolve,reject)=>{let log='';chrome.stderr.on('data',d=>{log+=d;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m)resolve(m[1]);});chrome.once('error',reject)});
  ws=new WebSocket(endpoint);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
  let id=0;const pending=new Map();ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result)}};
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const seq=++id;pending.set(seq,{resolve,reject});ws.send(JSON.stringify({id:seq,method,params,sessionId}))});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'}),{sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const render=function(symbol){
   const c=document.createElement('canvas');c.width=1200;c.height=800;const x=c.getContext('2d');
   x.fillStyle='#f3efe7';x.fillRect(0,0,c.width,c.height);x.textAlign='center';x.textBaseline='middle';
   x.fillStyle='#193b4b';x.font='bold 100px Arial';
   if(symbol==='SEQUENCE')x.fillText('2   4   6   8   ?',600,400);
   else if(symbol==='FIVES')x.fillText('5   10   15   ?   25',600,400);
   else if(symbol==='SQUARES') {x.fillStyle='#205d84';for(let i=0;i<4;i++)x.fillRect(100+i*275,300,170,170)}
   else if(symbol==='BALLS'){for(let i=0;i<7;i++){x.beginPath();x.fillStyle='#ec8127';x.arc(135+i*155,400,62,0,2*Math.PI);x.fill();x.fillStyle='#b52720';x.font='40px Arial';x.fillText('★',135+i*155,400)}}
   else if(symbol==='APPLES'){x.font='130px Segoe UI Emoji';for(let i=0;i<5;i++)x.fillText('🍎',150+i*225,400)}
   else if(symbol==='SEASONS'){x.font='150px Segoe UI Emoji';['🌷','☀️','🍂','❄️'].forEach((a,i)=>x.fillText(a,150+i*300,400))}
   else if(symbol==='ROUND'){x.fillStyle='#a56536';x.beginPath();x.arc(600,400,225,0,2*Math.PI);x.fill();for(let i=0;i<8;i++){const a=i*Math.PI/4;x.fillStyle='#485663';x.fillRect(600+300*Math.cos(a)-40,400+300*Math.sin(a)-40,80,80)}}
   else if(symbol==='MAZE'){x.strokeStyle='#26568b';x.lineWidth=24;x.beginPath();x.rect(150,100,900,600);x.moveTo(150,240);x.lineTo(800,240);x.moveTo(400,420);x.lineTo(1050,420);x.moveTo(150,570);x.lineTo(800,570);x.stroke();x.font='110px Segoe UI Emoji';x.fillText('🟡',260,345)}
   else{x.font=(Array.from(symbol).length>6?'170':'270')+'px Segoe UI Emoji';x.fillText(symbol,600,410)}
   return c.toDataURL('image/png').split(',')[1]
  };
  const records=[];
  for(const [slug,symbol] of Object.entries(icons)){
   if(!used.includes(slug))continue;
   // Prefer actual cached photographs over symbolic illustrations.
   if(fs.existsSync(path.join(assets,slug+'.json')))continue;
   const result=await send('Runtime.evaluate',{expression:'('+render.toString()+')('+JSON.stringify(symbol)+')',returnByValue:true},sessionId);
   fs.writeFileSync(path.join(assets,slug+'.png'),Buffer.from(result.result.value,'base64'));
   const diagram=['SEQUENCE','FIVES','SQUARES','ROUND','BALLS'].includes(symbol);
   const record={slug,title:'Indice visuel — '+slug,file:slug+'.png',artist:'Trivia Party — diagramme ou indice visuel local',license:diagram?'CC0':'Illustration locale ; glyphes système crédités',licenseUrl:diagram?'https://creativecommons.org/publicdomain/zero/1.0/':'https://learn.microsoft.com/en-us/typography/fonts/font-faq',commons:null,credit:diagram?'Diagramme dessiné pour le jeu.':'Graphisme de jeu ; symboles rendus avec la police système Segoe UI Emoji, sans redistribution du fichier de police.',changes:'Indice représentatif, pas une image du film ou de la bande dessinée.'};
   fs.writeFileSync(path.join(assets,slug+'.json'),JSON.stringify(record,null,2)+'\n');records.push(record);
  }
  console.log('Rendered '+records.length+' original visual clues / diagrams.');await send('Browser.close');
 }finally{ws?.close();chrome?.kill()}
})().catch(e=>{console.error(e);process.exitCode=1});
