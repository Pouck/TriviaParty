package com.example.triviaparty.network

import com.example.triviaparty.model.AnswerValue
import com.example.triviaparty.model.GameSession
import com.example.triviaparty.model.CategoryGameRules
import com.example.triviaparty.model.HourglassConfig
import kotlinx.serialization.Serializable

@Serializable
sealed class GameEvent {

    // --- Client -> Server Events ---
    @Serializable
    data class JoinRoom(val roomId: String, val teamName: String, val sessionToken: String) : GameEvent()

    @Serializable
    data class UpdateDraftAnswer(val teamId: String, val questionId: String, val answer: AnswerValue) : GameEvent()

    @Serializable
    data class LockAnswer(val teamId: String, val questionId: String, val answer: AnswerValue) : GameEvent()
    @Serializable data class PlayerReady(val teamId: String,val questionId: String,val clueIndex: Int) : GameEvent()
    @Serializable data class HostJudgeWrittenAnswer(val teamId: String,val questionId: String,val correct: Boolean) : GameEvent()

    @Serializable data class HostContinueWrittenReview(val questionId: String) : GameEvent()

    @Serializable
    data class HostStartGame(
        val categories: List<String>,
        val totalRounds: Int = 5,
        val timingConfig: HourglassConfig = HourglassConfig(),
        val answerTimeSeconds: Int = 10,
        val categoryRules: Map<String, CategoryGameRules> = emptyMap(),
        val voteSettings: com.example.triviaparty.model.VoteSettings? = null,
        val allAudiencesOnly: Boolean = false
    ) : GameEvent()

    @Serializable data class HostSkipCategory(val category: String) : GameEvent()

    @Serializable object HostOpenSubjectVote : GameEvent()
    @Serializable object HostCloseSubjectVote : GameEvent()
    @Serializable data class SubmitSubjectVote(val teamId: String, val round: Int, val subjects: List<String>) : GameEvent()
    @Serializable data class HostBreakSubjectTie(val subjects: List<String>) : GameEvent()

    @Serializable
    object HostBeginCategorySelect : GameEvent()

    @Serializable
    object HostOfferCategoryWager : GameEvent()

    @Serializable
    data class SubmitCategoryWager(val teamId: String, val questionId: String, val amount: Int) : GameEvent()

    @Serializable
    data class HostSelectCategory(val category: String) : GameEvent()

    @Serializable
    data class HostNextQuestion(val questionId: String? = null) : GameEvent()

    @Serializable
    object HostPauseTimer : GameEvent()

    @Serializable
    object HostResumeTimer : GameEvent()

    @Serializable
    object HostStartQuestionTimer : GameEvent()

    @Serializable
    object HostRevealAnswer : GameEvent()

    @Serializable
    data class HostJudgeTextBuzz(val teamId: String, val correct: Boolean) : GameEvent()

    @Serializable
    object HostStartTextAnswerTimer : GameEvent()

    @Serializable
    data class HostAdjustScore(val teamId: String, val deltaPoints: Int) : GameEvent()

    @Serializable
    data class HostSetScore(val teamId: String, val newScore: Int) : GameEvent()

    @Serializable
    data class HostApproveRejoin(val teamName: String, val newSessionToken: String) : GameEvent()

    @Serializable
    data class HostSetValidationMode(val requireValidation: Boolean) : GameEvent()

    @Serializable
    data class HostValidateTeam(val teamName: String, val approve: Boolean, val sessionToken: String? = null) : GameEvent()


    // --- Server -> Client Events ---
    @Serializable
    data class RoomStateBroadcast(val session: GameSession) : GameEvent()

    @Serializable
    data class JoinResponse(
        val success: Boolean,
        val message: String,
        val teamId: String? = null,
        val requiresHostApproval: Boolean = false
    ) : GameEvent()

    @Serializable
    data class HourglassTick(val flipNumber: Int, val elapsedSecondsInFlip: Int) : GameEvent()

    @Serializable
    data class ErrorEvent(val message: String) : GameEvent()
}
