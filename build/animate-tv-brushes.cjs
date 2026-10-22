const fs=require('fs');let js=fs.readFileSync('cast-receiver/receiver.js','utf8');
const a=js.indexOf('    var formatNames ='), b=js.indexOf('    var mode =',a);
js=js.slice(0,a)+`    var formats = [], titleParts = [];
    // Imported names also append compound formats, e.g. "Qui suis-je écrit".
    var formatSuffix = /(?:^|\\s+(?:[-–—]\\s*)?)(qui\\s+suis[-–—\\s]+je\\s*\\??(?:\\s*(?:[-–—]\\s*)?(?:[ée]crit(?:e|es|s)?|oral(?:e|es|s)?|au buzzer))?|qcm|choix multiples|buzzer|chronologie|r[ée]ponses? [ée]crites?|r[ée]ponses? simultan[ée]es)\\s*$/i;
    (state.category || '').split(/\\s+[-–—]\\s+/).filter(Boolean).forEach(function (part) {
      var match;
      while ((match = formatSuffix.exec(part))) {
        var label = match[1];
        formats.push(/^qui\\s+suis/i.test(label) ? 'Qui suis-je ?' : key(label) === 'qcm' ? 'Choix multiples' : label.trim());
        part = part.slice(0, match.index).trim();
      }
      if (part) titleParts.push(part);
    });
`+js.slice(b);
js=js.replace("type = type.replace(/\\s+[–—-]\\s+réponse écrite$/i, '').trim();", "type = type.replace(/\\s+[–—-]\\s+réponse écrite$/i, '').trim();\n      if (/^qui\\s+suis[-–—\\s]+je/i.test(type)) type = 'Qui suis-je ?';");
js=js.replace("        feedback.appendChild(node('span', null, 'brush-mark'));",`        var mark = node('span', null, 'brush-mark');
        // Animated SVG masks reveal the original bitmap along each brush stroke.
        var svgNamespace = 'http://www.w3.org/2000/svg';
        function svgNode(tag, attributes) {
          var element = doc.createElementNS(svgNamespace, tag);
          Object.keys(attributes).forEach(function (name) { element.setAttribute(name, attributes[name]); });
          return element;
        }
        var svg = svgNode('svg', {width:0, height:0, 'aria-hidden':'true'});
        var defs = svgNode('defs', {});
        var mask = svgNode('mask', {id:'feedback-stroke-mask', maskUnits:'objectBoundingBox', maskContentUnits:'objectBoundingBox', x:0, y:0, width:1, height:1, style:'mask-type:alpha'});
        var paths = state.answerSound === 'good' ? ['M .07 .49 L .40 .86', 'M .40 .86 L .95 .07'] : ['M .08 .08 L .93 .93', 'M .08 .93 L .93 .08'];
        paths.forEach(function (path, index) {
          mask.appendChild(svgNode('path', {d:path, pathLength:1, fill:'none', stroke:'white', 'stroke-width':.32, 'stroke-linecap':'round', 'class':'paint-stroke stroke-' + index}));
        });
        defs.appendChild(mask); svg.appendChild(defs); mark.appendChild(svg); feedback.appendChild(mark);`);
let css=fs.readFileSync('cast-receiver/receiver.css','utf8');
css+=`
/* Trace each painted stroke in sequence; retain the full mark until cue expiry. */
#answer-feedback .brush-mark { mask:url('#feedback-stroke-mask'); -webkit-mask:url('#feedback-stroke-mask'); }
.brush-mark > svg { position:absolute; }
.paint-stroke { stroke-dasharray:1; stroke-dashoffset:1; animation:paint-stroke .42s ease-out forwards; }
.paint-stroke.stroke-1 { animation-delay:.36s; animation-duration:.48s; }
@keyframes paint-stroke { to { stroke-dashoffset:0; } }
@media (prefers-reduced-motion:reduce) { .paint-stroke { animation:none; stroke-dashoffset:0; } }
`;
for(const dir of ['cast-receiver/','app/src/main/assets/tv/']){fs.writeFileSync(dir+'receiver.js',js);fs.writeFileSync(dir+'receiver.css',css);}
let t=fs.readFileSync('cast-receiver/receiver.test.js','utf8');t=t.replace('createElement: tag => new Element(tag),','createElement: tag => new Element(tag),\n      createElementNS: (namespace, tag) => new Element(tag),');
t+=`
test('compound written and oral formats appear only in the last two category rows',()=> {
 for (const renderer of [receiver,currentReceiver]) {
  const doc=documentStub(),render=renderer.makeRenderer(doc);
  for(const category of ['Légendes de France — Régions et créatures — Qui suis-je écrit','Légendes de France — Régions et créatures qui suis-je écrit','Légendes de France — Régions et créatures — Qui suis-je ? — réponse écrite']) {
   render(state({phase:'CATEGORY_INTRO',category,categoryQuestionTypes:['Qui suis-je ? — réponse écrite'],categoryAnswerMode:'WRITTEN'}));
   const scene=doc.getElementById('scene');
   assert.deepEqual(scene.firstChild.children.map(line=>line.textContent),['Légendes de France','Régions et créatures']);
   assert.equal(doc.getElementById('category').textContent,'Légendes de France · Régions et créatures');
   assert.equal((scene.textContent.match(/Qui suis-je/g)||[]).length,1);
   assert.equal((scene.textContent.match(/Réponses écrites/g)||[]).length,1);
   assert.equal(scene.children.at(-2).textContent,'Qui suis-je ?');
   assert.equal(scene.children.at(-1).textContent,'Réponses écrites');
  }
 }
});
`;fs.writeFileSync('cast-receiver/receiver.test.js',t);
