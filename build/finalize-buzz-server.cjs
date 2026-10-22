const fs=require('fs');const path='app/src/main/java/com/example/triviaparty/network/GameServer.kt';let s=fs.readFileSync('build/game-server-before-queue.kt','utf8').replace(/\r\n/g,'\n');
s=s.replace('                get("/tv/hourglass.svg") {',`                listOf("feedback-good.png", "feedback-bad.png", "feedback-red-stroke.png").forEach { name ->
                    get("/tv/$name") {
                        val bytes = readTvBinaryAsset?.invoke(name)
                        if (bytes == null) call.respondText("Not found", status = io.ktor.http.HttpStatusCode.NotFound)
                        else call.respondBytes(bytes, ContentType("image", "png"))
                    }
                }
                get("/tv/hourglass.svg") {`);
s=s.replace('                get("/play/player.css") {',`                get("/play/sound-credits") { call.respondText(readPlayerAsset?.invoke("sound-credits.html") ?: "", ContentType.Text.Html) }
                get("/play/sounds/{name}") {
                    val name = call.parameters["name"]?.removeSuffix(".mp3")
                    val bytes = if (name in CategoryBuzzerSounds.ids) readTvBinaryAsset?.invoke("phone-sounds/$name.mp3") else null
                    if (bytes == null) call.respondText("Not found", status = io.ktor.http.HttpStatusCode.NotFound)
                    else call.respondBytes(bytes, ContentType("audio", "mpeg"))
                }
                get("/play/player.css") {`);
const a=s.indexOf('        if (question.isOralBuzzerQuestion()',s.indexOf('private fun handleLockAnswer'));
const b=s.indexOf('        val team = currentSession.teams.find',a);if(a<0||b<a)throw Error('Missing buzz branch');
s=s.slice(0,a)+`        if (question.isOralBuzzerQuestion() || (event.answer as? AnswerValue.TextSelection)?.text == "BUZZ") {
            val updated = currentSession.recordBuzz(event.teamId, System.currentTimeMillis())
            if (updated == currentSession) return
            _gameSession.value = updated
            startTextAnswerTimer()
            broadcastState()
            return
        }

`+s.slice(b);
s=s.replaceAll('textBuzzedTeamIds = emptyList(),','textBuzzedTeamIds = emptyList(), buzzQueue = emptyList(),').replaceAll('textBuzzedTeamIds=emptyList()','textBuzzedTeamIds=emptyList(),buzzQueue=emptyList()');
s=s.replace('textBuzzedTeamIds = if (nextClue) emptyList() else session.textBuzzedTeamIds)', 'textBuzzedTeamIds = if (nextClue) emptyList() else session.textBuzzedTeamIds,\n            buzzQueue = if (nextClue) emptyList() else session.buzzQueue)');
s=s.replace('state = GameState.CATEGORY_INTRO,','state = GameState.CATEGORY_INTRO,\n            categoryBuzzerSound = CategoryBuzzerSounds.choose(currentSession.categoryBuzzerSound),');
s=s.replace('current.rejectOralAnswer(selected.teamId).copy(answerTimerRemainingSeconds=0)', 'current.rejectOralAnswer(selected.teamId).advanceBuzzQueue()');
s=s.replace('                        broadcastState()\n                        if (hasPointsTimerExpired(_gameSession.value)) evaluateQuestionScoresAndReveal()', '                        startTextAnswerTimer()\n                        broadcastState()\n                        if (!_gameSession.value.answerTimerRunning && hasPointsTimerExpired(_gameSession.value)) evaluateQuestionScoresAndReveal()');
s=s.replace('        val submission = session.submissions[event.teamId]?.takeIf { it.isLocked && it.questionId == question.id', '        if (session.answerTimerTeamId != event.teamId) return\n        val submission = session.submissions[event.teamId]?.takeIf { it.isLocked && it.questionId == question.id');
s=s.replace('val rejected = session.rejectOralAnswer(event.teamId)','val rejected = session.rejectOralAnswer(event.teamId).advanceBuzzQueue()');
s=s.replace('            if (hasPointsTimerExpired(rejected)) {','            startTextAnswerTimer()\n            if (rejected.answerTimerTeamId != null) { broadcastState(); return }\n            if (hasPointsTimerExpired(rejected)) {');
fs.writeFileSync(path,s);
