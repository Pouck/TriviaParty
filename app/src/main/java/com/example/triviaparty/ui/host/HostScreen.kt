package com.example.triviaparty.ui.host

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
import com.example.triviaparty.cast.GoogleCastController
import com.example.triviaparty.ui.cast.GoogleCastDeviceList
import com.example.triviaparty.data.QuestionBankRepository
import com.example.triviaparty.model.CategoryGameRules
import com.example.triviaparty.model.GameSession
import com.example.triviaparty.model.GameState
import com.example.triviaparty.model.HourglassConfig
import com.example.triviaparty.model.activePrompt
import com.example.triviaparty.model.isOralBuzzerQuestion
import com.example.triviaparty.model.Question
import com.example.triviaparty.model.Team
import com.example.triviaparty.model.isBuzz
import com.example.triviaparty.model.label
import com.example.triviaparty.model.spectatorOptions
import com.example.triviaparty.model.revealPrompt
import com.example.triviaparty.network.GameClient
import com.example.triviaparty.network.ClientConnectionState
import com.example.triviaparty.network.GameEvent
import com.example.triviaparty.network.GameServer
import com.example.triviaparty.ui.player.components.MapPinView
import com.example.triviaparty.util.SimpleQrCodeComposable
import kotlinx.coroutines.delay

private val HostBackground = Color(0xFF12121D)
private val HostPanel = Color(0xFF252536)
private val HostGold = Color(0xFFFFD54F)

@Composable
fun HostScreen(
    server: GameServer,
    client: GameClient,
    googleCast: GoogleCastController,
    selectedCategories: List<String>,
    modifier: Modifier = Modifier,
    totalRounds: Int = 5,
    timingConfig: HourglassConfig = HourglassConfig(),
    answerTimeSeconds: Int = 10,
    categoryRules: Map<String, CategoryGameRules> = emptyMap(),
    voteSettings: com.example.triviaparty.model.VoteSettings? = null,
    startNewGame: Boolean = true,
    onGameStarted: () -> Unit = {},
    onBackToMain: () -> Unit
) {
    val session by client.gameSession.collectAsState()
    val castStatus by googleCast.status.collectAsState()
    var showCastDialog by remember { mutableStateOf(false) }
    var showPrivateAnswer by remember { mutableStateOf(false) }
    val connectionState by client.connectionState.collectAsState()
    var connectionAttempt by remember { mutableIntStateOf(0) }
    var startupTimedOut by remember { mutableStateOf(false) }
    val shouldStartNewGame = remember { startNewGame }
    var showScoreDialog by remember { mutableStateOf(false) }
    var showJoinDialog by remember { mutableStateOf(false) }
    var editingTeam by remember { mutableStateOf<Team?>(null) }
    var scoreText by remember { mutableStateOf("") }
    val reviewContext = androidx.compose.ui.platform.LocalContext.current
    val reviewStore = remember { com.example.triviaparty.data.HostReviewStore(java.io.File(reviewContext.filesDir,"host-review.json")) }
    var reviewing by remember { mutableStateOf<com.example.triviaparty.data.QuestionReview?>(null) }
    reviewing?.let { QuestionReviewDialog(reviewStore,it) { reviewing=null } }
    val countedPackages = remember { mutableSetOf<String>() }
    LaunchedEffect(session?.currentCategory, session?.state) {
        val current = session
        if(current?.state == GameState.QUESTION_ACTIVE) {
            val packages = com.example.triviaparty.data.GamePackageRepository.packages.filter {
                current.currentCategory in com.example.triviaparty.data.GamePackageRepository.categoryNamesFor(it)
            }.map { it.id }.filter { it !in countedPackages }
            if(packages.isNotEmpty()) { reviewStore.recordPackages(packages,current.roomId); countedPackages.addAll(packages) }
        }
    }

    LaunchedEffect(connectionAttempt) {
        startupTimedOut = false
        server.start()
        if (shouldStartNewGame || client.connectionState.value != ClientConnectionState.CONNECTED) {
            delay(300)
            client.connect(hostIp = "127.0.0.1") {
                if (shouldStartNewGame) {
                    client.sendEvent(GameEvent.HostStartGame(selectedCategories, totalRounds, timingConfig, answerTimeSeconds, categoryRules,voteSettings))
                }
            }
        }
        delay(10000)
        startupTimedOut = client.gameSession.value == null
    }

    LaunchedEffect(session != null) {
        if (session != null) onGameStarted()
    }

    val game = session
    val timerPaused = game?.timerPaused == true
    val played = game?.playedQuestionIds.orEmpty()
    val categoriesInPlay = game?.let { it.masterCategories.size - it.retiredCategories.size } ?: 0
    val categoriesPlayed = game?.masterCategories?.count { category ->
        val categoryQuestions = QuestionBankRepository.getQuestionsForCategory(category)
        categoryQuestions.isNotEmpty() && categoryQuestions.all { it.id in played }
    } ?: 0
    val currentCategoryQuestionIndex = game?.let { state ->
        state.currentCategory?.let { category ->
            QuestionBankRepository.getQuestionsForCategory(category).count { it.id in state.playedQuestionIds }
        }
    } ?: 0
    val hasMoreInCategory = game?.currentCategory?.let { category ->
        QuestionBankRepository.getQuestionsForCategory(category).any { it.id !in game.playedQuestionIds }
    } ?: false
    val hasAnyUnplayedQuestion = game?.let { state ->
        state.masterCategories.asSequence()
            .filterNot { it in state.retiredCategories }
            .flatMap { QuestionBankRepository.getQuestionsForCategory(it).asSequence() }
            .any { it.id !in state.playedQuestionIds }
    } ?: true
    val leader = game?.teams?.maxByOrNull { it.score }

    Box(modifier = modifier.fillMaxSize().background(HostBackground).padding(10.dp)) {
        Card(
            modifier = Modifier.fillMaxSize(),
            shape = RoundedCornerShape(18.dp),
            colors = CardDefaults.cardColors(containerColor = HostPanel)
        ) {
            if (game == null) {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        if (startupTimedOut || connectionState == ClientConnectionState.ERROR ||
                            connectionState == ClientConnectionState.DISCONNECTED) {
                            Text("Connexion à la partie interrompue.", color = Color.White)
                            Button(onClick = { connectionAttempt++ }) { Text("Réessayer") }
                            TextButton(onClick = onBackToMain) { Text("Retour aux packages") }
                        } else {
                            CircularProgressIndicator(color = HostGold)
                            Text("Connexion à la partie…", color = Color.White)
                        }
                    }
                }
            } else {
                PrivateHostDashboard(game, client, hasMoreInCategory, hasAnyUnplayedQuestion,
                    onEditTeam = { editingTeam = it; scoreText = it.score.toString() })
            }
        }

        Row(
            Modifier.align(Alignment.TopEnd).padding(6.dp)
                .background(Color(0xDD181824), RoundedCornerShape(10.dp))
                .padding(horizontal = 5.dp, vertical = 2.dp),
            horizontalArrangement = Arrangement.spacedBy(2.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            HeaderButton("JOINDRE", onClick = { showJoinDialog = true })
            HeaderButton("SCORE", onClick = { showScoreDialog = true })
            HeaderButton("TV", onClick = { showCastDialog = true })
            game?.currentQuestion?.let { question ->
                HeaderButton("NOTE", onClick = {
                    reviewing=reviewStore.read().reviews[question.id] ?: com.example.triviaparty.data.QuestionReview(question.id,question.category,
                        question.prompt + if(question is Question.GuessWho) "\n"+question.clues.joinToString("\n") else "")
                })
            }
            if (castStatus.connected && game?.currentQuestion?.isOralBuzzerQuestion() == true && game.state == GameState.QUESTION_ACTIVE) {
                HeaderButton("RÉPONSE", onClick = { showPrivateAnswer = true })
            }
            HeaderButton("FIN", color = Color(0xFFB74343)) {
                googleCast.stopCasting()
                server.stop()
                client.disconnect()
                onBackToMain()
            }
        }
    }

    if (showCastDialog) {
        DisposableEffect(googleCast) {
            googleCast.startDiscovery()
            onDispose { googleCast.stopDiscovery() }
        }
        AlertDialog(onDismissRequest = { showCastDialog = false },
            title = { Text("Diffuser la page de jeu") },
            text = { Column(Modifier.heightIn(max = 360.dp).verticalScroll(rememberScrollState())) {
                Text("Le téléviseur reçoit une page indépendante. Les commandes restent sur le Pixel.")
                GoogleCastDeviceList(googleCast, scanning = true)
            } },
            confirmButton = { TextButton(onClick = { showCastDialog = false }) { Text("Fermer") } })
    }
    if (showPrivateAnswer && castStatus.connected && game?.state == GameState.QUESTION_ACTIVE) {
        val answers = when (val question = game.currentQuestion) {
            is Question.TextAnswer -> question.acceptableAnswers
            is Question.GuessWho -> question.acceptableAnswers
            else -> emptyList()
        }
        AlertDialog(onDismissRequest = { showPrivateAnswer = false },
            title = { Text("Réponse privée · hôte") },
            text = { Text(answers.joinToString("\n"), modifier = Modifier.heightIn(max = 300.dp).verticalScroll(rememberScrollState())) },
            confirmButton = { TextButton(onClick = { showPrivateAnswer = false }) { Text("Fermer") } })
    }
    LaunchedEffect(castStatus.connected, game?.currentQuestion?.id, game?.state) { showPrivateAnswer = false }

    if (showJoinDialog && game != null) {
        AlertDialog(onDismissRequest = { showJoinDialog = false },
            title = { Text("Jouer sans installer d’application") },
            text = { BrowserJoinInfo(game, server.port) },
            confirmButton = { TextButton(onClick = { showJoinDialog = false }) { Text("Fermer") } })
    }

    if (showScoreDialog && game != null) {
        AlertDialog(
            onDismissRequest = { showScoreDialog = false },
            title = { Text("Modifier les scores") },
            text = {
                if (game.teams.isEmpty()) Text("Aucune équipe")
                else Column(Modifier.heightIn(max=360.dp).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    game.teams.sortedByDescending { it.score }.forEach { team ->
                        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("${team.name} · ${team.score} pts", color = Color.White, modifier = Modifier.weight(1f))
                            TextButton(onClick = {
                                editingTeam = team
                                scoreText = team.score.toString()
                                showScoreDialog = false
                            }) { Text("Modifier") }
                        }
                    }
                }
            },
            confirmButton = { TextButton(onClick = { showScoreDialog = false }) { Text("Fermer") } }
        )
    }

    editingTeam?.let { team ->
        AlertDialog(
            onDismissRequest = { editingTeam = null },
            title = { Text("Score de ${team.name}") },
            text = {
                OutlinedTextField(value = scoreText, onValueChange = { scoreText = it },
                    label = { Text("Nouveau score") }, singleLine = true)
            },
            confirmButton = {
                Button(onClick = {
                    client.sendEvent(GameEvent.HostSetScore(team.id, scoreText.toIntOrNull() ?: team.score))
                    editingTeam = null
                }) { Text("Enregistrer") }
            },
            dismissButton = { TextButton(onClick = { editingTeam = null }) { Text("Annuler") } }
        )
    }
}

@Composable
private fun HeaderButton(label: String, color: Color = Color(0xFF414157), onClick: () -> Unit) {
    CompositionLocalProvider(LocalMinimumInteractiveComponentSize provides 0.dp) {
        TextButton(onClick = onClick,
            modifier = Modifier.width(when (label) { "JOINDRE" -> 70.dp; "SCORE" -> 60.dp; "RÉPONSE" -> 76.dp; else -> 44.dp })
                .height(44.dp).background(color, RoundedCornerShape(8.dp)),
            colors = ButtonDefaults.textButtonColors(contentColor = Color.White),
            contentPadding = PaddingValues(horizontal = 4.dp, vertical = 0.dp)) {
            Text(label, fontWeight = FontWeight.Bold, fontSize = 13.sp, maxLines = 1)
        }
    }
}

@Composable
private fun PanelContent(content: @Composable ColumnScope.() -> Unit) {
    Column(
        Modifier.fillMaxSize().padding(start = 24.dp, end = 24.dp, top = 48.dp, bottom = 10.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        content = content
    )
}

@Composable
private fun LobbyPanel(game: GameSession, client: GameClient, port: Int) {
    PanelContent {
        Text("SALLE DE JEU", color = HostGold, fontSize = 24.sp, fontWeight = FontWeight.Black)
        Text("En attente des joueurs", color = Color.LightGray, fontSize = 16.sp)
        BrowserJoinInfo(game, port)
        Column(Modifier.weight(1f).verticalScroll(rememberScrollState())) {
        if (game.teams.isEmpty()) Text("Les équipes apparaîtront ici lorsqu’elles rejoindront la partie.", color = Color.White)
        else game.teams.forEach { Text("• ${it.name}", color = Color.White, fontSize = 20.sp) }

        if (game.pendingJoinRequests.isNotEmpty()) {
            Text("Demandes en attente", color = HostGold, fontWeight = FontWeight.Bold)
            game.pendingJoinRequests.forEach { name ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically) {
                    Text(name, color = Color.White)
                    TextButton(onClick = { client.sendEvent(GameEvent.HostValidateTeam(name, true)) }) { Text("Accepter") }
                    TextButton(onClick = { client.sendEvent(GameEvent.HostValidateTeam(name, false)) }) { Text("Refuser") }
                }
            }
        }
        }
        Button(onClick = { client.sendEvent(GameEvent.HostBeginCategorySelect) },
            colors = ButtonDefaults.buttonColors(containerColor = HostGold, contentColor = Color.Black),
            modifier = Modifier.height(40.dp), contentPadding = PaddingValues(horizontal=16.dp,vertical=4.dp)) {
            Text("COMMENCER LA PARTIE", fontWeight = FontWeight.Black, fontSize = 18.sp)
        }
    }
}

@Composable
private fun BrowserJoinInfo(game: GameSession, port: Int) {
    val url = "http://${game.hostIpAddress}:$port/play?room=${game.roomId}"
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
        SimpleQrCodeComposable(url, size = 128.dp)
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("iPhone ou Android : scannez et jouez", color = HostGold, fontWeight = FontWeight.Bold)
            Text("Connectez-vous au même Wi-Fi que l’hôte, puis scannez ce QR avec votre appareil photo.", color = Color.LightGray)
            SelectionContainer { Text("http://${game.hostIpAddress}:$port/play", color = Color.White, fontSize = 13.sp) }
        }
    }
}

@Composable
private fun CategoryIntroPanel(game: GameSession, completed: Int, total: Int, leader: Team?, onWager: () -> Unit, onStart: () -> Unit) {
    PanelContent {
        Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("NOUVELLE CATÉGORIE (${(completed + 1).coerceAtMost(total)}/$total)", color = HostGold,
            fontSize = 22.sp, fontWeight = FontWeight.Black, textAlign = TextAlign.Center)
        Text(game.currentCategory.orEmpty(), color = Color.White, fontSize = 34.sp, fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center)
        Text("${game.currentCategoryQuestionCount} questions", color = Color.White, fontSize = 22.sp)
        Text("Types : ${game.currentCategoryQuestionTypes.joinToString(" · ")}", color = Color.LightGray, fontSize = 16.sp)
        val answerTimeInfo = if (game.currentCategoryAnswerTimeSeconds > 0)
            " · Réponse après buzzer : ${game.currentCategoryAnswerTimeSeconds} s" else ""
        Text("Mode : ${game.currentCategoryAnswerMode?.label().orEmpty()}$answerTimeInfo",
            color = Color.LightGray, fontSize = 16.sp, textAlign = TextAlign.Center)
        leader?.let { Text("En tête : ${it.name} · ${it.score} pts", color = HostGold, fontSize = 18.sp) }
        }
        OutlinedButton(onClick = onWager,modifier=Modifier.height(36.dp),contentPadding=PaddingValues(horizontal=12.dp,vertical=4.dp)) { Text("PROPOSER UNE MISE", color = HostGold) }
        Button(onClick = onStart, modifier = Modifier.height(40.dp), contentPadding = PaddingValues(horizontal=16.dp,vertical=4.dp),
            colors = ButtonDefaults.buttonColors(containerColor = HostGold, contentColor = Color.Black)) {
            Text("COMMENCER", fontWeight = FontWeight.Black, fontSize = 18.sp)
        }
    }
}

@Composable
private fun ActiveQuestionPanel(
    game: GameSession, paused: Boolean, onPause: () -> Unit, onReveal: () -> Unit,
    onJudgeText: (String, Boolean) -> Unit, onStartTimer: () -> Unit
) {
    val question = game.currentQuestion ?: return
    val index = game.currentCategory?.let { category ->
        QuestionBankRepository.getQuestionsForCategory(category).count { it.id in game.playedQuestionIds }
    } ?: game.roundNumber
    val image = !question.imageUrl.isNullOrBlank()
    if (image) {
        // The map starts at the top edge; the header shares the controls column.
        Row(Modifier.fillMaxSize().padding(horizontal = 12.dp, vertical = 4.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Box(Modifier.weight(1.8f).fillMaxHeight(), contentAlignment = Alignment.Center) {
                if (question is Question.MapPin) {
                    MapPinView(question.imageUrl, question.options, null, { _, _ -> }, Modifier.fillMaxSize())
                } else AsyncImage(model = question.imageUrl, contentDescription = "Illustration de la question",
                    contentScale = ContentScale.Fit, modifier = Modifier.fillMaxSize())
            }
            Column(Modifier.weight(1f).fillMaxHeight().padding(top = 44.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("QUESTION $index/${game.currentCategoryQuestionCount}", color = HostGold,
                    fontSize = 18.sp, fontWeight = FontWeight.Black)
                QuestionControls(game, question, paused, onPause, onReveal, onJudgeText,
                    Modifier.weight(1f).fillMaxWidth(), compact = true, onStartTimer = onStartTimer)
            }
        }
    } else Column(Modifier.fillMaxSize().padding(horizontal = 12.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)) {
        // Reserve the right side for JOINDRE / SCORE / FIN, on the same header line.
        Row(Modifier.fillMaxWidth().height(36.dp).padding(end = 260.dp),
            verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("QUESTION $index/${game.currentCategoryQuestionCount}", color = HostGold,
                fontSize = 16.sp, fontWeight = FontWeight.Black)
            QuestionTimer(game, Modifier.weight(1f))
        }
        QuestionControls(game, question, paused, onPause, onReveal, onJudgeText,
            Modifier.weight(1f).fillMaxWidth(), compact = false, onStartTimer = onStartTimer)
    }
}

@Composable
private fun QuestionTimer(game: GameSession, modifier: Modifier = Modifier) {
    val question = game.currentQuestion ?: return
    val remaining = if (game.answerTimerRunning) game.answerTimerRemainingSeconds ?: game.answerTimeSeconds
        else (game.timingConfig.secondsPerFlip-game.elapsedSecondsInFlip).coerceAtLeast(0)
    val points = game.timingConfig.calculateScore(question.basePoints,game.currentFlipNumber,game.elapsedSecondsInFlip)
    Text(if (game.questionReading) "LECTURE" else
        (if (game.answerTimerRunning) "Réponse · " else "") + "$remaining s · $points pts",
        modifier=modifier,color=HostGold,fontSize=14.sp,fontWeight=FontWeight.Bold)
}

@Composable
private fun QuestionControls(
    game: GameSession, question: Question, paused: Boolean, onPause: () -> Unit, onReveal: () -> Unit,
    onJudgeText: (String, Boolean) -> Unit, modifier: Modifier, compact: Boolean, onStartTimer: () -> Unit
) {
    val config = game.timingConfig
    val elapsed = game.elapsedSecondsInFlip.coerceIn(0, config.secondsPerFlip.coerceAtLeast(1))
    val points = config.calculateScore(question.basePoints, game.currentFlipNumber, elapsed)
    val answering = game.answerTimerTeamId?.let { id -> game.teams.find { it.id == id } }
        ?: game.submissions.values.firstOrNull { it.isLocked && it.isCorrect != false && it.isBuzz() }
            ?.let { submission -> game.teams.find { it.id == submission.teamId } }
    val buzzer = question.isOralBuzzerQuestion() || game.currentCategoryAnswerMode == com.example.triviaparty.model.CategoryAnswerMode.BUZZER
    Column(modifier, verticalArrangement = Arrangement.spacedBy(6.dp)) {
        if (compact && game.answerTimerRunning) AnswerTimerControls(game, compact)
        else if (compact) Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("$points pts", color = HostGold, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            LinearProgressIndicator(progress = { 1f - elapsed.toFloat() / config.secondsPerFlip.coerceAtLeast(1) },
                modifier = Modifier.weight(1f).height(8.dp), color = HostGold, trackColor = HostBackground)
            Text("${(config.secondsPerFlip - elapsed).coerceAtLeast(0)} s", color = Color.White)
        }
        if (buzzer && answering != null) {
            Text("${answering.name} À LA PAROLE",
                color = HostGold, fontWeight = FontWeight.Black,
                fontSize = if (compact) 18.sp else 22.sp,
                modifier = Modifier.fillMaxWidth().background(HostBackground, RoundedCornerShape(8.dp)).padding(8.dp))
        }
        val hasPublicChoices = question.spectatorOptions().isNotEmpty()
        if (!compact && hasPublicChoices) {
            // Long question text must not push the spectators' choices out of view.
            Column(Modifier.weight(0.35f).fillMaxWidth().verticalScroll(rememberScrollState())) {
                Text(question.activePrompt(game.currentFlipNumber), color = Color.White, fontWeight = FontWeight.Bold, fontSize = 19.sp)
            }
            Column(Modifier.weight(0.65f).fillMaxWidth().verticalScroll(rememberScrollState())) {
                SpectatorChoices(question, columns = 2)
            }
        } else Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(question.activePrompt(game.currentFlipNumber), color = Color.White, fontWeight = FontWeight.Bold,
                fontSize = if (question is Question.GuessWho && question.clues.size >= 4) {
                    if (compact) 15.sp else 16.sp
                } else if (compact) 17.sp else 20.sp)
            SpectatorChoices(question, columns = if (compact) 1 else 2)
        }
        answering?.let { team ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { onJudgeText(team.id, true) }, modifier = Modifier.height(36.dp),
                    contentPadding = PaddingValues(6.dp)) { Text("Bonne réponse", fontSize = 13.sp) }
                Button(onClick = { onJudgeText(team.id, false) }, modifier = Modifier.height(36.dp),
                    contentPadding = PaddingValues(6.dp)) { Text("Mauvaise réponse", fontSize = 13.sp) }
            }
        }
        if (game.questionReading) {
            Button(onClick=onStartTimer, modifier=Modifier.height(38.dp), contentPadding=PaddingValues(horizontal=12.dp,vertical=4.dp)) {
                Text("DÉMARRER LE CHRONO", fontWeight=FontWeight.Bold)
            }
        } else Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            OutlinedButton(onClick = onPause, enabled = !game.answerTimerRunning, modifier=Modifier.height(36.dp),
                contentPadding = PaddingValues(8.dp)) { Text(if (paused) "Reprendre" else "Pause") }
            val connected = game.teams.filter { it.isConnected }
            val allAnswered = connected.isEmpty() || connected.all { game.submissions[it.id]?.isLocked == true }
            if (answering == null && allAnswered) {
                Button(onClick = onReveal, modifier = Modifier.height(38.dp), contentPadding = PaddingValues(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = HostGold, contentColor = Color.Black)) {
                    Text("RÉVÉLER LA RÉPONSE", fontWeight = FontWeight.Black, fontSize = 13.sp)
                }
            } else if (answering == null && question !is Question.GuessWho) Text("En attente des réponses…", color = Color.LightGray, fontSize = 13.sp)
        }
    }
}

/** Fixed public list; never follows a player's private ordering draft. */
@Composable
internal fun SpectatorChoices(question: Question, columns: Int = 2) {
    val choices = question.spectatorOptions()
    CompactGrid(choices, columns) { value ->
        Text(value, color = Color.White, fontSize = 15.sp,
            modifier = Modifier.fillMaxWidth().background(HostBackground, RoundedCornerShape(8.dp)).padding(10.dp))
    }
}

@Composable
private fun <T> CompactGrid(values: List<T>, columns: Int = 2, content: @Composable (T) -> Unit) {
    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        values.chunked(columns).forEach { row ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                row.forEach { value -> Box(Modifier.weight(1f)) { content(value) } }
                repeat(columns - row.size) { Spacer(Modifier.weight(1f)) }
            }
        }
    }
}

@Composable
private fun AnswerTimerControls(game: GameSession, compact: Boolean) {
    val question = game.currentQuestion ?: return
    val duration = game.answerTimeSeconds
    if (duration <= 0) return
    val submission = game.submissions.values.firstOrNull {
        it.isLocked && it.questionId == question.id && it.isCorrect != false && it.isBuzz()
    } ?: return
    val team = game.teams.firstOrNull { it.id == submission.teamId } ?: return
    if (game.answerTimerRunning && game.answerTimerTeamId == team.id) {
        val remaining = game.answerTimerRemainingSeconds ?: duration
        Text("TEMPS DE RÉPONSE · ${team.name} · ${remaining}s", color = HostGold,
            fontSize = if (compact) 14.sp else 16.sp, fontWeight = FontWeight.Bold)
        LinearProgressIndicator(progress = { (remaining.toFloat() / duration).coerceIn(0f, 1f) },
            modifier = Modifier.fillMaxWidth().height(if (compact) 8.dp else 10.dp),
            color = Color(0xFF75D69C), trackColor = Color(0xFF171722))
    }
}

@Composable
private fun RevealPanel(game: GameSession, categoryQuestionIndex: Int, hasMore: Boolean, isLastQuestion: Boolean, onNext: () -> Unit) {
    val question = game.currentQuestion
    val answer = when (question) {
        is Question.MultipleChoice -> question.options.getOrNull(question.correctOptionIndex).orEmpty()
        is Question.Ordering -> question.correctOrderIds.mapIndexedNotNull { index, id ->
            question.items.find { it.id == id }?.text?.let { "${index + 1}. $it" }
        }.joinToString("\n")
        is Question.TextAnswer -> question.acceptableAnswers.firstOrNull().orEmpty()
        is Question.GuessWho -> question.acceptableAnswers.firstOrNull().orEmpty()
        is Question.MapPin -> question.options.getOrNull(question.correctOptionIndex)?.label.orEmpty()
        is Question.Wager -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex).orEmpty()
        is Question.SpeedRace -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex).orEmpty()
        null -> ""
    }
    Column(Modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(Modifier.fillMaxWidth().height(40.dp).padding(end = 260.dp), contentAlignment = Alignment.CenterStart) {
            Text(if (game.state == GameState.WAGER_RESULTS) "RÉSULTATS DES MISES" else
                "QUESTION $categoryQuestionIndex/${game.currentCategoryQuestionCount} · RÉPONSE",
                color = HostGold, fontSize = 18.sp, fontWeight = FontWeight.Black)
        }
        Row(Modifier.weight(1f).fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Column(Modifier.weight(1.2f).fillMaxHeight().verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(8.dp)) {
                if (game.state == GameState.WAGER_RESULTS) {
                    CompactGrid(game.categoryWagerResults) { result ->
                        val outcome = if (result.amount == 0) "Aucune mise" else if (result.correct) "Gagnée" else "Perdue"
                        Column(Modifier.fillMaxWidth().background(HostBackground, RoundedCornerShape(8.dp)).padding(8.dp)) {
                            Text(result.teamName, color = HostGold, fontWeight = FontWeight.Bold)
                            Text("Mise : ${result.amount} · $outcome", color = Color.White, fontSize = 13.sp)
                            Text("${if (result.delta > 0) "+" else ""}${result.delta} pts", color = Color.White)
                        }
                    }
                } else {
                    Text(question?.revealPrompt().orEmpty(), color = Color.LightGray, fontSize = 16.sp)
                    Text(answer, color = Color.White, fontSize = 20.sp, lineHeight = 25.sp, fontWeight = FontWeight.Bold,
                        modifier = Modifier.fillMaxWidth().background(Color(0xFF173D30), RoundedCornerShape(8.dp)).padding(8.dp))
                }
            }
            Leaderboard(game, Modifier.weight(1f).fillMaxHeight())
        }
        Button(onClick = onNext, modifier = Modifier.align(Alignment.End).height(38.dp), contentPadding = PaddingValues(horizontal=14.dp,vertical=4.dp),
            colors = ButtonDefaults.buttonColors(containerColor = HostGold, contentColor = Color.Black)) {
            Text(when {
                game.categoryWagerSettled && !game.categoryWagerResultsShown -> "RÉSULTATS DES MISES"
                isLastQuestion -> "TERMINER LA PARTIE"
                hasMore -> "QUESTION SUIVANTE"
                else -> "CATÉGORIE SUIVANTE"
            }, fontWeight = FontWeight.Black)
        }
    }
}

@Composable
private fun Leaderboard(game: GameSession, modifier: Modifier = Modifier) {
    Column(modifier, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("CLASSEMENT", color = HostGold, fontWeight = FontWeight.Bold, fontSize = 20.sp)
        Column(Modifier.weight(1f).verticalScroll(rememberScrollState())) {
            game.teams.sortedByDescending { it.score }.forEach { team ->
                val rank = 1 + game.teams.count { it.score > team.score }
                Row(Modifier.fillMaxWidth().padding(bottom = 5.dp).background(HostBackground, RoundedCornerShape(8.dp)).padding(8.dp),
                    verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("$rank. ${team.name}", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp, modifier = Modifier.weight(1f))
                    Text("${team.score} pts", color = HostGold, fontSize = 15.sp)
                }
            }
        }
    }
}

@Composable
private fun WagerOfferPanel(game: GameSession, onStart: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(Modifier.fillMaxWidth().height(40.dp).padding(end = 260.dp), contentAlignment = Alignment.CenterStart) {
            Text("MISES", color = HostGold, fontSize = 20.sp, fontWeight = FontWeight.Black)
        }
        Text(game.currentCategory.orEmpty(), color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
        Text("Première question uniquement · Sans choix : 0 point", color = Color.LightGray, fontSize = 14.sp)
        Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())) {
            CompactGrid(game.teams) { team ->
                Column(Modifier.fillMaxWidth().background(HostBackground, RoundedCornerShape(8.dp)).padding(8.dp)) {
                    Text(team.name, color = HostGold, fontWeight = FontWeight.Bold)
                    Text("${game.categoryWagers[team.id] ?: 0} / ${game.categoryWagerLimits[team.id] ?: 0} pts · " +
                        if (team.id in game.categoryWagers) "Prête" else "En attente", color = Color.White, fontSize = 14.sp)
                }
            }
        }
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween) {
            Text("${game.categoryWagers.size}/${game.categoryWagerLimits.size} équipes prêtes", color = HostGold)
            Button(onClick = onStart,modifier=Modifier.height(38.dp),contentPadding=PaddingValues(horizontal=10.dp,vertical=4.dp)) { Text("FERMER LES MISES ET COMMENCER",fontSize=13.sp) }
        }
    }
}

@Composable
private fun EndPanel(game: GameSession) {
    val winner = game.teams.maxByOrNull { it.score }?.takeIf { it.score > 0 }
    Column(Modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("PARTIE TERMINÉE", color = HostGold, fontSize = 28.sp, fontWeight = FontWeight.Black)
        Text(winner?.let { "Gagnant : ${it.name}" } ?: "Aucun gagnant · Bel effort !", color = Color.White, fontSize = 25.sp, fontWeight = FontWeight.Bold)
        Text("Score : ${winner?.score ?: 0} pts", color = Color.LightGray, fontSize = 20.sp)
        Leaderboard(game, Modifier.weight(1f).fillMaxWidth())
    }
}
