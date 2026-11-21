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

  function safeImageUrl(value, pageLocation, allowedOrigin) {
    if (typeof value !== "string") return null;
    if (value.indexOf("data:image/") === 0) return value;
    try {
      var url = new URL(value);
      var currentLocation = pageLocation || root.location;
      // The published receiver page is HTTPS, but Cast permits its media
      // resources to come from HTTP. Keep the phone's LAN URL so the TV can
      // fetch game media directly without a computer-side HTTPS relay.
      var sameOriginHttp = url.protocol === "http:" && (currentLocation && url.host === currentLocation.host || allowedOrigin && url.origin === allowedOrigin);
      return url.protocol === "https:" || sameOriginHttp ? url.href : null;
    }
    catch (_) { return null; }
  }

  // Display format metadata once, separate from the subject and subtitle.
  function categoryPresentation(state) {
    function key(value) { return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[?!.]/g, '').replace(/\s+/g, ' ').trim(); }
    var formats = [], titleParts = [];
    // Imported names also append compound formats, e.g. "Qui suis-je écrit".
    var formatSuffix = /(?:^|\s+(?:[-–—]\s*)?)(qui\s+suis[-–—\s]+je\s*\??(?:\s*(?:[-–—]\s*)?(?:[ée]crit(?:e|es|s)?|oral(?:e|es|s)?|au buzzer))?|qcm|choix multiples|buzzer|chronologie|r[ée]ponses? [ée]crites?|r[ée]ponses? simultan[ée]es)\s*$/i;
    (state.category || '').split(/\s+[-–—]\s+/).filter(Boolean).forEach(function (part) {
      var match;
      while ((match = formatSuffix.exec(part))) {
        var label = match[1];
        formats.push(/^qui\s+suis/i.test(label) ? 'Qui suis-je ?' : key(label) === 'qcm' ? 'Choix multiples' : label.trim());
        part = part.slice(0, match.index).trim();
      }
      if (part) {
        // A numbered edition belongs to its preceding title, even across a dash.
        if (/^\d+$/.test(part) && titleParts.length) titleParts[titleParts.length - 1] += '\u00a0' + part;
        else titleParts.push(part.replace(/(\S)\s+(\d+)$/, '$1\u00a0$2'));
      }
    });
    var mode = state.categoryAnswerMode === 'WRITTEN' ? 'Réponses écrites' : state.categoryAnswerMode === 'BUZZER' ? 'Buzzer' : 'Réponses simultanées';
    var modeKeys = state.categoryAnswerMode === 'WRITTEN' ? ['reponse ecrite','reponses ecrites'] : [key(mode)];
    var seen = [], types = [];
    (state.categoryQuestionTypes || []).concat(formats).forEach(function (type) {
      if (typeof type !== 'string' || !type.trim()) return;
      type = type.replace(/\s+[–—-]\s+réponse écrite$/i, '').trim();
      if (/^qui\s+suis[-–—\s]+je/i.test(type)) type = 'Qui suis-je ?';
      var normalized = key(type);
      if (modeKeys.indexOf(normalized) >= 0 || seen.indexOf(normalized) >= 0) return;
      seen.push(normalized); types.push(type);
    });
    return { titleParts: titleParts.length ? titleParts : ['Nouvelle catégorie'], types: types, mode: mode };
  }

  function stopImageReveal(canvas) {
    if (!canvas) return;
    canvas._stopped = true;
    if (canvas._animationFrame) root.cancelAnimationFrame(canvas._animationFrame);
    canvas._animationFrame = 0;
  }

  function applyImageReveal(wrapper, image, question, answerRevealed, latestState) {
    // An image request can finish after the next question has replaced its
    // scene. Never start an animation for a detached, obsolete question.
    if (!wrapper || !image || !document.documentElement.contains(wrapper)) return;
    var mode = question.imageRevealMode;
    // The host may publish the question and its image mode in adjacent state
    // updates. The music mode is already authoritative for image QSJ, so mask
    // the source image on the first render instead of flashing it unpixelated.
    if ((!mode || mode === "NONE") && latestState && latestState.inRoundMusicMode === "IMAGE_GUESS_WHO") mode = "PIXELATE";
    if ((mode !== "PIXELATE" && mode !== "BLUR" && mode !== "SHUFFLE" && mode !== "UNCOVER") || answerRevealed) return;
    // A later state tick may arrive before a slow image request finishes.
    // Never create/hide behind a zero-sized canvas; let image.onload start it.
    if (!image || !image.complete || !image.naturalWidth || !image.naturalHeight) return;
    var steps = Math.max(2, Number(question.imageRevealSteps) || 5);
    var state = latestState || { question: question, flip: Number(question.imageRevealStep) || 0, secondsRemaining: 32, secondsPerFlip: 32 };
    var canvas = wrapper.querySelector("canvas.progressive-image");
    if (canvas) {
      if (canvas._revealMode !== mode) {
        stopImageReveal(canvas);
        canvas.remove(); canvas = null;
      }
    }
    if (canvas) {
      canvas._latestState = state;
      canvas._stateUpdatedAt = root.performance ? root.performance.now() : Date.now();
      // Reuse the renderer closure created with this canvas. A fresh call to
      // applyImageReveal has no access to that closure's canvas/context state.
      if (!canvas._animationFrame && canvas._draw) canvas._animationFrame = root.requestAnimationFrame(canvas._draw);
      return;
    }
    canvas = document.createElement("canvas");
    var context = canvas.getContext("2d");
    if (!context) return;
    canvas.className = "progressive-image";
    canvas.setAttribute("aria-label", "Image partiellement r\u00e9v\u00e9l\u00e9e");
    canvas._latestState = state;
    canvas._revealMode = mode;
    canvas._stateUpdatedAt = root.performance ? root.performance.now() : Date.now();
    // Match the sampler's output backing size. CSS expands this to the TV panel.
    canvas.width = Math.min(1000, image.naturalWidth || 1000);
    canvas.height = Math.max(1, Math.round(canvas.width * image.naturalHeight / image.naturalWidth));
    image.hidden = true;
    wrapper.insertBefore(canvas, image);

    function seeded(seed) {
      var value = seed >>> 0;
      return function () { value = (value * 1664525 + 1013904223) >>> 0; return value / 4294967296; };
    }
    function permutation(count, seed) {
      var random = seeded(seed), values = Array.from({ length: count }, function (_, index) { return index; });
      for (var i = values.length - 1; i > 0; i--) {
        var j = Math.floor(random() * (i + 1)), temp = values[i]; values[i] = values[j]; values[j] = temp;
      }
      return values;
    }
    var imageSeed = String(question.id || "image").split("").reduce(function (value, character) {
      return (value * 31 + character.charCodeAt(0)) >>> 0;
    }, 7);
    var tileCols = mode === "SHUFFLE" ? 20 : 32, tileRows = mode === "SHUFFLE" ? 15 : 24;
    var totalTiles = tileCols * tileRows;
    var initialShuffle = mode === "SHUFFLE" ? permutation(totalTiles, imageSeed) : null;
    var fixOrder = mode === "SHUFFLE" ? permutation(totalTiles, imageSeed ^ 0x9e3779b9) : null;
    var fixSwaps = [];
    if (mode === "SHUFFLE") {
      var probe = initialShuffle.slice();
      for (var fixedIndex = 0; fixedIndex < totalTiles; fixedIndex++) {
        var place = fixOrder[fixedIndex], found = probe.indexOf(place);
        fixSwaps.push([place, found]);
        if (found !== place) { var swap = probe[place]; probe[place] = probe[found]; probe[found] = swap; }
      }
    }
    var revealOrder = mode === "UNCOVER" ? permutation(totalTiles, imageSeed ^ 0x517cc1b7) : null;
    function draw() {
      canvas._animationFrame = 0;
      if (canvas._stopped) return;
      var current = canvas._latestState || state;
      var currentFlip = Math.max(0, Number(current.question && current.question.imageRevealStep) || 0);
      var hasCurrentRemaining = current.secondsRemaining !== null && current.secondsRemaining !== undefined && Number.isFinite(Number(current.secondsRemaining));
      var duration = Math.max(1, Number(current.secondsPerFlip) || 32);
      var currentRemaining = hasCurrentRemaining ? Math.max(0, Math.min(duration, Number(current.secondsRemaining))) : duration;
      var now = root.performance ? root.performance.now() : Date.now();
      var elapsedInFlip = Math.min(duration, Math.max(0, duration - currentRemaining) + (current.timerPaused ? 0 : Math.max(0, now - canvas._stateUpdatedAt) / 1000));
      var currentRevealDuration = Math.max(0, Number(current.imageRevealDurationSeconds) || 0);
      var progress = currentRevealDuration > 0 ? Math.min(1, elapsedInFlip / currentRevealDuration) : Math.min(1, (currentFlip + elapsedInFlip / duration) / steps);
      if (current.phase === "QUESTION_ACTIVE" || current.phase === "ANSWER_REVIEW") progress = Math.min(.999, progress);
      if (progress >= 1) progress = 0.999;
      if (mode !== "PIXELATE") context.clearRect(0, 0, canvas.width, canvas.height);
      if (mode === "PIXELATE") {
        var pixelLimit = Math.min(60, canvas.width), limitProgress = 0.65;
        // Fewer source samples make the opening mosaic blocks visibly larger.
        var pixelStart = Math.min(4, pixelLimit);
        var pixelSpan = Math.max(1, canvas.width - pixelStart);
        var revealTail = Math.max(0, (progress - limitProgress) / (1 - limitProgress));
        var resolution = progress <= limitProgress
          ? ((pixelLimit - pixelStart) * progress / limitProgress) / pixelSpan
          : (pixelLimit - pixelStart + (canvas.width - pixelLimit) * (0.1 * revealTail + 0.9 * Math.pow(revealTail, 2.5))) / pixelSpan;
        var pixelWidth = Math.max(pixelStart, Math.min(canvas.width, Math.round(pixelStart + pixelSpan * resolution)));
        // Keep a fixed-size buffer and draw into a variable-width region. This
        // matches the sampler's one-pixel progression without resizing a canvas
        // every frame (which can flash black on TV compositors). Never render
        // the full-resolution source until the answer is explicitly revealed.
        pixelWidth = progress >= 1 ? canvas.width : Math.min(canvas.width - 1, Math.max(pixelStart, pixelWidth));
        var small = canvas._pixelBuffer || (canvas._pixelBuffer = document.createElement("canvas"));
        if (small.width !== canvas.width) small.width = canvas.width;
        var smallHeight = Math.max(1, Math.round(pixelWidth * canvas.height / canvas.width));
        if (small.height !== canvas.height) small.height = canvas.height;
        var smallContext = small.getContext("2d");
        if (!smallContext) return;
        smallContext.imageSmoothingEnabled = true;
        smallContext.drawImage(image, 0, 0, pixelWidth, smallHeight);
        context.imageSmoothingEnabled = false;
        context.drawImage(small, 0, 0, pixelWidth, smallHeight, 0, 0, canvas.width, canvas.height);
        context.imageSmoothingEnabled = true;
      } else if (mode === "BLUR") {
        context.filter = "blur(" + (Math.pow(1 - progress, 2.2) * 88 * canvas.width / 720) + "px)";
        context.drawImage(image, 0, 0, canvas.width, canvas.height); context.filter = "none";
      } else if (mode === "SHUFFLE") {
        var mapping = initialShuffle.slice(), fixedCount = Math.floor(totalTiles * progress);
        for (var j = 0; j < fixedCount; j++) {
          var pair = fixSwaps[j], left = pair[0], right = pair[1];
          if (left !== right) { var temp = mapping[left]; mapping[left] = mapping[right]; mapping[right] = temp; }
        }
        var sourceWidth = image.naturalWidth / tileCols, sourceHeight = image.naturalHeight / tileRows;
        for (var cell = 0; cell < totalTiles; cell++) {
          var source = mapping[cell];
          context.drawImage(image, (source % tileCols) * sourceWidth, Math.floor(source / tileCols) * sourceHeight, sourceWidth + 1, sourceHeight + 1,
            (cell % tileCols) * canvas.width / tileCols, Math.floor(cell / tileCols) * canvas.height / tileRows, canvas.width / tileCols + 0.5, canvas.height / tileRows + 0.5);
        }
      } else {
        context.fillStyle = "#11111d"; context.fillRect(0, 0, canvas.width, canvas.height);
        var count = Math.floor(totalTiles * progress);
        for (var k = 0; k < count; k++) {
          var tile = revealOrder[k], col = tile % tileCols, row = Math.floor(tile / tileCols);
          var sx = Math.floor(col * image.naturalWidth / tileCols), sy = Math.floor(row * image.naturalHeight / tileRows);
          context.drawImage(image, sx, sy, Math.ceil(image.naturalWidth / tileCols), Math.ceil(image.naturalHeight / tileRows),
            Math.floor(col * canvas.width / tileCols), Math.floor(row * canvas.height / tileRows), Math.ceil(canvas.width / tileCols), Math.ceil(canvas.height / tileRows));
        }
      }
      if (!canvas._stopped && !current.timerPaused && current.phase === "QUESTION_ACTIVE") canvas._animationFrame = root.requestAnimationFrame(draw);
    }
    canvas._draw = draw;
    // Paint the initial obscured frame synchronously so the source image never
    // flashes and the display never briefly shows a blank/black canvas.
    draw();
  }

  function makeSoundPlayer(doc, options) {
    options = options || {};
    var audioVersion=null;
    var buzzerContext=null,buzzerBuffer=null,buzzerSource=null,buzzerKey=null;
    function resumeBuzzer() {
      if(buzzerContext && buzzerContext.resume) {
        try { var resumed=buzzerContext.resume();if(resumed && resumed.catch) resumed.catch(function(){}); } catch(_) {}
      }
    }
    // Decode the short cue while players are joining, rather than fetching it on a press.
    function warmBuzzer() {
      var Context=root.AudioContext || root.webkitAudioContext;
      if(!origin || !Context || !root.fetch) return;
      var key=origin+'/tv/sounds/buzzer.wav'+(audioVersion?'?v='+encodeURIComponent(audioVersion):'');
      if(key===buzzerKey) return;
      buzzerKey=key;buzzerBuffer=null;
      try {
        if(!buzzerContext) buzzerContext=new Context({latencyHint:'interactive'});
        root.fetch(key).then(function(response){if(!response.ok)throw new Error('Buzzer unavailable');return response.arrayBuffer();})
          .then(function(bytes){return buzzerContext.decodeAudioData(bytes);})
          .then(function(buffer){if(buzzerKey===key)buzzerBuffer=buffer;})
          .catch(function(){if(buzzerKey===key)buzzerKey=null;});
        resumeBuzzer();
      } catch(_) {buzzerKey=null;}
    }
    // Only the most recently activated debug display may play audio. Cast is independent.
    var debugOwner=true, channel=null, ownerId=String(Date.now())+'-'+Math.random();
    if(options.localAudio && root.BroadcastChannel) {
      channel=new root.BroadcastChannel('triviaparty-debug-audio');
      if(channel.unref) channel.unref();
      channel.onmessage=function(event) {
        if(event.data && event.data.type==='claim' && event.data.owner!==ownerId) {
          debugOwner=false; enabled=false; stop();
          if(control) { control.style.display='block'; control.textContent='Activer le son ici'; }
        }
      };
    }
    // The Cast receiver itself is served by the phone's local web server, so
    // its origin is already valid before the first game-state message arrives.
    // This lets the sound check at Cast startup fetch its MP3 without waiting
    // for the host's first state broadcast.
    var queued=[],audio, origin = root.location && root.location.protocol !== 'https:' ? root.location.origin : null, control = doc.getElementById('tv-audio-control'), enabled = !options.localAudio, attempt = 0, controlTimeout=null;
    var anitraMusicUrl='/tv/music/anitra-dance.mp3';
    var catMusicUrl='/tv/music/cat-theme.mp3';
    var desiredMusic=null, activeMusicKey=null, musicCue=null, musicBed=null, musicToken=0, musicTimer=null, musicPaused=false;
    var warmedAnitra=null, musicAssetOrigin=null;
    function fadeMusic(player,target,milliseconds,token,done) {
      if(!player)return; var start=player.volume,begin=Date.now(),duration=Math.max(100,milliseconds);
      function step(){if(token!==musicToken)return;var t=Math.min(1,(Date.now()-begin)/duration);player.volume=Math.max(0,Math.min(1,start+(target-start)*t));
        if(t<1)root.requestAnimationFrame(step);else if(done)done();}
      root.requestAnimationFrame(step);
    }
    function playMusicMedia(player,token){
      try {
        var playback=player.play();
        if(playback&&playback.then)playback.then(function(){if(token!==musicToken)return;if(options.onAudioStatus)options.onAudioStatus('playing');if(controlTimeout){root.clearTimeout(controlTimeout);controlTimeout=null;}if(control)control.style.display='none';})
          .catch(function(error){if(token===musicToken)report(error,true);});
      } catch(error) { if(token===musicToken)report(error,true); }
    }
    function pauseMusic(){if(musicTimer){root.clearTimeout(musicTimer);musicTimer=null;}musicPaused=true;[musicCue,musicBed].forEach(function(player){if(player)player.pause();});}
    function stopMusic(fadeMs){
      var token=++musicToken;if(musicTimer){root.clearTimeout(musicTimer);musicTimer=null;}activeMusicKey=null;musicPaused=false;
      [musicCue,musicBed].forEach(function(player){if(!player)return;if(fadeMs)fadeMusic(player,0,fadeMs,token,function(){player.pause();player.currentTime=0;player.playbackRate=1;});else{player.pause();player.currentTime=0;player.volume=0;player.playbackRate=1;}});
    }
    function startMusicBed(token){
      if(token!==musicToken||!desiredMusic||desiredMusic.mode!=='GUESS_WHO')return;
      var oldBed=musicBed,base=origin||(root.location&&root.location.origin)||'';musicBed=musicBed||new root.Audio(base+catMusicUrl);musicBed.preload='auto';musicBed.pause();musicBed.currentTime=0;musicBed.volume=0;
      musicBed.onerror=function(){if(token===musicToken)report({name:'MediaError',code:musicBed.error&&musicBed.error.code},true);};
      playMusicMedia(musicBed,token);
      fadeMusic(musicBed,.18,800,token);fadeMusic(musicCue,0,800,token,function(){if(musicCue){musicCue.pause();musicCue.currentTime=0;}});
      if(oldBed&&oldBed!==musicBed)fadeMusic(oldBed,0,400,token,function(){oldBed.pause();oldBed.currentTime=0;});
    }
    function startMusic(request){
      var token=++musicToken,oldCue=musicCue,oldBed=musicBed;if(musicTimer){root.clearTimeout(musicTimer);musicTimer=null;}
      activeMusicKey=request.key;musicPaused=false;
      var base=origin||(root.location&&root.location.origin)||'';
      if(request.mode==='IMAGE_GUESS_WHO'){
        musicCue=musicCue||warmedAnitra||new root.Audio(base+anitraMusicUrl);warmedAnitra=null;musicCue.preload='auto';musicCue.pause();musicCue.currentTime=0;musicCue.playbackRate=1;musicCue.volume=0;
        musicCue.onerror=function(){if(token===musicToken)report({name:'MediaError',code:musicCue.error&&musicCue.error.code},true);};
        playMusicMedia(musicCue,token);fadeMusic(musicCue,.26,650,token);
        [oldCue,oldBed].forEach(function(player){if(player&&player!==musicCue)fadeMusic(player,0,650,token,function(){player.pause();player.currentTime=0;player.playbackRate=1;});});
        musicTimer=root.setTimeout(function(){if(token===musicToken)fadeMusic(musicCue,0,850,token,function(){musicCue.pause();musicCue.currentTime=0;});},Math.max(0,(Math.max(.85,Number(request.duration)||32)-.85)*1000));
        return;
      }
      musicCue=musicCue||warmedAnitra||new root.Audio(base+anitraMusicUrl);warmedAnitra=null;musicCue.preload='auto';musicCue.pause();musicCue.currentTime=0;musicCue.playbackRate=1;musicCue.volume=0;
      musicCue.onerror=function(){if(token===musicToken)report({name:'MediaError',code:musicCue.error&&musicCue.error.code},true);};
      playMusicMedia(musicCue,token);fadeMusic(musicCue,.26,650,token);
      [oldCue,oldBed].forEach(function(player){if(player&&player!==musicCue){if(request.speedUp)player.playbackRate=1.8;fadeMusic(player,0,request.speedUp?1000:650,token,function(){player.pause();player.currentTime=0;player.playbackRate=1;});}});
      if(request.mode==='GUESS_WHO')musicTimer=root.setTimeout(function(){startMusicBed(token);},4125);
      else musicTimer=root.setTimeout(function(){if(token===musicToken)fadeMusic(musicCue,0,850,token,function(){musicCue.pause();musicCue.currentTime=0;});},Math.max(500,(request.duration-.5)*1000));
    }
    function syncMusic(request){
      desiredMusic=request;
      if(!enabled)return;
      if(!request||!request.mode){if(activeMusicKey)stopMusic(200);return;}
      if(request.paused){if(!musicPaused)pauseMusic();return;}
      if(activeMusicKey!==request.key){startMusic(request);return;}
      if(musicPaused){musicPaused=false;[musicCue,musicBed].forEach(function(player){if(player&&!player.ended)playMusicMedia(player,musicToken);});
        if(request.mode==='GUESS_WHO'&&!musicBed&&musicCue)musicTimer=root.setTimeout(function(){startMusicBed(musicToken);},Math.max(0,(4.125-musicCue.currentTime)*1000));
        else if(request.mode==='IMAGE_GUESS_WHO'&&musicCue)musicTimer=root.setTimeout(function(){fadeMusic(musicCue,0,850,musicToken,function(){musicCue.pause();musicCue.currentTime=0;});},Math.max(0,(request.duration-musicCue.currentTime-.85)*1000));
        else if(request.mode!=='GUESS_WHO'&&musicCue)musicTimer=root.setTimeout(function(){fadeMusic(musicCue,0,850,musicToken,function(){musicCue.pause();musicCue.currentTime=0;});},Math.max(500,(request.duration-musicCue.currentTime-.5)*1000));}
    }
    function stopAnswer() { queued=[];++attempt; if(buzzerSource){try{buzzerSource.stop();}catch(_){}buzzerSource=null;} if (audio) { audio.onended = null; if (audio.pause) audio.pause(); } }
    function stop() { stopAnswer(); stopMusic(350); }
    function primeMusicPlayers() {
      if(!root.Audio || desiredMusic) return;
      var base=origin||(root.location&&root.location.origin)||'';
      if(!musicCue) { musicCue=warmedAnitra||new root.Audio(base+anitraMusicUrl); warmedAnitra=null; }
      if(!musicBed) musicBed=new root.Audio(base+catMusicUrl);
      musicAssetOrigin=origin;
      [musicCue,musicBed].forEach(function(player){
        if(!player || !player.paused) return;
        player.preload='auto';player.volume=0;player.muted=true;player.currentTime=0;
        try {
          var priming=player.play();
          if(priming&&priming.then) priming.then(function(){player.pause();player.currentTime=0;player.muted=false;player.volume=0;})
            .catch(function(){player.muted=false;player.volume=0;});
          else {player.pause();player.currentTime=0;player.muted=false;}
        } catch(_) {player.muted=false;player.volume=0;}
      });
    }
    function report(error, musicPlayback) {
      var blocked = error && error.name === "NotAllowedError";
      // A missing/temporarily unreachable file should not permanently disable
      // all later music and answer cues. Only an autoplay block needs an
      // explicit activation before playback can be retried.
      if (blocked && !musicPlayback) enabled = false;
      var mediaCode = error && Number(error.code);
      var status = blocked ? "blocked" :
        error && error.name === "NotSupportedError" || mediaCode === 4 ? "unsupported" :
        mediaCode === 2 ? "network-error" : mediaCode === 3 ? "decode-error" : "error";
      if (options.onAudioStatus) options.onAudioStatus(status);
      if(!musicPlayback) queued=[];
      if (!control) return;
      control.style.display = 'block';
      control.textContent = error && error.name !== 'NotAllowedError' ? 'Son indisponible · Réessayer' : 'Activer le son';
      if(controlTimeout)root.clearTimeout(controlTimeout);
      controlTimeout=blocked?null:root.setTimeout(function(){control.style.display='none';controlTimeout=null;},7000);
    }
    function play(file, remaining, continuing) {
      if (!root.Audio || !origin) { report({name:"AudioUnavailable"}); return; }
      if (!debugOwner) return;
      // Validation sounds have their own audio element. Do not tear down the
      // thinking soundtrack whenever an answer is checked.
      if(!continuing) stopAnswer();
      if(file==='buzzer.wav' && buzzerBuffer && buzzerContext && buzzerContext.state==='running') {
        try {
          buzzerSource=buzzerContext.createBufferSource();buzzerSource.buffer=buzzerBuffer;
          buzzerSource.connect(buzzerContext.destination);buzzerSource.start(0);
          enabled=true;if(control)control.style.display='none';return;
        } catch(_) {buzzerSource=null;}
      }
      var url = origin + '/tv/sounds/' + file + (audioVersion?'?v='+encodeURIComponent(audioVersion):'');
      if (!audio) audio = new root.Audio(url); else audio.src = url;
      audio.volume = /^game-end/.test(file) ? 0.38 : 0.70;
      audio.preload = 'auto';
      var thisAttempt = ++attempt;
      audio.onerror = function () { if (thisAttempt === attempt) report({name:"MediaError",code:audio.error&&audio.error.code}); };
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
          if (options.onAudioStatus) options.onAudioStatus("playing");
          if(controlTimeout){root.clearTimeout(controlTimeout);controlTimeout=null;}
          if (control) control.style.display = 'none';
          syncMusic(desiredMusic);
        }).catch(function (error) { if (thisAttempt === attempt) report(error); });
        else { enabled = true; if (options.onAudioStatus) options.onAudioStatus('playing'); if(controlTimeout){root.clearTimeout(controlTimeout);controlTimeout=null;} if (control) control.style.display = 'none'; syncMusic(desiredMusic); }
      } catch (error) { report(error); }
    }
    if (control) {
      control.onclick = function () {
        resumeBuzzer();debugOwner=true;
        if(channel) channel.postMessage({type:'claim',owner:ownerId});
        // Start both the confirmation cue and the current soundtrack directly
        // in the click gesture; deferring music until the cue's promise resolves
        // loses the browser's autoplay allowance on some Cast receivers.
        play(options.localAudio ? 'enabled.wav' : 'enabled.mp3');
        enabled=true;
        activeMusicKey=null;
        syncMusic(desiredMusic);
      };
      if (options.localAudio) { control.textContent = 'Activer le son'; control.style.display = 'block'; }
    }
    return {
      test: function () { debugOwner=true; resumeBuzzer(); primeMusicPlayers(); play("enabled.mp3"); },
      setVersion: function(version) { audioVersion=typeof version==='string'?version:null;warmBuzzer(); },
      setOrigin: function (joinUrl) {
        try {
          // Hosted on HTTPS (GitHub Pages), the page's own origin has no game audio:
          // the sound files live on the host phone, whose address arrives in joinUrl.
          var hosted = root.location && root.location.protocol === 'https:';
          var nextOrigin = hosted ? (joinUrl ? new URL(joinUrl).origin : origin)
            : root.location ? root.location.origin : (joinUrl ? new URL(joinUrl).origin : null);
          origin = nextOrigin;
          if (!options.localAudio && musicAssetOrigin !== origin) {
            musicAssetOrigin = origin;
            warmedAnitra = root.Audio ? new root.Audio(origin + anitraMusicUrl) : null;
            if (warmedAnitra) {
              warmedAnitra.preload = 'auto';
              warmedAnitra.load();
            }
          }
        } catch (_) {}
      },
      play: play, setMusic: syncMusic, playSequence: function (files) {
        if(!files.length || !debugOwner) return;
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
    var allowedMediaOrigin = null;
    var feedbackTimeout, feedbackQuestion = null;
    var lastScene = "";
    var hourglass, topSand, bottomSand, sandStream, timerLabel;
    var lastTimerFlip = -1;
    var overlayGlass, overlayTop, overlayBottom, overlayStream, overlayLabel, overlayAnswer, overlayName;
    var displayedQuestionId = null, displayedImageRevealStep = -1, displayedProgressiveImage = false, questionOptions = [], answerSlot, answerText, promptNode, questionLayout, questionDetails;
    var fitKey = '', layoutObserver;
    var scoreKey = '';
    var chronologyLines = [], chronologyPrompt = '', chronologyRevealed = false;
    var progressiveClueList=null, pendingMusicKey=null, pendingMusicState=null, pendingMusicTimer=null, revealedMusicKey=null;
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
    function updateProgressiveClues(details,prompt,count) {
      var parts=(prompt||'').split(/\n+(?=\d+\.\s)/);
      if(!promptNode)return;
      promptNode.sourcePrompt=prompt;
      promptNode.textContent=questionText(parts.shift()||'');
      if(!progressiveClueList){
        details.appendChild(node('p',count+" indices au total",'clue-count'));
        progressiveClueList=node('div',null,'clue-list');details.appendChild(progressiveClueList);
      } else {
        var countNode=details.querySelector('.clue-count');
        if(countNode)countNode.textContent=count+" indices au total";
      }
      clear(progressiveClueList);
      parts.forEach(function(clue){progressiveClueList.appendChild(node('span',questionText(clue.replace(/^\d+\.\s*/,'')),'clue-text'));});
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
        // Image buzzer prompts are short and have a reserved row. Scaling them
        // to fit answer text makes the prompt unexpectedly tiny.
        if (questionLayout.classList.contains('image-buzzer')) elements = elements.filter(function (element) { return element !== promptNode; });
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
    function visual(parent, question, reveal, state) {
      var url = safeImageUrl(question.imageUrl,root.location,allowedMediaOrigin);
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
      var progressiveImage = ["PIXELATE", "BLUR", "SHUFFLE", "UNCOVER"].indexOf(question.imageRevealMode) >= 0 || state.inRoundMusicMode === "IMAGE_GUESS_WHO";
      if (!reveal && progressiveImage) image.hidden = true;
      image.src = url;
      image.alt = "Question illustration";
      image.onerror = function () { wrapper.textContent = "Image unavailable"; };
      image.onload = function () { applyImageReveal(wrapper, image, question, reveal, state); };
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
      if (image.complete && image.naturalWidth) applyImageReveal(wrapper, image, question, reveal, state);
    }
    function render(state) {
      // A new room ends the previous room's audio session. Stop it before
      // synchronizing the incoming state, or that cleanup would immediately
      // stop the new room's soundtrack on the same render pass.
      if (lastSoundRoom !== state.roomId) soundPlayer.stop();
      soundPlayer.setOrigin(state.joinUrl);
      var imageQuestion = state.question && (['PIXELATE','BLUR','SHUFFLE','UNCOVER'].indexOf(state.question.imageRevealMode) >= 0 || state.inRoundMusicMode === 'IMAGE_GUESS_WHO');
      var mainPanel = doc.querySelector ? doc.querySelector('main') : null;
      if (mainPanel) mainPanel.classList.toggle('image-question', !!imageQuestion);
      try { allowedMediaOrigin = state.joinUrl ? new URL(state.joinUrl).origin : null; } catch (_) { allowedMediaOrigin = null; }
      soundPlayer.setVersion(state.audioBankVersion);
      var musicMode=state.inRoundMusicMode||null;
      if(state.answerSecondsRemaining!=null)musicMode=null;
      var musicKey=musicMode==='GUESS_WHO' || musicMode==='IMAGE_GUESS_WHO' || musicMode
        ? state.roomId+'/'+(state.question&&state.question.id||state.round)+'/thinking' : null;
      soundPlayer.setMusic(musicMode?{mode:musicMode,key:musicKey,paused:!!state.timerPaused,duration:state.secondsPerFlip||32,speedUp:!!state.speedUpMusicForClueTransition}:null);
      if(musicKey && pendingMusicKey===musicKey && pendingMusicTimer){pendingMusicState=state;return;}
      if(musicKey && musicKey!==revealedMusicKey){
        pendingMusicKey=musicKey;pendingMusicState=state;
        if(pendingMusicTimer)root.clearTimeout(pendingMusicTimer);
        pendingMusicTimer=root.setTimeout(function(){var latest=pendingMusicState,key=pendingMusicKey;pendingMusicTimer=null;pendingMusicState=null;pendingMusicKey=null;revealedMusicKey=key;if(latest)render(latest);},420);
        return;
      }
      if(!musicKey){if(pendingMusicTimer)root.clearTimeout(pendingMusicTimer);pendingMusicTimer=null;pendingMusicKey=null;pendingMusicState=null;revealedMusicKey=null;}
      var feedback = doc.getElementById('answer-feedback');
      var feedbackKey = state.roomId + '/' + (state.question && state.question.id || state.round);
      if (lastSoundRoom !== state.roomId || feedbackQuestion !== feedbackKey || lastPhase !== state.phase && ['QUESTION_ACTIVE','ANSWER_REVIEW','REVEAL_ANSWER','ROUND_SUMMARY'].indexOf(state.phase)<0) {
        if (feedbackTimeout) root.clearTimeout(feedbackTimeout);
        feedback.style.display = 'none';
        feedbackQuestion = feedbackKey;
      }
      var sameSoundRoom = lastSoundRoom === state.roomId;
      if (!sameSoundRoom) { lastSoundRoom = state.roomId; lastSoundId = state.answerSoundId || 0; lastBuzzerId = state.buzzerSoundId || 0; }
      if (sameSoundRoom && lastPhase && lastPhase !== 'GAME_ENDED' && state.phase === 'GAME_ENDED') {
        var ending = /^game-end-(zarathustra|te-deum|fireworks|aida|pomp|kiev|william-tell)\.mp3$/.test(state.gameEndSoundClip || '') ? state.gameEndSoundClip : 'game-end.wav';
        soundPlayer.play(ending);
      }
      lastPhase = state.phase;
      // Buzzer audio is local to the player who presses; televisions stay silent.
      lastBuzzerId = Math.max(lastBuzzerId || 0,state.buzzerSoundId || 0);
      if ((state.answerSoundId || 0) > lastSoundId && ["good","bad"].indexOf(state.answerSound) >= 0) {
        if (feedbackTimeout) root.clearTimeout(feedbackTimeout);
        clear(feedback);
        var mark = node('span', null, 'brush-mark');
        feedback.appendChild(mark);
        feedback.className = 'answer-feedback ' + state.answerSound;
        feedback.setAttribute('aria-label', state.answerSound === 'good' ? 'Bonne réponse' : 'Mauvaise réponse');
        feedback.style.display = 'flex';
        feedbackTimeout = root.setTimeout(function () { feedback.style.display = 'none'; }, 2200);
        try {
          var classicalClip=state.answerSound==='good'?'aria-correct.mp3':'variation15-incorrect.mp3';
          if(state.answerSoundClip===classicalClip || state.answerSoundClip===classicalClip.replace(/\.mp3$/,'.wav')) soundPlayer.playSequence([classicalClip]);
          else if(state.answerSoundPlaybackEnabled!==false) {
            var file = /^(good|bad)-\d{2,4}\.(wav|mp3)$/.test(state.answerSoundClip || '') && state.answerSoundClip.indexOf(state.answerSound + '-') === 0 ? state.answerSoundClip : state.answerSound + '.wav';
            soundPlayer.playSequence(state.answerSoundClip === null ? [state.answerSound + '-ping.wav'] : [state.answerSound + '-ping.wav',file]);
          }
        } catch (_) {}
      }
      lastSoundId = state.answerSoundId || 0;
      var categoryInfo = categoryPresentation(state);
      text("category", state.phase === "SUBJECT_VOTING" ? "Choix des catégories" : state.category ? categoryInfo.titleParts.join(" · ") : "Salon");
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
      overlayAnswer.textContent=reviewing?"Réponse : "+state.submittedAnswer:"";
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
        if (displayedProgressiveImage || state.question.imageRevealMode) {
          var originalImage = questionLayout && questionLayout.querySelector(".visual img");
          var imageMask = questionLayout && questionLayout.querySelector("canvas.progressive-image");
          stopImageReveal(imageMask);
          if (imageMask) imageMask.remove();
          if (originalImage) originalImage.hidden = false;
          displayedImageRevealStep = Math.max(0, Number(state.question.imageRevealSteps) - 1);
        }
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
      if (displayedQuestionId === qid && questionLayout && (state.question.imageRevealMode || displayedProgressiveImage)) {
        var revealImage = questionLayout.querySelector(".visual img");
        if (revealImage) {
          var revealState = state.phase === "QUESTION_ACTIVE" ? state : Object.assign({}, state, { timerPaused: true });
          applyImageReveal(revealImage.parentNode, revealImage, state.question, false, revealState);
          displayedImageRevealStep = state.question.imageRevealStep;
        }
      }
      if (active && displayedQuestionId === qid && promptNode) {
        if (!chronologyLines.length && promptNode.sourcePrompt !== state.question.prompt) {
          if(progressiveClueList)updateProgressiveClues(questionDetails,state.question.prompt,state.clueCount||0);
          else setPrompt(promptNode, state.question.prompt);
        }
        fitLayout();
        return;
      }
      var sceneKey = isQuestion ? JSON.stringify([state.roomId, qid, state.question.prompt, state.question.imageUrl]) :
        JSON.stringify([state.roomId, state.phase, state.category, state.categoryQuestionTypes, state.categoryAnswerMode, state.categoryQuestionCount, state.categories, state.subjectVote, state.picker, state.wagerResults, state.joinUrl, state.joinQrUrl, state.phase === "LOBBY" ? state.teams.length : null]);
      if (sceneKey === lastScene) return;
      lastScene = sceneKey;
      var scene = doc.getElementById("scene");
      if (scene.querySelectorAll) Array.prototype.forEach.call(scene.querySelectorAll("canvas.progressive-image"), stopImageReveal);
      clear(scene);
      scene.className = state.phase === "WAGER_RESULTS" ? "wager-results-scene" : state.phase === "CATEGORY_INTRO" ? "category-intro-scene" : state.phase === "WAGER_OPEN" ? "wager-open-scene" : "";
      var categoryHash = Array.from(state.category || '').reduce(function (hash, character) { return (hash * 31 + character.charCodeAt(0)) | 0; }, 0);
      var categoryHue = ((categoryHash % 360) + 360) % 360;
      scene.style.background = ['CATEGORY_INTRO','WAGER_OPEN'].indexOf(state.phase) >= 0 ? 'linear-gradient(135deg,hsl(' + categoryHue + ',52%,25%),hsl(' + ((categoryHue + 35) % 360) + ',45%,13%))' : '';
      if (layoutObserver) layoutObserver.disconnect();
      displayedQuestionId = null; displayedImageRevealStep = -1; displayedProgressiveImage = false; questionOptions = []; answerSlot = null; answerText = null;
      questionLayout = null; questionDetails = null; fitKey = '';
      progressiveClueList=null;
      chronologyLines = []; chronologyRevealed = false;
      function categoryHeading() {
        var heading = node('h1', null, 'category-heading');
        categoryInfo.titleParts.forEach(function (part) { heading.appendChild(node('span', part, 'category-title-line')); });
        scene.appendChild(heading);
      }
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
          categoryHeading();
          scene.appendChild(node("p", "Choisissez votre mise sur votre téléphone\nPremière question uniquement", "wager-instructions"));
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
          var qrUrl = safeImageUrl(state.joinQrUrl, root.location, allowedMediaOrigin);
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
          categoryHeading();
          scene.appendChild(node("p", (state.categoryQuestionCount || 0) + " questions", "category-count"));
          if (categoryInfo.types.length) scene.appendChild(node("p", categoryInfo.types.join(" · "), "category-types"));
          scene.appendChild(node("p", categoryInfo.mode, "category-mode"));
          if (state.clueCount > 0) scene.appendChild(node("p", state.clueCount + " indices pour cette question", "clue-count"));
          break;
        case "QUESTION_ACTIVE":
        case "ANSWER_REVIEW":
        case "REVEAL_ANSWER":
        case "ROUND_SUMMARY":
          var question = state.question;
          if (question) {
            displayedQuestionId = qid;
            displayedImageRevealStep = question.imageRevealStep == null ? -1 : question.imageRevealStep;
            displayedProgressiveImage = !!question.imageRevealMode || state.inRoundMusicMode === "IMAGE_GUESS_WHO";
            var hasVisual = safeImageUrl(question.imageUrl,root.location,allowedMediaOrigin) || question.mapOptions && question.mapOptions.length;
            var imageBuzzer = hasVisual && (question.imageRevealMode || ['BUZZER','WRITTEN'].indexOf(question.answerMode)>=0 || ['BUZZER','WRITTEN'].indexOf(state.categoryAnswerMode)>=0);
            var layout = node("div", null, hasVisual ? imageBuzzer ? "question-layout image-buzzer" : "question-layout with-visual" : "question-layout");
            var progressiveClues = /\n\n1\.\s/.test(question.prompt || "");
            var details = node("div", null, progressiveClues ? "question-details progressive-clues" : "question-details");
            var events = (question.prompt || '').split('\n').filter(function (line) { return /^\s*•/.test(line); });
            var chronology = events.length >= 2 && !question.options.length;
            promptNode = node("h1");
            if(progressiveClues && state.clueCount>0) {
              details.appendChild(promptNode);updateProgressiveClues(details,question.prompt,state.clueCount);
            } else { setPrompt(promptNode, chronology ? question.prompt.split('\n')[0] : question.prompt); details.appendChild(promptNode); }
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
              var imagePanel = node("div", null, "image-panel"); visual(imagePanel, question, reveal, state); layout.appendChild(imagePanel);
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
    }
    render.testAudio = function () { soundPlayer.test(); };
    render.buzzerCue=function(cue) {
      if(!cue || cue.type!=='buzzer' || cue.version!==1 || cue.roomId!==lastSoundRoom || lastPhase!=='QUESTION_ACTIVE' ||
          !Number.isSafeInteger(cue.buzzerSoundId) || cue.buzzerSoundId<=lastBuzzerId) return false;
      lastBuzzerId=cue.buzzerSoundId;return true;
    };
    return render;
  }

  function connectReceiver(context, framework, doc) {
    var render = makeRenderer(doc, {onAudioStatus:function (status) {
      context.getSenders().forEach(function(sender) {
        context.sendCustomMessage(namespace, sender.senderId, {type:'audio-status', version:1, status:status});
      });
    }});
    function ready(senderId) { context.sendCustomMessage(namespace, senderId, { type: "ready", version: 1 }); }
    context.addCustomMessageListener(namespace, function (event) {
      var command = event.data;
      if (typeof command === 'string') { try { command = JSON.parse(command); } catch (_) {} }
      if (command && command.type === 'audio-test' && command.version === 1) { render.testAudio(); return; }
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
