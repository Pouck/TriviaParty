(function () {
  "use strict";
  if (window.triviaPreviewShell) return;
  var status = document.getElementById("connection");
  var render = window.TriviaReceiver.makeRenderer(document,{localAudio:true});
  var retryDelay = 1000;
  var stopped = false;

  function connect() {
    if (stopped) return;
    var scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
    var socket;
    try {
      socket = new WebSocket(scheme + "//" + window.location.host + "/tv/ws");
    } catch (_) {
      retry();
      return;
    }
    socket.onopen = function () {
      retryDelay = 1000;
      status.textContent = "Connecté à la partie sur le réseau local";
    };
    socket.onmessage = function (event) {
      var message;try { message=JSON.parse(event.data); } catch(_) { return; }
      if(message && message.type==='buzzer') { render.buzzerCue(message);return; }
      if (!window.TriviaReceiver.parseState(message)) return;
      render(message);
      status.textContent = "Connecté à la partie sur le réseau local";
    };
    socket.onerror = function () {
      status.textContent = "Hôte inaccessible. Nouvelle tentative…";
    };
    socket.onclose = function () {
      status.textContent = "Connexion perdue. Nouvelle tentative…";
      retry();
    };
    window.addEventListener("beforeunload", function () {
      stopped = true;
      socket.close();
    }, { once: true });
  }

  function retry() {
    if (stopped) return;
    window.setTimeout(connect, retryDelay);
    retryDelay = Math.min(retryDelay * 2, 15000);
  }

  connect();
})();
