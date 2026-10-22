const fs=require('fs');const file='app/src/main/assets/player/player.js';let s=fs.readFileSync(file,'utf8');
s=s.replace("    if (!hasChoices(state) && state.buzzActiveTeamId) return 'blocked';", "    if (usesBuzzer(state) && (state.buzzQueue || []).some(press => press.teamId === teamId && press.questionId === state.currentQuestion?.id)) return 'queued';");
s=s.replace('  const api = { event, answer, buzzerState };',`  function makePhoneSoundPlayer(env) {
    const ids = ['wolf','owl','rooster','dog','bells','coyote','boat','train'];
    let context, selected, buffer, fallback, active, loading;
    function unlock() {
      const Context = env.AudioContext || env.webkitAudioContext;
      try {
        if (!context && Context) context = new Context({latencyHint:'interactive'});
        if (context?.state === 'suspended') context.resume().catch(() => {});
      } catch (_) {}
    }
    function prepare(id) {
      id = ids.includes(id) ? id : 'wolf';
      if (selected === id && loading) return loading;
      selected = id; buffer = null;
      const url = '/play/sounds/' + id + '.mp3';
      if (env.Audio) { fallback = new env.Audio(url); fallback.preload = 'auto'; fallback.load?.(); }
      unlock();
      loading = context && env.fetch ? env.fetch(url).then(r => { if (!r.ok) throw Error('Audio unavailable'); return r.arrayBuffer(); })
        .then(bytes => context.decodeAudioData(bytes)).then(decoded => { if (selected === id) buffer = decoded; })
        .catch(() => { if (selected === id) loading = null; }) : null;
      return loading;
    }
    function play() {
      unlock();
      try {
        if (buffer && context?.state === 'running') {
          active?.stop(); active = context.createBufferSource(); active.buffer = buffer;
          active.connect(context.destination); active.start(); return;
        }
        if (fallback) { fallback.currentTime = 0; const result = fallback.play(); result?.catch?.(() => {}); }
      } catch (_) {}
    }
    return {prepare, unlock, play};
  }
  const api = { event, answer, buzzerState, makePhoneSoundPlayer };`);
s=s.replace("  const $ = id => document.getElementById(id);", "  const $ = id => document.getElementById(id);\n  const phoneSound = makePhoneSoundPlayer(global);");
s=s.replace('        state = data.session;', '        state = data.session;\n        phoneSound.prepare(state.categoryBuzzerSound);');
s=s.replace("(!hasChoices(state) && state.buzzActiveTeamId) || state.state !== 'QUESTION_ACTIVE'", "(state.buzzQueue || []).some(press => press.teamId === teamId) || state.state !== 'QUESTION_ACTIVE'");
s=s.replace("    e.preventDefault();\n    const teamName", "    e.preventDefault();\n    phoneSound.unlock();\n    const teamName");
s=s.replace("      pendingLock = true; lastView = ''; render();\n      setTimeout", "      phoneSound.play();\n      pendingLock = true; lastView = ''; render();\n      setTimeout");
s=s.replace("      blocked: 'Une autre équipe répond',", "      queued: 'Buzz enregistré · attendez votre tour', blocked: 'Une autre équipe répond',");
s=s.replace("      const buzz = button('', lock, 'buzz ' + status, status !== 'ready');", "      const buzz = button('', lock, 'buzz ' + status, status !== 'ready');\n      if (status === 'queued') scene.append(node('p', 'Buzz enregistré · vous répondrez si les joueurs précédents se trompent.', 'waiting-message'));\n      else if (status === 'pressed') scene.append(node('p', state.buzzActiveTeamId === teamId ? 'À vous de répondre !' : 'Buzz envoyé…', 'waiting-message')); ");
s=s.replace('      state.currentCategoryAnswerMode, state.currentQuestion?.options,', '      state.currentCategoryAnswerMode, state.buzzActiveTeamId, state.buzzQueue, state.currentQuestion?.options,');
fs.writeFileSync(file,s);
const server='app/src/main/java/com/example/triviaparty/network/GameServer.kt';let k=fs.readFileSync(server,'utf8');k=k.replace('                get("/play/sounds/{name}") {','                get("/play/sound-credits") { call.respondText(readPlayerAsset?.invoke("sound-credits.html") ?: "", ContentType.Text.Html) }\n                get("/play/sounds/{name}") {');fs.writeFileSync(server,k);
const index='app/src/main/assets/player/index.html';fs.writeFileSync(index,fs.readFileSync(index,'utf8').replace('  <script src="/play/player.js">','  <a href="/play/sound-credits" target="_blank" rel="noopener" style="font-size:11px;color:#aaa">Crédits des sons</a>\n  <script src="/play/player.js">'));
fs.appendFileSync('app/src/main/assets/player/player.css','\n.buzz.queued { background:#434356; color:#eee; }\n');
