const fs=require('node:fs');
const file='app/src/main/assets/player/player.js';
let s=fs.readFileSync(file,'utf8');
const start=s.indexOf('  function canBuzz('), end=s.indexOf('  if (typeof module',start);
s=s.slice(0,start)+`  function buzzerState(state, teamId, connected = true, pending = false) {
    if (!connected) return 'disconnected';
    if (state.state === 'GAME_ENDED') return 'ended';
    const own = state.submissions?.[teamId];
    if (own?.isCorrect === false || (state.textBuzzedTeamIds || []).includes(teamId)) return 'incorrect';
    if (own?.isCorrect === true) return 'correct';
    if (state.state !== 'QUESTION_ACTIVE' || !state.currentQuestion) return 'waiting';
    if (own?.isLocked || pending) return 'pressed';
    if (state.buzzActiveTeamId) return 'blocked';
    return 'ready';
  }
  const api = { event, answer, buzzerState };
`+s.slice(end);
s=s.replace('teamId = null, draft = null, questionId = null','teamId = null, questionId = null, joined = false');
s=s.replace('identity = null; teamId = null; waitingApproval = false;', 'identity = null; teamId = null; joined = false; waitingApproval = false;');
s=s.replace('if (identity && !teamId && !waitingApproval)', 'if (identity && !joined && !waitingApproval)');
s=s.replace('        pendingLock = false;\n        render();','        if (state.currentQuestion?.id !== questionId || state.submissions?.[teamId]?.isLocked ||\n            state.buzzActiveTeamId || state.state !== \'QUESTION_ACTIVE\') pendingLock = false;\n        render();');
s=s.replace('teamId = data.teamId; waitingApproval', 'teamId = data.teamId; joined = true; waitingApproval');
s=s.replace('        updateTimer();','');
s=s.replace('pendingLock = false; waitingApproval = false; teamId = null; lastView = \'\';','pendingLock = false; waitingApproval = false; joined = false; lastView = \'\';\n      render();');
const from=s.indexOf('  function updateTimer()'), to=s.indexOf("  document.addEventListener('visibilitychange'",from);
s=s.slice(0,from)+`  function lock() {
    if (!joined || pendingLock || buzzerState(state, teamId, online()) !== 'ready') return;
    if (send(event('LockAnswer', { teamId, questionId, answer: answer('TextSelection', { text: 'BUZZ' }) }))) {
      pendingLock = true; lastView = ''; render();
      setTimeout(() => { pendingLock = false; lastView = ''; render(); }, 1200);
    }
  }
  function render() {
    $('join').hidden = Boolean(teamId);
    $('game').hidden = !teamId;
    $('join-button').disabled = !online() || waitingApproval;
    if (!teamId || !state) return;
    const me = state.teams.find(team => team.id === teamId);
    $('team').textContent = me?.name || identity?.teamName || '';
    $('score').textContent = (me?.score || 0) + ' pts';
    questionId = state.currentQuestion?.id;
    const status = buzzerState(state, teamId, online() && joined, pendingLock);
    if (status === lastView) return;
    lastView = status;
    const labels = {
      waiting: 'En attente', ready: 'À vous de jouer', pressed: 'Vous avez la parole',
      blocked: 'Une autre équipe répond', incorrect: 'Mauvaise réponse · désactivé',
      correct: 'Bonne réponse', ended: 'Partie terminée', disconnected: 'Reconnexion…'
    };
    const scene = $('scene'); scene.replaceChildren(); $('feedback').textContent = '';
    const buzz = button('', lock, 'buzz ' + status, status !== 'ready');
    buzz.setAttribute('aria-label', 'Buzzer — ' + labels[status]);
    buzz.append(node('strong', 'BUZZER'), node('span', labels[status]));
    scene.append(buzz);
  }
`+s.slice(to);
fs.writeFileSync(file,s);
const html='app/src/main/assets/player/index.html';
fs.writeFileSync(html,fs.readFileSync(html,'utf8').replace('<span id="timer"></span>',''));
const css='app/src/main/assets/player/player.css';
s=fs.readFileSync(css,'utf8');
s=s.slice(0,s.indexOf('.order-row'));
s+=`\n#game { min-height: min(65vh, 600px); display: flex; flex-direction: column; }
#scene { flex: 1; display: flex; align-items: center; }
button.buzz { min-height: clamp(220px, 42vh, 420px); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; width: 100%; }
button.buzz strong { font-size: clamp(34px, 9vw, 52px); }
button.buzz span { font-size: 17px; font-weight: 650; }
button.buzz:disabled { opacity: 1; }
.buzz.waiting, .buzz.blocked, .buzz.ended, .buzz.disconnected { background: #55556d; color: white; }
.buzz.ready { background: #ffd54f; color: #12121d; }
.buzz.pressed { background: #4da3ff; color: #12121d; }
.buzz.incorrect { background: #e45b67; color: #12121d; }
.buzz.correct { background: #70d69b; color: #12121d; }
`;
fs.writeFileSync(css,s);
