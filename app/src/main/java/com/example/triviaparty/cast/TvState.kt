package com.example.triviaparty.cast

import com.example.triviaparty.model.GameSession
import com.example.triviaparty.model.GameState
import com.example.triviaparty.model.AnswerValue
import com.example.triviaparty.model.Question
import com.example.triviaparty.model.CategoryAnswerMode
import com.example.triviaparty.model.CategoryWagerResult
import com.example.triviaparty.model.ImageRevealTiming
import com.example.triviaparty.model.spectatorOptions
import com.example.triviaparty.model.revealPrompt
import com.example.triviaparty.model.activePrompt
import com.example.triviaparty.model.isChronologyQuestion
import com.example.triviaparty.model.choiceVerdict
import com.example.triviaparty.model.pendingWrittenAnswers
import com.example.triviaparty.util.LocalMediaUrls
import kotlinx.serialization.Serializable
import kotlinx.serialization.EncodeDefault
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

/** Public TV data only: never send team credentials or private draft answers to a receiver. */
@Serializable
data class TvState(
    val type: String = "state",
    val version: Int = 1,
    val roomId: String,
    val phase: GameState,
    val category: String?,
    val categories: List<String>,
    val categoryAnswerMode: CategoryAnswerMode?,
    val categoryQuestionTypes: List<String>,
    val categoryQuestionCount: Int,
    val picker: String?,
    val round: Int,
    val totalRounds: Int,
    val question: TvQuestion?,
    val teams: List<TvTeam>,
    val flip: Int,
    val secondsRemaining: Int,
    val points: Int,
    val categoryAnswerTimeSeconds: Int = 0,
    val answeringTeam: String? = null,
    val submittedAnswer: String? = null,
    val submittedAnswerResult: Boolean? = null,
    val answerSecondsRemaining: Int? = null,
    val wagerResults: List<CategoryWagerResult> = emptyList(),
    val questionReading: Boolean = false,
    val joinUrl: String = "",
    val joinQrUrl: String = "",
    val secondsPerFlip: Int = 5,
    val imageRevealDurationSeconds: Int = 0,
    val answerTimeSeconds: Int = 10,
    val timerPaused: Boolean = false,
    val subjectVote: TvSubjectVote? = null,
    val answerSoundId: Int = 0,
    val answerSound: String? = null,
    val answerSoundClip: String? = null,
    val answerSoundPlaybackEnabled: Boolean = true,
    val speedUpMusicForClueTransition: Boolean = false,
    val gameEndSoundClip: String = "game-end.wav",
    val audioBankVersion: String = "classical-answer-cues-20261025",
    val buzzerSoundId: Int = 0,
    val pointsCountdown: Boolean = false,
    val readyCount: Int = 0,
    val connectedCount: Int = 0,
    val playersReadyReading: Boolean = false,
    val clueCount: Int = 0,
    val inRoundMusicMode: String? = null
) {
    fun encode(): String = json.encodeToString(this)

    companion object {
        private val json = Json { encodeDefaults = true }

        fun from(session: GameSession, port: Int = 8080): TvState {
            val networkSession = LocalMediaUrls.networkSession(session)
            val questionVisible = session.state in setOf(
                GameState.QUESTION_ACTIVE, GameState.ANSWER_REVIEW, GameState.REVEAL_ANSWER, GameState.ROUND_SUMMARY
            )
            val q = networkSession.currentQuestion?.takeIf { questionVisible }
            val reveal = session.state in setOf(GameState.REVEAL_ANSWER, GameState.ROUND_SUMMARY)
            val reviewSubmission = if(session.state==GameState.ANSWER_REVIEW)
                session.validatedWrittenTeamId?.let {session.submissions[it]} ?: session.pendingWrittenAnswers().firstOrNull() else null
            val config = session.timingConfig
            return TvState(
                roomId = session.roomId,
                phase = session.state,
                questionReading = session.questionReading,
                joinUrl = "http://${session.hostIpAddress}:$port/play",
                joinQrUrl = "http://${session.hostIpAddress}:$port/tv/join-qr.svg",
                secondsPerFlip = session.timingConfig.secondsPerFlip,
                imageRevealDurationSeconds = (session.currentQuestion as? Question.GuessWho)
                    ?.takeIf { it.imageRevealMode != com.example.triviaparty.model.ImageRevealMode.NONE }
                    ?.let { ImageRevealTiming.REVEAL_DURATION_SECONDS } ?: 0,
                answerTimeSeconds = session.answerTimeSeconds,
                timerPaused = session.timerPaused,
                subjectVote=session.subjectVoting?.let { TvSubjectVote(it.candidates,it.selected,it.totals(),it.round,it.remainingSlots,it.hostTieBreak,it.completed,it.ballots.size) },
                answerSoundId=session.answerSoundId,answerSound=session.answerSound,answerSoundClip=session.answerSoundClip,
                answerSoundPlaybackEnabled=session.answerSoundPlaybackEnabled,
                speedUpMusicForClueTransition=session.speedUpMusicForClueTransition,
                audioBankVersion=session.audioBankVersion,
                gameEndSoundClip=session.gameEndSoundClip,
                buzzerSoundId=session.buzzerSoundId,
                pointsCountdown=session.timingConfig.pointsDecayPerSecond!=null,
                readyCount=session.teams.count { it.isConnected && it.id in session.readyTeamIds },
                connectedCount=session.teams.count { it.isConnected },
                playersReadyReading=session.questionReading && session.currentQuestion?.isChronologyQuestion()==true,
                clueCount=(session.currentQuestion as? Question.GuessWho)?.let { if (it.imageRevealMode == com.example.triviaparty.model.ImageRevealMode.NONE) it.clues.size else it.imageRevealSteps } ?: 0,
                inRoundMusicMode=when {
                    session.state != GameState.QUESTION_ACTIVE || session.questionReading -> null
                    session.currentQuestion is Question.GuessWho && session.currentQuestion.imageRevealMode != com.example.triviaparty.model.ImageRevealMode.NONE -> "IMAGE_GUESS_WHO"
                    session.currentQuestion is Question.GuessWho -> "GUESS_WHO"
                    else -> "THINKING"
                },
                category = session.currentCategory,
                categories = session.availableCategories,
                categoryAnswerMode = session.currentCategoryAnswerMode,
                categoryQuestionTypes = session.currentCategoryQuestionTypes,
                categoryQuestionCount = session.currentCategoryQuestionCount,
                picker = session.teams.find { it.id == session.pickerTeamId }?.name,
                round = session.roundNumber,
                totalRounds = session.totalRounds,
                question = q?.let { TvQuestion.from(it, reveal, session.currentFlipNumber).let { tv ->
                    when {
                        tv.imageRevealMode != null -> tv.copy(answerMode="BUZZER")
                        session.currentCategoryAnswerMode==CategoryAnswerMode.WRITTEN -> tv.copy(answerMode="WRITTEN")
                        else -> tv
                    }
                } },
                teams = session.teams.mapIndexed { colorIndex,it ->
                    val submission = session.submissions[it.id]
                    val matching = q != null && submission?.questionId == q.id && submission.isLocked
                    val result = if(!matching) null else if(reveal || session.state==GameState.ANSWER_REVIEW) submission?.isCorrect
                        else if(session.state==GameState.QUESTION_ACTIVE) q?.choiceVerdict(submission!!.answer) else null
                    TvTeam(it.name, it.score, submission?.isLocked == true, it.isConnected,
                        correct = reveal && q != null && submission?.questionId == q.id &&
                            submission.isLocked && submission.isCorrect == true,
                        answerResult = result,colorIndex=colorIndex)
                },
                flip = session.currentFlipNumber,
                secondsRemaining = (config.secondsPerFlip - session.elapsedSecondsInFlip).coerceAtLeast(0),
                points = q?.let { config.calculateScore(it.basePoints, session.currentFlipNumber,session.elapsedSecondsInFlip) } ?: 0,
                categoryAnswerTimeSeconds = session.currentCategoryAnswerTimeSeconds,
                submittedAnswer = (reviewSubmission?.answer as? AnswerValue.TextSelection)?.text,
                submittedAnswerResult = reviewSubmission?.isCorrect,
                answeringTeam = (if(session.state==GameState.ANSWER_REVIEW) reviewSubmission?.teamId else session.answerTimerTeamId)
                    ?.let { teamId -> session.teams.find { it.id == teamId }?.name },
                answerSecondsRemaining = session.answerTimerRemainingSeconds.takeIf { session.answerTimerRunning },
                wagerResults = session.categoryWagerResults.takeIf { session.state == GameState.WAGER_RESULTS }.orEmpty()
            )
        }
    }
}

@Serializable data class TvSubjectVote(val candidates: List<String>, val selected: List<String>, val totals: Map<String,Int>,
    val round: Int, val slots: Int, val hostTieBreak: Boolean, val completed: Boolean, val ballots: Int)

@Serializable
data class TvTeam(val name: String, val score: Int, val locked: Boolean, val connected: Boolean,
    val correct: Boolean = false, val answerResult: Boolean? = null,val colorIndex: Int = 0)

@Serializable
data class TvQuestion(
    val prompt: String,
    val imageUrl: String?,
    val options: List<String>,
    val answer: String?,
    val mapTarget: Question.MapTarget? = null,
    val mapOptions: List<TvMapOption> = emptyList(),
    val id: String = "",
    val answerMode: String? = null,
    val imageRevealMode: String? = null,
    val imageRevealStep: Int = 0,
    val imageRevealSteps: Int = 1,
    @OptIn(ExperimentalSerializationApi::class)
    @EncodeDefault(EncodeDefault.Mode.NEVER)
    val correctOptionIndex: Int? = null
) {
    companion object {
        fun from(question: Question, reveal: Boolean, flipNumber: Int = 0): TvQuestion {
            val choices = when (question) {
                is Question.MultipleChoice -> question
                is Question.Wager -> question.subQuestion
                is Question.SpeedRace -> question.subQuestion
                else -> null
            }
            val answer = if (!reveal) null else when (question) {
                is Question.MultipleChoice -> question.options.getOrNull(question.correctOptionIndex)
                is Question.Wager -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex)
                is Question.SpeedRace -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex)
                is Question.Ordering -> question.correctOrderIds.mapNotNull { id ->
                    question.items.find { it.id == id }?.text
                }.joinToString(" → ")
                is Question.TextAnswer -> question.acceptableAnswers.firstOrNull()
                is Question.GuessWho -> question.acceptableAnswers.firstOrNull()
                is Question.MapPin -> question.options.getOrNull(question.correctOptionIndex)?.label ?: "Réponse indiquée sur la carte"
            }
            return TvQuestion(
                id = question.id,
                answerMode = if (question is Question.TextAnswer || question is Question.GuessWho) "BUZZER" else "SIMULTANEOUS",
                imageRevealMode = (question as? Question.GuessWho)?.imageRevealMode?.takeIf { it != com.example.triviaparty.model.ImageRevealMode.NONE }?.name,
                imageRevealStep = flipNumber,
                imageRevealSteps = (question as? Question.GuessWho)?.let { if (it.imageRevealMode == com.example.triviaparty.model.ImageRevealMode.NONE) it.clues.size else it.imageRevealSteps } ?: 1,
                correctOptionIndex = choices?.correctOptionIndex?.takeIf { reveal },
                prompt = if (question is Question.Ordering) {
                    question.prompt.substringBefore('\n') + "\n" +
                        question.items.joinToString("\n") { "• ${it.text}" }
                } else if (reveal && !question.isChronologyQuestion()) {
                    question.revealPrompt()
                } else {
                    val rawPrompt = question.activePrompt(flipNumber)
                    // Compact long descriptions or prompts if needed to stay well within limits
                    if (rawPrompt.length > 1000) rawPrompt.take(1000) + "…" else rawPrompt
                },
                imageUrl = question.imageUrl ?: choices?.imageUrl,
                options = question.spectatorOptions().let { opts ->
                    if (opts.size > 20) opts.take(20) else opts
                },
                answer = answer,
                mapTarget = (question as? Question.MapPin)?.target?.takeIf { reveal },
                mapOptions = (question as? Question.MapPin)?.options?.map { TvMapOption(it.label, it.xRatio, it.yRatio) }?.let { if (it.size > 50) it.take(50) else it }.orEmpty()
            )
        }
    }
}

@Serializable
data class TvMapOption(val label: String, val xRatio: Float, val yRatio: Float)
