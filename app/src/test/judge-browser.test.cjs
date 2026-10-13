const test=require('node:test'), assert=require('node:assert/strict'), vm=require('node:vm'), fs=require('node:fs');
function harness() {
  const nodes={},sockets=[],timers=[];
  class Socket { constructor(url) { this.url=url;this.readyState=1;this.sent=[];sockets.push(this); } send(message) { this.sent.push(JSON.parse(message)); } }
  const document={getElementById:id=>nodes[id]||=( {disabled:false,hidden:false,textContent:''} )};
  vm.runInNewContext(fs.readFileSync('app/src/main/assets/player/judge.js','utf8'),{document,location:{hash:'#private-token',protocol:'http:',host:'host:8080'},WebSocket:Socket,setTimeout:f=>timers.push(f),clearTimeout(){}});
  const socket=sockets[0];socket.onopen();
  return {nodes,socket,update:state=>socket.onmessage({data:JSON.stringify(state)}),timers};
}
test('private arbiter reveals the solution and submits judgment for the active question only',()=>{
  const h=harness();
  assert.match(h.socket.url,/judge\/ws\?token=private-token/);
  h.update({questionId:'q',phase:'QUESTION_ACTIVE',answer:'Platon',teamId:'a',teamName:'Équipe A',answering:true,seconds:10,penalty:5});
  assert.equal(h.nodes.answer.textContent,'Platon');assert.equal(h.nodes.correct.disabled,false);
  h.nodes.wrong.onclick();
  assert.deepEqual(h.socket.sent[0],{type:'com.example.triviaparty.network.GameEvent.HostJudgeTextBuzz',questionId:'q',teamId:'a',correct:false});
  assert.equal(h.nodes.correct.disabled,true);assert.equal(h.nodes.wrong.disabled,true);
  h.update({questionId:'q',phase:'QUESTION_ACTIVE',answer:'Platon',answering:false,seconds:20,penalty:5});
  assert.equal(h.nodes.correct.disabled,true);assert.match(h.nodes.penalty.textContent,/−5 pts/);
});
test('arbiter starts a reading question, resumes a paused timer and disables controls after disconnect',()=>{
  const h=harness();
  h.update({questionId:'c',phase:'QUESTION_ACTIVE',reading:true,answering:false,paused:false,seconds:15});
  assert.equal(h.nodes.start.hidden,false);h.nodes.start.onclick();
  assert.equal(h.socket.sent[0].type,'com.example.triviaparty.network.GameEvent.HostStartQuestionTimer');
  h.update({questionId:'c',phase:'QUESTION_ACTIVE',reading:false,answering:false,paused:true,seconds:15});
  assert.equal(h.nodes.pause.textContent,'Reprendre');h.nodes.pause.onclick();
  assert.equal(h.socket.sent[1].type,'com.example.triviaparty.network.GameEvent.HostResumeTimer');
  h.socket.onclose({code:1006});
  assert.equal(h.nodes.pause.disabled,true);assert.equal(h.nodes.start.disabled,true);assert.equal(h.nodes.correct.disabled,true);
});
