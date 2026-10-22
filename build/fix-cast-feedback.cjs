const fs=require('fs');let js=fs.readFileSync('cast-receiver/receiver.js','utf8');
js=js.replace("      if ((state.buzzerSoundId || 0) > lastBuzzerId) soundPlayer.play('buzzer.wav');",'      // Buzzer audio is local to the player who presses; televisions stay silent.');
js=js.replace("lastBuzzerId=cue.buzzerSoundId; soundPlayer.play('buzzer.wav'); return true;","lastBuzzerId=cue.buzzerSoundId; return true;");
// Keep protocol deduplication, but never play a network-delayed buzz at the TV.
js=js.replace("soundPlayer.play('buzzer.wav');return true;","return true;");
const a=js.indexOf("        var svg = svgNode('svg', {width:0"),b=js.indexOf('        feedback.className =',a);if(a<0||b<a)throw Error('Missing feedback SVG');
js=js.slice(0,a)+`        var svg = svgNode('svg', {viewBox:'0 0 1 1', width:'100%', height:'100%', 'aria-hidden':'true'});
        var defs = svgNode('defs', {}); svg.appendChild(defs);
        var sourceScript = doc.querySelector && doc.querySelector('script[src$="receiver.js"]');
        var imageBase = sourceScript ? sourceScript.src.replace(/[^/]*$/, '') : '/tv/';
        function paintedImage(file, maskId, mirrored) {
          var image = svgNode('image', {x:0, y:0, width:1, height:1, mask:'url(#' + maskId + ')', href:imageBase + file});
          if (image.setAttributeNS) image.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', imageBase + file);
          if (mirrored) image.setAttribute('transform', 'translate(1 0) scale(-1 1)');
          svg.appendChild(image);
        }
        var paths = state.answerSound === 'good' ? ['M .07 .49 L .40 .86', 'M .40 .86 L .95 .07'] : ['M .08 .08 L .93 .93', 'M .08 .08 L .93 .93'];
        var sharedMask = svgNode('mask', {id:'feedback-stroke-mask', maskUnits:'userSpaceOnUse', x:0, y:0, width:1, height:1});
        paths.forEach(function (path, index) {
          var stroke = svgNode('path', {d:path, pathLength:1, fill:'none', stroke:'white', 'stroke-width':.32, 'stroke-linecap':'round', 'class':'paint-stroke stroke-' + index});
          if (state.answerSound === 'bad') {
            var maskId = 'feedback-x-mask-' + index;
            var strokeMask = svgNode('mask', {id:maskId, maskUnits:'userSpaceOnUse', x:0, y:0, width:1, height:1});
            strokeMask.appendChild(stroke); defs.appendChild(strokeMask);
            paintedImage('feedback-red-stroke.png', maskId, index === 1);
          } else sharedMask.appendChild(stroke);
        });
        if (state.answerSound === 'good') { defs.appendChild(sharedMask); paintedImage('feedback-good.png', 'feedback-stroke-mask', false); }
        mark.appendChild(svg); feedback.appendChild(mark);
`+js.slice(b);
let css=fs.readFileSync('cast-receiver/receiver.css','utf8');
css=css.replace(/#answer-feedback\.bad \.brush-mark \{ background-image:[^}]+\}/g,'').replace(/#answer-feedback\.good \.brush-mark \{ background-image:[^}]+\}/g,'');
css=css.replace(/#answer-feedback \.brush-mark \{ mask:[^}]+\}/g,'').replace(/#answer-feedback\.bad \.brush-mark \{ position:relative; background-image:none;[^}]+\}/g,'');
css=css.replace(/\.x-stroke[^\n]*\n/g,'');
css+=`
/* Cast receivers may not support inset, min(), clamp(), or HTML fragment masks. */
#answer-overlay { top:0; right:0; bottom:12vh; left:0; text-align:center; }
#answer-overlay > * { flex-shrink:0; align-self:center; }
.selected-player-name { font-size:4.2vw; }
#answer-feedback { top:0; right:0; bottom:0; left:0; }
#answer-feedback .brush-mark { position:relative; width:40vw; height:40vw; max-width:62vh; max-height:62vh; background:none; -webkit-mask:none; mask:none; }
#answer-feedback .brush-mark > svg { position:absolute; top:0; left:0; width:100%; height:100%; overflow:visible; }
`;
for(const dir of ['cast-receiver/','app/src/main/assets/tv/']){fs.writeFileSync(dir+'receiver.js',js);fs.writeFileSync(dir+'receiver.css',css);}
// Match the preload on the actual Cast entry page too.
const cast='app/src/main/assets/tv/cast.html';let html=fs.readFileSync(cast,'utf8');html=html.replace('</head>','  <link rel="preload" as="image" href="/tv/feedback-red-stroke.png">\n  <link rel="preload" as="image" href="/tv/feedback-good.png">\n</head>');fs.writeFileSync(cast,html);
