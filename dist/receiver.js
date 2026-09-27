(function (root) {
  "use strict";
  var namespace = "urn:x-cast:com.example.triviaparty";
  var phases = ["LOBBY", "CATEGORY_SELECT", "QUESTION_ACTIVE", "REVEAL_ANSWER", "ROUND_SUMMARY", "GAME_ENDED"];

  function parseState(data) {
    try {
      var state = typeof data === "string" ? JSON.parse(data) : data;
      if (!state || state.type !== "state" || state.version !== 1 || phases.indexOf(state.phase) < 0 ||
          typeof state.roomId !== "string" || !Array.isArray(state.teams) || !Array.isArray(state.categories)) return null;
      if (!state.teams.every(function (t) { return t && typeof t.name === "string" && Number.isFinite(t.score); })) return null;
      if (state.question && (typeof state.question.prompt !== "string" || !Array.isArray(state.question.options))) return null;
      return state;
    } catch (_) { return null; }
  }

  function safeImageUrl(value) {
    if (typeof value !== "string") return null;
    try { var url = new URL(value); return url.protocol === "https:" ? url.href : null; }
    catch (_) { return null; }
  }

  function makeRenderer(doc) {
    var lastScene = "";
    function node(tag, text, className) {
      var element = doc.createElement(tag);
      if (text != null) element.textContent = String(text);
      if (className) element.className = className;
      return element;
    }
    function clear(element) { while (element.firstChild) element.removeChild(element.firstChild); }
    function text(id, value) { doc.getElementById(id).textContent = value; }
    function choices(parent, items) {
      var list = node("ul", null, "options");
      items.forEach(function (item, index) { list.appendChild(node("li", (index + 1) + ". " + item)); });
      parent.appendChild(list);
    }
    function visual(parent, question, reveal) {
      var url = safeImageUrl(question.imageUrl);
      if (!url) return;
      var wrapper = node("div", null, "visual");
      var image = node("img");
      image.src = url;
      image.alt = "Question illustration";
      image.onerror = function () { wrapper.textContent = "Image unavailable"; };
      wrapper.appendChild(image);
      var t = reveal && question.mapTarget;
      if (t) {
        var circle = t.type && t.type.indexOf("CenterRadius") >= 0;
        var left = circle ? t.xRatio - t.maxDistanceRatio : t.minXRatio;
        var top = circle ? t.yRatio - t.maxDistanceRatio : t.minYRatio;
        var width = circle ? t.maxDistanceRatio * 2 : t.maxXRatio - t.minXRatio;
        var height = circle ? t.maxDistanceRatio * 2 : t.maxYRatio - t.minYRatio;
        if ([left, top, width, height].every(Number.isFinite)) {
          var target = node("div", null, "target" + (circle ? " circle" : ""));
          target.style.left = left * 100 + "%";
          target.style.top = top * 100 + "%";
          target.style.width = width * 100 + "%";
          target.style.height = height * 100 + "%";
          wrapper.appendChild(target);
        }
      }
      parent.appendChild(wrapper);
    }
    return function render(state) {
      text("room", "ROOM " + state.roomId);
      text("category", state.category || "Lobby");
      text("round", "Round " + state.round + " of " + state.totalRounds);
      text("timer", state.phase === "QUESTION_ACTIVE" ?
        state.secondsRemaining + "s · Flip " + state.flip + " · " + state.points + " pts" : "");
      // Timer ticks must not reload images or reset the scene's scroll position.
      var sceneKey = JSON.stringify([state.roomId, state.phase, state.question, state.categories, state.picker, state.teams]);
      if (sceneKey === lastScene) return;
      lastScene = sceneKey;
      var scene = doc.getElementById("scene");
      clear(scene);
      switch (state.phase) {
        case "LOBBY":
          scene.appendChild(node("h1", "Join the game!"));
          scene.appendChild(node("p", "Enter room code " + state.roomId + " on your phone."));
          scene.appendChild(node("p", state.teams.length + " teams ready"));
          break;
        case "CATEGORY_SELECT":
          scene.appendChild(node("h1", (state.picker || "The host") + " is choosing a category"));
          choices(scene, state.categories);
          break;
        case "QUESTION_ACTIVE":
        case "REVEAL_ANSWER":
        case "ROUND_SUMMARY":
          var reveal = state.phase !== "QUESTION_ACTIVE";
          if (reveal) scene.appendChild(node("h1", state.phase === "ROUND_SUMMARY" ? "Round results" : "Answer revealed"));
          var question = state.question;
          if (question) {
            scene.appendChild(node(reveal ? "p" : "h1", question.prompt));
            visual(scene, question, reveal);
            if (reveal && question.answer) scene.appendChild(node("p", question.answer, "answer"));
            else if (!reveal) choices(scene, question.options);
          }
          break;
        case "GAME_ENDED":
          scene.appendChild(node("h1", "Final scores"));
          var best = Math.max.apply(null, state.teams.map(function (team) { return team.score; }));
          var winners = state.teams.filter(function (team) { return team.score === best; });
          scene.appendChild(node("p", winners.length ? "Winner" + (winners.length > 1 ? "s: " : ": ") +
            winners.map(function (team) { return team.name; }).join(" & ") : "Thanks for playing!"));
          break;
      }
      var scores = doc.getElementById("scores");
      clear(scores);
      state.teams.slice().sort(function (a, b) { return b.score - a.score; }).forEach(function (team) {
        var card = node("div", null, "team");
        card.appendChild(node("span", team.name + ": "));
        card.appendChild(node("b", team.score + " pts"));
        if (state.phase === "QUESTION_ACTIVE") card.appendChild(node("span", team.locked ? " · Locked" : " · Answering"));
        if (!team.connected) card.appendChild(node("span", " · Offline"));
        scores.appendChild(card);
      });
    };
  }

  function connectReceiver(context, framework, doc) {
    var render = makeRenderer(doc);
    function ready(senderId) { context.sendCustomMessage(namespace, senderId, { type: "ready", version: 1 }); }
    context.addCustomMessageListener(namespace, function (event) {
      var state = parseState(event.data);
      if (!state) return;
      render(state);
      doc.getElementById("connection").textContent = "Connected to host";
    });
    context.addEventListener(framework.system.EventType.READY, function () {
      context.getSenders().forEach(function (sender) { ready(sender.senderId); });
    });
    context.addEventListener(framework.system.EventType.SENDER_CONNECTED, function (event) { ready(event.senderId); });
    context.addEventListener(framework.system.EventType.SENDER_DISCONNECTED, function () {
      if (!context.getSenders().length) doc.getElementById("connection").textContent = "Host disconnected. Reconnect from the phone to continue.";
    });
    var options = { disableIdleTimeout: true, skipPlayersLoad: true, customNamespaces: {} };
    options.customNamespaces[namespace] = framework.system.MessageType.JSON;
    context.start(options);
  }

  function start() {
    var doc = root.document;
    if (new URLSearchParams(root.location.search).has("preview")) {
      var render = makeRenderer(doc);
      var preview = doc.getElementById("preview");
      preview.hidden = false;
      preview.textContent = "Preview phase: ";
      var select = doc.createElement("select");
      phases.forEach(function (phase) {
        var option = doc.createElement("option"); option.textContent = phase; option.value = phase; select.appendChild(option);
      });
      preview.appendChild(select);
      select.onchange = function () {
        render({ type: "state", version: 1, roomId: "1234", phase: select.value, category: "Science",
          categories: ["Science", "History", "Movies"], picker: "Quiz Wizards", round: 2, totalRounds: 5,
          question: { prompt: "Which planet is known as the Red Planet?", options: ["Venus", "Mars", "Jupiter", "Saturn"], answer: "Mars" },
          teams: [{ name: "Quiz Wizards", score: 180, locked: true, connected: true }, { name: "Brainstorm", score: 160, connected: true }],
          flip: 1, secondsRemaining: 8, points: 90 });
      };
      select.onchange();
      doc.getElementById("connection").textContent = "Browser preview · sample game";
      return;
    }
    var script = doc.createElement("script");
    script.src = "https://www.gstatic.com/cast/sdk/libs/caf_receiver/v3/cast_receiver_framework.js";
    script.onload = function () {
      try { connectReceiver(root.cast.framework.CastReceiverContext.getInstance(), root.cast.framework, doc); }
      catch (_) { doc.getElementById("connection").textContent = "Launch this page through Google Cast. For a browser preview, add ?preview=1 to the URL."; }
    };
    script.onerror = function () { doc.getElementById("connection").textContent = "Could not load Google Cast. Check the TV's internet connection and reconnect."; };
    doc.head.appendChild(script);
  }

  var api = { parseState: parseState, safeImageUrl: safeImageUrl, makeRenderer: makeRenderer, connectReceiver: connectReceiver, start: start };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.TriviaReceiver = api;
})(typeof window !== "undefined" ? window : globalThis);
