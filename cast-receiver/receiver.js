(function (root) {
  "use strict";
  var namespace = "urn:x-cast:com.example.triviaparty";
  var phases = ["LOBBY", "SUBJECT_VOTING", "CATEGORY_SELECT", "CATEGORY_INTRO", "WAGER_OPEN", "WAGER_RESULTS", "QUESTION_ACTIVE", "ANSWER_REVIEW", "REVEAL_ANSWER", "ROUND_SUMMARY", "GAME_ENDED"];

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

  function safeImageUrl(value, pageLocation) {
    if (typeof value !== "string") return null;
    try {
      var url = new URL(value);
      var currentLocation = pageLocation || root.location;
      var sameOriginHttp = url.protocol === "http:" && currentLocation && url.host === currentLocation.host;
      return url.protocol === "https:" || sameOriginHttp ? url.href : null;
    }
    catch (_) { return null; }
  }

  function makeSoundPlayer(doc, options) {
    options = options || {};
    var queued=[],audio, origin = options.localAudio && root.location ? root.location.origin : null, control = doc.getElementById('tv-audio-control'), enabled = false, attempt = 0;
    function stop() { queued=[];++attempt; if (audio) { audio.onended = null; if (audio.pause) audio.pause(); } }
    function report(error) {
      enabled = false;
      queued=[];
      if (!control) return;
      control.style.display = 'block';
      control.textContent = error && error.name !== 'NotAllowedError' ? 'Son indisponible · Réessayer' : 'Activer le son';
    }
    function play(file, remaining, continuing) {
      if (!root.Audio || !origin) return;
      if(!continuing) stop();
      var url = origin + '/tv/sounds/' + file;
      if (!audio) audio = new root.Audio(url); else audio.src = url;
      audio.volume = 1;
      audio.preload = 'auto';
      var thisAttempt = ++attempt;
      audio.onended = function () {
        if (thisAttempt !== attempt) return;
        var next=(remaining||[]).concat(queued);queued=[];
        if(next.length) play(next[0],next.slice(1),true);
      };
      try {
        var playback = audio.play();
        if (playback && playback.then) playback.then(function () {
          if (thisAttempt !== attempt) return;
          enabled = true;
          if (control) control.style.display = 'none';
        }).catch(function (error) { if (thisAttempt === attempt) report(error); });
        else { enabled = true; if (control) control.style.display = 'none'; }
      } catch (error) { report(error); }
    }
    if (control) {
      control.onclick = function () { play('enabled.wav'); };
      if (options.localAudio) { control.textContent = 'Activer le son'; control.style.display = 'block'; }
    }
    return {
      setOrigin: function (joinUrl) {
        try { origin = options.localAudio && root.location ? root.location.origin : new URL(joinUrl).origin; } catch (_) {}
      },
      play: play, playSequence: function (files) {
        if(!files.length) return;
        if(audio && audio.paused===false && enabled) queued=queued.concat(files);
        else play(files[0],files.slice(1));
      }, stop: stop,
      // Debug controls let the browser grant playback permission to this same element.
      enabled: function () { return enabled; }
    };
  }

  function makeRenderer(doc, options) {
    var lastSoundRoom = null, lastSoundId = null;
    var lastBuzzerId = null, soundPlayer = makeSoundPlayer(doc,options);
    var lastPhase = null;
    var feedbackTimeout, feedbackQuestion = null;
    var lastScene = "";
    var hourglass, topSand, bottomSand, sandStream, timerLabel;
    var lastTimerFlip = -1;
    var overlayGlass, overlayTop, overlayBottom, overlayStream, overlayLabel, overlayAnswer, overlayName;
    var displayedQuestionId = null, questionOptions = [], answerSlot, answerText, promptNode, questionLayout, questionDetails;
    var fitKey = '', layoutObserver;
    var scoreKey = '';
    var chronologyLines = [], chronologyPrompt = '', chronologyRevealed = false;
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
      items.forEach(function (item) {
        var option = node('li'); option.appendChild(node('span', item, 'choice-text')); list.appendChild(option);
      });
      parent.appendChild(list);
      return list;
    }
    function questionText(value) { return String(value || '').replace(/[ \t\r\n]+([?!;:])/g, '\u00a0$1'); }
    function setAnswer(value) {
      if (!answerText) return;
      answerText.textContent = questionText(value);
      answerSlot.style.backgroundColor = answerText.textContent ? '' : 'transparent';
      answerSlot.style.padding = answerText.textContent ? '' : '0';
    }
    function setPrompt(element, prompt) {
      element.sourcePrompt = prompt;
      var parts = (prompt || '').split(/\n+(?=\d+\.\s)/);
      if (parts.length < 2) { element.textContent = questionText(prompt); return; }
      clear(element); element.textContent = '';
      element.appendChild(node('span', questionText(parts[0]), 'clue-title'));
      parts.slice(1).forEach(function (clue) {
        element.appendChild(node('span', questionText(clue.replace(/^\d+\.\s*/, '')), 'clue-text'));
      });
    }
    // Older TV browsers may not support text-wrap: balance. Find the narrowest
    // text measure that retains the line count, leaving the surrounding panel fixed.
    function balanceLegacy(element) {
      if (root.CSS && root.CSS.supports && root.CSS.supports('text-wrap', 'balance')) return;
      if (!element || !element.getBoundingClientRect || !element.textContent.trim()) return;
      element.style.width = '';
      var bounds = element.getBoundingClientRect(), size = parseFloat(root.getComputedStyle(element).fontSize);
      if (!bounds.width || bounds.height < size * 1.5) return;
      var low = bounds.width * .35, high = bounds.width;
      for (var i = 0; i < 9; i++) {
        var width = (low + high) / 2; element.style.width = width + 'px';
        if (element.getBoundingClientRect().height <= bounds.height + 1) high = width; else low = width;
      }
      element.style.width = Math.min(bounds.width, Math.ceil(high) + 2) + 'px';
    }
    function fitLayout() {
      if (!questionLayout || !questionDetails || !root.getComputedStyle || !questionLayout.clientWidth) return;
      var key = JSON.stringify([promptNode.sourcePrompt, answerText.textContent, questionLayout.clientWidth, questionLayout.clientHeight]);
      if (key === fitKey) return;
      fitKey = key;
      var elements = Array.prototype.slice.call(questionDetails.querySelectorAll('h1, .clue-title, .clue-text, .options li, .chronology-line'));
      elements.forEach(function (element) { element.style.fontSize = ''; element.style.width = ''; });
      var sizes = elements.map(function (element) { return parseFloat(root.getComputedStyle(element).fontSize); });
      function apply(scale) { elements.forEach(function (element, i) { element.style.fontSize = sizes[i] * scale + 'px'; }); }
      function fits() { return questionDetails.scrollHeight <= questionDetails.clientHeight + 1 && questionDetails.scrollWidth <= questionDetails.clientWidth + 1; }
      if (!fits()) {
        var low = 0, high = 1;
        for (var i = 0; i < 10; i++) { var scale = (low + high) / 2; apply(scale); if (fits()) low = scale; else high = scale; }
        apply(low);
      }
      balanceLegacy(promptNode);
      Array.prototype.forEach.call(questionDetails.querySelectorAll('.choice-text'), balanceLegacy);
      if (answerText.textContent) {
        var style = root.getComputedStyle(answerSlot);
        var height = answerSlot.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
        var width = answerSlot.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
        var base = parseFloat(style.fontSize);
        answerText.style.fontSize = base + 'px'; answerText.style.width = '';
        function answerFits() { return answerText.scrollHeight <= height + 1 && answerText.scrollWidth <= width + 1; }
        if (!answerFits()) {
          var small = 1, large = base;
          for (var j = 0; j < 10; j++) {
            var font = (small + large) / 2; answerText.style.fontSize = font + 'px';
            if (answerFits()) small = font; else large = font;
          }
          answerText.style.fontSize = Math.floor(small * 10) / 10 + 'px';
        }
        balanceLegacy(answerText);
      }
    }
    if (root.addEventListener) root.addEventListener('resize', function () { fitKey = ''; fitLayout(); });
    function revealChronology(answer) {
      if (chronologyRevealed) return true;
      if (!chronologyLines.length) return false;
      var labels = (answer || '').replace(/^[A-D]\s*[)—.:-]\s*/, '').split('→').map(function (v) { return v.trim(); });
      if (labels.length !== chronologyLines.length) return false;
      function words(v) { return v.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().match(/[a-z0-9]+/g) || []; }
      // Package options can abbreviate the events. Compare every one-to-one assignment.
      var best = null, bestScore = -1, tied = false;
      function assign(order, remaining, score) {
        if (!remaining.length) {
          if (score > bestScore) { best = order; bestScore = score; tied = false; }
          else if (score === bestScore) tied = true;
          return;
        }
        var tokens = words(labels[order.length]);
        remaining.forEach(function (index) {
          var eventTokens = words(chronologyLines[index].textContent);
          var overlap = tokens.filter(function (token) { return eventTokens.indexOf(token) >= 0; }).length;
          if (!overlap) return;
          assign(order.concat(index), remaining.filter(function (v) { return v !== index; }), score + overlap / Math.max(tokens.length, 1));
        });
      }
      assign([], chronologyLines.map(function (_, i) { return i; }), 0);
      if (!best || tied) return false; // Never invent an ambiguous event ordering.
      chronologyRevealed = true;
      best.forEach(function (original, rank) {
        var line = chronologyLines[original];
        line.style.transform = 'translateY(' + ((rank - original) * 100) + '%)';
        line.className = 'chronology-line ranked';
        line.textContent = (rank + 1) + '. ' + line.textContent;
      });
      return true;
    }
    function visual(parent, question, reveal) {
      var url = safeImageUrl(question.imageUrl);
      if (!url) {
        if (!Array.isArray(question.mapOptions) || !question.mapOptions.length) return;
        var offlineMap = node("div", null, "visual map-fallback");
        offlineMap.appendChild(node("div", null, "map-land"));
        question.mapOptions.forEach(function (option) {
          if (!Number.isFinite(option.xRatio) || !Number.isFinite(option.yRatio)) return;
          var marker = node("span", option.label, "map-choice" + (reveal && question.answer === option.label ? " correct" : ""));
          marker.style.left = option.xRatio * 100 + "%";
          marker.style.top = option.yRatio * 100 + "%";
          offlineMap.appendChild(marker);
        });
        parent.appendChild(offlineMap);
        return;
      }
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
      soundPlayer.setOrigin(state.joinUrl);
      var feedback = doc.getElementById('answer-feedback');
      var feedbackKey = state.roomId + '/' + (state.question && state.question.id || state.round);
      if (lastSoundRoom !== state.roomId || feedbackQuestion !== feedbackKey || lastPhase !== state.phase && ['QUESTION_ACTIVE','ANSWER_REVIEW','REVEAL_ANSWER','ROUND_SUMMARY'].indexOf(state.phase)<0) {
        if (feedbackTimeout) root.clearTimeout(feedbackTimeout);
        feedback.style.display = 'none';
        if(lastSoundRoom !== state.roomId) soundPlayer.stop();
        feedbackQuestion = feedbackKey;
      }
      var sameSoundRoom = lastSoundRoom === state.roomId;
      if (!sameSoundRoom) { lastSoundRoom = state.roomId; lastSoundId = state.answerSoundId || 0; lastBuzzerId = state.buzzerSoundId || 0; }
      if (sameSoundRoom && lastPhase && lastPhase !== 'GAME_ENDED' && state.phase === 'GAME_ENDED') soundPlayer.play('game-end.wav');
      lastPhase = state.phase;
      if ((state.buzzerSoundId || 0) > lastBuzzerId) soundPlayer.play('buzzer.wav');
      lastBuzzerId = state.buzzerSoundId || 0;
      if ((state.answerSoundId || 0) > lastSoundId && ["good","bad"].indexOf(state.answerSound) >= 0) {
        if (feedbackTimeout) root.clearTimeout(feedbackTimeout);
        feedback.textContent = state.answerSound === 'good' ? '\u2713' : '\u2715';
        feedback.className = 'answer-feedback ' + state.answerSound;
        feedback.setAttribute('aria-label',state.answerSound === 'good' ? 'Bonne réponse' : 'Mauvaise réponse');
        feedback.style.display = 'flex';
        feedbackTimeout = root.setTimeout(function () { feedback.style.display = 'none'; },2200);
        try {
          var file = /^(good|bad)-\d{2}\.(wav|mp3)$/.test(state.answerSoundClip || '') && state.answerSoundClip.indexOf(state.answerSound + '-') === 0 ? state.answerSoundClip : state.answerSound + '.wav';
          soundPlayer.playSequence([state.answerSound + '-ping.wav',file]);
        } catch (_) {}
      }
      lastSoundId = state.answerSoundId || 0;
      text("category", state.phase === "SUBJECT_VOTING" ? "Choix des catégories" : state.category || "Salon");
      text("round", state.phase === "LOBBY" ? "" : state.phase === "SUBJECT_VOTING" ?
        state.subjectVote && state.subjectVote.hostTieBreak ? "Décision de l’hôte" : "Vote " + (state.subjectVote && state.subjectVote.round || 1) :
        "Question " + state.round + " sur " + state.totalRounds);
      var timer = doc.getElementById("timer");
      if (!hourglass) {
        clear(timer);
        hourglass = node("div", null, "hourglass");
        var glass = node("div", null, "hourglass-vessel");
        topSand = node("div", null, "sand-upper");
        bottomSand = node("div", null, "sand-lower");
        sandStream = node("div", null, "sand-stream");
        glass.appendChild(topSand); glass.appendChild(bottomSand); glass.appendChild(sandStream);
        hourglass.appendChild(glass); timer.appendChild(hourglass);
        timerLabel = node("span", null, "timer-label"); timer.appendChild(timerLabel);
      }
      var active = state.phase === "QUESTION_ACTIVE";
      var answering = active && Number.isFinite(state.answerSecondsRemaining);
      var duration = state.secondsPerFlip || 5;
      var seconds = state.secondsRemaining;
      var fraction = Math.max(0, Math.min(1, (Number(seconds) || 0) / Math.max(1, duration)));
      hourglass.style.display = active && !state.questionReading ? "" : "none";
      topSand.style.height = (fraction * 42) + "%";
      bottomSand.style.height = ((1 - fraction) * 42) + "%";
      sandStream.style.display = fraction > 0 && !state.timerPaused && !answering ? "" : "none";
      var timerFlip = state.flip;
      if (timerFlip !== lastTimerFlip) { hourglass.className = "hourglass " + (Number(state.flip) % 2 ? "turn-odd" : "turn-even"); lastTimerFlip = timerFlip; }
      timerLabel.textContent = !active ? "" : state.questionReading ? state.playersReadyReading ?
        'Prêts : '+state.readyCount+'/'+state.connectedCount : "Lecture · réponses fermées" :
        (state.pointsCountdown?'':seconds + " s · ") + state.points + " pts" + (state.timerPaused || answering ? " · Pause" : "");
      text("answering", state.phase==='ANSWER_REVIEW'?(state.answeringTeam?state.answeringTeam+' · Validation':'L’hôte valide les réponses écrites…'):active && state.answeringTeam ? state.answeringTeam + " À LA PAROLE" : "");
      var freeAnswer=state.question && ['BUZZER','WRITTEN'].indexOf(state.question.answerMode)>=0 || ['BUZZER','WRITTEN'].indexOf(state.categoryAnswerMode)>=0 || state.answeringTeam;
      doc.getElementById('answering').className=freeAnswer?'':'compact-status';
      var overlay = doc.getElementById("answer-overlay");
      if (!overlayGlass) {
        overlayName = node("div", null, "selected-player-name"); overlay.appendChild(overlayName);
        overlayGlass = node("div", null, "hourglass answer-hourglass");
        var vessel = node("div", null, "hourglass-vessel");
        overlayTop = node("div", null, "sand-upper"); overlayBottom = node("div", null, "sand-lower");
        overlayStream = node("div", null, "sand-stream");
        vessel.appendChild(overlayTop); vessel.appendChild(overlayBottom); vessel.appendChild(overlayStream);
        overlayGlass.appendChild(vessel); overlay.appendChild(overlayGlass);
        overlayLabel = node("div", null, "answer-countdown"); overlay.appendChild(overlayLabel);
        overlayAnswer = node("div", null, "submitted-answer"); overlay.appendChild(overlayAnswer);
      }
      var reviewing=state.phase==='ANSWER_REVIEW' && typeof state.submittedAnswer==='string';
      overlay.style.display = answering || reviewing ? "flex" : "none";
      doc.getElementById("scene").style.visibility=answering || reviewing ? "hidden" : "";
      overlayGlass.style.display=answering?"":"none";
      overlayAnswer.style.display=reviewing?"":"none";
      overlayAnswer.textContent=reviewing?state.submittedAnswer:"";
      overlayName.textContent=answering || reviewing ? state.answeringTeam || "" : "";
      overlay.className=reviewing && state.submittedAnswerResult!=null ? (state.submittedAnswerResult?"review-correct":"review-incorrect") : "";
      if(reviewing) text("answering",state.submittedAnswerResult===true?"Réponse acceptée":state.submittedAnswerResult===false?"Réponse refusée":"Validation de l’hôte");
      else if(answering) text("answering","À LA PAROLE");
      var answerFraction = Math.max(0, Math.min(1, (state.answerSecondsRemaining || 0) / Math.max(1, state.answerTimeSeconds || 10)));
      overlayTop.style.height = (answerFraction * 42) + "%"; overlayBottom.style.height = ((1 - answerFraction) * 42) + "%";
      overlayStream.style.display = answerFraction > 0 && !state.timerPaused ? "" : "none";
      overlayLabel.textContent = answering ? state.answerSecondsRemaining + " s" : "";
      var ranked = state.teams.slice().sort(function (a, b) { return b.score - a.score; });
      var nextScoreKey = JSON.stringify([ranked, state.answeringTeam, state.phase]);
      if (nextScoreKey !== scoreKey) {
        scoreKey = nextScoreKey;
        var scores = doc.getElementById("scores"); clear(scores); scores.style.display = "";
        ranked.forEach(function (team) {
          var resultPhase = ['QUESTION_ACTIVE','ANSWER_REVIEW','REVEAL_ANSWER','ROUND_SUMMARY'].indexOf(state.phase) >= 0;
          var result = team.answerResult;
          if (result == null && state.phase !== 'QUESTION_ACTIVE' && team.correct === true) result = true;
          var card = node("div", null, "team" + (state.phase === "GAME_ENDED" ? " podium-" + Math.min(4, 1 + ranked.filter(function (other) { return other.score > team.score; }).length) : "") + (state.answeringTeam === team.name ? " answering-team" : "") + (resultPhase && result === true ? " correct-team" : resultPhase && result === false ? " incorrect-team" : ""));
          var colorIndex=Number.isFinite(team.colorIndex)?team.colorIndex:state.teams.indexOf(team);
          var hue=(colorIndex*137.508+205)%360;
          card.style.borderLeft='6px solid hsl('+hue+',65%,60%)';
          if(!resultPhase || result==null) if(state.phase!=='GAME_ENDED' && state.answeringTeam!==team.name) card.style.backgroundColor='hsl('+hue+',38%,26%)';
          var rank = 1 + ranked.filter(function (other) { return other.score > team.score; }).length;
          card.appendChild(node("span", rank + ". " + team.name)); card.appendChild(node("b", team.score + " pts"));
          if (team.connected === false) card.appendChild(node("small", "Hors ligne"));
          scores.appendChild(card);
        });
      }
      // Timer ticks must not reload images or reset the scene's scroll position.
      var isQuestion = ["QUESTION_ACTIVE", "ANSWER_REVIEW", "REVEAL_ANSWER", "ROUND_SUMMARY"].indexOf(state.phase) >= 0;
      var qid = state.question && (state.question.id || state.question.imageUrl || "legacy-question");
      var reveal = ["REVEAL_ANSWER","ROUND_SUMMARY"].indexOf(state.phase)>=0;
      if (reveal && displayedQuestionId === qid && answerSlot) {
        var correct = state.question.answer;
        if (revealChronology(correct)) { fitLayout(); return; }
        if (questionOptions.length && (Number.isInteger(state.question.correctOptionIndex) || questionOptions.some(function (option) { return option.textContent === correct; }))) {
          questionOptions.forEach(function (option, index) {
            var good = Number.isInteger(state.question.correctOptionIndex) ? index === state.question.correctOptionIndex : option.textContent === correct;
            option.className = good ? "correct-choice" : "wrong-choice";
          });
        } else setAnswer(correct);
        fitLayout();
        return;
      }
      if (active && displayedQuestionId === qid && promptNode) {
        if (!chronologyLines.length && promptNode.sourcePrompt !== state.question.prompt) setPrompt(promptNode, state.question.prompt);
        fitLayout();
        return;
      }
      var sceneKey = isQuestion ? JSON.stringify([state.roomId, qid, state.question.prompt, state.question.imageUrl]) :
        JSON.stringify([state.roomId, state.phase, state.categories, state.subjectVote, state.picker, state.wagerResults, state.joinUrl, state.joinQrUrl, state.phase === "LOBBY" ? state.teams.length : null]);
      if (sceneKey === lastScene) return;
      lastScene = sceneKey;
      var scene = doc.getElementById("scene");
      clear(scene);
      scene.className = state.phase === "WAGER_RESULTS" ? "wager-results-scene" : "";
      if (layoutObserver) layoutObserver.disconnect();
      displayedQuestionId = null; questionOptions = []; answerSlot = null; answerText = null;
      questionLayout = null; questionDetails = null; fitKey = '';
      chronologyLines = []; chronologyRevealed = false;
      switch (state.phase) {
        case "SUBJECT_VOTING":
          var vote = state.subjectVote;
          if (vote) {
            scene.appendChild(node("h1", vote.hostTieBreak ? "L’hôte départage les sujets" : vote.round === 1 ? "Vote des catégories" : "Second vote · égalités"));
            if (vote.selected.length) scene.appendChild(node("p", "Déjà retenus : " + vote.selected.join(" · ")));
            scene.appendChild(node("p", vote.slots + (vote.slots === 1 ? " place" : " places") + " · " + vote.ballots +
              (vote.ballots === 1 ? " équipe a voté" : " équipes ont voté")));
            var voteGrid = node("div", null, "subject-vote-grid");
            vote.candidates.slice().sort(function (a,b) { return vote.totals[b] - vote.totals[a]; }).forEach(function (subject) {
              voteGrid.appendChild(node("div", subject + " · " + vote.totals[subject] + (vote.totals[subject] === 1 ? " vote" : " votes"), "subject-vote-card"));
            });
            scene.appendChild(voteGrid);
            scene.appendChild(node("p", vote.hostTieBreak ? "Égalité persistante : choix de l’hôte" : "Votez sur votre téléphone"));
          }
          break;
        case "WAGER_OPEN":
          scene.appendChild(node("h1", state.category || "Nouvelle catégorie"));
          scene.appendChild(node("p", "Choisissez votre mise sur votre téléphone · Première question uniquement"));
          break;
        case "WAGER_RESULTS":
          scene.appendChild(node("h1", "Résultats des mises"));
          var wagerGrid = node("div", null, "wager-grid");
          (state.wagerResults || []).slice().sort(function (a, b) { return b.delta - a.delta; }).forEach(function (result) {
            wagerGrid.appendChild(node("p", result.teamName + " · Mise : " + result.amount + " · " +
              (result.amount === 0 ? "Aucune mise" : result.correct ? "Gagnée" : "Perdue") + " · " +
              (result.delta > 0 ? "+" : "") + result.delta + " pts", result.delta > 0 ? "wager-gain" : result.delta < 0 ? "wager-loss" : "wager-zero"));
          });
          scene.appendChild(wagerGrid);
          break;
        case "LOBBY":
          scene.appendChild(node("h1", state.subjectVote && state.subjectVote.completed ? "Sujets retenus" : "Rejoignez la partie !"));
          if (state.subjectVote && state.subjectVote.completed) scene.appendChild(node("p", state.subjectVote.selected.join(" · ")));
          var qrUrl = safeImageUrl(state.joinQrUrl);
          if (qrUrl) {
            var qr = node("img", null, "join-qr"); qr.src = qrUrl; qr.alt = "Code QR pour rejoindre la partie";
            scene.appendChild(qr);
          }
          scene.appendChild(node("p", "Même Wi-Fi que l’hôte · Scannez et jouez"));
          if (state.joinUrl) scene.appendChild(node("p", state.joinUrl, "join-url"));
          scene.appendChild(node("p", state.teams.length + (state.teams.length === 1 ? " équipe prête" : " équipes prêtes")));
          break;
        case "CATEGORY_SELECT":
          scene.appendChild(node("h1", (state.picker || "Le joueur en tête") + " choisit une catégorie"));
          choices(scene, state.categories);
          break;
        case "CATEGORY_INTRO":
          scene.appendChild(node("h1", state.category || "Nouvelle catégorie"));
          scene.appendChild(node("p", (state.categoryQuestionCount || 0) + " questions"));
          scene.appendChild(node("p", "Types : " + (state.categoryQuestionTypes || []).join(" · ")));
          scene.appendChild(node("p", "Mode : " + (state.categoryAnswerMode === "WRITTEN" ? "Réponses écrites" : state.categoryAnswerMode === "BUZZER" ? "Buzzer" : "Réponses simultanées")));
          break;
        case "QUESTION_ACTIVE":
        case "ANSWER_REVIEW":
        case "REVEAL_ANSWER":
        case "ROUND_SUMMARY":
          var question = state.question;
          if (question) {
            displayedQuestionId = qid;
            var hasVisual = safeImageUrl(question.imageUrl) || question.mapOptions && question.mapOptions.length;
            var imageBuzzer = hasVisual && (['BUZZER','WRITTEN'].indexOf(question.answerMode)>=0 || ['BUZZER','WRITTEN'].indexOf(state.categoryAnswerMode)>=0);
            var layout = node("div", null, hasVisual ? imageBuzzer ? "question-layout image-buzzer" : "question-layout with-visual" : "question-layout");
            var progressiveClues = /\n\n1\.\s/.test(question.prompt || "");
            var details = node("div", null, progressiveClues ? "question-details progressive-clues" : "question-details");
            var events = (question.prompt || '').split('\n').filter(function (line) { return /^\s*•/.test(line); });
            var chronology = events.length >= 2 && !question.options.length;
            promptNode = node("h1"); setPrompt(promptNode, chronology ? question.prompt.split('\n')[0] : question.prompt); details.appendChild(promptNode);
            if (chronology) {
              details.className += ' chronology-details';
              var eventList = node('div', null, 'chronology-events');
              events.forEach(function (event) {
                var line = node('div', event.replace(/^\s*•\s*/, ''), 'chronology-line');
                chronologyLines.push(line); eventList.appendChild(line);
              });
              details.appendChild(eventList);
            }
            if (hasVisual) {
              var imagePanel = node("div", null, "image-panel"); visual(imagePanel, question, reveal); layout.appendChild(imagePanel);
            }
            if (question.options.length) {
              var list = choices(details, question.options);
              questionOptions = Array.prototype.slice.call(list.children);
              if (reveal && (Number.isInteger(question.correctOptionIndex) || question.options.indexOf(question.answer) >= 0)) questionOptions.forEach(function (option, index) {
                option.className = (Number.isInteger(question.correctOptionIndex) ? index === question.correctOptionIndex : option.textContent === question.answer) ? "correct-choice" : "wrong-choice";
              });
            }
            answerSlot = node("p", null, "answer answer-slot");
            answerText = node("span", null, "answer-text"); answerSlot.appendChild(answerText);
            setAnswer(reveal && (!questionOptions.length || !Number.isInteger(question.correctOptionIndex) && question.options.indexOf(question.answer) < 0) ? question.answer : '');
            details.appendChild(answerSlot);
            layout.appendChild(details); scene.appendChild(layout);
            if (reveal && chronologyLines.length && revealChronology(question.answer)) setAnswer('');
            questionLayout = layout; questionDetails = details; fitLayout();
            if (root.ResizeObserver) { layoutObserver = new root.ResizeObserver(fitLayout); layoutObserver.observe(layout); }
          }
          break;
        case "GAME_ENDED":
          scene.appendChild(node("h1", "Classement final", "final-title"));
          var best = Math.max.apply(null, state.teams.map(function (team) { return team.score; }));
          var winners = state.teams.filter(function (team) { return team.score > 0 && team.score === best; });
          scene.appendChild(node("p", winners.length ? "Gagnant" + (winners.length > 1 ? "s : " : " : ") +
            winners.map(function (team) { return team.name; }).join(" et ") : "Merci d’avoir joué !", "winner-line"));
          var podium = node("div", null, "final-podium");
          ranked.forEach(function (team) {
            var rank = 1 + ranked.filter(function (other) { return other.score > team.score; }).length;
            if (rank <= 3) podium.appendChild(node("p", rank + ". " + team.name + " · " + team.score + " pts", "podium-" + rank));
          });
          scene.appendChild(podium);
          break;
      }
    };
  }

  function connectReceiver(context, framework, doc) {
    var render = makeRenderer(doc);
    function ready(senderId) { context.sendCustomMessage(namespace, senderId, { type: "ready", version: 1 }); }
    context.addCustomMessageListener(namespace, function (event) {
      var state = parseState(event.data);
      if (!state) return;
      render(state);
      doc.getElementById("connection").textContent = "Connecté à l’hôte";
    });
    context.addEventListener(framework.system.EventType.READY, function () {
      context.getSenders().forEach(function (sender) { ready(sender.senderId); });
    });
    context.addEventListener(framework.system.EventType.SENDER_CONNECTED, function (event) { ready(event.senderId); });
    context.addEventListener(framework.system.EventType.SENDER_DISCONNECTED, function () {
      if (!context.getSenders().length) doc.getElementById("connection").textContent = "Hôte déconnecté. Reconnectez depuis le téléphone.";
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

  var api = { parseState: parseState, safeImageUrl: safeImageUrl, makeSoundPlayer: makeSoundPlayer, makeRenderer: makeRenderer, connectReceiver: connectReceiver, start: start };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.TriviaReceiver = api;
})(typeof window !== "undefined" ? window : globalThis);
