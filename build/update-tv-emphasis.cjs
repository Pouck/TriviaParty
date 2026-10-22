const fs=require('fs');
let js=fs.readFileSync('cast-receiver/receiver.js','utf8');
js=js.replace("feedback.textContent = state.answerSound === 'good' ? '\\u2713' : '\\u2715';", "clear(feedback);\n        feedback.appendChild(node('span', null, 'brush-mark')); ");
js=js.replace('scene.className = state.phase === "WAGER_RESULTS" ? "wager-results-scene" : "";', `scene.className = state.phase === "WAGER_RESULTS" ? "wager-results-scene" : state.phase === "CATEGORY_INTRO" ? "category-intro-scene" : state.phase === "WAGER_OPEN" ? "wager-open-scene" : "";
      var categoryHash = Array.from(state.category || '').reduce(function (hash, character) { return (hash * 31 + character.charCodeAt(0)) | 0; }, 0);
      var categoryHue = ((categoryHash % 360) + 360) % 360;
      scene.style.background = ['CATEGORY_INTRO','WAGER_OPEN'].indexOf(state.phase) >= 0 ? 'linear-gradient(135deg,hsl(' + categoryHue + ',52%,25%),hsl(' + ((categoryHue + 35) % 360) + ',45%,13%))' : '';`);
js=js.replace('scene.appendChild(node("p", "Choisissez votre mise sur votre téléphone · Première question uniquement"));', 'scene.appendChild(node("p", "Choisissez votre mise sur votre téléphone\\nPremière question uniquement", "wager-instructions"));');
const start=js.indexOf('          scene.appendChild(node("p", (state.categoryQuestionCount || 0)');
const end=js.indexOf('          break;',start);
js=js.slice(0,start)+`          scene.appendChild(node("p", (state.categoryQuestionCount || 0) + " questions", "category-count"));
          var modeLabel = state.categoryAnswerMode === "WRITTEN" ? "Réponses écrites" : state.categoryAnswerMode === "BUZZER" ? "Buzzer" : "Réponses simultanées";
          var types = (state.categoryQuestionTypes || []).filter(function (type) {
            return typeof type === 'string' && type.trim() && !/^(buzzer|réponses? écrites?|réponses? simultanées?)$/i.test(type.trim());
          });
          types = types.filter(function (type, index) { return types.indexOf(type) === index; });
          if (types.length) scene.appendChild(node("p", types.join(" · "), "category-types"));
          scene.appendChild(node("p", modeLabel, "category-mode"));
`+js.slice(end);
fs.writeFileSync('cast-receiver/receiver.js',js);
let css=fs.readFileSync('cast-receiver/receiver.css','utf8');
css+=`
/* Spacious category and wager cards, with a stable color for each category. */
.category-intro-scene, .wager-open-scene { display:flex; flex-direction:column; align-items:center; justify-content:center; border-radius:14px; padding:4vh 2vw; gap:2.5vh; }
.category-intro-scene h1, .wager-open-scene h1 { font-size:4.4vw; line-height:1.12; text-wrap:balance; margin:0 0 2vh; color:#fff3b0; }
.category-intro-scene p { margin:0; font-size:2.7vw; line-height:1.25; text-wrap:balance; }
.category-intro-scene .category-count { color:#fff; font-weight:700; }
.category-intro-scene .category-types { color:#e0f4ff; }
.category-intro-scene .category-mode { padding:1.5vh 2vw; border-radius:14px; background:#ffffff24; color:#fff3b0; font-weight:700; }
.wager-open-scene .wager-instructions { font-size:3.2vw; font-weight:700; line-height:1.5; white-space:pre-line; margin:3vh 0 0; text-wrap:balance; }
.winner-line { font-size:4.8vw; line-height:1.15; text-wrap:balance; margin:3vh 0 4vh; overflow-wrap:anywhere; }
/* Oversized tapered paint strokes remain crisp at television resolution. */
#answer-feedback .brush-mark { position:relative; display:block; width:min(40vw,62vh); height:min(40vw,62vh); filter:drop-shadow(0 8px 12px #0009); }
.brush-mark::before, .brush-mark::after { content:''; position:absolute; background:currentColor; }
.bad .brush-mark::before { inset:4% 0; clip-path:polygon(5% 0,18% 4%,98% 88%,96% 98%,83% 94%,2% 13%,0 5%); }
.bad .brush-mark::after { inset:0 2%; clip-path:polygon(87% 0,100% 5%,95% 19%,15% 98%,2% 100%,0 88%,79% 5%); }
.good .brush-mark::before { inset:0; clip-path:polygon(0 48%,10% 43%,34% 67%,29% 92%,19% 81%,2% 60%); }
.good .brush-mark::after { inset:0; clip-path:polygon(25% 76%,87% 5%,100% 0,97% 17%,34% 95%,25% 98%,18% 86%); }
`;
fs.writeFileSync('cast-receiver/receiver.css',css);
for(const name of ['receiver.js','receiver.css'])fs.copyFileSync('cast-receiver/'+name,'app/src/main/assets/tv/'+name);
