package com.example.triviaparty.model

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
    if (state != GameState.QUESTION_ACTIVE || questionReading || currentCategoryAnswerMode == CategoryAnswerMode.WRITTEN ||
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
    return copy(submissions = submissions + (next.teamId to submission), buzzerSoundId = buzzerSoundId + 1, answerTimerTeamId = next.teamId,
        answerTimerRemainingSeconds = null, answerTimerRunning = false)
}
