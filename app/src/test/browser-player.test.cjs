const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');
const source = fs.readFileSync('app/src/main/assets/player/player.js', 'utf8');

test('players confirm readiness for chronology reading without showing a buzzer or the private answer', () => {
  const h=harness();h.join();
  h.update({state:'QUESTION_ACTIVE',questionReading:true,readingQuestionId:'clues',currentQuestion:null,currentFlipNumber:0,readyTeamIds:[]});
  const ready=h.all().find(e=>e.tag==='button'&&e.textContent==='PRÊT');assert.ok(ready);ready.click();
  assert.equal(h.socket.sent.at(-1).type,'com.example.triviaparty.network.GameEvent.PlayerReady');assert.equal(h.socket.sent.at(-1).questionId,'clues');assert.equal(h.socket.sent.at(-1).clueIndex,0);
  h.update({readyTeamIds:['a']});assert.equal(h.all().find(e=>e.tag==='button'&&e.textContent==='PRÊT ✓').disabled,true);
  h.update({currentFlipNumber:1,readyTeamIds:[]});assert.equal(h.all().find(e=>e.tag==='button'&&e.textContent==='PRÊT').disabled,false);
  assert.equal(h.all().some(e=>e.className?.startsWith('buzz')),false);
});

test('written answers submit once, survive state updates and show private host-validation waiting', () => {
  const h=harness();h.join();
  h.update({state:'QUESTION_ACTIVE',currentQuestion:{id:'written',type:'guessWho'},currentCategoryAnswerMode:'WRITTEN',questionReading:false,currentFlipNumber:0,submissions:{}});
  assert.equal(h.all().some(e=>e.className?.startsWith('buzz')),false);
  const input=h.all().find(e=>e.tag==='input'&&e['aria-label']==='Votre réponse écrite');input.value='Ma réponse';input.oninput();
  h.all().find(e=>e.tag==='button'&&e.textContent==='ENVOYER').click();
  const payload=h.socket.sent.at(-1);assert.ok(payload.type.endsWith('.LockAnswer'));assert.equal(payload.answer.text,'Ma réponse');assert.equal(payload.questionId,'written');
  assert.equal(h.all().some(e=>e.tag==='button'&&e.textContent==='ENVOYER'),false);
  h.update({state:'ANSWER_REVIEW',submissions:{a:{isLocked:true,answer:{text:'Ma réponse'}}}});
  assert.match(h.$('scene').textContent,/Validation par l’hôte/);assert.equal(h.all().find(e=>e['aria-label']==='Votre réponse écrite').value,'Ma réponse');
  h.update({state:'QUESTION_ACTIVE',currentFlipNumber:1,submissions:{}});
  assert.equal(h.all().find(e=>e['aria-label']==='Votre réponse écrite').value,'');
});

test('subject ballot limits choices, confirms privately and resets for the tie round', () => {
  const h=harness(); h.join();
  h.update({state:'SUBJECT_VOTING',currentQuestion:null,subjectVoting:{settings:{categories:2,setsPerCategory:1},
    candidates:['Arts','Musique','Nature'],selected:[],round:1,hostTieBreak:false,ballots:{}}});
  const option=text=>h.all().find(el=>el.tag==='button' && el.textContent===text);
  option('Arts').click(); option('Musique').click();
  assert.equal(option('Nature').disabled,true);
  option('CONFIRMER LE VOTE').click();
  const vote=h.socket.sent.find(e=>e.type.endsWith('.SubmitSubjectVote'));
  assert.equal(vote.teamId,'a'); assert.equal(vote.round,1);
  assert.deepEqual(Array.from(vote.subjects),['Arts','Musique']);
  assert.equal(h.all().some(el=>el.className?.startsWith('buzz')),false);
  h.update({subjectVoting:{settings:{categories:2},candidates:['Musique','Nature'],selected:['Arts'],round:2,hostTieBreak:false,ballots:{}}});
  assert.equal(option('CONFIRMER LE VOTE').disabled,true);
  option('Nature').click(); assert.equal(option('Musique').disabled,true);
  h.update({subjectVoting:{settings:{categories:2},candidates:['Musique','Nature'],selected:['Arts'],round:3,hostTieBreak:true,ballots:{}}});
  assert.match(h.$('scene').textContent,/L’hôte départage/);
  assert.equal(h.all().some(el=>el.tag==='button'),false);
});

test('Qui suis-je shows only a buzzer and score, locks once and disables a wrong answer', () => {
  const h = harness(); h.join();
  h.update({ state: 'QUESTION_ACTIVE', currentCategoryAnswerMode: 'BUZZER',
    currentQuestion: { id: 'clues', type: 'guessWho' } });
  const button = () => h.all().find(el => el.tag === 'button' && el.className?.startsWith('buzz'));
  assert.ok(button()); assert.equal(button().disabled, false);
  button().click(); button().click();
  const locks = h.socket.sent.filter(e => e.type.endsWith('.LockAnswer'));
  assert.equal(locks.length, 1); assert.equal(locks[0].answer.text, 'BUZZ');
  h.update({ submissions: { a: { isLocked: true, isCorrect: false } }, textBuzzedTeamIds: ['a'] });
  assert.equal(button().disabled, true);
  assert.doesNotMatch(h.$('scene').textContent, /Indice|Qui suis-je/);
});

test('ordering supports touch dragging, keyboard access, private drafts and one final lock without arrow buttons', () => {
  const h = harness(); h.join();
  const items = [{ id: 'z', text: 'Événement Z' }, { id: 'x', text: 'Événement X' }, { id: 'y', text: 'Événement Y' }];
  h.update({ state: 'QUESTION_ACTIVE', currentCategoryAnswerMode: 'SIMULTANEOUS',
    currentQuestion: { id: 'order', type: 'ordering', items, prompt: 'Secret host question' } });
  const list = () => h.all().find(el => el.className === 'ordering-list');
  const submit = () => h.all().find(el => el.className === 'order-submit');
  const locks = () => h.socket.sent.filter(e => e.type.endsWith('.LockAnswer'));
  assert.equal(h.all().some(el => el.className?.startsWith('buzz')), false);
  assert.doesNotMatch(h.$('scene').textContent, /Secret host question/);
  const originalColors=Object.fromEntries(list().children.map(row=>[row.children[1].textContent,row.style.backgroundColor]));
  assert.equal(new Set(Object.values(originalColors)).size,3);
  list().children.forEach((row, i) => { row.getBoundingClientRect = () => ({ top: i * 100, height: 100 }); });
  const card = list().children[0];
  card.events.pointerdown({ clientY: 50, pointerId: 1, preventDefault() {} });
  card.events.pointermove({ clientY: 350 }); card.events.pointerup();
  let draft = h.socket.sent.at(-1);
  assert.equal(draft.type, 'com.example.triviaparty.network.GameEvent.UpdateDraftAnswer');
  assert.deepEqual(draft.answer.orderedItemIds, ['x', 'y', 'z']);
  list().children.forEach(row=>assert.equal(row.style.backgroundColor,originalColors[row.children[1].textContent]));
  assert.equal(locks().length, 0);
  assert.equal(h.all().some(el=>el.className==='order-step'),false);
  list().children[1].events.keydown({key:'ArrowUp',preventDefault(){}});
  draft = h.socket.sent.at(-1);
  assert.deepEqual(draft.answer.orderedItemIds, ['y', 'x', 'z']);
  h.update({ elapsedSecondsInFlip: 5 });
  assert.equal(list().children[0].children[1].textContent, 'Événement Y');
  submit().click();
  assert.equal(locks().length, 1);
  assert.deepEqual(locks()[0].answer.orderedItemIds, ['y', 'x', 'z']);
  assert.equal(locks()[0].answer.type, 'com.example.triviaparty.model.AnswerValue.OrderingSelection');
  submit().click(); assert.equal(locks().length, 1);
  h.update({ submissions: { a: { isLocked: true, answer: { orderedItemIds: ['y','x','z'] } } } });
  assert.equal(submit().textContent, 'ORDRE ENVOYÉ');
  h.update({ currentQuestion: { id: 'next', type: 'ordering', items }, submissions: {} });
  assert.equal(list().children[0].children[1].textContent, 'Événement Z');
  h.update({ state: 'CATEGORY_INTRO' }); assert.equal(list(), undefined);
});

test('ordering restores a valid saved private draft on reconnect and disables edits after reveal', () => {
  const h = harness(); h.join();
  h.update({ state: 'QUESTION_ACTIVE', currentQuestion: { id: 'restore', type: 'ordering',
    items: [{ id: 'a', text: 'A' }, { id: 'b', text: 'B' }, { id: 'c', text: 'C' }] },
    submissions: { a: { isLocked: false, answer: { orderedItemIds: ['c', 'a', 'b'] } } } });
  const list = () => h.all().find(el => el.className === 'ordering-list');
  assert.equal(list().children[0].children[1].textContent, 'C');
  h.update({ state: 'REVEAL_ANSWER' });
  assert.equal(h.all().filter(el => el.tag === 'button').every(el => el.disabled), true);
});

test('category wagers use a bounded slider and lock only on explicit confirmation', () => {
  const h = harness(); h.join();
  h.update({ state: 'WAGER_OPEN', currentQuestion: null, categoryWagerQuestionId: 'first',
    categoryWagerLimits: { a: 100 }, categoryWagers: {} });
  const slider = () => h.all().find(el => el.tag === 'input' && el.type === 'range');
  assert.equal(slider().min, '0'); assert.equal(slider().max, '100');
  assert.equal(h.all().some(el => el.className?.startsWith('buzz')), false);
  slider().value = '45'; slider().events.input();
  assert.match(h.$('scene').textContent, /45 pts/);
  const before = h.socket.sent.length;
  slider().events.change?.();
  assert.equal(h.socket.sent.length,before);
  h.all().find(el => el.textContent === 'VERROUILLER LA MISE').click();
  const wager = h.socket.sent.at(-1);
  assert.equal(wager.type, 'com.example.triviaparty.network.GameEvent.SubmitCategoryWager');
  assert.equal(wager.amount, 45); assert.equal(wager.questionId, 'first'); assert.equal(wager.teamId, 'a');
  h.update({ categoryWagers: { a: 45 } });
  assert.equal(slider().value, '45');
  assert.equal(slider().disabled,true);
  h.update({ teams: [{ id: 'a', name: 'Team', score: -10 }], categoryWagerLimits: { a: 15 }, categoryWagers: { a: 0 } });
  assert.equal(slider().max, '15');
  h.update({ state: 'QUESTION_ACTIVE', currentQuestion: { id: 'first', type: 'multipleChoice', options: ['A','B','C','D'] } });
  assert.equal(slider(), undefined);
  h.update({ state: 'WAGER_RESULTS', currentQuestion: null });
  assert.equal(slider(), undefined); assert.equal(h.$('scene').textContent, 'En attente…');
});

class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.events = {}; this.style = {}; this.value = ''; }
  set textContent(value) { this.text = String(value); this.children = []; }
  get textContent() { return (this.text || '') + this.children.map(child => child.textContent).join(''); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; this.text = ''; }
  addEventListener(type, handler) { this.events[type] = handler; }
  setAttribute(name, value) { this[name] = value; }
  click() { if (!this.disabled) this.events.click?.({}); }
}
function harness(saved, search = '?room=1234') {
  const elements = {}, sockets = [], timers = [], storage = new Map();
  if (saved) storage.set('trivia-player:192.168.1.2:8080', JSON.stringify(saved));
  const all = () => Object.values(elements).flatMap(function walk(el) { return [el, ...el.children.flatMap(walk)]; });
  const document = {
    visibilityState: 'visible', createElement: tag => new Element(tag), addEventListener() {},
    getElementById: id => all().find(el => el.id === id) || (elements[id] ||= Object.assign(new Element('div'), { id })),
    querySelectorAll: () => all().filter(el => ['button', 'input'].includes(el.tag))
  };
  class Socket {
    constructor(url) { this.url = url; this.readyState = 0; this.sent = []; sockets.push(this); }
    send(text) { this.sent.push(JSON.parse(text)); }
    open() { this.readyState = 1; this.onopen(); }
    receive(name, fields) { this.onmessage({ data: JSON.stringify({ type: 'com.example.triviaparty.network.GameEvent.' + name, ...fields }) }); }
    disconnect() { this.readyState = 3; this.onclose(); }
  }
  const context = { document, WebSocket: Socket, location: { protocol: 'http:', host: '192.168.1.2:8080', search },
    URLSearchParams, Uint8Array, crypto: webcrypto, navigator: {},
    sessionStorage: { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value), removeItem: key => storage.delete(key) },
    setTimeout: fn => { timers.push(fn); return timers.length; }, clearTimeout() {} };
  context.window = context;
  vm.runInNewContext(source, context);
  const $ = document.getElementById;
  const socket = sockets[0]; socket.open();
  const state = { roomId: '1234', state: 'LOBBY', teams: [{ id: 'a', name: '<b>Team</b>', score: 100 }], submissions: {},
    textBuzzedTeamIds: [], availableCategories: [], playedQuestionIds: [], currentFlipNumber: 0, elapsedSecondsInFlip: 0 };
  socket.receive('RoomStateBroadcast', { session: state });
  function join() {
    $('name').value = '<b>Team</b>';
    $('join-form').events.submit({ preventDefault() {} });
    socket.receive('JoinResponse', { success: true, teamId: 'a', message: 'Joined' });
  }
  return { $, socket, sockets, timers, state, join, all, storage, update: fields => { Object.assign(state, fields); socket.receive('RoomStateBroadcast', { session: state }); } };
}

test('joining a plain browser link needs only a team name', () => {
  const h = harness(null, ''); h.join();
  assert.equal(h.socket.sent[0].roomId, '1234');
  assert.equal(h.$('scene').textContent, 'En attente…');
  assert.equal(fs.readFileSync('app/src/main/assets/player/index.html', 'utf8').includes('id="room"'), false);
});

test('joins with a real protocol payload and preserves identity through refresh', () => {
  const h = harness(); h.join();
  assert.equal(h.socket.url, 'ws://192.168.1.2:8080/play/ws');
  const join = h.socket.sent[0];
  assert.equal(join.type, 'com.example.triviaparty.network.GameEvent.JoinRoom');
  assert.equal(join.roomId, '1234'); assert.equal(join.teamName, '<b>Team</b>');
  assert.match(join.sessionToken, /^[0-9a-f]{48}$/);
  assert.equal(h.$('join').hidden, true); assert.equal(h.$('team').textContent, '<b>Team</b>');
  const restored = harness({ roomId: join.roomId, teamName: join.teamName, sessionToken: join.sessionToken });
  assert.equal(restored.socket.sent[0].sessionToken, join.sessionToken);
});


test('persistent buzzer has waiting, ready, pressed, blocked, incorrect and correct states', () => {
  const h = harness(); h.join();
  const buzz = () => h.all().find(el => el.className?.startsWith('buzz '));
  assert.equal(buzz(), undefined); assert.equal(h.$('scene').textContent, 'En attente…');
  h.update({ state: 'QUESTION_ACTIVE', currentQuestion: { id: 'q1', type: 'textAnswer', prompt: 'Secret question', options: ['Hidden answer'] } });
  assert.equal(buzz().className, 'buzz ready');
  assert.equal(h.$('scene').textContent.includes('Secret question'), false);
  assert.equal(h.$('scene').textContent.includes('Hidden answer'), false);
  buzz().click(); assert.equal(buzz().className, 'buzz pressed');
  const locks = () => h.socket.sent.filter(e => e.type.endsWith('.LockAnswer'));
  assert.equal(locks().length, 1); assert.equal(locks()[0].answer.text, 'BUZZ');
  buzz().click(); assert.equal(locks().length, 1);
  h.update({ submissions: { a: { isLocked: true, isCorrect: false } }, textBuzzedTeamIds: ['a'] });
  assert.equal(buzz().className, 'buzz incorrect'); assert.equal(buzz().disabled, true);
  h.update({ currentQuestion: { id: 'q2', type: 'textAnswer' }, submissions: {}, textBuzzedTeamIds: [], buzzActiveTeamId: 'b' });
  assert.equal(buzz().className, 'buzz blocked');
  h.update({ buzzActiveTeamId: null }); assert.equal(buzz().className, 'buzz ready');
  h.update({ state: 'REVEAL_ANSWER', submissions: { a: { isLocked: true, isCorrect: true } } });
  assert.equal(buzz().className, 'buzz correct');
  for (const phase of ['LOBBY','CATEGORY_SELECT','CATEGORY_INTRO','ROUND_SUMMARY','GAME_ENDED']) {
    h.update({ state: phase, submissions: {}, currentQuestion: null });
    assert.equal(buzz(), undefined);
    assert.equal(h.$('scene').textContent, phase === 'GAME_ENDED' ? 'Gagnant!' : 'En attente…');
  }
});

test('connection loss keeps the score and disabled buzzer visible while restoring team identity', () => {
  const h = harness(); h.join();
  h.update({ state: 'QUESTION_ACTIVE', currentQuestion: { id: 'q8', type: 'textAnswer' } });
  h.socket.disconnect();
  assert.equal(h.$('game').hidden, false);
  assert.equal(h.all().find(el => el.className === 'buzz disconnected').disabled, true);
  h.timers.at(-1)(); const next = h.sockets[1]; next.open(); next.receive('RoomStateBroadcast', { session: h.state });
  assert.equal(next.sent[0].teamName, '<b>Team</b>');
  next.receive('JoinResponse', {success: true, teamId: 'a', message: 'Restored'});
  assert.equal(h.all().find(el => el.className === 'buzz ready').disabled, false);
});

test('new room clears old identity and presents a new join form', () => {
  const h = harness(); h.join(); h.update({ roomId: '5678', teams: [] });
  assert.equal(h.$('join').hidden, false);
  assert.equal(h.storage.size, 0); assert.match(h.$('join-message').textContent, /nouvelle partie/);
  h.join(); assert.equal(h.socket.sent.at(-1).roomId, '5678');
});

test('choice and speed-race answers lock with one tap without displaying the question', () => {
  const h = harness(); h.join();
  for (const [index, type] of ['multipleChoice', 'speedRace'].entries()) {
    h.update({ state: 'QUESTION_ACTIVE', currentQuestion: { id: 'choice' + index, type,
      prompt: 'TV-only question', imageUrl: 'hidden.png', options: ['First option', 'Second option'] },
      submissions: {}, buzzActiveTeamId: 'another-team', textBuzzedTeamIds: [] });
    const options = () => h.all().filter(el => ['option', 'selected'].includes(el.className));
    assert.equal(options().length, 2);
    assert.equal(options().every(el => !el.disabled), true);
    assert.equal(h.$('scene').textContent.includes('TV-only question'), false);
    assert.equal(h.all().some(el => el.tag === 'img'), false);
    assert.equal(h.$('scene').textContent.includes('VALIDER'), false);
    const second = options()[1]; second.click();
    const submission = h.socket.sent.at(-1);
    assert.equal(submission.type, 'com.example.triviaparty.network.GameEvent.LockAnswer');
    assert.equal(submission.questionId, 'choice' + index);
    assert.equal(submission.answer.optionIndex, 1);
    assert.equal(h.socket.sent.some(event => event.type.endsWith('.UpdateDraftAnswer')), false);
    const sent = h.socket.sent.length;
    second.click(); assert.equal(h.socket.sent.length, sent);
    assert.equal(options().every(el => el.disabled), true);
    h.update({ submissions: { a: { isLocked: true, answer: submission.answer } } });
    assert.equal(options()[1].className, 'selected');
    assert.equal(h.all().some(el => el.className?.startsWith('buzz ')), false);
    h.update({ state: 'REVEAL_ANSWER', submissions: { a: { isLocked: true, isCorrect: true, answer: submission.answer } } });
    assert.equal(options().length, 2);
    assert.equal(options().every(el => el.disabled), true);
    assert.equal(h.all().some(el => el.className?.startsWith('buzz ')), false);
  }
});

test('non-buzzer formats never render a buzzer and buzzer labels stay minimal and French', () => {
  const h = harness(); h.join();
  for (const type of ['ordering', 'mapChoice', 'wager']) {
    h.update({ state: 'QUESTION_ACTIVE', currentCategoryAnswerMode: 'SIMULTANEOUS', currentQuestion: { id: type, type } });
    assert.equal(h.all().some(el => el.className?.startsWith('buzz ')), false);
  }
  h.update({ state: 'QUESTION_ACTIVE', currentCategoryAnswerMode: 'BUZZER', currentQuestion: { id: 'spoken', type: 'textAnswer' } });
  const buzz = () => h.all().find(el => el.className?.startsWith('buzz '));
  assert.equal(buzz().textContent, 'BUZZER');
  buzz().click(); assert.equal(buzz().textContent, 'BUZZER');
  h.socket.disconnect(); assert.equal(buzz().textContent, 'Reconnexion…');
});


test('prepared choices stay hidden until the host starts each question', () => {
  const h = harness(); h.join();
  for (const type of ['multipleChoice', 'speedRace']) {
    for (const phase of ['LOBBY', 'CATEGORY_SELECT', 'CATEGORY_INTRO']) {
      h.update({ state: phase, currentQuestion: { id: 'prepared', type, options: ['Early A', 'Early B'] } });
      assert.equal(h.$('scene').textContent, 'En attente…');
      assert.equal(h.all().some(el => ['option', 'selected'].includes(el.className)), false);
    }
    h.update({ state: 'QUESTION_ACTIVE' });
    assert.equal(h.all().filter(el => el.className === 'option').length, 2);
    h.update({ state: 'REVEAL_ANSWER' });
    assert.equal(h.all().filter(el => el.className === 'option').length, 2);
    h.update({ state: 'CATEGORY_SELECT' });
    assert.equal(h.$('scene').textContent, 'En attente…');
  }
});


test('end of game replaces choices or buzzer with winner or effort message, including ties', () => {
  const h = harness(); h.join();
  for (const type of ['multipleChoice', 'textAnswer']) {
    h.update({ state: 'GAME_ENDED', currentQuestion: { id: 'last', type, options: ['A', 'B'] },
      teams: [{ id: 'a', score: 100 }, { id: 'b', score: 200 }] });
    assert.equal(h.$('scene').textContent, 'Bel effort!');
    assert.equal(h.all().some(el => el.className?.startsWith('buzz ') || el.className === 'option'), false);
    h.update({ teams: [{ id: 'a', score: 200 }, { id: 'b', score: 200 }] });
    assert.equal(h.$('scene').textContent, 'Gagnant!');
    h.update({ teams: [{ id: 'a', score: 300 }, { id: 'b', score: 200 }] });
    assert.equal(h.$('scene').textContent, 'Gagnant!');
  }
});


test('zero scores never receive the winner message', () => {
  const h = harness(); h.join();
  for (const teams of [[{ id: 'a', score: 0 }], [{ id: 'a', score: 0 }, { id: 'b', score: 0 }]]) {
    h.update({ state: 'GAME_ENDED', currentQuestion: null, teams });
    assert.equal(h.$('scene').textContent, 'Bel effort!');
  }
  h.update({ teams: [{ id: 'a', score: 1 }, { id: 'b', score: 0 }] });
  assert.equal(h.$('scene').textContent, 'Gagnant!');
});

test('map marker questions display letter choices and submit the selected coordinates', () => {
 const h=harness(); h.join();
 h.update({state:'QUESTION_ACTIVE',currentCategoryAnswerMode:'SIMULTANEOUS',currentQuestion:{id:'map',type:'mapChoice',options:['A','B'],mapOptions:[{xRatio:.2,yRatio:.3},{xRatio:.5,yRatio:.6}]}});
 const choices=h.all().filter(el=>el.tag==='button' && el.className==='option');
 assert.equal(choices.length,2); choices[1].click();
 const lock=h.socket.sent.find(e=>e.type.endsWith('.LockAnswer'));
 assert.ok(lock.answer.type.endsWith('.MapPinSelection'));
 assert.equal(lock.answer.xRatio,.5);assert.equal(lock.answer.yRatio,.6);
});


test('unfinished written draft and its input survive every hourglass flip', () => {
  const h=harness();h.join();
  h.update({state:'QUESTION_ACTIVE',currentCategoryAnswerMode:'WRITTEN',currentQuestion:{id:'draft-flips',type:'textAnswer'},currentFlipNumber:0,submissions:{}});
  const original=h.all().find(e=>e['aria-label']==='Votre réponse écrite');original.value='Une réponse en cours';original.oninput();
  for(const currentFlipNumber of [1,2,3]) {
    h.update({currentFlipNumber});
    const input=h.all().find(e=>e['aria-label']==='Votre réponse écrite');
    assert.equal(input,original);assert.equal(input.value,'Une réponse en cours');
  }
  h.all().find(e=>e.tag==='button'&&e.textContent==='ENVOYER').click();
  assert.equal(h.socket.sent.at(-1).answer.text,'Une réponse en cours');
});
