const fs=require('fs');let s=fs.readFileSync('cast-receiver/receiver.js','utf8');
s=s.replace('      enabled = false;\n      queued=[];','      enabled = false;\n      if (options.onAudioStatus) options.onAudioStatus(error && error.name === "NotAllowedError" ? "blocked" : "error");\n      queued=[];');
s=s.replace('      var thisAttempt = ++attempt;','      var thisAttempt = ++attempt;\n      audio.onerror = function () { if (thisAttempt === attempt) report({name:"MediaError"}); };');
s=s.replace('          enabled = true;\n          if (control)', '          enabled = true;\n          if (options.onAudioStatus) options.onAudioStatus("playing");\n          if (control)');
s=s.replace('      setVersion: function(version)', '      test: function () { debugOwner=true; resumeBuzzer(); play("enabled.wav"); },\n      setVersion: function(version)');
s=s.replace('    render.buzzerCue=function(cue)', '    render.testAudio = function () { soundPlayer.test(); };\n    render.buzzerCue=function(cue)');
s=s.replace('    var render = makeRenderer(doc);\n    function ready(senderId)', `    var render = makeRenderer(doc, {onAudioStatus:function (status) {
      context.getSenders().forEach(function(sender) {
        context.sendCustomMessage(namespace, sender.senderId, {type:'audio-status', version:1, status:status});
      });
    }});
    function ready(senderId)`);
s=s.replace('      var state = parseState(event.data);', `      var command = event.data;
      if (typeof command === 'string') { try { command = JSON.parse(command); } catch (_) {} }
      if (command && command.type === 'audio-test' && command.version === 1) { render.testAudio(); return; }
      var state = parseState(event.data);`);
for(const dir of ['cast-receiver/','app/src/main/assets/tv/'])fs.writeFileSync(dir+'receiver.js',s);
const cast='app/src/main/java/com/example/triviaparty/cast/GoogleCastController.kt';let k=fs.readFileSync(cast,'utf8').replace(/\r\n/g,'\n');
k=k.replace('    val connected: Boolean = false,','    val audioStatus: String? = null,\n    val connected: Boolean = false,');
k=k.replace(`                if (session === connectedSession && runCatching {
                        JSONObject(message).optString("type") == "ready"
                    }.getOrDefault(false)) sendLatest()`, `                if (session === connectedSession) runCatching {
                    val payload = JSONObject(message)
                    when (payload.optString("type")) {
                        "ready" -> sendLatest()
                        "audio-status" -> _status.value = _status.value.copy(audioStatus = when (payload.optString("status")) {
                            "playing" -> "Son TV en lecture · vérifiez le volume du téléviseur si vous ne l’entendez pas."
                            "blocked" -> "Le téléviseur bloque le son. Reconnectez la diffusion puis réessayez."
                            else -> "Le téléviseur ne peut pas charger le son. Réessayez ou reconnectez la diffusion."
                        })
                    }
                }`);
k=k.replace('    fun resend() = sendLatest()',`    fun testAudio() {
        val active = session?.takeIf { it.isConnected } ?: return
        _status.value = _status.value.copy(audioStatus = "Test du son TV…")
        try {
            active.sendMessage(TRIVIA_CAST_NAMESPACE, "{\\"type\\":\\"audio-test\\",\\"version\\":1}").setResultCallback { result ->
                if (!result.isSuccess) _status.value = _status.value.copy(audioStatus = "Le test audio n’a pas atteint le téléviseur. Reconnectez la diffusion.")
            }
        } catch (_: Exception) {
            _status.value = _status.value.copy(audioStatus = "Test audio impossible. Reconnectez la diffusion.")
        }
    }

    fun resend() = sendLatest()`);fs.writeFileSync(cast,k);
const host='app/src/main/java/com/example/triviaparty/ui/host/HostScreen.kt';k=fs.readFileSync(host,'utf8').replace('                GoogleCastDeviceList(googleCast, scanning = true)',`                GoogleCastDeviceList(googleCast, scanning = true)
                if (castStatus.connected) {
                    Button(onClick = { googleCast.testAudio() }) { Text("Tester le son TV") }
                    castStatus.audioStatus?.let { Text(it, fontSize = 14.sp) }
                }`);fs.writeFileSync(host,k);
