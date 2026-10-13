const assert=require('node:assert/strict'),fs=require('node:fs');
// Forward localhost through adb first: adb forward tcp:18080 tcp:8080.
const prefix='com.example.triviaparty.network.GameEvent.',host=process.argv[2]||'127.0.0.1:18080';
async function connect(path){
 const socket=new WebSocket('ws://'+host+path),queue=[],waiters=[];
 socket.onmessage=e=>{queue.push(JSON.parse(e.data));pump();};
 function pump(){if(!waiters.length)return; const waiter=waiters[0];while(queue.length){const message=queue.shift();if(waiter.test(message)){waiters.shift();clearTimeout(waiter.timeout);waiter.resolve(message);pump();return;}}}
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
 return {socket,send:(name,fields={})=>socket.send(JSON.stringify({type:prefix+name,...fields})),
  wait:test=>new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('Timed out waiting for '+path)),15000);waiters.push({test,resolve,timeout});pump();})};
}
const state=(test)=>message=>message.type===prefix+'RoomStateBroadcast'&&test(message.session);
(async()=>{
 const connections=[];
 try {
  const h=await connect('/ws');connections.push(h);
  let session=(await h.wait(state(s=>s.state==='LOBBY'&&s.subjectVoting&&!s.subjectVoting.completed))).session;
  console.log('Voting lobby received.');
  const room=session.roomId,count=session.subjectVoting.settings.categories;
  assert.equal(count,5);assert.equal(session.subjectVoting.settings.setsPerCategory,1);
  const a=await connect('/play/ws'),b=await connect('/play/ws');connections.push(a,b);
  a.send('JoinRoom',{roomId:room,teamName:'Vérification vote A',sessionToken:'smoke-a'});
  const aid=(await a.wait(m=>m.type===prefix+'JoinResponse'&&m.success)).teamId;
  b.send('JoinRoom',{roomId:room,teamName:'Vérification vote B',sessionToken:'smoke-b'});
  const bid=(await b.wait(m=>m.type===prefix+'JoinResponse'&&m.success)).teamId;
  await h.wait(state(s=>s.teams.length===2));
  console.log('Both teams joined.');
  h.send('HostOpenSubjectVote');session=(await h.wait(state(s=>s.state==='SUBJECT_VOTING'))).session;
  const candidates=session.subjectVoting.candidates,common=candidates.slice(0,count-1);
  a.send('SubmitSubjectVote',{teamId:aid,round:1,subjects:common.concat(candidates[count-1])});
  b.send('SubmitSubjectVote',{teamId:bid,round:1,subjects:common.concat(candidates[count])});
  await h.wait(state(s=>Object.keys(s.subjectVoting.ballots).length===2));h.send('HostCloseSubjectVote');
  console.log('First round submitted.');
  session=(await h.wait(state(s=>s.subjectVoting.round===2))).session;
  assert.equal(session.subjectVoting.selected.length,4);assert.equal(session.subjectVoting.candidates.length,2);
  a.send('SubmitSubjectVote',{teamId:aid,round:2,subjects:[session.subjectVoting.candidates[0]]});
  b.send('SubmitSubjectVote',{teamId:bid,round:2,subjects:[session.subjectVoting.candidates[1]]});
  await h.wait(state(s=>s.subjectVoting.round===2&&Object.keys(s.subjectVoting.ballots).length===2));h.send('HostCloseSubjectVote');
  session=(await h.wait(state(s=>s.subjectVoting.hostTieBreak))).session;
  fs.writeFileSync('build/pixel-vote-tie.json',JSON.stringify(session,null,2));
  h.send('HostBreakSubjectTie',{subjects:[session.subjectVoting.candidates[0]]});
  session=(await h.wait(state(s=>s.subjectVoting.completed))).session;
  assert.equal(session.roomId,room);assert.equal(session.teams.length,2);assert.equal(session.masterCategories.length,5);
  assert.equal(session.playedQuestionIds.length,0);
  fs.writeFileSync('build/pixel-vote-complete.json',JSON.stringify(session,null,2));
  console.log('Pixel: joined before voting; cutoff tie re-voted; repeated tie resolved by host; five packages selected; no questions or usage statistics consumed.');
 } finally {connections.forEach(c=>c.socket.close());}
})().catch(e=>{console.error(e);process.exitCode=1;});
