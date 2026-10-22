const fs=require('fs');
for(const dir of ['cast-receiver/','app/src/main/assets/tv/'])fs.copyFileSync('C:/Users/pierr/.codex/generated_images/01a1403e-72af-7b80-a4bd-84d87d314708/exec-121b9b66-b6fc-4010-bf33-4eff898dcd25.png',dir+'feedback-red-stroke.png');
let js=fs.readFileSync('cast-receiver/receiver.js','utf8');
js=js.replace("['M .08 .08 L .93 .93', 'M .08 .93 L .93 .08']","['M .08 .08 L .93 .93', 'M .08 .08 L .93 .93']");
js=js.replace("          mask.appendChild(svgNode('path', {d:path, pathLength:1, fill:'none', stroke:'white', 'stroke-width':.32, 'stroke-linecap':'round', 'class':'paint-stroke stroke-' + index}));",`          var stroke = svgNode('path', {d:path, pathLength:1, fill:'none', stroke:'white', 'stroke-width':.32, 'stroke-linecap':'round', 'class':'paint-stroke stroke-' + index});
          if (state.answerSound === 'bad') {
            var strokeMask = svgNode('mask', {id:'feedback-x-mask-' + index, maskUnits:'objectBoundingBox', maskContentUnits:'objectBoundingBox', x:0, y:0, width:1, height:1, style:'mask-type:alpha'});
            strokeMask.appendChild(stroke); defs.appendChild(strokeMask);
            mark.appendChild(node('span', null, 'x-stroke x-stroke-' + index));
          } else mask.appendChild(stroke);`);
let css=fs.readFileSync('cast-receiver/receiver.css','utf8');css+=`
/* Separate paint layers prevent the first diagonal from revealing the other. */
#answer-feedback.bad .brush-mark { position:relative; background-image:none; mask:none; -webkit-mask:none; }
.x-stroke { position:absolute; inset:0; background:url('feedback-red-stroke.png') center/contain no-repeat; }
.x-stroke-0 { mask:url('#feedback-x-mask-0'); -webkit-mask:url('#feedback-x-mask-0'); }
.x-stroke-1 { transform:scaleX(-1); mask:url('#feedback-x-mask-1'); -webkit-mask:url('#feedback-x-mask-1'); }
`;
for(const dir of ['cast-receiver/','app/src/main/assets/tv/']){fs.writeFileSync(dir+'receiver.js',js);fs.writeFileSync(dir+'receiver.css',css);}
const ktPath='app/src/main/java/com/example/triviaparty/network/GameServer.kt';fs.writeFileSync(ktPath,fs.readFileSync(ktPath,'utf8').replace('listOf("feedback-good.png", "feedback-bad.png")','listOf("feedback-good.png", "feedback-bad.png", "feedback-red-stroke.png")'));
for(const name of ['cast-receiver/index.html','app/src/main/assets/tv/display.html']){let html=fs.readFileSync(name,'utf8');html=html.replace('feedback-bad.png','feedback-red-stroke.png');fs.writeFileSync(name,html);}
let p=fs.readFileSync('build/preview-tv-brush-animation.cjs','utf8').replace('feedback-(good|bad)','feedback-(good|bad|red-stroke)');fs.writeFileSync('build/preview-tv-brush-animation.cjs',p);
fs.appendFileSync('app/src/main/assets/tv/feedback-image-prompts.txt', '\nSingle X stroke, built-in image_gen, transparent background. Saved as feedback-red-stroke.png in the TV and cast-receiver directories.\nPrompt: Production transparent UI asset. Square canvas. Exactly ONE vivid saturated red hand-painted dry brush stroke running diagonally down from top left (about 10%,10%) to bottom right (about 90%,90%). One straight broad sweeping stroke only, NOT an X, NOT a checkmark. Natural visible bristle streaks, pigment texture, feathered irregular edges and tapered ends, transparent gaps through paint. Width around 15% of canvas perpendicular to the diagonal. Flat front-facing real paint appearance, no paper, background fully transparent, no shadows, no other marks, no text. This will be layered with a mirrored copy to animate an X, so absolutely no trace of a crossing stroke.\n');
