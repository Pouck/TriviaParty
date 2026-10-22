const fs=require('fs');const p='app/src/main/assets/player/player.js';let s=fs.readFileSync(p,'utf8');const a=s.indexOf('  function makePhoneSoundPlayer('),b=s.indexOf('  const api =',a);
s=s.slice(0,a)+`  function makePhoneSoundPlayer(env, onStatus = () => {}) {
    const ids = ['wolf','owl','rooster','dog','bells','coyote','boat','train'];
    let context, selected, buffer, fallback, active, loading, pendingPlay = false, failed = false;
    function report(error) {
      failed = error?.name !== 'NotAllowedError';
      onStatus(failed ? 'error' : 'blocked', error?.message || '');
    }
    function bufferedPlay() {
      try {
        active?.stop(); active = context.createBufferSource(); active.buffer = buffer;
        active.connect(context.destination); active.start(); pendingPlay = false; failed = false;
        onStatus('playing');
      } catch (error) { report(error); }
    }
    function flush() {
      if (!pendingPlay) return;
      if (buffer && context?.state === 'running') bufferedPlay();
      else if (fallback && !buffer) { pendingPlay = false; htmlPlay(); }
    }
    function unlock() {
      const Context = env.AudioContext || env.webkitAudioContext;
      try {
        if (!context && Context) context = new Context({latencyHint:'interactive'});
        if (context && context.state !== 'running') {
          // Touch contact sends the buzz immediately; touch release can grant audio activation.
          Promise.resolve(context.resume()).then(flush).catch(report);
        } else if (context?.state === 'running') flush();
      } catch (error) { report(error); }
    }
    function htmlPlay() {
      try {
        if (!fallback) { onStatus('error', 'Aucun fichier audio chargé'); return; }
        fallback.volume = 1; fallback.muted = false; fallback.currentTime = 0;
        const result = fallback.play();
        if (result?.then) result.then(() => { failed = false; onStatus('playing'); }).catch(error => {
          pendingPlay = error?.name === 'NotAllowedError'; report(error);
        });
        else { failed = false; onStatus('playing'); }
      } catch (error) { report(error); }
    }
    function prepare(id, retry = false) {
      id = ids.includes(id) ? id : 'wolf';
      if (selected === id && !retry && (loading || fallback || buffer)) return loading;
      selected = id; buffer = null; failed = false; pendingPlay = false;
      const url = '/play/sounds/' + id + '.mp3?v=2';
      onStatus('loading');
      if (env.Audio) {
        fallback = new env.Audio(url); fallback.preload = 'auto';
        fallback.onerror = () => { if (selected === id) report(Error('Fichier audio inaccessible : ' + id)); };
        fallback.load?.();
      }
      unlock();
      loading = context && env.fetch ? env.fetch(url, {cache:'no-store'}).then(r => {
        if (!r.ok) throw Error('Chargement audio : HTTP ' + r.status); return r.arrayBuffer();
      }).then(bytes => context.decodeAudioData(bytes)).then(decoded => {
        if (selected === id) { buffer = decoded; flush(); }
      }).catch(error => { if (selected === id) { loading = null; report(error); } }) : null;
      return loading;
    }
    function play() {
      if (failed) prepare(selected, true);
      unlock();
      if (buffer && context) {
        if (context.state === 'running') bufferedPlay();
        else { pendingPlay = true; onStatus('blocked'); unlock(); }
      } else htmlPlay();
    }
    return {prepare, unlock, play};
  }
`+s.slice(b);
s=s.replace('  const phoneSound = makePhoneSoundPlayer(global);',`  const soundButton = $('sound-button');
  const soundStatus = $('sound-status');
  const phoneSound = makePhoneSoundPlayer(global, (status, detail) => {
    soundButton.textContent = status === 'playing' ? 'Tester le son' : status === 'error' ? 'Réessayer le son' : 'Activer / tester le son';
    soundStatus.textContent = status === 'playing' ? 'Son activé sur cet appareil' : status === 'error' ? 'Son indisponible — touchez Réessayer le son.' : status === 'blocked' ? 'Touchez le bouton pour autoriser le son.' : '';
    soundStatus.title = detail || '';
  });
  soundButton.addEventListener('click', () => { phoneSound.prepare(state?.categoryBuzzerSound); phoneSound.play(); });
  document.addEventListener('pointerup', () => phoneSound.unlock(), true);
  document.addEventListener('touchend', () => phoneSound.unlock(), true);`);
fs.writeFileSync(p,s);
const index='app/src/main/assets/player/index.html';s=fs.readFileSync(index,'utf8').replace('  <main>', '  <div class="sound-controls"><button id="sound-button" type="button">Activer / tester le son</button><span id="sound-status" role="status" aria-live="polite"></span></div>\n  <main>').replace('/play/player.js"','/play/player.js?v=audio2"');fs.writeFileSync(index,s);
fs.appendFileSync('app/src/main/assets/player/player.css','\n.sound-controls { display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:8px;margin:0 0 10px; }\n.sound-controls button { width:auto;min-height:40px;padding:8px 14px;font-size:16px;background:#264866;color:white;border:1px solid #5eaade;border-radius:10px; }\n#sound-status { font-size:14px;color:#ddd;text-align:center; }\n');
const server='app/src/main/java/com/example/triviaparty/network/GameServer.kt';s=fs.readFileSync(server,'utf8');for(const route of ['/play','/play/player.js','/play/player.css','/play/sounds/{name}'])s=s.replace('get("'+route+'") {','get("'+route+'") {\n                    call.response.headers.append("Cache-Control", "no-store, max-age=0")');fs.writeFileSync(server,s);
