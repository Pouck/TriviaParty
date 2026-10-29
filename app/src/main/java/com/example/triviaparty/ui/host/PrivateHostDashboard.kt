package com.example.triviaparty.ui.host

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.triviaparty.model.*
import com.example.triviaparty.network.*
import com.example.triviaparty.ui.components.HourglassTimer

@Composable
internal fun PrivateHostDashboard(game: GameSession, client: GameClient, hasMore: Boolean,
    hasUnplayed: Boolean, onEditTeam: (Team) -> Unit) {
    val gold = Color(0xFFFFD54F)
    val question = game.currentQuestion
    val answering = game.answerTimerTeamId?.let { id -> game.teams.find { it.id == id } }
    val answer = when (question) {
        is Question.MultipleChoice -> question.options.getOrNull(question.correctOptionIndex).orEmpty()
        is Question.TextAnswer -> question.acceptableAnswers.firstOrNull().orEmpty()
        is Question.GuessWho -> question.acceptableAnswers.firstOrNull().orEmpty()
        is Question.Ordering -> question.correctOrderIds.mapNotNull { id -> question.items.find { it.id == id }?.text }.joinToString(" → ")
        is Question.MapPin -> question.options.getOrNull(question.correctOptionIndex)?.label.orEmpty()
        is Question.Wager -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex).orEmpty()
        is Question.SpeedRace -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex).orEmpty()
        null -> ""
    }
    val aliases = when (question) {
        is Question.TextAnswer -> question.acceptableAnswers.drop(1)
        is Question.GuessWho -> question.acceptableAnswers.drop(1)
        else -> emptyList()
    }.filterNot { it.equals(answer, ignoreCase=true) }.distinct()
    var showAliases by remember(question?.id) { mutableStateOf(false) }
    var playNextSound by remember(game.roomId, game.answerSoundsEnabled, game.currentQuestion?.id) { mutableStateOf(false) }
    var confirmSkipCategory by remember(game.currentCategory) { mutableStateOf(false) }
    val dashboardScroll = rememberScrollState()
    LaunchedEffect(question?.id,game.state) { dashboardScroll.scrollTo(0);if(game.state==GameState.ANSWER_REVIEW) showAliases=false }
    fun send(event: GameEvent) = client.sendEvent(event)
    @Composable fun Action(label: String, enabled: Boolean = true, event: GameEvent,
        color: Color = Color(0xFF414157), modifier: Modifier = Modifier.fillMaxWidth()) {
        Button(onClick = { send(event) }, enabled = enabled,
            colors=ButtonDefaults.buttonColors(containerColor=color,contentColor=Color.White),
            contentPadding = PaddingValues(horizontal=14.dp,vertical=12.dp),
            modifier = modifier.heightIn(min = 48.dp),shape=RoundedCornerShape(12.dp)) {
            Text(label, fontSize = 18.sp, fontWeight=FontWeight.SemiBold)
        }
    }
    LaunchedEffect(game.state) {
        if (game.state == GameState.CATEGORY_SELECT) send(GameEvent.HostBeginCategorySelect)
    }
    val canSkipCategory=game.currentCategory!=null && game.state in setOf(GameState.CATEGORY_INTRO,GameState.WAGER_OPEN,GameState.QUESTION_ACTIVE,GameState.ANSWER_REVIEW,GameState.REVEAL_ANSWER,GameState.ROUND_SUMMARY,GameState.WAGER_RESULTS)
    Box(Modifier.fillMaxSize().padding(top = 64.dp, start = 16.dp, end = 16.dp, bottom = 16.dp)) {
    Row(Modifier.fillMaxSize(),
        horizontalArrangement = Arrangement.spacedBy(16.dp)) {
        Column(Modifier.fillMaxWidth().fillMaxHeight().padding(bottom=if(canSkipCategory) 72.dp else 0.dp).verticalScroll(dashboardScroll),
            verticalArrangement = Arrangement.spacedBy(if(game.state==GameState.ANSWER_REVIEW) 12.dp else 18.dp)) {
            Text("COMMANDES DE L’HÔTE", color = gold, fontWeight = FontWeight.Bold, fontSize = 20.sp)
            Text(game.currentCategory ?: "Salon", color = Color.LightGray, fontSize = 18.sp,lineHeight=24.sp)
            if (question is Question.GuessWho) Text(
                if (question.imageRevealMode == com.example.triviaparty.model.ImageRevealMode.NONE) "${question.clues.size} indices au total"
                else "${question.imageRevealSteps} r\u00e9v\u00e9lations d’image",
                color = Color.LightGray, fontSize = 16.sp)
            if (question != null && game.state in setOf(GameState.QUESTION_ACTIVE,GameState.ANSWER_REVIEW,GameState.REVEAL_ANSWER,GameState.ROUND_SUMMARY)) {
                Surface(color=Color(0xFF173E30),shape=RoundedCornerShape(16.dp),modifier=Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(if(game.state==GameState.ANSWER_REVIEW) 12.dp else 18.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
                        Text("RÉPONSE ATTENDUE · PRIVÉE",color=Color(0xFFA6ECC3),fontSize=14.sp,fontWeight=FontWeight.Bold)
                        Text(answer,color=Color.White,fontSize=if(game.state==GameState.ANSWER_REVIEW) 24.sp else 30.sp,lineHeight=if(game.state==GameState.ANSWER_REVIEW) 29.sp else 36.sp,fontWeight=FontWeight.Bold)
                        if (aliases.isNotEmpty()) {
                            TextButton(onClick={ showAliases=!showAliases },contentPadding=PaddingValues(0.dp)) {
                                Text(if(showAliases) "Masquer les variantes" else "Autres réponses acceptées (${aliases.size})",
                                    color=Color(0xFFB9EAD1),fontSize=16.sp)
                            }
                            if(showAliases) Text(aliases.joinToString(" · "),color=Color(0xFFD1E8DA),fontSize=18.sp,lineHeight=24.sp)
                        }
                    }
                }
            }
            if (game.state == GameState.QUESTION_ACTIVE && question != null) {
                Text("Question ${game.roundNumber}/${game.totalRounds}", color = Color.White, fontSize = 18.sp)
                if (game.questionReading) {
                    if(question.isChronologyQuestion()) {
                        val connected=game.teams.count { it.isConnected }
                        Text("${game.teams.count { it.isConnected && it.id in game.readyTeamIds }}/$connected ${if(connected==1) "équipe prête" else "équipes prêtes"} · départ automatique",color=Color.White,fontSize=20.sp)
                    }
                    Action(if(question.isChronologyQuestion()) "DÉMARRER SANS ATTENDRE" else "DÉMARRER LE CHRONO", event = GameEvent.HostStartQuestionTimer)
                }
                else {
                    val duration = if (game.answerTimerRunning) game.answerTimeSeconds else game.timingConfig.secondsPerFlip
                    val remaining = if (game.answerTimerRunning) game.answerTimerRemainingSeconds ?: duration
                        else duration - game.elapsedSecondsInFlip
                    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=Alignment.CenterVertically) {
                        Text(if(game.answerTimerRunning) "Temps de réponse" else "Temps de question",color=Color.LightGray,fontSize=17.sp)
                        Text((if(game.timingConfig.pointsDecayPerSecond!=null) "" else "${remaining.coerceAtLeast(0)} s · ")+"${game.timingConfig.calculateScore(question.basePoints, game.currentFlipNumber,game.elapsedSecondsInFlip)} pts",
                            color = gold, fontSize = 25.sp, fontWeight = FontWeight.Bold)
                    }
                    if(!game.answerTimerRunning && !question.isChronologyQuestion()) Action(if (game.timerPaused) "REPRENDRE" else "PAUSE", true,
                        if (game.timerPaused) GameEvent.HostResumeTimer else GameEvent.HostPauseTimer)
                    if(question is Question.GuessWho && question.imageRevealMode==com.example.triviaparty.model.ImageRevealMode.NONE) Action(
                        "INDICE SUIVANT",!game.questionReading && !game.answerTimerRunning && !game.timerPaused && game.currentFlipNumber<game.timingConfig.maxFlips,
                        GameEvent.HostAdvanceClue,color=Color(0xFF555080))
                }
                answering?.let { team ->
                    Surface(color=Color(0xFF253F56),shape=RoundedCornerShape(16.dp),modifier=Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(14.dp)) {
                            Text("${team.name} répond", color = gold, fontWeight = FontWeight.Bold,fontSize=32.sp,lineHeight=38.sp)
                            Row(horizontalArrangement=Arrangement.spacedBy(12.dp)) {
                                Action("Bonne réponse",event=GameEvent.HostJudgeTextBuzz(team.id,true,playNextSound),color=Color(0xFF247249),modifier=Modifier.weight(1f))
                                Action("Mauvaise réponse",event=GameEvent.HostJudgeTextBuzz(team.id,false,playNextSound),color=Color(0xFF9C3636),modifier=Modifier.weight(1f))
                            }
                            if(!game.answerSoundsEnabled) Row(verticalAlignment=Alignment.CenterVertically) { Switch(playNextSound,{playNextSound=it});Text("Jouer une réplique aléatoire",color=Color.White) }
                        }
                    }
                }
                if(!game.questionReading && game.currentCategoryAnswerMode!=CategoryAnswerMode.WRITTEN) Action("RÉVÉLER LA RÉPONSE", event = GameEvent.HostRevealAnswer)
            } else when (game.state) {
                GameState.ANSWER_REVIEW -> {
                    val pending=game.pendingWrittenAnswers();val validated=game.validatedWrittenTeamId?.let {game.submissions[it]};val next=validated ?: pending.firstOrNull()
                    Text("VALIDATION · ${pending.size} restante(s)",color=gold,fontSize=20.sp,fontWeight=FontWeight.Bold)
                    next?.let { submission ->
                        Text(game.teams.find { it.id==submission.teamId }?.name.orEmpty(),color=Color.White,fontSize=32.sp,fontWeight=FontWeight.Bold)
                        Surface(color=Color(0xFF253F56),shape=RoundedCornerShape(14.dp),modifier=Modifier.fillMaxWidth()) {
                            Text((submission.answer as AnswerValue.TextSelection).text,color=Color.White,fontSize=28.sp,lineHeight=34.sp,
                                modifier=Modifier.padding(16.dp).heightIn(max=120.dp).verticalScroll(rememberScrollState()))
                        }
                        if(validated!=null) {
                            Text(if(validated.isCorrect==true) "Réponse acceptée" else "Réponse refusée",color=if(validated.isCorrect==true) Color(0xFFA6ECC3) else Color(0xFFFFABAB),fontSize=22.sp)
                            Action("CONTINUER",event=GameEvent.HostContinueWrittenReview(submission.questionId))
                        } else Row(horizontalArrangement=Arrangement.spacedBy(10.dp)) {
                            Action("Accepter",event=GameEvent.HostJudgeWrittenAnswer(submission.teamId,submission.questionId,true,playNextSound),color=Color(0xFF247249),modifier=Modifier.weight(1f))
                            Action("Refuser",event=GameEvent.HostJudgeWrittenAnswer(submission.teamId,submission.questionId,false,playNextSound),color=Color(0xFF9C3636),modifier=Modifier.weight(1f))
                        }
                        if(validated==null && !game.answerSoundsEnabled) Row(verticalAlignment=Alignment.CenterVertically) { Switch(playNextSound,{playNextSound=it});Text("Jouer une réplique aléatoire",color=Color.White) }
                    }
                }
                GameState.LOBBY -> {
                    val vote=game.subjectVoting
                    if(vote!=null && !vote.completed) {
                        Text("Les joueurs peuvent rejoindre avant le vote. ${vote.settings.categories} catégories · ${vote.settings.setsPerCategory} forfait(s) chacune.",color=Color.White)
                        Action("OUVRIR LE VOTE",game.teams.any { it.isConnected },GameEvent.HostOpenSubjectVote)
                    } else {
                        if(vote!=null) Text("Sujets retenus : ${vote.selected.joinToString(" · ")}",color=Color(0xFFA6ECC3))
                        Action("COMMENCER LA PARTIE", game.teams.isNotEmpty(), GameEvent.HostBeginCategorySelect)
                    }
                }
                GameState.SUBJECT_VOTING -> SubjectVotePanel(game) { send(it) }
                GameState.CATEGORY_INTRO -> {
                    Action("PROPOSER UNE MISE", event = GameEvent.HostOfferCategoryWager)
                    Action("COMMENCER", event = GameEvent.HostNextQuestion())
                }
                GameState.WAGER_OPEN -> {
                    Text("${game.categoryWagers.size}/${game.teams.size} mises verrouillées", color = Color.White)
                    Action("FERMER LES MISES ET COMMENCER", event = GameEvent.HostNextQuestion())
                }
                GameState.REVEAL_ANSWER, GameState.ROUND_SUMMARY, GameState.WAGER_RESULTS -> {
                    val wagerPending = game.categoryWagerSettled && !game.categoryWagerResultsShown
                    Action(when {
                        wagerPending -> "RÉSULTATS DES MISES"
                        !hasUnplayed -> "TERMINER LA PARTIE"
                        hasMore -> "QUESTION SUIVANTE"
                        else -> "CATÉGORIE SUIVANTE"
                    }, event = if (wagerPending || hasMore || !hasUnplayed) GameEvent.HostNextQuestion()
                        else GameEvent.HostBeginCategorySelect)
                }
                GameState.GAME_ENDED -> Text("Partie terminée", color = gold)
                else -> Unit
            }
        }
    }
    if(canSkipCategory) Button(onClick={confirmSkipCategory=true},colors=ButtonDefaults.buttonColors(containerColor=Color(0xFF65434B),contentColor=Color.White),
        modifier=Modifier.align(Alignment.BottomCenter).fillMaxWidth().heightIn(min=48.dp),shape=RoundedCornerShape(12.dp)) { Text("PASSER CETTE CATÉGORIE",fontSize=18.sp,fontWeight=FontWeight.SemiBold) }
    if(confirmSkipCategory && game.currentCategory!=null) AlertDialog(
        onDismissRequest={confirmSkipCategory=false},
        title={Text("Passer cette catégorie ?")},
        text={Text("Les questions restantes de « ${game.currentCategory} » ne seront pas jouées.")},
        confirmButton={TextButton(onClick={send(GameEvent.HostSkipCategory(game.currentCategory));confirmSkipCategory=false}){Text("Passer")}},
        dismissButton={TextButton(onClick={confirmSkipCategory=false}){Text("Annuler")}}
    )
    }
}
