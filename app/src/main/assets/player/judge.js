(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const token = location.hash.slice(1);
  let socket, state, reconnect;
  function send(type,fields={}) {
    if (!state || socket?.readyState!==1) return;
    socket.send(JSON.stringify({type:'com.example.triviaparty.network.GameEvent.'+type,questionId:state.questionId,...fields}));
    $('correct').disabled=$('wrong').disabled=true;
  }
  $('correct').onclick=()=>send('HostJudgeTextBuzz',{teamId:state.teamId,correct:true});
  $('wrong').onclick=()=>send('HostJudgeTextBuzz',{teamId:state.teamId,correct:false});
  $('start').onclick=()=>send('HostStartQuestionTimer');
  $('pause').onclick=()=>send(state.paused?'HostResumeTimer':'HostPauseTimer');
  function connect() {
    clearTimeout(reconnect);
    if (!token) { $('connection').textContent='Ouvrez le lien privé depuis l’écran de préparation de l’hôte.'; return; }
    socket=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/judge/ws?token='+encodeURIComponent(token));
    socket.onopen=()=>{ $('connection').textContent='Connecté · écran privé, à garder hors diffusion'; };
    socket.onmessage=message=>{
      state=JSON.parse(message.data);
      $('answer').textContent=state.answer || 'En attente d’une question orale';
      $('team').textContent=state.answering?state.teamName+' a la parole':'En attente';
      $('timer').textContent=state.phase==='QUESTION_ACTIVE'?(state.reading?'Lecture':state.seconds+' s'):'';
      $('correct').disabled=$('wrong').disabled=!state.answering;
      $('start').hidden=!state.reading;
      $('pause').hidden=state.phase!=='QUESTION_ACTIVE'||state.reading||state.answering;
      $('pause').textContent=state.paused?'Reprendre':'Pause';
      $('pause').disabled=$('start').disabled=false;
      $('penalty').textContent=state.penalty?'Mauvaise réponse ou délai dépassé : −'+state.penalty+' pts ; retour au prochain indice.':'';
    };
    socket.onclose=event=>{
      $('correct').disabled=$('wrong').disabled=true;
      $('pause').disabled=$('start').disabled=true;
      $('answer').textContent='Connexion interrompue';
      $('connection').textContent=event.code===1008?'Lien privé invalide':'Reconnexion…';
      if(event.code!==1008) reconnect=setTimeout(connect,1000);
    };
  }
  connect();
})();
