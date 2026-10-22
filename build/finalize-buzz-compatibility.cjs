const fs=require('fs');let p='app/src/main/java/com/example/triviaparty/model/BuzzQueue.kt';let s=fs.readFileSync(p,'utf8').replace('questionReading || !usesPlayerBuzzer() ||','questionReading || currentCategoryAnswerMode == CategoryAnswerMode.WRITTEN ||');fs.writeFileSync(p,s);
p='app/src/main/java/com/example/triviaparty/network/GameServer.kt';s=fs.readFileSync(p,'utf8').replace('_gameSession.value = current.rejectOralAnswer(selected.teamId).advanceBuzzQueue()', '_gameSession.value = current.rejectOralAnswer(selected.teamId).advanceBuzzQueue().let {\n                            if (it.answerTimerTeamId == null) it.copy(answerTimerRemainingSeconds = 0) else it\n                        }');fs.writeFileSync(p,s);
p='app/src/test/browser-player.test.cjs';s=fs.readFileSync(p,'utf8').replace("function harness(saved, search = '?room=1234') {", "function harness(saved, search = '?room=1234', audioEnvironment = {}) {").replace('    URLSearchParams, Uint8Array, crypto: webcrypto, navigator: {},','    URLSearchParams, Uint8Array, crypto: webcrypto, navigator: {}, ...audioEnvironment,');
s+=`
test('a later phone still sounds and queues its own buzz but promotion does not replay it',()=> {
 let played=0;
 class Audio {constructor(url){this.src=url;}load(){}play(){played++;return Promise.resolve();}}
 const h=harness(null,'?room=1234',{Audio});h.join();
 h.update({state:'QUESTION_ACTIVE',categoryBuzzerSound:'owl',currentQuestion:{id:'oral',type:'textAnswer'},submissions:{},buzzQueue:[],buzzActiveTeamId:'b'});
 const buzz=()=>h.all().find(el=>el.className?.startsWith('buzz '));
 assert.equal(buzz().disabled,false);buzz().click();
 assert.equal(played,1);assert.ok(h.socket.sent.at(-1).type.endsWith('.LockAnswer'));
 h.update({buzzQueue:[{teamId:'b',questionId:'oral'},{teamId:'a',questionId:'oral'}]});
 assert.equal(buzz().className,'buzz queued');assert.equal(buzz().disabled,true);
 h.update({buzzActiveTeamId:'a',submissions:{a:{isLocked:true}}});
 assert.equal(buzz().className,'buzz pressed');assert.equal(played,1);
});
`;fs.writeFileSync(p,s);
