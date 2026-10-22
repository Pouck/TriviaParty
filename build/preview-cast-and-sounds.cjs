const fs=require('fs');for(const dir of ['cast-receiver/','app/src/main/assets/tv/']) {let p=dir+'receiver.css';let s=fs.readFileSync(p,'utf8').replace('#answer-overlay { top:0; right:0; bottom:12vh; left:0; text-align:center; }','#answer-overlay { top:1.5vh; right:1.3vw; bottom:12vh; left:1.3vw; text-align:center; }');fs.writeFileSync(p,s);}
let p='build/preview-tv-brush-animation.cjs';let s=fs.readFileSync(p,'utf8');
s=s.replace("path.join(assets,'display.html')","path.join(assets,'cast.html')").replace(".replace('<script src=\"/tv/display.js\"></script>','')", ".replace('<script>TriviaReceiver.start();</script>','')");
const a=s.indexOf("let cueId=0;");
s=s.slice(0,a)+`const answering={...base,question:{...base.question,options:[],answerMode:'BUZZER'},categoryAnswerMode:'BUZZER',answeringTeam:'Les étoiles',answerSecondsRemaining:8};
await send('Runtime.evaluate',{expression:'window.renderPreview('+JSON.stringify(answering)+')'},sessionId);
const centered=await send('Runtime.evaluate',{expression:\"JSON.stringify((()=>{const scene=document.getElementById('scene').getBoundingClientRect();return ['.selected-player-name','.answer-hourglass'].map(selector=>{const r=document.querySelector(selector).getBoundingClientRect();return Math.abs((r.left+r.right-scene.left-scene.right)/2)})})())\",returnByValue:true},sessionId);
if(JSON.parse(centered.result.value).some(offset=>offset>1))throw Error('Answer overlay not centered: '+centered.result.value);
const png=await send('Page.captureScreenshot',{format:'png'},sessionId);fs.writeFileSync(path.join(output,'tv-cast-answer-overlay.png'),Buffer.from(png.data,'base64'));
`+s.slice(a);
fs.writeFileSync('build/preview-cast-compatibility.cjs',s);
const labels={wolf:'Loup',owl:'Hibou',rooster:'Coq',dog:'Chien',bells:'Cloches',coyote:'Coyote',boat:'Bateau',train:'Train à vapeur'};
const sampler='<meta charset="utf-8"><title>Sons des buzzers</title><style>body{background:#12121d;color:white;font:24px system-ui;padding:30px}button{font:inherit;padding:20px;margin:10px;background:#264866;color:white;border:0;border-radius:12px}</style><h1>Sons des buzzers des téléphones</h1><p>Un son est choisi au hasard pour chaque catégorie.</p>'+Object.entries(labels).map(([id,label])=>'<button onclick="new Audio(\'/play/sounds/'+id+'.mp3\').play()">'+label+'</button>').join('')+'<p><a style="color:lightblue" href="/play/sound-credits">Sources et licences</a></p>';
fs.writeFileSync('app/src/main/assets/player/sound-sampler.html',sampler);
p='app/src/main/java/com/example/triviaparty/network/GameServer.kt';s=fs.readFileSync(p,'utf8').replace('                get("/play/sound-credits")', '                get("/play/sound-sampler") { call.respondText(readPlayerAsset?.invoke("sound-sampler.html") ?: "", ContentType.Text.Html) }\n                get("/play/sound-credits")');fs.writeFileSync(p,s);
