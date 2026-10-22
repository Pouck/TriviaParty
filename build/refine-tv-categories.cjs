const fs=require('fs');
const dir='C:/Users/pierr/.codex/generated_images/01a1403e-72af-7b80-a4bd-84d87d314708/';
for(const [kind,file] of [['bad','exec-550ea387-bd3c-41cc-abab-c1c4f3dc426e.png'],['good','exec-98800405-4fb6-4c80-99f1-097491150a14.png']]) {
 for(const target of ['cast-receiver/','app/src/main/assets/tv/'])fs.copyFileSync(dir+file,target+'feedback-'+kind+'.png');
}
let js=fs.readFileSync('cast-receiver/receiver.js','utf8');
const helper=`  // Display format metadata once, separate from the subject and subtitle.
  function categoryPresentation(state) {
    function key(value) { return value.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase().replace(/[?!.]/g, '').replace(/\\s+/g, ' ').trim(); }
    var formatNames = ['qcm','choix multiples','buzzer','qui suis-je','chronologie','reponse ecrite','reponses ecrites','reponses simultanees'];
    var formats = [], titleParts = [];
    (state.category || '').split(/\\s+[-–—]\\s+/).filter(Boolean).forEach(function (part) {
      if (formatNames.indexOf(key(part)) >= 0) formats.push(key(part) === 'qcm' ? 'Choix multiples' : part.trim());
      else titleParts.push(part.trim());
    });
    var mode = state.categoryAnswerMode === 'WRITTEN' ? 'Réponses écrites' : state.categoryAnswerMode === 'BUZZER' ? 'Buzzer' : 'Réponses simultanées';
    var modeKeys = state.categoryAnswerMode === 'WRITTEN' ? ['reponse ecrite','reponses ecrites'] : [key(mode)];
    var seen = [], types = [];
    (state.categoryQuestionTypes || []).concat(formats).forEach(function (type) {
      if (typeof type !== 'string' || !type.trim()) return;
      type = type.replace(/\\s+[–—-]\\s+réponse écrite$/i, '').trim();
      var normalized = key(type);
      if (modeKeys.indexOf(normalized) >= 0 || seen.indexOf(normalized) >= 0) return;
      seen.push(normalized); types.push(type);
    });
    return { titleParts: titleParts.length ? titleParts : ['Nouvelle catégorie'], types: types, mode: mode };
  }

`;
js=js.replace('  function makeSoundPlayer(doc, options) {',helper+'  function makeSoundPlayer(doc, options) {');
js=js.replace("feedback.appendChild(node('span', null, 'brush-mark')); ","feedback.appendChild(node('span', null, 'brush-mark'));");
js=js.replace('text("category", state.phase === "SUBJECT_VOTING" ? "Choix des catégories" : state.category || "Salon");','var categoryInfo = categoryPresentation(state);\n      text("category", state.phase === "SUBJECT_VOTING" ? "Choix des catégories" : state.category ? categoryInfo.titleParts.join(" · ") : "Salon");');
js=js.replace('      switch (state.phase) {',`      function categoryHeading() {
        var heading = node('h1', null, 'category-heading');
        categoryInfo.titleParts.forEach(function (part) { heading.appendChild(node('span', part, 'category-title-line')); });
        scene.appendChild(heading);
      }
      switch (state.phase) {`);
js=js.replaceAll('scene.appendChild(node("h1", state.category || "Nouvelle catégorie"));','categoryHeading();');
const start=js.indexOf('          var modeLabel ='); const end=js.indexOf('          break;',start);
js=js.slice(0,start)+`          if (categoryInfo.types.length) scene.appendChild(node("p", categoryInfo.types.join(" · "), "category-types"));
          scene.appendChild(node("p", categoryInfo.mode, "category-mode"));
`+js.slice(end);
let css=fs.readFileSync('cast-receiver/receiver.css','utf8');
css=css.slice(0,css.indexOf('/* Oversized tapered paint strokes'))+`/* Transparent painted feedback assets preserve natural bristle texture. */
#answer-feedback .brush-mark { display:block; width:min(40vw,62vh); height:min(40vw,62vh); background:center/contain no-repeat; filter:drop-shadow(0 8px 12px #0009); }
#answer-feedback.bad .brush-mark { background-image:url('feedback-bad.png'); }
#answer-feedback.good .brush-mark { background-image:url('feedback-good.png'); }
.category-title-line { display:block; text-wrap:balance; }
.category-title-line + .category-title-line { margin-top:1vh; font-size:.78em; color:#fff; }
.category-intro-scene h1, .wager-open-scene h1 { font-size:3.9vw; max-width:100%; flex-shrink:0; }
.category-intro-scene, .wager-open-scene { gap:2vh; }
.winner-line { font-size:5.5vw; line-height:1.15; margin:6vh 0 7vh; }
`;
for(const dir of ['cast-receiver/','app/src/main/assets/tv/']){fs.writeFileSync(dir+'receiver.js',js);fs.writeFileSync(dir+'receiver.css',css);}
let kt=fs.readFileSync('app/src/main/java/com/example/triviaparty/network/GameServer.kt','utf8');
kt=kt.replace('                get("/tv/hourglass.svg") {',`                listOf("feedback-good.png", "feedback-bad.png").forEach { name ->
                    get("/tv/$name") {
                        val bytes = readTvBinaryAsset?.invoke(name)
                        if (bytes == null) call.respondText("Not found", status = io.ktor.http.HttpStatusCode.NotFound)
                        else call.respondBytes(bytes, ContentType("image", "png"))
                    }
                }
                get("/tv/hourglass.svg") {`);
fs.writeFileSync('app/src/main/java/com/example/triviaparty/network/GameServer.kt',kt);
