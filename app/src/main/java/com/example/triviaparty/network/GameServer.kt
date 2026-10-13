package com.example.triviaparty.network

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.data.QuestionBankRepository
import com.example.triviaparty.data.balancedCategoryOrder
import com.example.triviaparty.data.categoryProfileFor
import com.example.triviaparty.data.GamePackageRepository
import com.example.triviaparty.data.browseGroup
import com.example.triviaparty.data.isTestPackage
import com.example.triviaparty.data.combineGamePackages
import com.example.triviaparty.data.selectBalancedPackages
import com.example.triviaparty.data.CategoryProfile
import com.example.triviaparty.data.CategoryFormat
import com.example.triviaparty.data.HostReviewStore
import com.example.triviaparty.model.*
import com.example.triviaparty.util.LocalMediaUrls
import com.example.triviaparty.util.NetworkUtils
import io.ktor.http.ContentType
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.cio.*
import io.ktor.server.response.respondText
import io.ktor.server.response.respondBytes
import io.ktor.server.request.*
import kotlinx.serialization.json.jsonPrimitive
import io.ktor.server.routing.*
import io.ktor.server.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonObject
import java.util.*
import java.io.File
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.hypot

class GameServer(
    val port: Int = 8080,
    private val readTvAsset: ((String) -> String)? = null,
    private val importedPackagesDirectory: File? = null,
    private val readPlayerAsset: ((String) -> String)? = null,
    private val readTvBinaryAsset: ((String) -> ByteArray)? = null
) {

    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    private var serverEngine: ApplicationEngine? = null

    private val _gameSession = MutableStateFlow(GameSession(roomId = generateRoomId(), hostIpAddress = NetworkUtils.getLocalIpAddress()))
    val gameSession: StateFlow<GameSession> = _gameSession.asStateFlow()

    private val clientSessions = ConcurrentHashMap<WebSocketSession, String>() // WebSocketSession -> TeamId/Host
    // Hosts and TV viewers subscribe without joining as a player.
    private val subscribers = ConcurrentHashMap.newKeySet<WebSocketSession>()
    private val tvSubscribers = ConcurrentHashMap.newKeySet<WebSocketSession>()
    private val browserPlayers = ConcurrentHashMap.newKeySet<WebSocketSession>()
    private val judges = ConcurrentHashMap.newKeySet<WebSocketSession>()
    private val judgeToken = UUID.randomUUID().toString() + UUID.randomUUID().toString()
    fun privateJudgeUrl(): String = "http://${NetworkUtils.getLocalIpAddress()}:$port/judge#$judgeToken"
    private val pendingPlayers = ConcurrentHashMap<WebSocketSession, GameEvent.JoinRoom>()

    private val serverScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private val clientMutationMutex = Mutex()
    private var broadcastJob: Job? = null
    private var timerJob: Job? = null
    private var answerTimerJob: Job? = null
    private var isTimerPaused = false
    private var gameTimingConfig: HourglassConfig? = null
    private var votePackages: List<GamePackage> = emptyList()
    private var soundQuestionId: String? = null
    private var soundedResults: Map<String, Boolean?> = emptyMap()
    private var questionHasSound = false
    private var revealedSoundQuestionId: String? = null

    fun start() {
        if (serverEngine != null) return
        val localIp = NetworkUtils.getLocalIpAddress()
        _gameSession.value = _gameSession.value.copy(hostIpAddress = localIp)


        serverEngine = embeddedServer(CIO, port = port, host = "0.0.0.0") {
            install(WebSockets) {
                pingPeriodMillis = 15000L
                timeoutMillis = 30000L
            }
            routing {
                get("/play") {
                    call.respondText(readPlayerAsset?.invoke("index.html") ?: "Player page unavailable",
                        ContentType.Text.Html)
                }
                get("/play/player.css") {
                    call.respondText(readPlayerAsset?.invoke("player.css") ?: "", ContentType.Text.CSS)
                }
                get("/play/player.js") {
                    call.respondText(readPlayerAsset?.invoke("player.js") ?: "", ContentType("application", "javascript"))
                }
                webSocket("/play/ws") {
                    browserPlayers.add(this)
                    subscribers.add(this)
                    try {
                        sendToSession(this, GameEvent.RoomStateBroadcast(LocalMediaUrls.networkSession(_gameSession.value, port)))
                        for (frame in incoming) {
                            if (frame is Frame.Text) handleClientMessage(this, frame.readText())
                        }
                    } finally {
                        browserPlayers.remove(this)
                        subscribers.remove(this)
                        pendingPlayers.remove(this)
                        clientSessions.remove(this)?.let { teamId ->
                            if (!clientSessions.containsValue(teamId)) markTeamDisconnected(teamId)
                        }
                    }
                }
                get("/judge") {
                    call.respondText(readPlayerAsset?.invoke("judge.html") ?: "",ContentType.Text.Html)
                }
                get("/judge.js") {
                    call.respondText(readPlayerAsset?.invoke("judge.js") ?: "",ContentType("application","javascript"))
                }
                webSocket("/judge/ws") {
                    if (call.request.queryParameters["token"] != judgeToken) {
                        close(CloseReason(CloseReason.Codes.VIOLATED_POLICY,"Accès privé requis"))
                        return@webSocket
                    }
                    judges.add(this)
                    try {
                        send(Frame.Text(judgeStateText(_gameSession.value)))
                        for (frame in incoming) if (frame is Frame.Text) {
                            val fields = runCatching { Json.parseToJsonElement(frame.readText()).jsonObject }.getOrNull() ?: continue
                            val type = fields["type"]?.jsonPrimitive?.content?.substringAfterLast('.') ?: continue
                            if (type !in setOf("HostJudgeTextBuzz","HostStartQuestionTimer","HostPauseTimer","HostResumeTimer")) continue
                            if (fields["questionId"]?.jsonPrimitive?.content != _gameSession.value.currentQuestion?.id) continue
                            handleClientMessage(this,frame.readText())
                        }
                    } finally { judges.remove(this) }
                }
                get("/tv") {
                    call.respondText(
                        readTvAsset?.invoke("display.html") ?: localTvShell,
                        ContentType.Text.Html
                    )
                }

                get("/tv/cast") {
                    call.respondText(readTvAsset?.invoke("cast.html") ?: "Receiver unavailable", ContentType.Text.Html)
                }

                get("/tv/join-qr.svg") {
                    val url = "http://${_gameSession.value.hostIpAddress}:$port/play"
                    call.respondText(com.example.triviaparty.util.JoinQrSvg.render(url), ContentType("image", "svg+xml"))
                }

                get("/tv/display.css") {
                    call.respondText(
                        readTvAsset?.invoke("receiver.css") ?: "",
                        ContentType.Text.CSS
                    )
                }

                get("/tv/display.js") {
                    call.respondText(
                        readTvAsset?.invoke("display.js") ?: "",
                        ContentType("application", "javascript")
                    )
                }

                get("/tv/receiver.js") {
                    call.respondText(
                        readTvAsset?.invoke("receiver.js") ?: "",
                        ContentType("application", "javascript")
                    )
                }

                get("/tv/hourglass.svg") {
                    call.respondText(readTvAsset?.invoke("hourglass.svg") ?: "", ContentType("image", "svg+xml"))
                }
                get("/tv/sounds/{name}") {
                    val name=call.parameters["name"]
                    val bytes=if(com.example.triviaparty.model.AnswerReactions.isAllowed(name)) readTvBinaryAsset?.invoke("sounds/$name") else null
                    if(bytes==null) call.respondText("Not found",status=io.ktor.http.HttpStatusCode.NotFound)
                    else call.respondBytes(bytes,ContentType("audio",if(name?.endsWith(".mp3")==true) "mpeg" else "wav"))
                }

                get("/media/{packageId}/{assetPath...}") {
                    val packageId = call.parameters["packageId"]
                    val assetPath = call.parameters.getAll("assetPath")?.joinToString("/")
                    val image = if (packageId != null && assetPath != null) {
                        importedPackagesDirectory?.let { GamePackageImportRepository.mediaFile(it, packageId, assetPath) }
                    } else null
                    if (image == null) {
                        call.respondText("Not found", status = io.ktor.http.HttpStatusCode.NotFound)
                    } else {
                        val contentType = when (image.extension.lowercase()) {
                            "png" -> ContentType.Image.PNG
                            "jpg", "jpeg" -> ContentType.Image.JPEG
                            "webp" -> ContentType("image", "webp")
                            else -> ContentType.Application.OctetStream
                        }
                        call.respondBytes(image.readBytes(), contentType)
                    }
                }

                webSocket("/tv/ws") {
                    tvSubscribers.add(this)
                    try {
                        send(Frame.Text(TvState.from(LocalMediaUrls.networkSession(_gameSession.value, port)).encode()))
                        for (frame in incoming) {
                            if (frame is Frame.Close) break
                        }
                    } catch (_: Exception) {
                        // TVs can disconnect when their browser is closed or sleeps.
                    } finally {
                        tvSubscribers.remove(this)
                    }
                }

                webSocket("/ws") {
                    // Only the Android host uses the full, answer-bearing protocol.
                    // remoteHost can resolve to "localhost" on Android; use the socket IP.
                    if (call.request.local.remoteAddress !in setOf("127.0.0.1","::1","0:0:0:0:0:0:0:1")) {
                        close(CloseReason(CloseReason.Codes.VIOLATED_POLICY,"Utilisez /play"))
                        return@webSocket
                    }
                    subscribers.add(this)
                    try {
                        sendToSession(this, GameEvent.RoomStateBroadcast(LocalMediaUrls.networkSession(_gameSession.value, port)))

                        for (frame in incoming) {
                            if (frame is Frame.Text) {
                                val text = frame.readText()
                                handleClientMessage(this, text)
                            }
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                    } finally {
                        subscribers.remove(this)
                        pendingPlayers.remove(this)
                        clientSessions.remove(this)?.let { teamId ->
                            if (!clientSessions.containsValue(teamId)) markTeamDisconnected(teamId)
                        }
                    }
                }
            }
        }.start(wait = false)
    }

    fun stop() {
        timerJob?.cancel()
        stopAnswerTimer()
        serverEngine?.stop(1000, 2000)
        serverEngine = null
        subscribers.clear()
        tvSubscribers.clear()
        clientSessions.clear()
        browserPlayers.clear()
        judges.clear()
        pendingPlayers.clear()
    }

    private suspend fun handleClientMessage(session: WebSocketSession, text: String) {
        val event = try {
            json.decodeFromString<GameEvent>(text)
        } catch (e: Exception) {
            return
        }

        // Browser connections are always players, including before they join.
        if (session in browserPlayers && event !is GameEvent.JoinRoom &&
            event !is GameEvent.UpdateDraftAnswer && event !is GameEvent.LockAnswer && event !is GameEvent.SubmitCategoryWager && event !is GameEvent.SubmitSubjectVote && event !is GameEvent.PlayerReady) return

        clientMutationMutex.withLock { when (event) {
            is GameEvent.JoinRoom -> handleJoinRoom(session, event)
            is GameEvent.SubmitCategoryWager -> if (clientSessions[session] == event.teamId) handleCategoryWager(event)
            is GameEvent.HostOfferCategoryWager -> if (!clientSessions.containsKey(session)) offerCategoryWager()
            is GameEvent.UpdateDraftAnswer -> if (clientSessions[session] == event.teamId) handleUpdateDraftAnswer(event)
            is GameEvent.LockAnswer -> if (clientSessions[session] == event.teamId) handleLockAnswer(event)
            is GameEvent.HostStartGame -> if (!clientSessions.containsKey(session)) handleHostStartGame(event)
            is GameEvent.HostOpenSubjectVote -> if (!clientSessions.containsKey(session)) {
                val current=_gameSession.value
                if(current.state==GameState.LOBBY && current.subjectVoting!=null && current.teams.any { it.isConnected }) {
                    _gameSession.value=current.copy(state=GameState.SUBJECT_VOTING); broadcastState()
                }
            }
            is GameEvent.SubmitSubjectVote -> if(clientSessions[session]==event.teamId) handleSubjectVote(event)
            is GameEvent.HostCloseSubjectVote -> if(!clientSessions.containsKey(session)) closeSubjectVote()
            is GameEvent.HostBreakSubjectTie -> if(!clientSessions.containsKey(session)) breakSubjectTie(event)
            is GameEvent.HostBeginCategorySelect -> if (!clientSessions.containsKey(session)) handleHostBeginCategorySelect()
            is GameEvent.HostSelectCategory -> handleHostSelectCategory(session, event)
            is GameEvent.HostNextQuestion -> if (!clientSessions.containsKey(session)) handleHostNextQuestion(event)
            is GameEvent.HostPauseTimer -> if (!clientSessions.containsKey(session)) {
                isTimerPaused = true
                _gameSession.value = _gameSession.value.copy(timerPaused=true)
                broadcastState()
            }
            is GameEvent.HostResumeTimer -> if (!clientSessions.containsKey(session)) {
                isTimerPaused = false
                _gameSession.value = _gameSession.value.copy(timerPaused=false)
                broadcastState()
            }
            is GameEvent.HostStartQuestionTimer -> if (!clientSessions.containsKey(session)) {
                handleHostStartQuestionTimer()
            }
            is GameEvent.HostRevealAnswer -> if (!clientSessions.containsKey(session)) handleHostRevealAnswer()
            is GameEvent.PlayerReady -> if(clientSessions[session]==event.teamId) handlePlayerReady(event)
            is GameEvent.HostJudgeWrittenAnswer -> if(!clientSessions.containsKey(session)) handleWrittenJudgement(event)
            is GameEvent.HostJudgeTextBuzz -> handleHostJudgeTextBuzz(session, event)
            is GameEvent.HostStartTextAnswerTimer -> if (!clientSessions.containsKey(session)) startTextAnswerTimer()
            is GameEvent.HostAdjustScore -> handleHostAdjustScore(event)
            is GameEvent.HostSetScore -> handleHostSetScore(event)
            is GameEvent.HostApproveRejoin -> handleHostApproveRejoin(event)
            is GameEvent.HostSetValidationMode -> handleHostSetValidationMode(event)
            is GameEvent.HostValidateTeam -> handleHostValidateTeam(session, event)
            else -> {}
        } }
    }

    private suspend fun handleJoinRoom(session: WebSocketSession, event: GameEvent.JoinRoom) {
        val currentSession = _gameSession.value
        if (event.roomId != currentSession.roomId || event.teamName.isBlank() ||
            event.teamName.length > 60 || event.sessionToken.isBlank()) {
            sendToSession(session, GameEvent.JoinResponse(false, "Code de partie ou nom d’équipe invalide."))
            return
        }
        if (clientSessions.containsKey(session)) return
        val existingTeam = currentSession.teams.find { it.name.equals(event.teamName, ignoreCase = true) }

        if (existingTeam != null) {
            if (existingTeam.sessionToken == event.sessionToken) {
                val updatedTeams = currentSession.teams.map {
                    if (it.id == existingTeam.id) it.copy(isConnected = true) else it
                }
                _gameSession.value = currentSession.copy(teams = updatedTeams)
                clientSessions[session] = existingTeam.id
                sendToSession(session, GameEvent.JoinResponse(success = true, message = "Connexion rétablie", teamId = existingTeam.id))
                broadcastState()
            } else {
                pendingPlayers[session] = event
                _gameSession.value = currentSession.copy(pendingJoinRequests = (currentSession.pendingJoinRequests + event.teamName).distinct())
                sendToSession(session, GameEvent.JoinResponse(success = false, message = "Nom d’équipe déjà utilisé. Demande envoyée à l’hôte.", requiresHostApproval = true))
                broadcastState()
            }
        } else {
            if (currentSession.requireHostValidation) {
                pendingPlayers[session] = event
                val updatedPending = (currentSession.pendingJoinRequests + event.teamName).distinct()
                _gameSession.value = currentSession.copy(pendingJoinRequests = updatedPending)
                sendToSession(session, GameEvent.JoinResponse(success = false, message = "Validation de l’hôte requise. Demande envoyée.", requiresHostApproval = true))
                broadcastState()
            } else {
                val newTeamId = UUID.randomUUID().toString()
                val newTeam = Team(id = newTeamId, name = event.teamName, sessionToken = event.sessionToken)
                val updatedTeams = currentSession.teams + newTeam
                _gameSession.value = currentSession.copy(teams = updatedTeams)
                clientSessions[session] = newTeamId
                sendToSession(session, GameEvent.JoinResponse(success = true, message = "Vous avez rejoint la partie", teamId = newTeamId))
                broadcastState()
            }
        }
    }

    private fun handleUpdateDraftAnswer(event: GameEvent.UpdateDraftAnswer) {
        val currentSession = _gameSession.value
        if (currentSession.state != GameState.QUESTION_ACTIVE || currentSession.questionReading || currentSession.currentQuestion?.id != event.questionId) return

        val existingSub = currentSession.submissions[event.teamId]
        if (existingSub?.isLocked == true) return

        val newSub = AnswerSubmission(
            teamId = event.teamId,
            questionId = event.questionId,
            answer = event.answer,
            isLocked = false,
            timestamp = System.currentTimeMillis(),
            flipNumberWhenLocked = currentSession.currentFlipNumber
        )
        val newMap = currentSession.submissions + (event.teamId to newSub)
        _gameSession.value = currentSession.copy(submissions = newMap)
        broadcastState()
    }

    @Synchronized
    private fun handleLockAnswer(event: GameEvent.LockAnswer) {
        val currentSession = _gameSession.value
        if (currentSession.state != GameState.QUESTION_ACTIVE || currentSession.questionReading || currentSession.currentQuestion?.id != event.questionId) return
        if (currentSession.submissions[event.teamId]?.isLocked == true) return

        val question = currentSession.currentQuestion
        if(currentSession.currentCategoryAnswerMode==CategoryAnswerMode.WRITTEN) {
            val text=(event.answer as? AnswerValue.TextSelection)?.text?.trim()?.take(240) ?: return
            if(text.isBlank()) return
            val submission=AnswerSubmission(event.teamId,question.id,AnswerValue.TextSelection(text),true,System.currentTimeMillis(),currentSession.currentFlipNumber,currentSession.elapsedSecondsInFlip)
            _gameSession.value=currentSession.copy(submissions=currentSession.submissions+(event.teamId to submission))
            val connected=currentSession.teams.filter { it.isConnected }
            if(connected.isNotEmpty() && connected.all { _gameSession.value.submissions[it.id]?.isLocked==true }) beginWrittenReview()
            else broadcastState()
            return
        }
        if (question.isOralBuzzerQuestion() || (event.answer as? AnswerValue.TextSelection)?.text == "BUZZ") {
            if (event.teamId in currentSession.textBuzzedTeamIds) return
            if (currentSession.submissions.values.any {
                    it.isLocked && it.questionId == question.id && it.isCorrect != false && it.isBuzz()
                }) return
            val buzz = AnswerValue.TextSelection("BUZZ")
            val newSub = AnswerSubmission(
                teamId = event.teamId,
                questionId = question.id,
                answer = buzz,
                isLocked = true,
                timestamp = System.currentTimeMillis(),
                flipNumberWhenLocked = currentSession.currentFlipNumber,
                elapsedSecondsInFlipWhenLocked = currentSession.elapsedSecondsInFlip
            )
            _gameSession.value = currentSession.copy(
                submissions = currentSession.submissions + (event.teamId to newSub),
                buzzerSoundId = currentSession.buzzerSoundId + 1,
                answerTimerTeamId = event.teamId,
                answerTimerRemainingSeconds = null,
                answerTimerRunning = false
            )
            startTextAnswerTimer()
            broadcastState()
            return
        }

        val team = currentSession.teams.find { it.id == event.teamId } ?: return
        val acceptedAnswer = if (question is Question.Wager) {
            val wager = event.answer as? AnswerValue.WagerSelection ?: return
            wager.copy(wageredAmount = wager.wageredAmount.coerceIn(0, team.score.coerceAtLeast(0)))
        } else event.answer

        val newSub = AnswerSubmission(
            teamId = event.teamId,
            questionId = event.questionId,
            answer = acceptedAnswer,
            isLocked = true,
            timestamp = System.currentTimeMillis(),
            flipNumberWhenLocked = currentSession.currentFlipNumber,
            elapsedSecondsInFlipWhenLocked = currentSession.elapsedSecondsInFlip
        )
        val newMap = currentSession.submissions + (event.teamId to newSub)
        _gameSession.value = currentSession.copy(submissions = newMap)

        val activeTeams = currentSession.teams.filter { it.isConnected }
        val allLocked = activeTeams.all { team -> newMap[team.id]?.isLocked == true }
        if (allLocked && activeTeams.isNotEmpty()) {
            stopTimer()
            evaluateQuestionScoresAndReveal()
        } else {
            broadcastState()
        }
    }

    private fun handleHostStartGame(event: GameEvent.HostStartGame) {
        votePackages=if(event.voteSettings==null) emptyList() else GamePackageRepository.packages.filter { pack ->
            !pack.isTestPackage() && GamePackageRepository.categoryNamesFor(pack).any { it in event.categories }
        }
        val settings=event.voteSettings?.let { VoteSettings(it.categories.coerceIn(1,50),it.setsPerCategory.coerceIn(1,50)) }
        val subjects=votePackages.groupBy { it.browseGroup() }.filterValues { it.size >= (settings?.setsPerCategory ?: 1) }.keys.sorted()
        val voting=settings?.takeIf { subjects.isNotEmpty() }?.let {
            SubjectVoting(it.copy(categories=it.categories.coerceAtMost(subjects.size)),subjects)
        }
        soundQuestionId=null; soundedResults=emptyMap();questionHasSound=false;revealedSoundQuestionId=null
        gameTimingConfig = event.timingConfig
        stopTimer()
        stopAnswerTimer()
        isTimerPaused = false
        val previousPlayerSessions = clientSessions.keys.toList()
        clientSessions.clear()
        pendingPlayers.clear()
        if (previousPlayerSessions.isNotEmpty()) {
            serverScope.launch {
                previousPlayerSessions.forEach { socket ->
                    runCatching { socket.close(CloseReason(CloseReason.Codes.NORMAL, "A new game has started")) }
                }
            }
        }

        val selectedCategories = if (event.categories.isNotEmpty()) event.categories else QuestionBankRepository.sampleCategories
        val poolCategories = if(voting!=null) selectedCategories.distinct() else balancedCategoryOrder(
            getRemainingCategories(selectedCategories.distinct(), emptyList()), ::categoryProfileFor)
        val validCategories = poolCategories

        val totalAvailableQuestions = poolCategories.flatMap { cat ->
            QuestionBankRepository.getQuestionsForCategory(cat)
        }.size
        val configuredRounds = totalAvailableQuestions.coerceAtLeast(1)

        val freshRoomId = generateRoomId()
        _gameSession.value = _gameSession.value.copy(
            roomId = freshRoomId,
            subjectVoting=voting,
            answerSoundId=0,answerSound=null,answerSoundClip=null,buzzerSoundId=0,
            state = GameState.LOBBY,
            categoryWagerQuestionId = null,
            categoryWagerLimits = emptyMap(),
            categoryWagers = emptyMap(),
            categoryWagerResults = emptyList(),
            categoryWagerSettled = false,
            categoryWagerResultsShown = false,
            currentCategory = null,
            currentCategoryAnswerMode = null,
            currentCategoryAnswerTimeSeconds = 0,
            currentCategoryQuestionTypes = emptyList(),
            currentCategoryQuestionCount = 0,
            masterCategories = poolCategories,
            availableCategories = validCategories,
            retiredCategories = emptyList(),
            pickerTeamId = null,
            currentQuestion = null,
            teams = emptyList(),
            pendingJoinRequests = emptyList(),
            requireHostValidation = false,
            currentFlipNumber = 0,
            elapsedSecondsInFlip = 0,
            submissions = emptyMap(),
            textBuzzedTeamIds = emptyList(),
            answerTimerTeamId = null,
            answerTimerRemainingSeconds = null,
            answerTimerRunning = false,
            roundNumber = 0,
            totalRounds = configuredRounds,
            timingConfig = event.timingConfig,
            answerTimeSeconds = event.answerTimeSeconds.coerceAtLeast(1),
            categoryRules = event.categoryRules.filterKeys { it in validCategories },
            playedQuestionIds = emptyList()
        )
        broadcastState()
    }

    @Synchronized private fun handleSubjectVote(event: GameEvent.SubmitSubjectVote) {
        val current=_gameSession.value
        val vote=current.subjectVoting ?: return
        if(current.state!=GameState.SUBJECT_VOTING || vote.hostTieBreak || vote.completed || event.round!=vote.round) return
        if(current.teams.none { it.id==event.teamId && it.isConnected }) return
        if(event.subjects.isEmpty() || event.subjects.size>vote.remainingSlots || event.subjects.distinct().size!=event.subjects.size ||
            event.subjects.any { it !in vote.candidates }) return
        _gameSession.value=current.copy(subjectVoting=vote.copy(ballots=vote.ballots + (event.teamId to event.subjects)))
        broadcastState()
    }

    @Synchronized private fun closeSubjectVote() {
        val current=_gameSession.value
        val vote=current.subjectVoting ?: return
        if(current.state!=GameState.SUBJECT_VOTING || vote.hostTieBreak || vote.completed) return
        val next=vote.closeRound()
        _gameSession.value=current.copy(subjectVoting=next)
        if(next.completed) finishSubjectVote(next) else broadcastState()
    }

    @Synchronized private fun breakSubjectTie(event: GameEvent.HostBreakSubjectTie) {
        val current=_gameSession.value
        val vote=current.subjectVoting ?: return
        if(current.state!=GameState.SUBJECT_VOTING || !vote.hostTieBreak || event.subjects.size!=vote.remainingSlots ||
            event.subjects.distinct().size!=event.subjects.size || event.subjects.any { it !in vote.candidates }) return
        finishSubjectVote(vote.copy(selected=vote.selected+event.subjects,completed=true,hostTieBreak=false))
    }

    private fun finishSubjectVote(vote: SubjectVoting) {
        val packs=votePackages.filter { it.browseGroup() in vote.selected }
        val byId=packs.associateBy { it.id }
        val usage=importedPackagesDirectory?.parentFile?.let { HostReviewStore(File(it,"host-review.json")).read().usage }.orEmpty()
        val chosen=selectBalancedPackages(packs.map { it.id },vote.selected.size*vote.settings.setsPerCategory,usage,{ id ->
            val pack=byId.getValue(id)
            val formats=GamePackageRepository.categoryNamesFor(pack).map { categoryProfileFor(it).format }.distinct()
            CategoryProfile(formats.singleOrNull() ?: CategoryFormat.MIXED,pack.browseGroup())
        },subjectLimit=vote.settings.setsPerCategory).map(byId::getValue)
        val combined=combineGamePackages(chosen,GamePackageRepository::categoryNamesFor) { QuestionBankRepository.getQuestionsForCategory(it).size }
        val categories=balancedCategoryOrder(combined.categories,::categoryProfileFor)
        _gameSession.value=_gameSession.value.copy(state=GameState.LOBBY,subjectVoting=vote,
            masterCategories=categories,availableCategories=categories,totalRounds=combined.totalQuestions,categoryRules=combined.categoryRules)
        broadcastState()
    }

    @Synchronized private fun handleHostBeginCategorySelect() {
        if(_gameSession.value.subjectVoting?.completed==false) return
        val session = _gameSession.value
        if (showWagerResultsBeforeContinuing()) return
        if (session.state !in setOf(GameState.LOBBY, GameState.REVEAL_ANSWER,
                GameState.ROUND_SUMMARY, GameState.CATEGORY_SELECT, GameState.WAGER_RESULTS)) return
        val next = session.masterCategories.asSequence()
            .filterNot { it in session.retiredCategories }
            .flatMap { QuestionBankRepository.getQuestionsForCategory(it).asSequence() }
            .firstOrNull { it.id !in session.playedQuestionIds }
        if (next != null && session.playedQuestionIds.size < session.totalRounds) {
            introduceCategory(next, next.category)
        } else {
            _gameSession.value = session.copy(state = GameState.GAME_ENDED)
            broadcastState()
        }
    }

    private fun handleHostSelectCategory(socket: WebSocketSession, event: GameEvent.HostSelectCategory) {
        val currentSession = _gameSession.value
        if (currentSession.state != GameState.CATEGORY_SELECT) return
        val requestingTeamId = clientSessions[socket]
        val teamId = requestingTeamId
        val highestScore = currentSession.teams.maxOfOrNull { it.score } ?: return
        if (teamId != null && teamId != currentSession.pickerTeamId) return
        if (teamId != null && currentSession.teams.find { it.id == teamId }?.score != highestScore) return
        if (event.category !in currentSession.availableCategories) return

        val newlyRetired = currentSession.availableCategories.filter { it != event.category }
        val retiredQuestionCount = newlyRetired.sumOf { QuestionBankRepository.getQuestionsForCategory(it).size }

        if (currentSession.playedQuestionIds.size >= currentSession.totalRounds) {
            _gameSession.value = currentSession.copy(state = GameState.GAME_ENDED)
            broadcastState()
            return
        }

        val categoryQuestions = QuestionBankRepository.getQuestionsForCategory(event.category)
        val unplayedInCategory = categoryQuestions.filter { !currentSession.playedQuestionIds.contains(it.id) }

        val question = unplayedInCategory.firstOrNull() ?: QuestionBankRepository.sampleQuestions.find { q ->
            currentSession.masterCategories.contains(q.category) && !currentSession.playedQuestionIds.contains(q.id)
        }

        if (question != null) {
            _gameSession.value = currentSession.copy(
                retiredCategories = (currentSession.retiredCategories + newlyRetired).distinct(),
                totalRounds = (currentSession.totalRounds - retiredQuestionCount).coerceAtLeast(currentSession.playedQuestionIds.size + 1)
            )
            introduceCategory(question, event.category)
        } else {
            _gameSession.value = currentSession.copy(state = GameState.GAME_ENDED)
            broadcastState()
        }
    }

    @Synchronized
    private fun handleHostNextQuestion(event: GameEvent.HostNextQuestion) {
        if(_gameSession.value.subjectVoting?.completed==false) return
        val currentSession = _gameSession.value
        if (showWagerResultsBeforeContinuing()) return

        if (currentSession.state in setOf(GameState.CATEGORY_INTRO, GameState.WAGER_OPEN)) {
            val question = currentSession.currentQuestion ?: return
            startQuestion(question, currentSession.currentCategory ?: question.category)
            return
        }

        if (currentSession.playedQuestionIds.size >= currentSession.totalRounds) {
            _gameSession.value = currentSession.copy(state = GameState.GAME_ENDED)
            broadcastState()
            return
        }

        val allowedCategories = if (currentSession.masterCategories.isNotEmpty()) {
            currentSession.masterCategories
        } else {
            QuestionBankRepository.sampleCategories
        }

        val nextInCurrentCategory = currentSession.currentCategory?.let { category ->
            QuestionBankRepository.getQuestionsForCategory(category)
                .firstOrNull { it.id !in currentSession.playedQuestionIds }
        }
        val nextQuestion = nextInCurrentCategory ?: QuestionBankRepository.sampleQuestions.firstOrNull { q ->
            allowedCategories.contains(q.category) && q.id !in currentSession.playedQuestionIds
        }

        if (nextQuestion != null) {
            startQuestion(nextQuestion, nextQuestion.category)
        } else {
            _gameSession.value = currentSession.copy(state = GameState.GAME_ENDED)
            broadcastState()
        }
    }

    private fun startQuestion(question: Question, category: String) {
        stopTimer()
        stopAnswerTimer()
        val currentSession = _gameSession.value
        val wagerApplies = currentSession.categoryWagerQuestionId == question.id && !currentSession.categoryWagerSettled
        val updatedPlayedIds = currentSession.playedQuestionIds + question.id
        val newRoundNumber = updatedPlayedIds.size

        val categoryRules = currentSession.categoryRules[category]
        val configured = categoryRules?.timingConfig ?: gameTimingConfig ?: currentSession.timingConfig.also { gameTimingConfig=it }
        val compatibleQuestion = if (question is Question.Wager) question.subQuestion.copy(
            id = question.id, category = question.category, prompt = question.prompt,
            imageUrl = question.imageUrl ?: question.subQuestion.imageUrl,
            basePoints = question.basePoints, penaltyPoints = question.penaltyPoints
        ) else question
        val activeQuestion = compatibleQuestion.withRandomVariant().withChronologyCards()
        val reading = activeQuestion.isChronologyQuestion()
        val effectiveConfig = when {
            activeQuestion is Question.GuessWho -> configured.copy(secondsPerFlip=20,maxFlips=activeQuestion.clues.size-1,pointsDecayPerSecond=null)
            activeQuestion.isChronologyQuestion() -> configured.copy(secondsPerFlip=maxOf(configured.secondsPerFlip,
                (45 + configured.maxFlips) / (configured.maxFlips + 1)))
            activeQuestion is Question.MultipleChoice || activeQuestion is Question.SpeedRace || activeQuestion is Question.MapPin && activeQuestion.options.isNotEmpty() ->
                configured.copy(secondsPerFlip=activeQuestion.basePoints.coerceAtLeast(1),maxFlips=0,pointsDecayPerFlip=null,pointsDecayPerSecond=1)
            else -> configured
        }
        isTimerPaused = false

        _gameSession.value = currentSession.copy(
            state = GameState.QUESTION_ACTIVE,
            timingConfig = effectiveConfig,
            answerTimeSeconds = categoryRules?.answerTimeSeconds ?: currentSession.answerTimeSeconds,
            currentCategory = category,
            currentQuestion = activeQuestion,
            questionReading = reading,
            readyTeamIds = emptyList(),
            timerPaused = false,
            categoryWagerQuestionId = currentSession.categoryWagerQuestionId.takeIf { wagerApplies },
            categoryWagerLimits = if (wagerApplies) currentSession.categoryWagerLimits else emptyMap(),
            categoryWagers = if (wagerApplies) currentSession.categoryWagers else emptyMap(),
            categoryWagerResults = emptyList(),
            categoryWagerSettled = false,
            categoryWagerResultsShown = false,
            currentFlipNumber = 0,
            elapsedSecondsInFlip = 0,
            submissions = emptyMap(),
            textBuzzedTeamIds = emptyList(),
            answerTimerTeamId = null,
            answerTimerRemainingSeconds = null,
            answerTimerRunning = false,
            playedQuestionIds = updatedPlayedIds,
            roundNumber = newRoundNumber
        )
        broadcastState()
        if (!reading) startTimer(effectiveConfig)
    }

    private fun startTimer(config: HourglassConfig) {
        timerJob?.cancel()
        isTimerPaused = false
        timerJob = serverScope.launch {
            while (isActive) {
                delay(1000)
                if (!advanceQuestionTimer(config)) break
            }
        }
    }

    @Synchronized
    private fun advanceQuestionTimer(config: HourglassConfig): Boolean {
        val session = _gameSession.value
        if (session.state != GameState.QUESTION_ACTIVE) return false
        if (session.questionReading || isTimerPaused || session.currentCategoryAnswerMode!=CategoryAnswerMode.WRITTEN && session.submissions.values.any {
                it.isLocked && it.isCorrect != false && it.isBuzz()
            }) return true
        var newElapsed = session.elapsedSecondsInFlip + 1
        var newFlip = session.currentFlipNumber
        if (newElapsed >= config.secondsPerFlip) {
            newElapsed = 0
            newFlip += 1
        }
        if(session.currentCategoryAnswerMode==CategoryAnswerMode.WRITTEN && (session.currentQuestion is Question.GuessWho && newFlip!=session.currentFlipNumber || newFlip>config.maxFlips)) {
            _gameSession.value=session.copy(elapsedSecondsInFlip=config.secondsPerFlip)
            beginWrittenReview()
            return false
        }
        if (newFlip > config.maxFlips) {
            _gameSession.value = session.copy(currentFlipNumber = config.maxFlips,
                elapsedSecondsInFlip = config.secondsPerFlip)
            evaluateQuestionScoresAndReveal()
            return false
        }
        val nextClue = session.currentQuestion is Question.GuessWho && newFlip != session.currentFlipNumber
        _gameSession.value = session.copy(currentFlipNumber = newFlip, elapsedSecondsInFlip = newElapsed,
            questionReading = false,
            readyTeamIds = if(nextClue) emptyList() else session.readyTeamIds,
            submissions = if (nextClue) session.submissions.filterValues { it.isCorrect != false } else session.submissions,
            textBuzzedTeamIds = if (nextClue) emptyList() else session.textBuzzedTeamIds)
        broadcastState()
        return true
    }

    private fun stopTimer() {
        timerJob?.cancel()
        timerJob = null
    }

    @Synchronized
    private fun handleHostStartQuestionTimer() {
        val current = _gameSession.value
        if(current.state!=GameState.QUESTION_ACTIVE || !current.questionReading) return
        _gameSession.value=current.copy(questionReading=false,timerPaused=false)
        startTimer(current.timingConfig)
        broadcastState()
    }

    @Synchronized
    private fun handlePlayerReady(event: GameEvent.PlayerReady) {
        val current=_gameSession.value
        if(current.state!=GameState.QUESTION_ACTIVE || !current.questionReading || current.currentQuestion?.isChronologyQuestion()!=true ||
            current.currentQuestion.id!=event.questionId || current.currentFlipNumber!=event.clueIndex ||
            current.teams.none { it.id==event.teamId && it.isConnected }) return
        _gameSession.value=current.copy(readyTeamIds=(current.readyTeamIds+event.teamId).distinct())
        broadcastState()
    }

    @Synchronized
    private fun beginWrittenReview() {
        val current=_gameSession.value
        if(current.state!=GameState.QUESTION_ACTIVE || current.currentCategoryAnswerMode!=CategoryAnswerMode.WRITTEN) return
        stopTimer();stopAnswerTimer()
        _gameSession.value=current.copy(state=GameState.ANSWER_REVIEW,questionReading=false,timerPaused=false)
        if(_gameSession.value.pendingWrittenAnswers().isEmpty()) finishWrittenReview() else broadcastState()
    }

    @Synchronized
    private fun handleWrittenJudgement(event: GameEvent.HostJudgeWrittenAnswer) {
        val current=_gameSession.value
        val question=current.currentQuestion ?: return
        if(current.state!=GameState.ANSWER_REVIEW || current.currentCategoryAnswerMode!=CategoryAnswerMode.WRITTEN || question.id!=event.questionId) return
        val submission=current.pendingWrittenAnswers().firstOrNull { it.teamId==event.teamId } ?: return
        val reward=if(event.correct) current.timingConfig.calculateScore(question.basePoints,submission.flipNumberWhenLocked,submission.elapsedSecondsInFlipWhenLocked)
            else -(if(question is Question.GuessWho) question.wrongAnswerPenalty() else question.penaltyPoints)
        _gameSession.value=current.copy(teams=current.teams.map { if(it.id==event.teamId) it.copy(score=it.score+reward) else it },
            submissions=current.submissions+(event.teamId to submission.copy(isCorrect=event.correct)))
        broadcastState()
        if(_gameSession.value.pendingWrittenAnswers().isEmpty()) finishWrittenReview()
    }

    private fun finishWrittenReview() {
        val current=_gameSession.value
        val question=current.currentQuestion ?: return
        val correct=current.submissions.values.any { it.questionId==question.id && it.isCorrect==true }
        if(question is Question.GuessWho && !correct && current.currentFlipNumber<current.timingConfig.maxFlips) {
            _gameSession.value=current.copy(state=GameState.QUESTION_ACTIVE,currentFlipNumber=current.currentFlipNumber+1,
                elapsedSecondsInFlip=0,questionReading=false,readyTeamIds=emptyList(),submissions=emptyMap(),textBuzzedTeamIds=emptyList())
            startTimer(current.timingConfig)
        } else _gameSession.value=current.copy(state=GameState.REVEAL_ANSWER).settleCategoryWagers()
        broadcastState()
    }

    private fun stopAnswerTimer() {
        answerTimerJob?.cancel()
        answerTimerJob = null
    }

    @Synchronized
    private fun startTextAnswerTimer() {
        val session = _gameSession.value
        val question = session.currentQuestion ?: return
        if (session.state != GameState.QUESTION_ACTIVE || session.answerTimerRunning) return
        val seconds = session.answerTimeSeconds
        if (seconds <= 0) return
        val selected = session.submissions.values.firstOrNull {
            it.isLocked && it.questionId == question.id && it.isCorrect != false && it.isBuzz()
        } ?: return
        stopAnswerTimer()
        _gameSession.value = session.copy(
            answerTimerTeamId = selected.teamId,
            answerTimerRemainingSeconds = seconds,
            answerTimerRunning = true
        )
        broadcastState()
        answerTimerJob = serverScope.launch {
            repeat(seconds) {
                delay(1000)
                synchronized(this@GameServer) {
                    val current = _gameSession.value
                    if (current.state != GameState.QUESTION_ACTIVE || !current.answerTimerRunning ||
                        current.answerTimerTeamId != selected.teamId || current.currentQuestion?.id != question.id) return@launch
                    val remaining = (current.answerTimerRemainingSeconds ?: return@launch) - 1
                    if (remaining > 0) {
                        _gameSession.value = current.copy(answerTimerRemainingSeconds = remaining)
                        broadcastState()
                    } else {
                        val submission = current.submissions[selected.teamId]
                            ?.takeIf { it.isLocked && it.questionId == question.id && it.isCorrect != false && it.isBuzz() }
                            ?: return@launch
                        _gameSession.value = current.rejectOralAnswer(selected.teamId).copy(answerTimerRemainingSeconds=0)
                        broadcastState()
                        if (hasPointsTimerExpired(_gameSession.value)) evaluateQuestionScoresAndReveal()
                        return@launch
                    }
                }
            }
        }
    }

    private fun hasPointsTimerExpired(session: GameSession): Boolean =
        session.currentFlipNumber >= session.timingConfig.maxFlips &&
            session.elapsedSecondsInFlip >= session.timingConfig.secondsPerFlip

    @Synchronized
    private fun evaluateQuestionScoresAndReveal() {
        val session = _gameSession.value
        if (session.state != GameState.QUESTION_ACTIVE) return
        val question = session.currentQuestion ?: return
        if(session.currentCategoryAnswerMode==CategoryAnswerMode.WRITTEN) { beginWrittenReview();return }
        stopAnswerTimer()

        val updatedSubmissions = session.submissions.mapValues { (_, sub) ->
            if (!sub.isLocked || sub.questionId != question.id) sub
            else if ((sub.answer as? AnswerValue.TextSelection)?.text == "BUZZ") sub.copy(isCorrect = sub.isCorrect ?: false)
            else sub.copy(isCorrect = evaluateAnswer(question, sub.answer))
        }
        val updatedTeams = session.teams.map { team ->
            val sub = updatedSubmissions[team.id]
            if (sub != null && sub.isLocked && sub.questionId == question.id) {
                if (question.isOralBuzzerQuestion() || (sub.answer as? AnswerValue.TextSelection)?.text == "BUZZ") return@map team
                val isCorrect = evaluateAnswer(question, sub.answer)
                val pointsAwarded = if (isCorrect) {
                    val basePoints = getEffectiveBasePoints(question, sub.answer)
                    session.timingConfig.calculateScore(
                        basePoints,
                        sub.flipNumberWhenLocked,
                        sub.elapsedSecondsInFlipWhenLocked
                    )
                } else {
                    if (question is Question.Wager) {
                        -(sub.answer as? AnswerValue.WagerSelection)?.wageredAmount.orZero()
                    } else {
                        -question.penaltyPoints
                    }
                }
                team.copy(score = team.score + pointsAwarded)
            } else {
                team
            }
        }

        _gameSession.value = session.copy(
            state = GameState.REVEAL_ANSWER,
            teams = updatedTeams,
            submissions = updatedSubmissions,
            answerTimerTeamId = null,
            answerTimerRemainingSeconds = null,
            answerTimerRunning = false
        ).settleCategoryWagers()
        broadcastState()
    }

    private fun getEffectiveBasePoints(question: Question, answer: AnswerValue): Int {
        return when (question) {
            is Question.Wager -> {
                (answer as? AnswerValue.WagerSelection)?.wageredAmount?.coerceAtLeast(0) ?: 0
            }
            else -> question.basePoints
        }
    }

    private fun evaluateAnswer(question: Question, answer: AnswerValue): Boolean {
        return when (question) {
            is Question.MultipleChoice -> {
                question.choiceVerdict(answer) == true
            }
            is Question.Ordering -> {
                val userOrder = (answer as? AnswerValue.OrderingSelection)?.orderedItemIds ?: emptyList()
                userOrder == question.correctOrderIds
            }
            is Question.TextAnswer -> {
                val userText = (answer as? AnswerValue.TextSelection)?.text?.trim()?.lowercase() ?: ""
                if (userText.isBlank()) false else {
                    question.acceptableAnswers.any { acc ->
                        val cleanAcc = acc.trim().lowercase()
                        userText == cleanAcc || (question.allowFuzzyMatch && (userText.contains(cleanAcc) || cleanAcc.contains(userText)))
                    }
                }
            }
            is Question.GuessWho -> false // Oral answer is judged by the host, never auto-scored.
            is Question.MapPin -> {
                val mapPin = answer as? AnswerValue.MapPinSelection ?: return false
                if (question.options.isNotEmpty()) {
                    return question.choiceVerdict(answer) == true
                }
                when (val target = question.target) {
                    is Question.MapTarget.CenterRadius -> {
                        val dist = hypot(mapPin.xRatio - target.xRatio, mapPin.yRatio - target.yRatio)
                        dist <= target.maxDistanceRatio
                    }
                    is Question.MapTarget.BoundingBox -> {
                        mapPin.xRatio in target.minXRatio..target.maxXRatio && mapPin.yRatio in target.minYRatio..target.maxYRatio
                    }
                    null -> false
                }
            }
            is Question.Wager -> {
                question.choiceVerdict(answer) == true
            }
            is Question.SpeedRace -> {
                question.choiceVerdict(answer) == true
            }
        }
    }

    private fun handleHostRevealAnswer() {
        val session = _gameSession.value
        if (session.state != GameState.QUESTION_ACTIVE) return
        if (session.currentCategoryAnswerMode!=CategoryAnswerMode.WRITTEN && session.currentQuestion?.isOralBuzzerQuestion() == true && session.submissions.values.any { it.isLocked && it.isCorrect != false && it.isBuzz() }) return
        if (session.questionReading) return
        stopTimer()
        evaluateQuestionScoresAndReveal()
    }

    private fun introduceCategory(question: Question, category: String) {
        stopTimer()
        stopAnswerTimer()
        val currentSession = _gameSession.value
        val categoryPackage = QuestionBankRepository.getCategoryPackage(category)
        val rules = currentSession.categoryRules[category]
        val answerSeconds = rules?.answerTimeSeconds ?: currentSession.answerTimeSeconds
        val questionCount = QuestionBankRepository.getQuestionsForCategory(category)
            .count { it.id !in currentSession.playedQuestionIds }
        _gameSession.value = currentSession.copy(
            state = GameState.CATEGORY_INTRO,
            categoryWagerQuestionId = null,
            categoryWagerLimits = emptyMap(),
            categoryWagers = emptyMap(),
            categoryWagerResults = emptyList(),
            categoryWagerSettled = false,
            categoryWagerResultsShown = false,
            timingConfig = rules?.timingConfig ?: currentSession.timingConfig,
            answerTimeSeconds = answerSeconds,
            currentCategory = category,
            currentCategoryAnswerMode = categoryPackage?.answerMode ?: CategoryAnswerMode.SIMULTANEOUS,
            currentCategoryAnswerTimeSeconds = answerSeconds,
            currentCategoryQuestionTypes = categoryPackage?.questionTypes.orEmpty(),
            currentCategoryQuestionCount = questionCount,
            currentQuestion = question,
            currentFlipNumber = 0,
            elapsedSecondsInFlip = 0,
            submissions = emptyMap(),
            textBuzzedTeamIds = emptyList(),
            answerTimerTeamId = null,
            answerTimerRemainingSeconds = null,
            answerTimerRunning = false
        )
        broadcastState()
    }

    @Synchronized
    private fun offerCategoryWager() {
        val session = _gameSession.value
        if (session.state != GameState.CATEGORY_INTRO) return
        val question = session.currentQuestion ?: return
        val maximum = maximumCategoryReward(session)
        _gameSession.value = session.copy(state = GameState.WAGER_OPEN,
            categoryWagerQuestionId = question.id,
            categoryWagerLimits = session.teams.associate { it.id to categoryWagerLimit(it.score, maximum) },
            categoryWagers = emptyMap())
        broadcastState()
    }

    @Synchronized
    private fun handleCategoryWager(event: GameEvent.SubmitCategoryWager) {
        val session = _gameSession.value
        if (session.state != GameState.WAGER_OPEN || event.questionId != session.categoryWagerQuestionId || event.teamId in session.categoryWagers) return
        val limit = session.categoryWagerLimits[event.teamId] ?: return
        if (event.amount !in 0..limit) return
        _gameSession.value = session.copy(categoryWagers = session.categoryWagers + (event.teamId to event.amount))
        broadcastState()
    }

    private fun showWagerResultsBeforeContinuing(): Boolean {
        val session = _gameSession.value
        if (session.state !in setOf(GameState.REVEAL_ANSWER, GameState.ROUND_SUMMARY) ||
            !session.categoryWagerSettled || session.categoryWagerResultsShown) return false
        _gameSession.value = session.copy(state = GameState.WAGER_RESULTS, categoryWagerResultsShown = true)
        broadcastState()
        return true
    }

    private fun Int?.orZero(): Int = this ?: 0

    private fun maximumCategoryReward(session: GameSession): Int =
        QuestionBankRepository.getQuestionsForCategory(session.currentCategory.orEmpty())
            .filter { it.id !in session.playedQuestionIds }.maxOfOrNull { it.basePoints }
            ?: session.currentQuestion?.basePoints ?: 0

    @Synchronized
    private fun handleHostJudgeTextBuzz(socket: WebSocketSession, event: GameEvent.HostJudgeTextBuzz) {
        if (clientSessions.containsKey(socket)) return
        val session = _gameSession.value
        if(session.currentCategoryAnswerMode==CategoryAnswerMode.WRITTEN) return
        val question = session.currentQuestion ?: return
        if (session.state != GameState.QUESTION_ACTIVE) return
        val submission = session.submissions[event.teamId]?.takeIf { it.isLocked && it.questionId == question.id && it.isCorrect != false && it.isBuzz() } ?: return

        if (event.correct) {
            val points = session.timingConfig.calculateScore(
                question.basePoints,
                submission.flipNumberWhenLocked,
                submission.elapsedSecondsInFlipWhenLocked
            )
            val teams = session.teams.map { team ->
                if (team.id == event.teamId) team.copy(score = team.score + points) else team
            }
            stopTimer()
            stopAnswerTimer()
            _gameSession.value = session.copy(
                state = GameState.REVEAL_ANSWER,
                teams = teams,
                submissions = session.submissions + (event.teamId to submission.copy(isCorrect = true)),
                answerTimerTeamId = null,
                answerTimerRemainingSeconds = null,
                answerTimerRunning = false
            ).settleCategoryWagers()
        } else {
            stopAnswerTimer()
            val rejected = session.rejectOralAnswer(event.teamId)
            _gameSession.value = rejected
            if (hasPointsTimerExpired(rejected)) {
                evaluateQuestionScoresAndReveal()
                return
            }
        }
        broadcastState()
    }

    private fun markTeamDisconnected(teamId: String) {
        if (clientSessions.containsValue(teamId)) return
        val currentSession = _gameSession.value
        val updatedTeams = currentSession.teams.map { team ->
            if (team.id == teamId) team.copy(isConnected = false) else team
        }
        if (updatedTeams != currentSession.teams) {
            _gameSession.value = currentSession.copy(teams = updatedTeams)
            broadcastState()
        }
    }

    private fun handleHostAdjustScore(event: GameEvent.HostAdjustScore) {
        val currentSession = _gameSession.value
        val updatedTeams = currentSession.teams.map { team ->
            if (team.id == event.teamId) {
                team.copy(score = team.score + event.deltaPoints)
            } else team
        }
        _gameSession.value = currentSession.copy(teams = updatedTeams)
        broadcastState()
    }

    private fun handleHostSetScore(event: GameEvent.HostSetScore) {
        val currentSession = _gameSession.value
        val updatedTeams = currentSession.teams.map { team ->
            if (team.id == event.teamId) {
                team.copy(score = event.newScore)
            } else team
        }
        _gameSession.value = currentSession.copy(teams = updatedTeams)
        broadcastState()
    }

    private fun handleHostApproveRejoin(event: GameEvent.HostApproveRejoin) {
        val currentSession = _gameSession.value
        val updatedTeams = currentSession.teams.map { team ->
            if (team.name.equals(event.teamName, ignoreCase = true)) {
                team.copy(sessionToken = event.newSessionToken, isConnected = true)
            } else team
        }
        _gameSession.value = currentSession.copy(teams = updatedTeams)
        broadcastState()
    }

    private fun handleHostSetValidationMode(event: GameEvent.HostSetValidationMode) {
        _gameSession.value = _gameSession.value.copy(requireHostValidation = event.requireValidation)
        broadcastState()
    }

    private suspend fun handleHostValidateTeam(session: WebSocketSession, event: GameEvent.HostValidateTeam) {
        if (clientSessions.containsKey(session)) return
        val currentSession = _gameSession.value
        val request = pendingPlayers.entries.firstOrNull { it.value.teamName.equals(event.teamName, ignoreCase = true) } ?: return
        pendingPlayers.remove(request.key)
        val updatedPending = currentSession.pendingJoinRequests.filter { !it.equals(event.teamName, ignoreCase = true) }

        if (event.approve) {
            val existing = currentSession.teams.find { it.name.equals(event.teamName, ignoreCase = true) }
            val newTeamId = existing?.id ?: UUID.randomUUID().toString()
            val newTeam = Team(id = newTeamId, name = request.value.teamName, score = existing?.score ?: 0, sessionToken = request.value.sessionToken)
            val updatedTeams = currentSession.teams.filterNot { it.id == newTeamId } + newTeam
            _gameSession.value = currentSession.copy(teams = updatedTeams, pendingJoinRequests = updatedPending)
            clientSessions[request.key] = newTeamId
            sendToSession(request.key, GameEvent.JoinResponse(success = true, message = "L’hôte a accepté votre demande", teamId = newTeamId))
        } else {
            _gameSession.value = currentSession.copy(pendingJoinRequests = updatedPending)
            sendToSession(request.key, GameEvent.JoinResponse(success = false, message = "L’hôte a refusé votre demande."))
        }
        broadcastState()
    }

    @Synchronized
    private fun broadcastState() {
        val readiness=_gameSession.value
        val connectedReady=readiness.teams.filter { it.isConnected }
        if(readiness.state==GameState.QUESTION_ACTIVE && readiness.questionReading && readiness.currentQuestion?.isChronologyQuestion()==true &&
            connectedReady.isNotEmpty() && connectedReady.all { it.id in readiness.readyTeamIds }) {
            _gameSession.value=readiness.copy(questionReading=false,timerPaused=false)
            startTimer(readiness.timingConfig)
        }
        val soundState=_gameSession.value
        val qid=soundState.currentQuestion?.id
        if(qid!=soundQuestionId) { soundQuestionId=qid; soundedResults=emptyMap();questionHasSound=false }
        val results=soundState.submissions.filterValues { it.questionId==qid && it.isLocked }.mapValues { it.value.isCorrect }
        val changes=results.filter { (id,result) -> result!=null && soundedResults[id]!=result }.values
        val firstReveal=soundState.state==GameState.REVEAL_ANSWER && qid!=null && qid!=revealedSoundQuestionId
        if(firstReveal) revealedSoundQuestionId=qid
        if(changes.isNotEmpty() || firstReveal && !questionHasSound) {
            questionHasSound=true
            val outcome=if(changes.any { it==true }) "good" else "bad"
            _gameSession.value=soundState.copy(answerSoundId=soundState.answerSoundId+1,answerSound=outcome,
                answerSoundClip=com.example.triviaparty.model.AnswerReactions.choose(outcome,soundState.answerSoundClip))
        }
        soundedResults=results
        val current = _gameSession.value
        if (current.state == GameState.WAGER_OPEN) {
            val maximum = maximumCategoryReward(current)
            val limits = current.teams.associate { it.id to categoryWagerLimit(it.score, maximum) }
            _gameSession.value = current.copy(categoryWagerLimits = limits,
                categoryWagers = current.categoryWagers.filterKeys { it in limits }
                    .mapValues { (id, amount) -> amount.coerceIn(0, limits.getValue(id)) })
        }
        val networkSession = LocalMediaUrls.networkSession(_gameSession.value, port)
        val broadcastEvent: GameEvent = GameEvent.RoomStateBroadcast(networkSession)
        val text = json.encodeToString(broadcastEvent)
        // Chain delivery jobs so an older validation snapshot cannot overwrite its next phase.
        val previousBroadcast = broadcastJob
        broadcastJob = serverScope.launch {
            previousBroadcast?.join()
            judges.forEach { judge ->
                try { judge.send(Frame.Text(judgeStateText(networkSession))) } catch (_: Exception) { judges.remove(judge) }
            }
            val safeTvSnapshot = TvState.from(networkSession).encode()
            tvSubscribers.forEach { session ->
                try {
                    session.send(Frame.Text(safeTvSnapshot))
                } catch (_: Exception) {
                    tvSubscribers.remove(session)
                }
            }
            subscribers.forEach { session ->
                try {
                    session.send(Frame.Text(if (session in browserPlayers) browserStateText(networkSession, clientSessions[session]) else text))
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }

    private suspend fun sendToSession(session: WebSocketSession, event: GameEvent) {
        try {
            val text = if (session in browserPlayers && event is GameEvent.RoomStateBroadcast)
                browserStateText(event.session, clientSessions[session]) else json.encodeToString(event)
            session.send(Frame.Text(text))
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun judgeStateText(state: GameSession): String {
        val question = state.currentQuestion
        val active = state.state == GameState.QUESTION_ACTIVE
        val team = state.answerTimerTeamId?.let { id -> state.teams.find { it.id == id } }
        val solution = if (!active) "" else when (question) {
            is Question.GuessWho -> question.acceptableAnswers.joinToString(" / ")
            is Question.TextAnswer -> question.acceptableAnswers.joinToString(" / ")
            else -> ""
        }
        return JsonObject(mapOf(
            "questionId" to JsonPrimitive(question?.id.orEmpty()),
            "phase" to JsonPrimitive(state.state.name),
            "answer" to JsonPrimitive(solution),
            "teamId" to JsonPrimitive(team?.id.orEmpty()),
            "teamName" to JsonPrimitive(team?.name.orEmpty()),
            "answering" to JsonPrimitive(active && state.answerTimerRunning),
            "reading" to JsonPrimitive(state.questionReading),
            "paused" to JsonPrimitive(state.timerPaused),
            "seconds" to JsonPrimitive(if (state.answerTimerRunning) state.answerTimerRemainingSeconds ?: state.answerTimeSeconds else state.timingConfig.secondsPerFlip-state.elapsedSecondsInFlip),
            "penalty" to JsonPrimitive((question as? Question.GuessWho)?.wrongAnswerPenalty() ?: 0)
        )).toString()
    }

    private fun browserStateText(state: GameSession, teamId: String?): String {
        val stateJson = json.encodeToJsonElement(GameSession.serializer(), state).jsonObject.toMutableMap()
        if(state.questionReading && state.currentQuestion?.isChronologyQuestion()==true) stateJson["readingQuestionId"]=JsonPrimitive(state.currentQuestion.id)
        stateJson["teams"] = JsonArray(state.teams.map { team ->
            JsonObject(json.encodeToJsonElement(Team.serializer(), team).jsonObject.filterKeys { it != "sessionToken" })
        })
        stateJson["currentQuestion"] = state.currentQuestion?.takeUnless {
            state.questionReading || state.state in setOf(GameState.LOBBY, GameState.SUBJECT_VOTING, GameState.CATEGORY_SELECT, GameState.CATEGORY_INTRO, GameState.WAGER_OPEN, GameState.WAGER_RESULTS)
        }?.let { question ->
            val fields = mutableMapOf<String, kotlinx.serialization.json.JsonElement>("id" to JsonPrimitive(question.id))
            fields["type"] = JsonPrimitive(when (question) {
                is Question.MultipleChoice -> "multipleChoice"
                is Question.SpeedRace -> "speedRace"
                is Question.TextAnswer -> "textAnswer"
                is Question.GuessWho -> "guessWho"
                is Question.Ordering -> "ordering"
                is Question.MapPin -> "mapChoice"
                is Question.Wager -> "wager"
            })
            val choices = when (question) {
                is Question.MultipleChoice -> question.options
                is Question.SpeedRace -> question.subQuestion.options
                else -> null
            }
            if (choices != null) {
                fields["type"] = JsonPrimitive(if (question is Question.SpeedRace) "speedRace" else "multipleChoice")
                fields["options"] = JsonArray(choices.map { JsonPrimitive(it) })
            }
            if (question is Question.MapPin) {
                fields["options"] = JsonArray(question.options.map { JsonPrimitive(it.label) })
                fields["mapOptions"] = JsonArray(question.options.map { option ->
                    JsonObject(mapOf("xRatio" to JsonPrimitive(option.xRatio), "yRatio" to JsonPrimitive(option.yRatio)))
                })
            }
            if (question is Question.Ordering) {
                // Public event cards only. The chronological answer stays on the host.
                fields["items"] = JsonArray(question.items.map { item ->
                    JsonObject(mapOf("id" to JsonPrimitive(item.id), "text" to JsonPrimitive(item.text)))
                })
            }
            JsonObject(fields)
        } ?: kotlinx.serialization.json.JsonNull
        stateJson["submissions"] = JsonObject(stateJson.getValue("submissions").jsonObject.filterKeys { it == teamId })
        stateJson["categoryWagers"] = JsonObject(stateJson.getValue("categoryWagers").jsonObject.filterKeys { it == teamId })
        stateJson["categoryWagerLimits"] = JsonObject(stateJson.getValue("categoryWagerLimits").jsonObject.filterKeys { it == teamId })
        state.subjectVoting?.let { vote ->
            val publicVote=json.encodeToJsonElement(SubjectVoting.serializer(),vote).jsonObject.toMutableMap()
            publicVote["ballots"]=JsonObject(publicVote.getValue("ballots").jsonObject.filterKeys { it==teamId })
            stateJson["subjectVoting"]=JsonObject(publicVote)
        }
        state.submissions.values.firstOrNull { it.isLocked && it.isCorrect != false && it.isBuzz() }?.let {
            stateJson["buzzActiveTeamId"] = JsonPrimitive(it.teamId)
        }
        return JsonObject(mapOf("type" to JsonPrimitive("com.example.triviaparty.network.GameEvent.RoomStateBroadcast"),
            "session" to JsonObject(stateJson))).toString()
    }

    private fun getNextPickerTeamId(teams: List<Team>, currentPickerId: String?): String? {
        if (teams.isEmpty()) return null
        if (currentPickerId == null) return teams.first().id
        val currentIndex = teams.indexOfFirst { it.id == currentPickerId }
        if (currentIndex == -1) return teams.first().id
        val nextIndex = (currentIndex + 1) % teams.size
        return teams[nextIndex].id
    }

    private fun getRemainingCategories(selectedCategories: List<String>, playedIds: List<String>): List<String> {
        val poolCategories = if (selectedCategories.isNotEmpty()) selectedCategories else QuestionBankRepository.sampleCategories
        return poolCategories.filter { cat ->
            QuestionBankRepository.getQuestionsForCategory(cat).any { question -> !playedIds.contains(question.id) }
        }
    }

    private fun generateRoomId(): String {
        return (1000..9999).random().toString()
    }

    private val localTvShell = """
        <!doctype html><html lang="en"><meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Trivia Party TV</title><body style="background:#10101a;color:white;font:24px sans-serif;padding:3rem">
        <h1>Trivia Party TV</h1><p>The local TV display could not load.</p>
        </body></html>
    """.trimIndent()

}
