const fs = require('node:fs');
for (const file of ['app/src/main/java/com/example/triviaparty/network/GameServer.kt','app/src/main/java/com/example/triviaparty/ui/host/HostScreen.kt']) {
  let s = fs.readFileSync(file,'utf8');
  s = s.replace(/it\.isLocked && it\.questionId == question\.id && it\.isCorrect != false(?! && it\.isBuzz)/g,'it.isLocked && it.questionId == question.id && it.isCorrect != false && it.isBuzz()');
  s = s.replace(/it\.isLocked && it\.isCorrect != false(?! && it\.isBuzz)/g,'it.isLocked && it.isCorrect != false && it.isBuzz()');
  fs.writeFileSync(file,s);
}
const file='app/src/test/browser-player.test.cjs';
let s=fs.readFileSync(file,'utf8').replace("type: 'multipleChoice', prompt: 'Secret question', options: ['Hidden answer']", "type: 'textAnswer', prompt: 'Secret question', options: ['Hidden answer']");
fs.writeFileSync(file,s);
const test='app/src/test/java/com/example/triviaparty/BrowserPlayerTest.kt';
s=fs.readFileSync(test,'utf8').replace('assertEquals(setOf("id"), safe["currentQuestion"]!!.jsonObject.keys)','assertEquals(setOf("id", "type", "options"), safe["currentQuestion"]!!.jsonObject.keys)');
fs.writeFileSync(test,s);
const doc='BROWSER-PLAYERS.md';
s=fs.readFileSync(doc,'utf8').replace('Players see only their team score and a persistent buzzer. Questions and answers stay on the TV and host screens; the host selects categories and judges spoken answers for every question type.', 'Players see their team score and a persistent buzzer. Multiple-choice questions (including speed races) also show answer choices: one tap submits and locks the answer immediately, with no Validate button. Question prompts and illustrations stay on the TV and host screens. The host selects categories and judges spoken answers for the other formats.');
fs.writeFileSync(doc,s);
