const fs=require('fs');let js=fs.readFileSync('cast-receiver/receiver.js','utf8').replace(/\r\n/g,'\n');
js=js.replace('function paintedImage(file, maskId, mirrored) {','function paintedImage(file, maskId, mirrored, clipId) {').replace("          if (mirrored) image.setAttribute('transform', 'translate(1 0) scale(-1 1)');", "          if (mirrored) image.setAttribute('transform', 'translate(1 0) scale(-1 1)');\n          if (clipId) image.setAttribute('clip-path', 'url(#' + clipId + ')');");
const a=js.indexOf("        var paths = state.answerSound === 'good'"),b=js.indexOf('        mark.appendChild(svg);',a);
js=js.slice(0,a)+`        var paths = state.answerSound === 'good' ? ['M -.04 .37 L .44 .93', 'M .34 .94 L 1 -.02'] : ['M 0 0 L 1 1', 'M 0 0 L 1 1'];
        paths.forEach(function (path, index) {
          // A flat reveal front keeps the visible tip moving until each stroke ends.
          var stroke = svgNode('path', {d:path, pathLength:1, fill:'none', stroke:'white', 'stroke-width':.32, 'stroke-linecap':'butt', 'class':'paint-stroke stroke-' + index});
          var maskId = 'feedback-paint-mask-' + index;
          var strokeMask = svgNode('mask', {id:maskId, maskUnits:'userSpaceOnUse', x:0, y:0, width:1, height:1});
          strokeMask.appendChild(stroke); defs.appendChild(strokeMask);
          if (state.answerSound === 'bad') paintedImage('feedback-red-stroke.png', maskId, index === 1);
          else {
            // Partition the checkmark at its bend so the short stroke cannot pre-reveal the long one.
            var clipId = 'feedback-check-part-' + index;
            var clip = svgNode('clipPath', {id:clipId, clipPathUnits:'userSpaceOnUse'});
            clip.appendChild(svgNode('rect', {x:index === 0 ? 0 : .43, y:0, width:index === 0 ? .43 : .57, height:1}));
            defs.appendChild(clip); paintedImage('feedback-good.png', maskId, false, clipId);
          }
        });
`+js.slice(b);
let css=fs.readFileSync('cast-receiver/receiver.css','utf8').replace(/\r\n/g,'\n');
css=css.replace('animation:paint-stroke .42s ease-out forwards;', 'animation:paint-stroke .30s linear forwards;');
css=css.replace('.paint-stroke.stroke-1 { animation-delay:.36s; animation-duration:.48s; }','.paint-stroke.stroke-1 { animation-delay:.30s; }\n#answer-feedback.good .paint-stroke.stroke-0 { animation-duration:.22s; }\n#answer-feedback.good .paint-stroke.stroke-1 { animation-delay:.22s; animation-duration:.38s; }');
css=css.replace('#answer-feedback.bad .paint-stroke.stroke-1 { animation-delay:.46s; }','');
for(const dir of ['cast-receiver/','app/src/main/assets/tv/']){fs.writeFileSync(dir+'receiver.js',js);fs.writeFileSync(dir+'receiver.css',css);}
const preview='build/preview-cast-compatibility.cjs';let s=fs.readFileSync(preview,'utf8').replace('for(const moment of [200,550,1000])','for(const moment of [100,220,300,400,500,650])');fs.writeFileSync('build/preview-smooth-brushes.cjs',s);
