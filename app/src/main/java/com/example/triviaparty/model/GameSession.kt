package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
enum class GameState {
    LOBBY,
    SUBJECT_VOTING,
    CATEGORY_SELECT,
    CATEGORY_INTRO,
    WAGER_OPEN,
    WAGER_RESULTS,
    QUESTION_ACTIVE,
    ANSWER_REVIEW,
    REVEAL_ANSWER,
    ROUND_SUMMARY,
    GAME_ENDED
}

@Serializable
data class GameSession(
    val roomId: String,
    val subjectVoting: SubjectVoting? = null,
    val answerSoundId: Int = 0,
    val answerSound: String? = null,
    val answerSoundClip: String? = null,
    val buzzerSoundId: Int = 0,
    val state: GameState = GameState.LOBBY,
    val currentCategory: String? = null,
    val currentCategoryAnswerMode: CategoryAnswerMode? = null,
    val currentCategoryAnswerTimeSeconds: Int = 0,
    val currentCategoryQuestionTypes: List<String> = emptyList(),
    val currentCategoryQuestionCount: Int = 0,
    val masterCategories: List<String> = emptyList(),
    val availableCategories: List<String> = emptyList(),
    val retiredCategories: List<String> = emptyList(),
    val currentQuestion: Question? = null,
    val teams: List<Team> = emptyList(),
    val pendingJoinRequests: List<String> = emptyList(),
    val requireHostValidation: Boolean = false,
    val currentFlipNumber: Int = 0,
    val elapsedSecondsInFlip: Int = 0,
    val questionReading: Boolean = false,
    val readyTeamIds: List<String> = emptyList(),
    val validatedWrittenTeamId: String? = null,
    val timerPaused: Boolean = false,
    val submissions: Map<String, AnswerSubmission> = emptyMap(), // teamId -> AnswerSubmission
    val textBuzzedTeamIds: List<String> = emptyList(),
    val answerTimerTeamId: String? = null,
    val answerTimerRemainingSeconds: Int? = null,
    val answerTimerRunning: Boolean = false,
    val pickerTeamId: String? = null,
    val roundNumber: Int = 0,
    val totalRounds: Int = 5,
    val timingConfig: HourglassConfig = HourglassConfig(),
    val answerTimeSeconds: Int = 10,
    val categoryRules: Map<String, CategoryGameRules> = emptyMap(),
    val categoryWagerQuestionId: String? = null,
    val categoryWagerLimits: Map<String, Int> = emptyMap(),
    val categoryWagers: Map<String, Int> = emptyMap(),
    val categoryWagerResults: List<CategoryWagerResult> = emptyList(),
    val categoryWagerSettled: Boolean = false,
    val categoryWagerResultsShown: Boolean = false,
    val playedQuestionIds: List<String> = emptyList(),
    val hostIpAddress: String = "127.0.0.1"
)
