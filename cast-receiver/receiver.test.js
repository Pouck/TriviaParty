const { test } = require('node:test');
const assert = require('node:assert/strict');
const receiver = require('./receiver.js');
const currentReceiver = require('../app/src/main/assets/tv/receiver.js');

test('point countdown uses one fixed glass and readiness and written review preserve the public question', () => {
  const doc=documentStub(),render=currentReceiver.makeRenderer(doc);
  const q={id:'points',prompt:'Question',options:['A','B'],answer:null};
  render(state({question:q,pointsCountdown:true,secondsPerFlip:15,secondsRemaining:15,flip:0,points:15}));
  const scene=doc.getElementById('scene').firstChild;
  render(state({question:q,pointsCountdown:true,secondsPerFlip:15,secondsRemaining:12,flip:0,points:12}));
  assert.match(doc.getElementById('timer').textContent,/12 pts/);assert.doesNotMatch(doc.getElementById('timer').textContent,/12 s/);
  const glass=descendants(doc.getElementById('timer')).find(e=>e.className.startsWith('hourglass'));
  assert.equal(glass.className,'hourglass turn-even');assert.equal(doc.getElementById('scene').firstChild,scene);
  render(state({question:q,questionReading:true,playersReadyReading:true,readyCount:1,connectedCount:3}));assert.match(doc.getElementById('timer').textContent,/Prêts : 1\/3/);
  render(state({question:q,phase:'ANSWER_REVIEW',categoryAnswerMode:'WRITTEN'}));assert.ok(currentReceiver.parseState(state({phase:'ANSWER_REVIEW'})));
  assert.equal(doc.getElementById('scene').firstChild,scene);assert.match(doc.getElementById('answering').textContent,/valide les réponses écrites/);
});

test('pings finish before the vocal clip and interrupted sequences never resume', () => {
  const previous=global.Audio,played=[];let audio;
  global.Audio=class {constructor(src){this.src=src;audio=this;}pause(){}play(){played.push(this.src);return Promise.resolve();}};
  try {
    const player=currentReceiver.makeSoundPlayer(documentStub());player.setOrigin('http://host:8080/play');
    player.playSequence(['good-ping.wav','good-01.wav']);assert.equal(played.length,1);
    audio.onended();assert.equal(played.length,2);assert.ok(played[0].endsWith('/good-ping.wav'));assert.ok(played[1].endsWith('/good-01.wav'));
    player.playSequence(['bad-ping.wav','bad-04.mp3']);const finishOldPing=audio.onended;
    player.play('game-end.wav');finishOldPing();assert.ok(played.at(-1).endsWith('/game-end.wav'));assert.equal(played.length,4);
  } finally {global.Audio=previous;}
});

test('rapid reactions queue whole ping-and-voice sequences without clipping the previous first word', async () => {
  const previous=global.Audio,played=[];let audio;
  global.Audio=class {constructor(src){this.src=src;this.paused=true;audio=this;}pause(){this.paused=true;}play(){this.paused=false;played.push(this.src);return Promise.resolve();}};
  try {
    const player=currentReceiver.makeSoundPlayer(documentStub());player.setOrigin('http://host:8080/play');
    player.playSequence(['bad-ping.wav','bad-01.wav']);await Promise.resolve();
    player.playSequence(['good-ping.wav','good-03.wav']);assert.equal(played.length,1);
    audio.onended();await Promise.resolve();audio.onended();await Promise.resolve();audio.onended();
    assert.deepEqual(played,['bad-ping.wav','bad-01.wav','good-ping.wav','good-03.wav'].map(file=>'http://host:8080/tv/sounds/'+file));
  } finally {global.Audio=previous;}
});

test('game ending has a distinct sound once, including no replay on late connection', () => {
  const previous=global.Audio,played=[];global.Audio=class {constructor(src){this.src=src;}pause(){}play(){played.push(this.src);return Promise.resolve();}};
  try {
    for(const renderer of [receiver,currentReceiver]) {
      const render=renderer.makeRenderer(documentStub()),base=state({joinUrl:'http://host:8080/play'});
      render(base);render({...base,phase:'GAME_ENDED',question:null});render({...base,phase:'GAME_ENDED',question:null,teams:[{name:'A',score:20,connected:false}]});
      const late=renderer.makeRenderer(documentStub());late({...base,phase:'GAME_ENDED',question:null});
    }
    assert.deepEqual(played,['http://host:8080/tv/sounds/game-end.wav','http://host:8080/tv/sounds/game-end.wav']);
  } finally {global.Audio=previous;}
});

test('submitted choice cards turn green or red immediately and reset for the next question', () => {
  for(const renderer of [receiver,currentReceiver]) {
    const doc=documentStub(),render=renderer.makeRenderer(doc),q={id:'q',prompt:'Question',options:['A','B'],answer:null};
    const teams=[{name:'Right',score:0},{name:'Wrong',score:0},{name:'Waiting',score:0}];
    render(state({question:q,teams}));const scene=doc.getElementById('scene').firstChild;
    render(state({question:q,teams:teams.map((t,i)=>({...t,locked:i<2,answerResult:i===0?true:i===1?false:null}))}));
    const cards=doc.getElementById('scores').children;
    assert.ok(cards[0].className.includes('correct-team'));assert.ok(cards[1].className.includes('incorrect-team'));assert.equal(cards[2].className,'team');
    assert.equal(doc.getElementById('scene').firstChild,scene);
    render(state({question:{...q,id:'next'},teams}));assert.ok(doc.getElementById('scores').children.every(c=>c.className==='team'));
  }
});

test('blocked debug audio offers activation and reuses the activated element for voices and buzzers', async () => {
  const previous={Audio:global.Audio,location:global.location};let allowed=false,created=0;const played=[];
  global.location={origin:'http://localhost:18080'};
  global.Audio=class {constructor(src){this.src=src;created++;}pause(){}play(){played.push(this.src);return allowed?Promise.resolve():Promise.reject(Object.assign(new Error('Blocked'),{name:'NotAllowedError'}));}};
  try {
    const doc=documentStub(),player=currentReceiver.makeSoundPlayer(doc,{localAudio:true}),button=doc.getElementById('tv-audio-control');
    player.setOrigin('http://unreachable-host:8080/play');player.play('good-01.wav');await Promise.resolve();await Promise.resolve();
    assert.equal(button.style.display,'block');assert.equal(button.textContent,'Activer le son');assert.equal(player.enabled(),false);
    allowed=true;button.onclick();await Promise.resolve();await Promise.resolve();
    assert.equal(player.enabled(),true);assert.equal(button.style.display,'none');
    player.play('bad-04.mp3');player.play('buzzer.wav');await Promise.resolve();
    assert.equal(created,1);assert.deepEqual(played,['good-01.wav','enabled.wav','bad-04.mp3','buzzer.wav'].map(file=>'http://localhost:18080/tv/sounds/'+file));
  } finally {Object.assign(global,previous);}
});

test('new accepted buzzes play once and old buzzes do not replay when joining or reconnecting', () => {
  const previous=global.Audio,played=[];global.Audio=class {constructor(src){this.src=src;}pause(){}play(){played.push(this.src);return Promise.resolve();}};
  try {
    const render=currentReceiver.makeRenderer(documentStub()),base=state({joinUrl:'http://host:8080/play',buzzerSoundId:4});
    render(base);assert.equal(played.length,0);
    render({...base,buzzerSoundId:5,answeringTeam:'First'});render({...base,buzzerSoundId:5,answeringTeam:'First',answerSecondsRemaining:7});
    render({...base,buzzerSoundId:6,answeringTeam:'Next'});
    assert.deepEqual(played,['http://host:8080/tv/sounds/buzzer.wav','http://host:8080/tv/sounds/buzzer.wav']);
    render({...base,roomId:'new',buzzerSoundId:0});assert.equal(played.length,2);
  } finally {global.Audio=previous;}
});

test('recorded reaction and result symbol appear once, expire, and clear on a new question', () => {
  const previous={Audio:global.Audio,setTimeout:global.setTimeout,clearTimeout:global.clearTimeout};
  const played=[],timers=new Map();let sequence=0,stops=0,latest;
  global.Audio=class { constructor(url){this.src=url;latest=this;} play(){played.push(this.src);return Promise.resolve();} pause(){stops++;} };
  global.setTimeout=(callback,delay)=>{assert.equal(delay,2200);timers.set(++sequence,callback);return sequence;};
  global.clearTimeout=id=>timers.delete(id);
  try {
    for(const renderer of [receiver,currentReceiver]) {
      const doc=documentStub(),render=renderer.makeRenderer(doc);
      const base=state({joinUrl:'http://192.168.1.5:8080/play',answerSoundId:0,question:{id:'first',prompt:'Question',options:[],answer:null}});
      render(base);const scene=doc.getElementById('scene').firstChild,feedback=doc.getElementById('answer-feedback');
      assert.equal(feedback.style.display,'none');
      const bad={...base,answerSoundId:1,answerSound:'bad',answerSoundClip:'bad-04.mp3'};
      render(bad);assert.equal(feedback.textContent,'✕');assert.equal(feedback.className,'answer-feedback bad');assert.equal(feedback.style.display,'flex');
      assert.equal(played.at(-1),'http://192.168.1.5:8080/tv/sounds/bad-ping.wav');latest.onended();
      const count=played.length;render({...bad,secondsRemaining:3});assert.equal(played.length,count);assert.equal(doc.getElementById('scene').firstChild,scene);
      timers.get(sequence)();assert.equal(feedback.style.display,'none');
      render({...bad,answerSoundId:2,answerSound:'good',answerSoundClip:'good-03.wav'});
      assert.equal(played.at(-1),'http://192.168.1.5:8080/tv/sounds/good-ping.wav');latest.onended();
      assert.equal(feedback.textContent,'✓');assert.equal(feedback.style.display,'flex');
      render({...base,question:{...base.question,id:'next'},answerSoundId:2});assert.equal(feedback.style.display,'none');
      render({...base,question:{...base.question,id:'next'},answerSoundId:3,answerSound:'good',answerSoundClip:'../secret.wav'});
      latest.onended();
      assert.equal(played.at(-1),'http://192.168.1.5:8080/tv/sounds/good.wav');
      render({...base,roomId:'another',answerSoundId:20,answerSound:'good'});assert.equal(feedback.style.display,'none');
    }
    assert.ok(played.includes('http://192.168.1.5:8080/tv/sounds/bad-04.mp3'));assert.ok(stops>0);
  } finally {Object.assign(global,previous);}
});

test('answer sounds play once per new cue and never replay an old cue on initial connection', () => {
  const previous=global.Audio,played=[];let latest;
  global.Audio=class { constructor(url) { this.src=url;latest=this; } play() { played.push(this.src); return Promise.resolve(); } };
  try {
    const render=currentReceiver.makeRenderer(documentStub());
    const base=state({joinUrl:'http://192.168.1.5:8080/play',answerSoundId:4,answerSound:'good'});
    render(base); assert.equal(played.length,0);
    render({...base,answerSoundId:5,answerSound:'bad'});
    latest.onended();
    render({...base,answerSoundId:5,answerSound:'bad',secondsRemaining:3});
    render({...base,answerSoundId:6,answerSound:'good'});
    latest.onended();
    assert.deepEqual(played,['bad-ping.wav','bad.wav','good-ping.wav','good.wav'].map(file=>'http://192.168.1.5:8080/tv/sounds/'+file));
  } finally { global.Audio=previous; }
});

test('TV voting displays subjects, totals and the second-round selection without private ballots', () => {
  const doc=documentStub(),render=currentReceiver.makeRenderer(doc);
  const vote={candidates:['Arts','Musique'],selected:[],totals:{Arts:2,Musique:1},round:1,slots:1,hostTieBreak:false,completed:false,ballots:3};
  assert.ok(currentReceiver.parseState(state({phase:'SUBJECT_VOTING',question:null,subjectVote:vote})));
  render(state({phase:'SUBJECT_VOTING',question:null,subjectVote:vote}));
  assert.match(doc.getElementById('scene').textContent,/Arts · 2 vote/);
  render(state({phase:'SUBJECT_VOTING',question:null,subjectVote:{...vote,round:2,selected:['Nature'],totals:{Arts:0,Musique:0}}}));
  assert.match(doc.getElementById('scene').textContent,/Second vote/);
  assert.match(doc.getElementById('scene').textContent,/Déjà retenus : Nature/);
});

test('TV lobby shows the local join QR and URL; live questions name the answering team', () => {
  const doc = documentStub(), render = currentReceiver.makeRenderer(doc);
  render(state({ phase: 'LOBBY', question: null,
    joinUrl: 'http://192.168.1.5:8080/play', joinQrUrl: 'https://example.com/tv/join-qr.svg' }));
  const qr = descendants(doc.getElementById('scene')).find(child => child.className === 'join-qr');
  assert.equal(qr.src, 'https://example.com/tv/join-qr.svg');
  assert.match(doc.getElementById('scene').textContent, /192\.168\.1\.5/);
  render(state({ answeringTeam: 'Les amis', answerSecondsRemaining: 7, answerTimeSeconds: 10,
    teams: [{name: 'Les amis', score: 10}, {name: 'Autre', score: -5}] }));
  assert.match(doc.getElementById('answer-overlay').textContent, /Les amis/);
  assert.match(doc.getElementById('answering').textContent, /À LA PAROLE/);
  assert.match(doc.getElementById('scores').textContent, /Les amis.*Autre/);
  const timer = doc.getElementById('timer');
  assert.match(timer.textContent, /Pause/);
  assert.doesNotMatch(timer.textContent, /Réponse/);
  const upper = descendants(timer).find(child => child.className === 'sand-upper');
  assert.equal(parseFloat(upper.style.height), 42);
  render(state({ timerPaused: true, secondsRemaining: 3, secondsPerFlip: 5 }));
  const stream = descendants(timer).find(child => child.className === 'sand-stream');
  assert.equal(stream.style.display, 'none');
  assert.equal(doc.getElementById('answering').textContent, '');
});

test('progressive clue snapshots update at point drops and stay stable during answer countdown', () => {
  for (const renderer of [receiver, currentReceiver]) {
    const doc = documentStub(), render = renderer.makeRenderer(doc);
    const first = state({ question: { prompt: 'Qui suis-je ?\n\n1. Premier indice', options: [], answer: null }, points: 15 });
    render(first);
    assert.match(doc.getElementById('scene').textContent, /Premier indice/);
    const before = doc.getElementById('scene').firstChild;
    render({ ...first, answerSecondsRemaining: 9, answeringTeam: 'A' });
    assert.equal(doc.getElementById('scene').firstChild, before);
    const next = { ...first, flip: 1, points: 10, question: { ...first.question, prompt: first.question.prompt + '\n\n2. Deuxième indice' } };
    render(next);
    assert.match(doc.getElementById('scene').textContent, /Deuxième indice/);
    assert.equal(doc.getElementById('scene').firstChild, before);
    render({ ...next, phase: 'REVEAL_ANSWER', question: { prompt: 'Qui suis-je ?', options: [], answer: 'Solution' } });
    assert.match(doc.getElementById('scene').textContent, /Solution/);
    assert.match(doc.getElementById('scene').textContent, /Deuxième indice/);
  }
});

test('current TV shows wager phases and every team in score order including ties', () => {
  const doc = documentStub();
  const render = currentReceiver.makeRenderer(doc);
  const teams = [100, 80, 60, 60, 40].map((score, i) => ({ name: 'Team ' + i, score, connected: true }));
  render(state({ phase: 'REVEAL_ANSWER', teams }));
  const scores = doc.getElementById('scores');
  assert.equal(scores.style.display, '');
  assert.equal(scores.children.filter(el => el.className === 'team').length, 5);
  assert.match(scores.textContent, /Team 0.*Team 1.*Team 2.*Team 3.*Team 4/);
  assert.match(scores.textContent, /3\. Team 2/);
  assert.match(scores.textContent, /3\. Team 3/);
  assert.match(scores.textContent, /5\. Team 4/);
  assert.ok(currentReceiver.parseState(state({ phase: 'WAGER_OPEN' })));
  render(state({ phase: 'WAGER_OPEN', question: null }));
  assert.match(doc.getElementById('scene').textContent, /mise/);
  assert.doesNotMatch(doc.getElementById('scene').textContent, /Red planet/);
  render(state({ phase: 'WAGER_RESULTS', question: null, wagerResults: [{ teamName: 'Team 0', amount: 50, correct: false, delta: -50 }] }));
  assert.match(doc.getElementById('scene').textContent, /Perdue/);
  assert.match(doc.getElementById('scene').textContent, /-50 pts/);
});

class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.style = {}; this.value = ''; }
  set textContent(value) { this.value = String(value); this.children = []; }
  get textContent() { return this.value + this.children.map(child => child.textContent).join(''); }
  get firstChild() { return this.children[0]; }
  appendChild(child) { this.children.push(child); return child; }
  setAttribute(name,value) { this[name]=value; }
  removeChild(child) { this.children.splice(this.children.indexOf(child), 1); }
}
function documentStub() {
  const elements = {};
  return {
    createElement: tag => new Element(tag),
    getElementById: id => elements[id] || (elements[id] = new Element('div'))
  };
}
function descendants(element) { return element.children.flatMap(child => [child, ...descendants(child)]); }
function state(overrides = {}) {
  return { type: 'state', version: 1, roomId: '1234', phase: 'QUESTION_ACTIVE', category: 'Science',
    categories: [], round: 1, totalRounds: 5, flip: 0, secondsRemaining: 10, points: 100,
    question: { prompt: 'Red planet?', options: ['Mars', 'Venus'], answer: null },
    teams: [{ name: 'Team', score: 100, connected: true }], ...overrides };
}

test('correct teams highlight on reveal and clear on the next question without changing question nodes', () => {
  for (const renderer of [receiver, currentReceiver]) {
    const doc = documentStub(), render = renderer.makeRenderer(doc);
    const teams = [{name:'Right',score:15,correct:true},{name:'Wrong',score:10,correct:false},{name:'No answer',score:0}];
    const question = {id:'q',prompt:'Question',options:['A','B'],answer:null};
    const highlighted = () => doc.getElementById('scores').children.filter(el => el.className.includes('correct-team'));
    render(state({question,teams}));
    assert.equal(highlighted().length,0);
    const scene = doc.getElementById('scene').firstChild;
    render(state({phase:'REVEAL_ANSWER',question:{...question,answer:'A',correctOptionIndex:0},teams}));
    assert.equal(highlighted().length,1);
    assert.match(highlighted()[0].textContent,/Right/);
    assert.equal(doc.getElementById('scene').firstChild,scene);
    render(state({phase:'ROUND_SUMMARY',question:{...question,answer:'A'},teams}));
    assert.equal(highlighted().length,1);
    render(state({question:{...question,id:'next'},teams}));
    assert.equal(highlighted().length,0);
    render(state({phase:'REVEAL_ANSWER',question,teams:teams.map(t=>({...t,correct:false}))}));
    assert.equal(highlighted().length,0);
  }
});

test('question punctuation stays attached and long answers remain complete in a stable text node', () => {
  for (const renderer of [receiver, currentReceiver]) {
    const doc=documentStub(),render=renderer.makeRenderer(doc);
    const question={id:'typography',prompt:'Dans quelle ville se trouve ce monument ?',options:[],answer:null};
    render(state({question}));
    const heading=descendants(doc.getElementById('scene')).find(el=>el.tag==='h1');
    assert.match(heading.textContent,/monument\u00a0\?$/);
    const answer=descendants(doc.getElementById('scene')).find(el=>el.className==='answer-text');
    const complete='Le château de Chenonceau, dont la galerie traverse le Cher, avec ses jardins et ses collections historiques.';
    render(state({phase:'REVEAL_ANSWER',question:{...question,answer:complete}}));
    assert.equal(answer.textContent,complete);
    assert.equal(descendants(doc.getElementById('scene')).find(el=>el.className==='answer-text'),answer);
    render(state({question:{...question,id:'next'}}));
    assert.equal(descendants(doc.getElementById('scene')).find(el=>el.className==='answer-text').textContent,'');
  }
});
test('rejects malformed and incompatible messages', () => {
  assert.equal(receiver.parseState('{'), null);
  assert.equal(receiver.parseState(state({ version: 2 })), null);
  assert.equal(receiver.parseState(state({ teams: [null] })), null);
  assert.deepEqual(receiver.parseState(JSON.stringify(state())), state());
});
test('images require HTTPS or same-origin local HTTP', () => {
  assert.equal(receiver.safeImageUrl('javascript:alert(1)'), null);
  assert.equal(receiver.safeImageUrl('http://example.com/map.png'), null);
  assert.equal(receiver.safeImageUrl('https://example.com/map.png'), 'https://example.com/map.png');
  const page = { host: '192.168.1.20:8080' };
  assert.equal(receiver.safeImageUrl('http://192.168.1.20:8080/media/charades/images/nun-ace.png', page),
    'http://192.168.1.20:8080/media/charades/images/nun-ace.png');
  assert.equal(receiver.safeImageUrl('http://192.168.1.21:8080/media/charades/images/nun-ace.png', page), null);
});
test('renders all phases, reveals answers at the right time, and clears old content', () => {
  const doc = documentStub();
  const render = receiver.makeRenderer(doc);
  const question = { prompt: 'Red planet?', options: ['Mars', 'Venus'], answer: 'Mars' };
  for (const phase of ['LOBBY', 'CATEGORY_SELECT', 'QUESTION_ACTIVE', 'REVEAL_ANSWER', 'ROUND_SUMMARY', 'GAME_ENDED']) {
    render(state({ phase, question }));
    assert.ok(doc.getElementById('scene').children.length > 0);
    const correct = descendants(doc.getElementById('scene')).filter(child => child.className === 'correct-choice');
    assert.equal(correct.length, ['REVEAL_ANSWER', 'ROUND_SUMMARY'].includes(phase) ? 1 : 0);
  }
  assert.equal(doc.getElementById('timer').textContent, '');
});
test('buzzing, scores and revealing preserve question and image nodes while choices highlight in place', () => {
  const doc = documentStub(), render = currentReceiver.makeRenderer(doc);
  const question = {id: 'stable', prompt: 'Question', imageUrl: 'https://example.com/map.png', options: ['A','B','C','D'], answer: null};
  render(state({question, teams: [{name:'A', score:0, connected:true}]}));
  const layout = doc.getElementById('scene').firstChild;
  const image = descendants(layout).find(node => node.tag === 'img');
  render(state({question, answeringTeam:'A', answerSecondsRemaining:8, teams:[{name:'A', score:0, connected:true}]}));
  assert.equal(doc.getElementById('scene').firstChild, layout);
  assert.equal(doc.getElementById('answer-overlay').style.display, 'flex');
  render(state({phase:'REVEAL_ANSWER', question:{...question, answer:'C', correctOptionIndex:2}, teams:[{name:'A',score:15,connected:true}]}));
  assert.equal(doc.getElementById('scene').firstChild, layout);
  assert.equal(descendants(layout).find(node => node.tag === 'img'), image);
  assert.equal(descendants(layout).filter(node => node.className === 'wrong-choice').length, 3);
  assert.equal(descendants(layout).find(node => node.className === 'correct-choice').textContent, 'C');
  assert.equal(doc.getElementById('answer-overlay').style.display, 'none');
});
test('timer ticks preserve scene nodes and team names remain literal text', () => {
  const doc = documentStub();
  const render = receiver.makeRenderer(doc);
  const game = state({ teams: [{ name: '<img src=x onerror=alert(1)>', score: 50 }] });
  render(game);
  const firstNode = doc.getElementById('scene').firstChild;
  render({ ...game, secondsRemaining: 9 });
  assert.equal(doc.getElementById('scene').firstChild, firstNode);
  assert.match(doc.getElementById('timer').textContent, /9 s/);
  assert.equal(doc.getElementById('scores').style.display, '');
  render({ ...game, phase: 'CATEGORY_SELECT', question: null, categories: ['History'] });
  assert.equal(doc.getElementById('scores').style.display, '');
  const name = doc.getElementById('scores').firstChild.firstChild;
  assert.equal(name.tag, 'span');
  assert.match(name.textContent, /<img src=x onerror=alert\(1\)>/);
  assert.equal(name.children.length, 0);
});
test('receiver declares channel before starting and requests a snapshot on reconnect', () => {
  const events = {}, sent = [];
  let messageListener, options;
  const context = {
    addCustomMessageListener: (_, callback) => { messageListener = callback; },
    addEventListener: (name, callback) => { events[name] = callback; },
    sendCustomMessage: (...args) => sent.push(args),
    getSenders: () => [{ senderId: 'phone' }],
    start: value => { options = value; }
  };
  const system = { EventType: { READY: 'ready', SENDER_CONNECTED: 'connected', SENDER_DISCONNECTED: 'disconnected' }, MessageType: { JSON: 'json' } };
  const doc = documentStub();
  receiver.connectReceiver(context, { system }, doc);
  assert.equal(options.customNamespaces['urn:x-cast:com.example.triviaparty'], 'json');
  assert.equal(options.disableIdleTimeout, true);
  events.ready();
  events.connected({ senderId: 'phone' });
  assert.equal(sent.length, 2);
  assert.equal(sent[1][2].type, 'ready');
  messageListener({ data: state() });
  assert.equal(doc.getElementById('connection').textContent, 'Connecté à l’hôte');
});

test('renders offline map markers as labeled choices', () => {
  const doc = documentStub();
  const render = receiver.makeRenderer(doc);
  const question = { prompt: 'Choisissez la France.', imageUrl: '', options: ['A', 'B'], answer: null,
    mapOptions: [{ label: 'A', xRatio: 0.4, yRatio: 0.5 }, { label: 'B', xRatio: 0.7, yRatio: 0.4 }] };
  render(state({ question }));
  const scene = doc.getElementById('scene');
  const map = descendants(scene).find(child => child.className === 'visual map-fallback');
  assert.ok(map);
  assert.equal(map.children.filter(child => child.className.startsWith('map-choice')).length, 2);
});

test('current TV allocates a large image pane and keeps ordering choices fixed until reveal', () => {
  const doc = documentStub();
  const render = currentReceiver.makeRenderer(doc);
  render(state({ question: { prompt: 'Carte', imageUrl: 'https://example.com/map.png', options: ['A', 'B', 'C', 'D'], answer: null } }));
  const layout = doc.getElementById('scene').firstChild;
  assert.equal(layout.className, 'question-layout with-visual');
  assert.equal(layout.children[0].className, 'image-panel');
  assert.match(layout.children[1].textContent, /Carte.*A.*B.*C.*D/);
  const question = { prompt: 'Classez les événements', options: ['Événement Z', 'Événement X', 'Événement Y'], answer: null };
  render(state({ question }));
  const before = doc.getElementById('scene').textContent;
  render(state({ question, teams: [{ name: 'Team', score: 100, locked: true }] }));
  assert.equal(doc.getElementById('scene').textContent, before);
  assert.match(before, /Événement Z.*Événement X.*Événement Y/);
  render(state({ phase: 'REVEAL_ANSWER', question: { ...question, answer: 'Événement X → Événement Y → Événement Z' } }));
  assert.match(doc.getElementById('scene').textContent, /Événement X → Événement Y → Événement Z/);
});

test('renders category type and question count during the category introduction', () => {
  const doc = documentStub();
  const render = receiver.makeRenderer(doc);
  render(state({
    phase: 'CATEGORY_INTRO', category: 'Géographie', categoryQuestionCount: 5,
    categoryQuestionTypes: ['Carte', 'Classement'], categoryAnswerMode: 'SIMULTANEOUS', question: null
  }));
  const sceneText = doc.getElementById('scene').textContent;
  assert.match(sceneText, /Géographie/);
  assert.match(sceneText, /5 questions/);
  assert.match(sceneText, /Carte · Classement/);
});

test('chronology removes bullets and moves existing event rows into answer order only once', () => {
  const doc = documentStub(), render = currentReceiver.makeRenderer(doc);
  const question = { id: 'chrono', prompt: 'Du plus ancien au plus récent ?\n• Fondation de Québec\n• Premier voyage de Cartier\n• Arrivée de Cabot', options: [], answer: null };
  render(state({ question }));
  const lines = descendants(doc.getElementById('scene')).filter(el => el.className === 'chronology-line');
  assert.equal(lines.length, 3);
  assert.doesNotMatch(doc.getElementById('scene').textContent, /•/);
  const revealed = state({ phase: 'REVEAL_ANSWER', question: { ...question, prompt: 'Chronologie', answer: 'B — Cabot → Cartier → Québec' } });
  render(revealed);
  assert.equal(lines[2].style.transform, 'translateY(-200%)');
  assert.equal(lines[0].style.transform, 'translateY(200%)');
  assert.match(lines[2].textContent, /^1\. /);
  render(revealed);
  assert.doesNotMatch(lines[2].textContent, /^1\. 1\./);
  assert.equal(descendants(doc.getElementById('scene')).find(el => el.className === 'answer answer-slot').textContent, '');
});

test('clues are unnumbered, question timer stays frozen and only overlay counts the answer', () => {
  const doc = documentStub(), render = currentReceiver.makeRenderer(doc);
  const game = state({ secondsPerFlip: 20, secondsRemaining: 12, answerTimeSeconds: 10,
    question: { id: 'clues', prompt: 'Qui suis-je ?\n\n1. Premier indice\n2. Deuxième indice', options: [], answer: null } });
  render(game);
  const scene = doc.getElementById('scene');
  assert.equal(descendants(scene).filter(el => el.className === 'clue-text').length, 2);
  assert.doesNotMatch(scene.textContent, /[12]\. /);
  render({ ...game, answeringTeam: 'A', answerSecondsRemaining: 8 });
  const sand = descendants(doc.getElementById('timer')).find(el => el.className === 'sand-upper');
  const before = sand.style.height;
  render({ ...game, answeringTeam: 'A', answerSecondsRemaining: 7 });
  assert.equal(sand.style.height, before);
  assert.match(doc.getElementById('timer').textContent, /12 s/);
  assert.match(doc.getElementById('answer-overlay').textContent, /7 s/);
});
test('wagers sort by outcome and final podium gives tied teams the same medal', () => {
  const doc = documentStub(), render = currentReceiver.makeRenderer(doc);
  render(state({ phase: 'WAGER_RESULTS', question: null, wagerResults: [
    { teamName: 'Loss', amount: 10, delta: -10, correct: false },
    { teamName: 'Zero', amount: 0, delta: 0, correct: false },
    { teamName: 'Gain', amount: 15, delta: 15, correct: true }] }));
  assert.match(doc.getElementById('scene').textContent, /Gain.*Zero.*Loss/);
  assert.equal(descendants(doc.getElementById('scene')).filter(el => /^wager-(gain|loss|zero)$/.test(el.className)).length, 3);
  render(state({ phase: 'GAME_ENDED', question: null, teams: [{ name: 'A', score: 20 }, { name: 'B', score: 20 }, { name: 'C', score: 10 }] }));
  const podium = descendants(doc.getElementById('scene')).find(el => el.className === 'final-podium');
  assert.deepEqual(podium.children.map(el => el.className), ['podium-1', 'podium-1', 'podium-3']);
});

test('short chronology labels reorder on reveal, including a TV reconnect at reveal', () => {
 const question={id:'numbers',prompt:'Classez les nombres.\n• Trois\n• Un\n• Deux',options:[],answer:'C — Un → Deux → Trois'};
 for(const reconnect of [false,true]) {
  const doc=documentStub(),render=currentReceiver.makeRenderer(doc);
  if(!reconnect) render(state({question:{...question,answer:null}}));
  render(state({phase:'REVEAL_ANSWER',question}));
  const lines=descendants(doc.getElementById('scene')).filter(el=>el.className==='chronology-line ranked');
  assert.equal(lines.length,3);assert.equal(lines[0].style.transform,'translateY(200%)');
  assert.equal(descendants(doc.getElementById('scene')).find(el=>el.className==='answer answer-slot').textContent,'');
 }
});

test('lobby count updates as teams join and image buzzer nodes stay fixed on reveal', () => {
 const doc=documentStub(),render=currentReceiver.makeRenderer(doc);
 render(state({phase:'LOBBY',question:null,teams:[]}));
 assert.match(doc.getElementById('scene').textContent,/0 équipes prêtes/);
 render(state({phase:'LOBBY',question:null,teams:[{name:'A',score:0}]}));
 assert.match(doc.getElementById('scene').textContent,/1 équipe prête/);
 assert.doesNotMatch(doc.getElementById('scene').textContent,/1 équipes prêtes/);
 render(state({phase:'LOBBY',question:null,teams:[{name:'A',score:0},{name:'B',score:0}]}));
 assert.match(doc.getElementById('scene').textContent,/2 équipes prêtes/);
 const q={id:'image-buzzer',prompt:'Quelle est cette capitale ?',imageUrl:'https://example.com/capital.png',options:[],answer:null,answerMode:'BUZZER'};
 render(state({question:q}));
 const layout=doc.getElementById('scene').firstChild;
 assert.equal(layout.className,'question-layout image-buzzer');
 assert.equal(layout.children[0].className,'image-panel');
 const details=layout.children[1];
 render(state({phase:'REVEAL_ANSWER',question:{...q,answer:'Paris'}}));
 assert.equal(doc.getElementById('scene').firstChild,layout);
 assert.equal(layout.children[1],details);
 assert.match(details.children[details.children.length-1].textContent,/Paris/);
});


test('answering hides question content and validation displays only the selected submitted text', () => {
  const doc=documentStub(),render=currentReceiver.makeRenderer(doc);
  const q={id:'hidden-buzz',prompt:'Question visible avant le buzzer',options:[],answer:null};
  render(state({question:q}));const original=doc.getElementById('scene').firstChild;
  render(state({question:q,answeringTeam:'Alice',answerSecondsRemaining:10}));
  assert.equal(doc.getElementById('scene').style.visibility,'hidden');
  assert.equal(doc.getElementById('scene').firstChild,original);
  assert.match(doc.getElementById('answer-overlay').textContent,/Alice/);
  render(state({question:q}));assert.equal(doc.getElementById('scene').style.visibility,'');
  render(state({question:q,phase:'ANSWER_REVIEW',answeringTeam:'Bob',submittedAnswer:'Ma réponse <script>'}));
  assert.equal(doc.getElementById('scene').style.visibility,'hidden');
  assert.match(doc.getElementById('answer-overlay').textContent,/Bob/);
  assert.match(doc.getElementById('answer-overlay').textContent,/Ma réponse <script>/);
  render(state({question:q,phase:'REVEAL_ANSWER'}));
  assert.equal(doc.getElementById('scene').style.visibility,'');
  assert.equal(doc.getElementById('answer-overlay').style.display,'none');
  assert.doesNotMatch(doc.getElementById('answer-overlay').textContent,/Ma réponse/);
});

test('validated response and large name remain visible across repeated result snapshots', () => {
  const doc=documentStub(),render=currentReceiver.makeRenderer(doc);
  const review=state({phase:'ANSWER_REVIEW',answeringTeam:'Player One',submittedAnswer:'Written answer',submittedAnswerResult:true});
  render(review);render(review);
  assert.match(doc.getElementById('answer-overlay').textContent,/Player One/);
  assert.match(doc.getElementById('answer-overlay').textContent,/Written answer/);
  assert.equal(doc.getElementById('answer-overlay').className,'review-correct');
  assert.match(doc.getElementById('answering').textContent,/Réponse acceptée/);
  render({...review,answeringTeam:'Player Two',submittedAnswer:'Another answer',submittedAnswerResult:null});
  assert.doesNotMatch(doc.getElementById('answer-overlay').textContent,/Player One|Written answer/);
  assert.match(doc.getElementById('answer-overlay').textContent,/Player Two|Another answer/);
});

test('category intro always has a type and refreshes when category metadata changes',()=> {
 const doc=documentStub(),render=currentReceiver.makeRenderer(doc);
 render(state({phase:'CATEGORY_INTRO',category:'Legacy',categoryQuestionTypes:[],categoryAnswerMode:'BUZZER'}));
 assert.match(doc.getElementById('scene').textContent,/Type : Buzzer/);
 render(state({phase:'CATEGORY_INTRO',category:'Chronology',categoryQuestionTypes:['Chronologie'],categoryAnswerMode:'SIMULTANEOUS'}));
 assert.match(doc.getElementById('scene').textContent,/Type : Chronologie/);
 assert.doesNotMatch(doc.getElementById('scene').textContent,/Legacy/);
});

test('audio bank version forces fresh recordings without changing the authorized clip name',()=> {
 const original=global.Audio;let src;
 global.Audio=class {constructor(url){src=url;}play(){return Promise.resolve();}pause(){}};
 try {const sound=currentReceiver.makeSoundPlayer(documentStub());sound.setOrigin('http://host:8080/play');sound.setVersion('human-bank-20261014');sound.play('good-50.wav');assert.match(src,/good-50\.wav\?v=human-bank-20261014$/);}finally{global.Audio=original;}
});


test('activating a second debug display silences the first including queued speech', async () => {
  const previousAudio=global.Audio,previousChannel=global.BroadcastChannel,previousLocation=global.location;
  const channels=[],played=[];
  global.location={origin:'http://localhost:18080'};
  global.BroadcastChannel=class {constructor(){channels.push(this);}postMessage(data){channels.filter(c=>c!==this).forEach(c=>c.onmessage({data}));}};
  global.Audio=class {constructor(src){this.src=src;this.paused=true;}pause(){this.paused=true;}play(){this.paused=false;played.push(this.src);return Promise.resolve();}};
  try {
    const a=documentStub(),b=documentStub();
    const first=currentReceiver.makeSoundPlayer(a,{localAudio:true}),second=currentReceiver.makeSoundPlayer(b,{localAudio:true});
    a.getElementById('tv-audio-control').onclick();await Promise.resolve();
    b.getElementById('tv-audio-control').onclick();await Promise.resolve();
    const count=played.length;first.playSequence(['bad-ping.wav','bad-01.wav']);assert.equal(played.length,count);
    assert.equal(first.enabled(),false);assert.equal(second.enabled(),true);
    second.play('good-ping.wav');assert.equal(played.length,count+1);
    a.getElementById('tv-audio-control').onclick();await Promise.resolve();
    assert.equal(second.enabled(),false);assert.equal(first.enabled(),true);
  } finally {global.Audio=previousAudio;global.BroadcastChannel=previousChannel;global.location=previousLocation;}
});


test('buzzer is fetched and decoded before a press, starts from memory and honors debug ownership', async () => {
  const previous={Audio:global.Audio,AudioContext:global.AudioContext,fetch:global.fetch};
  const fetched=[],started=[],media=[];let stopped=0;
  global.Audio=class {constructor(src){this.src=src;}pause(){}play(){media.push(this.src);return Promise.resolve();}};
  global.AudioContext=class {
    constructor(options){assert.equal(options.latencyHint,'interactive');this.state='running';this.destination={};}
    resume(){return Promise.resolve();}
    decodeAudioData(bytes){return Promise.resolve({decoded:bytes});}
    createBufferSource(){return {connect(){},start(when){started.push({when,buffer:this.buffer});},stop(){stopped++;}};}
  };
  global.fetch=async url=>{fetched.push(url);return {ok:true,arrayBuffer:async()=>new ArrayBuffer(8)};};
  try {
    const player=currentReceiver.makeSoundPlayer(documentStub());player.setOrigin('http://host:8080/play');player.setVersion('bank1');
    await new Promise(setImmediate);assert.equal(fetched.length,1);assert.match(fetched[0],/buzzer.wav\?v=bank1$/);
    player.setVersion('bank1');assert.equal(fetched.length,1);
    player.play('buzzer.wav');assert.equal(started.length,1);assert.equal(started[0].when,0);assert.ok(started[0].buffer);assert.equal(media.length,0);
    player.play('buzzer.wav');assert.equal(started.length,2);assert.equal(stopped,1);assert.equal(fetched.length,1);
    player.stop();assert.equal(stopped,2);
    player.setVersion('bank2');await new Promise(setImmediate);assert.equal(fetched.length,2);
  } finally {Object.assign(global,previous);}
});

test('a failed buzzer preload keeps HTML audio available', async () => {
  const previous={Audio:global.Audio,AudioContext:global.AudioContext,fetch:global.fetch};const played=[];
  global.Audio=class {constructor(src){this.src=src;}pause(){}play(){played.push(this.src);return Promise.resolve();}};
  global.AudioContext=class {resume(){return Promise.resolve();}};
  global.fetch=async()=>{throw new Error('offline preload');};
  try {
    const player=currentReceiver.makeSoundPlayer(documentStub());player.setOrigin('http://host:8080/play');player.setVersion('bank');await new Promise(setImmediate);
    player.play('buzzer.wav');assert.equal(played.length,1);assert.match(played[0],/buzzer.wav/);
  } finally {Object.assign(global,previous);}
});
