const fs=require('node:fs');
const file='app/src/test/browser-player.test.cjs';
let s=fs.readFileSync(file,'utf8');
s=s.slice(0,s.indexOf("test('buzz locks once"))+`
test('persistent buzzer has waiting, ready, pressed, blocked, incorrect and correct states', () => {
  const h = harness(); h.join();
  const buzz = () => h.all().find(el => el.className?.startsWith('buzz '));
  assert.equal(buzz().className, 'buzz waiting'); assert.equal(buzz().disabled, true);
  h.update({ state: 'QUESTION_ACTIVE', currentQuestion: { id: 'q1', type: 'multipleChoice', prompt: 'Secret question', options: ['Hidden answer'] } });
  assert.equal(buzz().className, 'buzz ready');
  assert.equal(h.$('scene').textContent.includes('Secret question'), false);
  assert.equal(h.$('scene').textContent.includes('Hidden answer'), false);
  buzz().click(); assert.equal(buzz().className, 'buzz pressed');
  const locks = () => h.socket.sent.filter(e => e.type.endsWith('.LockAnswer'));
  assert.equal(locks().length, 1); assert.equal(locks()[0].answer.text, 'BUZZ');
  buzz().click(); assert.equal(locks().length, 1);
  h.update({ submissions: { a: { isLocked: true, isCorrect: false } }, textBuzzedTeamIds: ['a'] });
  assert.equal(buzz().className, 'buzz incorrect'); assert.equal(buzz().disabled, true);
  h.update({ currentQuestion: { id: 'q2' }, submissions: {}, textBuzzedTeamIds: [], buzzActiveTeamId: 'b' });
  assert.equal(buzz().className, 'buzz blocked');
  h.update({ buzzActiveTeamId: null }); assert.equal(buzz().className, 'buzz ready');
  h.update({ state: 'REVEAL_ANSWER', submissions: { a: { isLocked: true, isCorrect: true } } });
  assert.equal(buzz().className, 'buzz correct');
  for (const phase of ['LOBBY','CATEGORY_SELECT','CATEGORY_INTRO','ROUND_SUMMARY','GAME_ENDED']) {
    h.update({ state: phase, submissions: {}, currentQuestion: null });
    assert.ok(buzz()); assert.equal(buzz().disabled, true);
    assert.equal(h.all().filter(el => el.tag === 'button' && el.className?.startsWith('buzz ')).length, 1);
  }
});

test('connection loss keeps the score and disabled buzzer visible while restoring team identity', () => {
  const h = harness(); h.join();
  h.update({ state: 'QUESTION_ACTIVE', currentQuestion: { id: 'q8' } });
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
  assert.equal(h.$('join').hidden, false); assert.equal(h.$('room').value, '5678');
  assert.equal(h.storage.size, 0); assert.match(h.$('join-message').textContent, /nouvelle partie/);
});
`;
fs.writeFileSync(file,s);
const docs='BROWSER-PLAYERS.md';
s=fs.readFileSync(docs,'utf8').replace('The browser supports buzzing, multiple choice, ordering, map choices, wagers, category selection, and scores.', 'Players see only their team score and a persistent buzzer. Questions and answers stay on the TV and host screens; the host selects categories and judges spoken answers for every question type.');
s=s.replace('their snapshots omit answer keys, team session tokens, and other teams\' submissions.','their snapshots omit question content, answer keys, team session tokens, and other teams\' submissions.');
s+='\nBuzzer colors: yellow = ready, blue = pressed / your turn to answer, red = disabled after an incorrect answer, green = correct, gray = waiting / another team answering / disconnected / game ended. The buzzer remains visible throughout the game and resets for the next question.\n';
fs.writeFileSync(docs,s);
