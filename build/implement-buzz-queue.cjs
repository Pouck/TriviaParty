const fs=require('fs');const base='app/src/main/java/com/example/triviaparty/';
function edit(p,fn){p=base+p;fs.writeFileSync(p,fn(fs.readFileSync(p,'utf8')));}
edit('model/GameSession.kt',s=>s.replace('    val buzzerSoundId: Int = 0,','    val buzzerSoundId: Int = 0,\n    val categoryBuzzerSound: String = "wolf",\n    val buzzQueue: List<BuzzPress> = emptyList(),'));
fs.writeFileSync(base+'model/BuzzQueue.kt',`package com.example.triviaparty.model

import kotlinx.serialization.Serializable

/** Server arrival order is authoritative; timestamps and score timing remain available for review. */
@Serializable
data class BuzzPress(val teamId: String, val questionId: String, val timestamp: Long,
    val flip: Int, val elapsed: Int)

object CategoryBuzzerSounds {
    val ids = listOf("wolf", "owl", "rooster", "dog", "bells", "coyote", "boat", "train")
    fun choose(previous: String): String = ids.filter { it != previous }.random()
}

fun GameSession.recordBuzz(teamId: String, now: Long): GameSession {
    val question = currentQuestion ?: return this
    if (state != GameState.QUESTION_ACTIVE || questionReading || !usesPlayerBuzzer() ||
        teams.none { it.id == teamId && it.isConnected } || teamId in textBuzzedTeamIds ||
        submissions[teamId]?.isLocked == true || buzzQueue.any { it.teamId == teamId && it.questionId == question.id }) return this
    return copy(buzzQueue = buzzQueue + BuzzPress(teamId, question.id, now, currentFlipNumber, elapsedSecondsInFlip)).advanceBuzzQueue()
}

fun GameSession.advanceBuzzQueue(): GameSession {
    val question = currentQuestion ?: return this
    if (state != GameState.QUESTION_ACTIVE || submissions.values.any {
        it.questionId == question.id && it.isLocked && it.isCorrect != false && it.isBuzz()
    }) return this
    val next = buzzQueue.firstOrNull { press -> press.questionId == question.id &&
        press.teamId !in textBuzzedTeamIds && submissions[press.teamId]?.isLocked != true &&
        teams.any { it.id == press.teamId && it.isConnected } } ?: return this
    val submission = AnswerSubmission(next.teamId, question.id, AnswerValue.TextSelection("BUZZ"), true,
        next.timestamp, next.flip, next.elapsed)
    return copy(submissions = submissions + (next.teamId to submission), answerTimerTeamId = next.teamId,
        answerTimerRemainingSeconds = null, answerTimerRunning = false)
}
`);
edit('model/BuzzerStatus.kt',s=>s.replace('BLOCKED("Une autre équipe répond")','QUEUED("En file · attendez votre tour"), BLOCKED("Une autre équipe répond")').replace('    if (submissions.values.any { it.isLocked && it.isCorrect != false && it.isBuzz() }) return BuzzerStatus.BLOCKED','    if (buzzQueue.any { it.teamId == teamId && it.questionId == currentQuestion.id }) return BuzzerStatus.QUEUED'));
edit('network/GameServer.kt',s=>{
const a=s.indexOf('            if (event.teamId in currentSession.textBuzzedTeamIds) return',s.indexOf('private fun handleLockAnswer'));
const b=s.indexOf('            return\n        }',a);
s=s.slice(0,a)+`            val updated = currentSession.recordBuzz(event.teamId, System.currentTimeMillis())
            if (updated == currentSession) return
            _gameSession.value = updated
            startTextAnswerTimer()
            broadcastState()
`+s.slice(b);
s=s.replaceAll('textBuzzedTeamIds = emptyList(),','textBuzzedTeamIds = emptyList(), buzzQueue = emptyList(),').replaceAll('textBuzzedTeamIds=emptyList()','textBuzzedTeamIds=emptyList(),buzzQueue=emptyList()');
s=s.replace('textBuzzedTeamIds = if (nextClue) emptyList() else session.textBuzzedTeamIds)', 'textBuzzedTeamIds = if (nextClue) emptyList() else session.textBuzzedTeamIds,\n            buzzQueue = if (nextClue) emptyList() else session.buzzQueue)');
s=s.replace('state = GameState.CATEGORY_INTRO,','state = GameState.CATEGORY_INTRO,\n            categoryBuzzerSound = CategoryBuzzerSounds.choose(currentSession.categoryBuzzerSound),');
s=s.replace('if (session.state != GameState.QUESTION_ACTIVE || session.answerTimerRunning) return','if (session.state != GameState.QUESTION_ACTIVE || session.answerTimerRunning) return');
s=s.replace('current.rejectOralAnswer(selected.teamId).copy(answerTimerRemainingSeconds=0)', 'current.rejectOralAnswer(selected.teamId).advanceBuzzQueue()');
s=s.replace('                        broadcastState()\n                        if (hasPointsTimerExpired(_gameSession.value)) evaluateQuestionScoresAndReveal()', '                        startTextAnswerTimer()\n                        broadcastState()\n                        if (!_gameSession.value.answerTimerRunning && hasPointsTimerExpired(_gameSession.value)) evaluateQuestionScoresAndReveal()');
s=s.replace('val submission = session.submissions[event.teamId]?.takeIf { it.isLocked && it.questionId == question.id', 'if (session.answerTimerTeamId != event.teamId) return\n        val submission = session.submissions[event.teamId]?.takeIf { it.isLocked && it.questionId == question.id');
s=s.replace('val rejected = session.rejectOralAnswer(event.teamId)','val rejected = session.rejectOralAnswer(event.teamId).advanceBuzzQueue()');
s=s.replace('            if (hasPointsTimerExpired(rejected)) {','            startTextAnswerTimer()\n            if (!rejected.answerTimerTeamId.isNullOrEmpty()) { broadcastState(); return }\n            if (hasPointsTimerExpired(rejected)) {');
s=s.replace('                get("/play/player.css") {',`                get("/play/sounds/{name}") {
                    val name = call.parameters["name"]?.removeSuffix(".mp3")
                    val bytes = if (name in CategoryBuzzerSounds.ids) readTvBinaryAsset?.invoke("phone-sounds/$name.mp3") else null
                    if (bytes == null) call.respondText("Not found", status = io.ktor.http.HttpStatusCode.NotFound)
                    else call.respondBytes(bytes, ContentType("audio", "mpeg"))
                }
                get("/play/player.css") {`);
return s;
});
edit('ui/host/HostScreen.kt',s=>s.replace('        val hasPublicChoices = question.spectatorOptions().isNotEmpty()',`        if (buzzer && game.buzzQueue.isNotEmpty()) {
            Text("Ordre des buzz : " + game.buzzQueue.mapIndexed { index, press ->
                "\u0024{index + 1}. " + (game.teams.find { it.id == press.teamId }?.name ?: press.teamId)
            }.joinToString(" · "), color = Color.LightGray, fontSize = 14.sp)
        }
        val hasPublicChoices = question.spectatorOptions().isNotEmpty()`));
