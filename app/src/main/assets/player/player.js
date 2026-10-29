(function (global) {
  'use strict';
  const eventPrefix = 'com.example.triviaparty.network.GameEvent.';
  const answerPrefix = 'com.example.triviaparty.model.AnswerValue.';
  const event = (name, fields = {}) => ({ type: eventPrefix + name, ...fields });
  const answer = (name, fields) => ({ type: answerPrefix + name, ...fields });
  const awaitingQuestion = state => ['LOBBY', 'SUBJECT_VOTING', 'CATEGORY_SELECT', 'CATEGORY_INTRO', 'WAGER_OPEN', 'WAGER_RESULTS'].includes(state.state);
  const hasChoices = state => ['multipleChoice', 'speedRace', 'mapChoice'].includes(state.currentQuestion?.type);
  const isImageRevealQuestion = state => state.currentQuestion?.type === 'guessWho' && Boolean(state.currentQuestion.imageRevealMode) && state.currentQuestion.imageRevealMode !== 'NONE';
  const usesBuzzer = state => isImageRevealQuestion(state) || state.currentCategoryAnswerMode!=='WRITTEN' && Boolean(state.currentQuestion) && state.currentQuestion.type !== 'ordering' && !hasChoices(state) &&
    (['textAnswer', 'guessWho'].includes(state.currentQuestion.type) || state.currentCategoryAnswerMode === 'BUZZER');
  function buzzerState(state, teamId, connected = true, pending = false) {
    if (!connected) return 'disconnected';
    if (state.state === 'GAME_ENDED') return 'ended';
    const own = state.submissions?.[teamId];
    if (own?.isCorrect === false || (state.textBuzzedTeamIds || []).includes(teamId)) return 'incorrect';
    if (own?.isCorrect === true) return 'correct';
    if (state.state !== 'QUESTION_ACTIVE' || state.questionReading || !state.currentQuestion) return 'waiting';
    if (own?.isLocked || pending) return 'pressed';
    if (usesBuzzer(state) && (state.buzzQueue || []).some(press => press.teamId === teamId && press.questionId === state.currentQuestion?.id)) return 'queued';
    return 'ready';
  }
  function makePhoneSoundPlayer(env, onStatus = () => {}) {
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
  const api = { event, answer, buzzerState, makePhoneSoundPlayer };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (!global.document) return;

  const $ = id => document.getElementById(id);
  const soundButton = $('sound-button');
  const soundStatus = $('sound-status');
  const phoneSound = makePhoneSoundPlayer(global, (status, detail) => {
    soundButton.textContent = status === 'playing' ? 'Tester le son' : status === 'error' ? 'Réessayer le son' : 'Activer / tester le son';
    soundStatus.textContent = status === 'error' ? 'Son indisponible — touchez Réessayer le son.' : status === 'blocked' ? 'Touchez le bouton pour autoriser le son.' : '';
    soundStatus.title = detail || '';
  });
  let activationChime;
  soundButton.addEventListener('click', () => {
    phoneSound.prepare(state?.categoryBuzzerSound);
    phoneSound.unlock();
    try {
      if (!activationChime) { activationChime = new global.Audio('/tv/sounds/aria-correct.wav'); activationChime.preload = 'auto'; }
      activationChime.volume = .42;
      activationChime.currentTime = 0;
      const playback = activationChime.play();
      if (playback?.then) playback.then(() => { soundButton.textContent = 'Tester le son'; soundStatus.textContent = ''; })
        .catch(() => { soundStatus.textContent = 'Touchez de nouveau pour activer le son.'; });
      else { soundButton.textContent = 'Tester le son'; soundStatus.textContent = ''; }
    } catch (_) { soundStatus.textContent = 'Touchez de nouveau pour activer le son.'; }
  });
  document.addEventListener('pointerup', () => phoneSound.unlock(), true);
  document.addEventListener('touchend', () => phoneSound.unlock(), true);
  let socket, reconnectTimer, state, teamId = null, questionId = null, joined = false;
  let joinRequested = false, waitingApproval = false, pendingLock = false, lastView = '', playerId=null;
  let wakeLock;
  let orderQuestionId = null, orderedIds = [];
  let wagerQuestionId = null, wagerDraft = 0;
  let voteRoundKey = null, voteDraft = [];
  let writtenKey='',writtenDraft='',writtenSubmitted=false;
  const roomFromLink = new URLSearchParams(location.search).get('room') || '';
  const storageKey = 'trivia-player:' + location.host;
  let identity = null;
  try { identity = JSON.parse(sessionStorage.getItem(storageKey)); } catch (_) {}
  if (identity && roomFromLink && identity.roomId !== roomFromLink) identity = null;
  $('name').value = identity?.teamName || '';
  $('player-name').value = identity?.playerName || '';
  playerId=identity?.playerId||null;
  function persist() {
    try {
      if (identity) sessionStorage.setItem(storageKey, JSON.stringify(identity));
      else sessionStorage.removeItem(storageKey);
    } catch (_) {}
  }
  function token() {
    const bytes = new Uint8Array(24);
    global.crypto.getRandomValues(bytes);
    return Array.from(bytes, value => value.toString(16).padStart(2, '0')).join('');
  }
  function online() { return socket?.readyState === 1; }
  function updateJoinButton() {
    $('join-button').disabled=!online()||!state||waitingApproval||!$('name').value.trim()||Boolean(state.teamMode&&!$('player-name').value.trim());
  }
  $('name').addEventListener('input',updateJoinButton);$('player-name').addEventListener('input',updateJoinButton);
  function send(message) {
    if (!online()) return false;
    socket.send(JSON.stringify(message));
    return true;
  }
  function join() {
    if (!identity || joinRequested || !online()) return;
    joinRequested = true;
    send(event('JoinRoom', identity));
  }
  async function keepAwake() {
    try {
      if (navigator.wakeLock && document.visibilityState === 'visible' && teamId)
        wakeLock = await navigator.wakeLock.request('screen');
    } catch (_) {}
  }
  function connect() {
    clearTimeout(reconnectTimer);
    const current = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/play/ws');
    socket = current;
    joinRequested = false;
    current.onopen = () => {
      if (socket !== current) return;
      $('connection').textContent = 'Connecté à l’hôte';
      $('join-button').disabled = true;
      lastView = '';
      if (state) render();
      // Wait for the initial room snapshot before restoring a saved identity.
    };
    current.onmessage = message => {
      if (socket !== current) return;
      let data;
      try { data = JSON.parse(message.data); } catch (_) { return; }
      if (data.type === eventPrefix + 'RoomStateBroadcast') {
        state = data.session;
        phoneSound.prepare(state.categoryBuzzerSound);
        if (identity && identity.roomId !== state.roomId) {
          identity = null; teamId = null; joined = false; waitingApproval = false; persist();
          playerId=null;$('name').value='';$('player-name').value='';
          $('join-message').textContent = 'Une nouvelle partie a commencé. Rejoignez-la avec votre équipe.';
        }
        if (identity && !joined && !waitingApproval && (!state.teamMode || identity.playerName)) join();
        if (state.currentQuestion?.id !== questionId || state.submissions?.[teamId]?.isLocked ||
            (state.buzzQueue || []).some(press => press.teamId === teamId) || state.state !== 'QUESTION_ACTIVE') pendingLock = false;
        render();
      } else if (data.type === eventPrefix + 'JoinResponse') {
        $('join-message').textContent = data.message;
        if (data.success) {
          teamId = data.teamId;playerId=data.playerId||null;if(identity)identity.playerId=playerId;joined = true; waitingApproval = false; persist(); keepAwake();
        } else {
          teamId = null;
          waitingApproval = Boolean(data.requiresHostApproval);
          if (!waitingApproval) { identity = null; persist(); }
        }
        lastView = ''; render();
      } else if (data.type === eventPrefix + 'HourglassTick' && state) {
        state.currentFlipNumber = data.flipNumber;
        state.elapsedSecondsInFlip = data.elapsedSecondsInFlip;

      } else if (data.type === eventPrefix + 'ErrorEvent') {
        $('feedback').textContent = data.message;
      }
    };
    current.onclose = () => {
      if (socket !== current) return;
      $('connection').textContent = 'Connexion perdue — reconnexion en cours… Vérifiez le Wi-Fi.';
      $('join-button').disabled = true;
      pendingLock = false; waitingApproval = false; joined = false; lastView = '';
      render();
      document.querySelectorAll('#game button, #game input').forEach(control => { control.disabled = true; });
      reconnectTimer = setTimeout(connect, 1500);
    };
    current.onerror = () => { $('connection').textContent = 'Hôte inaccessible. Vérifiez que vous utilisez le même Wi-Fi.'; };
  }
  $('join-form').addEventListener('submit', e => {
    e.preventDefault();
    phoneSound.unlock();
    const teamName = $('name').value.trim(), playerName=$('player-name').value.trim(), roomId = state?.roomId;
    if (!teamName || state?.teamMode && !playerName || !roomId || !online()) return;
    identity = { teamName, playerName:state.teamMode?playerName:'', roomId, sessionToken: identity?.sessionToken || token() };
    persist(); waitingApproval = false; joinRequested = false;
    $('join-message').textContent = 'Connexion de votre équipe…';
    join();
  });
  function node(tag, text, className) {
    const result = document.createElement(tag);
    if (text != null) result.textContent = text;
    if (className) result.className = className;
    return result;
  }
  function button(text, handler, className = '', disabled = false) {
    const result = node('button', text, className);
    result.type = 'button'; result.disabled = disabled || !online();
    result.addEventListener('click', handler);
    return result;
  }
  function lock() {
    if (!joined || !usesBuzzer(state) || pendingLock || buzzerState(state, teamId, online()) !== 'ready') return;
    if (send(event('LockAnswer', { teamId, questionId, answer: answer('TextSelection', { text: 'BUZZ' }) }))) {
      if (state.buzzerSoundsEnabled !== false) phoneSound.play();
      pendingLock = true; lastView = ''; render();
      setTimeout(() => { pendingLock = false; lastView = ''; render(); }, 1200);
    }
  }
  function choose(index) {
    if (!joined || !hasChoices(state) || pendingLock || buzzerState(state, teamId, online()) !== 'ready') return;
    if (send(event('LockAnswer', { teamId, questionId, answer: state.currentQuestion.type === 'mapChoice' ? answer('MapPinSelection', state.currentQuestion.mapOptions[index]) : answer('MultipleChoiceSelection', { optionIndex: index }) }))) {
      pendingLock = true; lastView = ''; render();
    }
  }
  function arrange(from, to) {
    if (!joined || state?.state !== 'QUESTION_ACTIVE' || state.currentQuestion?.type !== 'ordering' ||
        pendingLock || buzzerState(state, teamId, online()) !== 'ready') return;
    to = Math.max(0, Math.min(orderedIds.length - 1, to));
    if (from < 0 || from >= orderedIds.length || from === to) return;
    const next = orderedIds.slice(); next.splice(to, 0, next.splice(from, 1)[0]); orderedIds = next;
    send(event('UpdateDraftAnswer', { teamId, questionId,
      answer: answer('OrderingSelection', { orderedItemIds: orderedIds.slice() }) }));
    lastView = ''; render();
  }
  function submitOrder() {
    if (!joined || state?.state !== 'QUESTION_ACTIVE' || state.currentQuestion?.type !== 'ordering' ||
        pendingLock || buzzerState(state, teamId, online()) !== 'ready') return;
    if (send(event('LockAnswer', { teamId, questionId,
      answer: answer('OrderingSelection', { orderedItemIds: orderedIds.slice() }) }))) {
      pendingLock = true; lastView = ''; render();
    }
  }
  function orderingCards(scene, status) {
    const editable = state.state === 'QUESTION_ACTIVE' && status === 'ready';
    const question = state.currentQuestion;
    const list = node('div', null, 'ordering-list');
    scene.append(node('p', 'Glissez les événements : du plus ancien au plus récent.', 'ordering-help'));
    orderedIds.forEach((id, index) => {
      const item = question.items.find(item => item.id === id);
      const row = node('div', null, 'ordering-card');
      // Color belongs to the event, so it stays recognizable after moving it.
      const colors = ['#254f78', '#285d49', '#65416f', '#72522b', '#5d4850', '#345e68'];
      row.style.backgroundColor = colors[question.items.findIndex(item => item.id === id) % colors.length];
      row.append(node('span', String(index + 1), 'order-position'), node('span', item.text, 'order-text'));
      row.tabIndex = editable ? 0 : -1;
      row.setAttribute('aria-label', 'Position '+(index+1)+' : '+item.text);
      row.addEventListener('keydown', e => {
        if(!editable || !['ArrowUp','ArrowDown'].includes(e.key)) return;
        e.preventDefault(); arrange(index,index+(e.key==='ArrowUp'?-1:1));
      });
      let drag = null;
      row.addEventListener('pointerdown', e => {
        if (!editable) return;
        e.preventDefault();
        const rect = row.getBoundingClientRect();
        drag = { y: e.clientY, center: rect.top + rect.height / 2, delta: 0, questionId };
        row.setPointerCapture?.(e.pointerId);
        row.style.zIndex = '2'; row.className = 'ordering-card dragging';
      });
      row.addEventListener('pointermove', e => {
        if (!drag) return;
        drag.delta = e.clientY - drag.y;
        row.style.transform = 'translateY(' + drag.delta + 'px)';
      });
      row.addEventListener('pointerup', () => {
        if (!drag) return;
        const center = drag.center + drag.delta;
        const target = Array.from(list.children).filter(card => card !== row).filter(card => {
          const rect = card.getBoundingClientRect(); return center > rect.top + rect.height / 2;
        }).length;
        const current = drag.questionId === questionId;
        drag = null; row.style.transform = ''; row.style.zIndex = ''; row.className = 'ordering-card';
        if (current) arrange(index, target);
      });
      row.addEventListener('pointercancel', () => {
        drag = null; row.style.transform = ''; row.style.zIndex = ''; row.className = 'ordering-card';
      });
      list.append(row);
    });
    scene.append(list);
    if (state.state === 'QUESTION_ACTIVE') scene.append(button(pendingLock || state.submissions?.[teamId]?.isLocked ?
      'ORDRE ENVOYÉ' : 'ENVOYER L’ORDRE', submitOrder, 'order-submit', !editable));
  }
  function render() {
    $('join').hidden = Boolean(teamId);
    $('game').hidden = !teamId;
    $('player-name-field').hidden = !state?.teamMode;
    $('player-name').required=Boolean(state?.teamMode);
    updateJoinButton();
    if (!teamId || !state) return;
    const me = state.teams.find(team => team.id === teamId);
    $('team').textContent = state.teamMode && identity?.playerName ? identity.playerName+' · '+(me?.name||identity.teamName) : me?.name || identity?.teamName || '';
    $('score').textContent = (me?.score || 0) + ' pts';
    questionId = state.currentQuestion?.id;
    if (state.currentQuestion?.type === 'ordering' && orderQuestionId !== questionId) {
      orderQuestionId = questionId;
      const items = state.currentQuestion.items || [];
      const saved = state.submissions?.[teamId]?.answer?.orderedItemIds;
      const valid = Array.isArray(saved) && saved.length === items.length && new Set(saved).size === items.length &&
        saved.every(id => items.some(item => item.id === id));
      orderedIds = valid ? saved.slice() : items.map(item => item.id);
    }
    const claimOwner=state.answeringPlayerIds?.[teamId];
    const status = state.teamMode && claimOwner && claimOwner!==playerId ? 'teammate' : buzzerState(state, teamId, online() && joined, pendingLock);
    const choiceMode = !awaitingQuestion(state) && hasChoices(state);
    const selectedIndex = state.submissions?.[teamId]?.answer?.optionIndex;
    const signature = JSON.stringify([status, questionId, state.state, state.currentQuestion?.type,
      state.currentCategoryAnswerMode, state.buzzActiveTeamId, state.buzzQueue, state.currentQuestion?.options, state.currentQuestion?.items, orderedIds, selectedIndex,
      state.categoryWagerQuestionId, state.categoryWagerLimits?.[teamId], state.categoryWagers?.[teamId],state.categoryWagerProposals?.[teamId],
      state.state === 'GAME_ENDED' ? state.teams.map(team => [team.id, team.score]) : null,
      state.subjectVoting, voteDraft,state.questionReading,state.readingQuestionId,state.currentCategoryAnswerMode==='WRITTEN'?0:state.currentFlipNumber,state.readyTeamIds,
      state.submissions?.[teamId]?.isLocked,state.submissions?.[teamId]?.isCorrect,state.submissions?.[teamId]?.answer?.text,
      state.teamMode&&claimOwner!==playerId?claimOwner:null]);
    if (signature === lastView) return;
    lastView = signature;
    const labels = {
      teammate:'Un co\u00e9quipier r\u00e9pond d\u00e9j\u00e0',
      waiting: 'En attente', ready: 'À vous de jouer', pressed: 'Vous avez la parole',
      queued: 'Buzz enregistré · attendez votre tour', blocked: 'Une autre équipe répond', incorrect: 'Mauvaise réponse · désactivé',
      correct: 'Bonne réponse', ended: 'Partie terminée', disconnected: 'Reconnexion…'
    };
    const scene = $('scene'); scene.replaceChildren(); $('feedback').textContent = '';
    if(status==='teammate'&&state.state==='QUESTION_ACTIVE'&&!state.questionReading)
      scene.append(node('p','Un co\u00e9quipier r\u00e9pond d\u00e9j\u00e0 pour votre \u00e9quipe.','waiting-message'));
    if(state.questionReading && state.readingQuestionId) {
      const ready=(state.readyTeamIds||[]).includes(teamId);
      scene.append(node('h2','Lisez la question sur le téléviseur'));
      scene.append(button(ready?'PRÊT ✓':'PRÊT',()=>send(event('PlayerReady',{teamId,questionId:state.readingQuestionId,clueIndex:state.currentFlipNumber})),ready?'selected':'',ready||!online()||!joined));
      scene.append(node('p',ready?'En attente des autres équipes…':'La suite commence quand toutes les équipes sont prêtes.'));
      return;
    }
    if(state.currentCategoryAnswerMode==='WRITTEN' && ['QUESTION_ACTIVE','ANSWER_REVIEW'].includes(state.state) && !state.questionReading) {
      const key=state.roomId+':'+questionId;
      if(key!==writtenKey) {writtenKey=key;writtenDraft='';writtenSubmitted=false;}
      const own=state.submissions?.[teamId];
      if(writtenSubmitted && !own?.isLocked && state.state==='QUESTION_ACTIVE') writtenDraft='';
      writtenSubmitted=Boolean(own?.isLocked);const submitted=own?.isLocked||pendingLock;const locked=submitted||state.state==='ANSWER_REVIEW'||status==='teammate';
      scene.append(node('h2',own?.isCorrect===true?'Réponse acceptée':own?.isCorrect===false?'Réponse refusée':submitted?'Réponse envoyée':state.state==='ANSWER_REVIEW'?'Temps écoulé':'Votre réponse'));
      const input=node('input');input.type='text';input.maxLength=240;input.autocomplete='off';input.value=own?.answer?.text||writtenDraft;input.disabled=locked;input.setAttribute('aria-label','Votre réponse écrite');
      input.oninput=()=>{writtenDraft=input.value;submit.disabled=!writtenDraft.trim()||!online()||!joined;};
      scene.append(input);
      const submit=button('ENVOYER',()=>{if(send(event('LockAnswer',{teamId,questionId,answer:answer('TextSelection',{text:writtenDraft.trim()})}))) {pendingLock=true;lastView='';render();}},'',locked||!writtenDraft.trim()||!online()||!joined);
      input.onkeydown=e=>{if(e.key==='Enter'&&!submit.disabled){e.preventDefault();submit.click();}};
      if(!locked) scene.append(submit);else scene.append(node('p',own?.isCorrect!=null?'En attente des autres validations…':submitted?'Validation par l’hôte…':'Aucune réponse envoyée.'));
      return;
    }
    if (state.state === 'SUBJECT_VOTING' && state.subjectVoting) {
      const vote = state.subjectVoting;
      const roundKey = state.roomId + ':' + vote.round;
      if (voteRoundKey !== roundKey) { voteRoundKey = roundKey; voteDraft = (vote.ballots?.[teamId] || []).slice(); }
      scene.append(node('h2', vote.hostTieBreak ? 'L’hôte départage les sujets' : vote.round === 1 ? 'Choisissez les catégories' : 'Départagez les égalités'));
      if (vote.selected.length) scene.append(node('p', 'Déjà retenus : ' + vote.selected.join(' · ')));
      if (vote.hostTieBreak) return;
      const slots = vote.settings.categories - vote.selected.length;
      scene.append(node('p', 'Choisissez jusqu’à ' + slots + (slots === 1 ? ' sujet' : ' sujets') + ', puis confirmez.'));
      const choices = node('div', null, 'choices');
      vote.candidates.forEach(subject => {
        const chosen = voteDraft.includes(subject);
        choices.append(button(subject, () => {
          voteDraft = chosen ? voteDraft.filter(value => value !== subject) : voteDraft.concat(subject);
          lastView = ''; render();
        }, chosen ? 'selected' : 'option', !online() || !joined || !chosen && voteDraft.length >= slots));
      });
      scene.append(choices);
      scene.append(button('CONFIRMER LE VOTE', () => send(event('SubmitSubjectVote', { teamId, round: vote.round, subjects: voteDraft.slice() })),
        '', !online() || !joined || !voteDraft.length));
      if (vote.ballots?.[teamId]) scene.append(node('p', 'Vote enregistré. Vous pouvez le modifier avant la fermeture.', 'muted'));
      return;
    }
    if (state.state === 'WAGER_OPEN') {
      const limit = state.categoryWagerLimits?.[teamId];
      if (!Number.isInteger(limit)) {
        scene.append(node('p', 'En attente de la première question…', 'waiting-message'));
        return;
      }
      const locked = state.categoryWagers?.[teamId] != null;
      const proposal=state.categoryWagerProposals?.[teamId];
      if(state.teamMode&&locked) {
        scene.append(node('h2','Mise approuv\u00e9e'));
        scene.append(node('p',state.categoryWagers[teamId]+' pts · la majorit\u00e9 de votre \u00e9quipe a accept\u00e9 cette mise.','waiting-message'));
        return;
      }
      if(state.teamMode&&proposal?.status==='PENDING') {
        const eligible=proposal.eligiblePlayerIds||[],approved=proposal.approvedPlayerIds||[],rejected=proposal.rejectedPlayerIds||[];
        const threshold=Math.floor(eligible.length/2)+1,voted=approved.includes(playerId)||rejected.includes(playerId);
        scene.append(node('h2','Approbation de mise'));
        scene.append(node('p','Proposition : '+proposal.amount+' pts. '+approved.length+'/'+threshold+' approbations requises.','wager-amount'));
        if(proposal.proposerPlayerId===playerId)scene.append(node('p','En attente des votes de vos co\u00e9quipiers. Refus : '+rejected.length+'/'+eligible.length+'.','muted'));
        else if(eligible.includes(playerId)) {
          if(voted)scene.append(node('p','Votre vote est enregistr\u00e9. En attente des autres co\u00e9quipiers.','muted'));
          else {
            scene.append(button('APPROUVER',()=>send(event('VoteCategoryWager',{teamId,questionId:state.categoryWagerQuestionId,proposalId:proposal.id,approve:true})),'selected'));
            scene.append(button('REFUSER',()=>send(event('VoteCategoryWager',{teamId,questionId:state.categoryWagerQuestionId,proposalId:proposal.id,approve:false})),'option'));
          }
        } else scene.append(node('p','Seuls les co\u00e9quipiers connect\u00e9s lors de la proposition peuvent voter.','muted'));
        return;
      }
      if(state.teamMode&&proposal?.status==='REJECTED')scene.append(node('p','La proposition a \u00e9t\u00e9 refus\u00e9e. Vous pouvez en proposer une autre.','muted'));
      if (wagerQuestionId !== state.categoryWagerQuestionId) {
        wagerQuestionId = state.categoryWagerQuestionId; wagerDraft = 0;
      }
      const amount = locked ? state.categoryWagers[teamId] : Math.min(wagerDraft, limit);
      scene.append(node('h2', 'Votre mise'));
      scene.append(node('p', 'Pour la première question uniquement. Bonne réponse : mise gagnée ; erreur ou absence de réponse : mise perdue.'));
      const output = node('p', amount + ' pts', 'wager-amount');
      const slider = node('input'); slider.type = 'range'; slider.min = '0'; slider.max = String(limit);
      slider.step = '1'; slider.value = String(amount); slider.disabled = locked || !online() || !joined || limit === 0;
      slider.setAttribute('aria-label', 'Mise de 0 à ' + limit + ' points');
      slider.addEventListener('input', () => { wagerDraft = Number(slider.value); output.textContent = slider.value + ' pts'; });
      const submit = () => {
        if (!joined || state.state !== 'WAGER_OPEN' || locked) return;
        if (send(event('SubmitCategoryWager', { teamId, questionId: state.categoryWagerQuestionId,
          amount: Number(slider.value) }))) { slider.disabled = true; lockButton.disabled = true; }
      };
      scene.append(output, slider, node('p', '0 — ' + limit + ' pts'));
      const lockButton = button(locked ? 'MISE VERROUILLÉE' : (state.teamMode ? 'PROPOSER LA MISE' : 'VERROUILLER LA MISE'), submit);
      lockButton.disabled = locked || !online() || !joined;
      scene.append(lockButton);
      scene.append(node('p', locked ? 'Mise confirmée' : 'Choisissez le montant, puis verrouillez votre mise.', 'muted'));
      return;
    }
    if (state.state === 'GAME_ENDED') {
      const highestScore = Math.max(...state.teams.map(team => team.score));
      const winner = Boolean(me) && me.score > 0 && me.score === highestScore;
      const result = node('p', winner ? 'Gagnant!' : 'Bel effort!', 'game-result');
      result.setAttribute('role', 'status');
      scene.append(result);
      return;
    }
    if (choiceMode) {
      const choices = node('div', null, 'choices');
      (state.currentQuestion.options || []).forEach((text, index) => {
        const option = button(text, () => choose(index), index === selectedIndex ? 'selected' : 'option', status !== 'ready');
        option.setAttribute('aria-pressed', String(index === selectedIndex));
        choices.append(option);
      });
      scene.append(choices);
    }
    if (!awaitingQuestion(state) && state.currentQuestion?.type === 'ordering') orderingCards(scene, status);
    if (awaitingQuestion(state) || !state.currentQuestion) {
      const waiting = node('p', state.state === 'GAME_ENDED' ? 'Partie terminée' :
        (!online() || !joined ? 'Reconnexion…' : 'En attente…'), 'waiting-message');
      waiting.setAttribute('role', 'status');
      scene.append(waiting);
    }
    if (!awaitingQuestion(state) && usesBuzzer(state)) {
      const buzz = button('', lock, 'buzz ' + status, status !== 'ready');
      if (status === 'queued') scene.append(node('p', 'Buzz enregistré · vous répondrez si les joueurs précédents se trompent.', 'waiting-message'));
      else if (status === 'pressed') scene.append(node('p', state.buzzActiveTeamId === teamId ? 'À vous de répondre !' : 'Buzz envoyé…', 'waiting-message'));
      // Send at first contact, not after the finger is released. Click remains for keyboard/accessibility.
      buzz.addEventListener('pointerdown', event => {
        if (buzz.disabled || event.isPrimary === false || (event.button != null && event.button !== 0)) return;
        event.preventDefault();lock();
      });
      buzz.setAttribute('aria-label', 'Buzzer — ' + labels[status]);
      buzz.append(node('strong', status === 'disconnected' ? 'Reconnexion…' : 'BUZZER'));
      scene.append(buzz);
    }
  }
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      if (!socket || socket.readyState > 1) connect();
      keepAwake();
    } else if (wakeLock) { wakeLock.release().catch(() => {}); wakeLock = null; }
  });
  connect();
})(typeof window !== 'undefined' ? window : globalThis);
