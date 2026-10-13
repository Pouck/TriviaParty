package com.example.triviaparty.ui.cast

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.triviaparty.model.GameSession
import com.example.triviaparty.model.GameState
import com.example.triviaparty.model.activePrompt
import com.example.triviaparty.model.Question
import com.example.triviaparty.model.label
import com.example.triviaparty.model.revealPrompt
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import com.example.triviaparty.ui.components.HourglassTimer
import com.example.triviaparty.ui.player.components.MapPinView

@Composable
fun CastTvScreen(
    session: GameSession,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFF0F0F1A))
            .padding(horizontal = 20.dp, vertical = 12.dp)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar: Room Code & Category
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "QUIZ ENTRE AMIS",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Black,
                    color = Color(0xFFFFD700)
                )

                Text(
                    text = "Catégorie : ${session.currentCategory ?: "Salon"}",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color.White
                )

            }

            Spacer(modifier = Modifier.height(8.dp))

            // Main Content Area
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                when (session.state) {
                    GameState.LOBBY -> LobbyTvView(session)
                    GameState.SUBJECT_VOTING -> Column(Modifier.verticalScroll(rememberScrollState()),horizontalAlignment=Alignment.CenterHorizontally) {
                        Text("Vote des catégories",color=Color.White,fontSize=32.sp)
                        session.subjectVoting?.let { vote ->
                            vote.candidates.forEach { Text("$it · ${vote.totals()[it]} vote(s)",color=Color.White,fontSize=22.sp) }
                        }
                    }
                    GameState.CATEGORY_SELECT -> CategorySelectTvView(session)
                    GameState.CATEGORY_INTRO -> CategoryIntroTvView(session)
                    GameState.WAGER_OPEN -> Text("${session.currentCategory}\nChoisissez votre mise sur votre téléphone",
                        color = Color.White, fontSize = 32.sp, textAlign = TextAlign.Center)
                    GameState.WAGER_RESULTS -> Column(Modifier.verticalScroll(rememberScrollState()),
                        horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("RÉSULTATS DES MISES", color = Color(0xFFFFD700), fontSize = 30.sp)
                        session.categoryWagerResults.forEach {
                            Text("${it.teamName} · Mise : ${it.amount} · ${if (it.delta > 0) "+" else ""}${it.delta} pts",
                                color = Color.White, fontSize = 24.sp)
                        }
                    }
                    GameState.QUESTION_ACTIVE,GameState.ANSWER_REVIEW -> ActiveQuestionTvView(session)
                    GameState.REVEAL_ANSWER -> RevealAnswerTvView(session)
                    GameState.ROUND_SUMMARY -> RoundSummaryTvView(session)
                    GameState.GAME_ENDED -> GameEndedTvView(session)
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            if (session.state in setOf(GameState.CATEGORY_SELECT, GameState.CATEGORY_INTRO, GameState.GAME_ENDED)) {
                TeamScoreTicker(session)
            }
            if (session.state in setOf(GameState.REVEAL_ANSWER, GameState.ROUND_SUMMARY, GameState.WAGER_RESULTS)) {
                Column(Modifier.fillMaxWidth().heightIn(max = 180.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    session.teams.sortedByDescending { it.score }.chunked(3).forEach { row ->
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            row.forEach { team ->
                                val rank = 1 + session.teams.count { it.score > team.score }
                                Text("$rank. ${team.name} · ${team.score} pts", color = Color(0xFFFFD700), fontSize = 16.sp,
                                    modifier = Modifier.weight(1f))
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun LobbyTvView(session: GameSession) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "REJOIGNEZ LA PARTIE !",
            fontSize = 40.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
        Text(
            text = "Scannez le code QR affiché par l’hôte pour rejoindre la partie",
            fontSize = 22.sp,
            color = Color.LightGray
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "ÉQUIPES CONNECTÉES (${session.teams.size}) :",
            fontSize = 18.sp,
            color = Color(0xFFFFD700)
        )

        Spacer(modifier = Modifier.height(12.dp))

        LazyRow(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            items(session.teams) { team ->
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF2D2D3F)),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        text = team.name,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun CategorySelectTvView(session: GameSession) {
    val pickerTeam = session.teams.find { it.id == session.pickerTeamId }
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "${pickerTeam?.name ?: "L’équipe en tête"} choisit une catégorie !",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFFD700)
        )
        Spacer(modifier = Modifier.height(24.dp))

        LazyRow(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            items(session.availableCategories) { cat ->
                Box(
                    modifier = Modifier
                        .size(180.dp, 120.dp)
                        .background(Color(0xFF2D2D3F), shape = RoundedCornerShape(16.dp))
                        .border(2.dp, Color(0xFFFFD700), shape = RoundedCornerShape(16.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = cat,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun ActiveQuestionTvView(session: GameSession) {
    val question = session.currentQuestion ?: return
    Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
        if (!question.imageUrl.isNullOrBlank()) {
            Box(Modifier.weight(1.8f).fillMaxHeight(), contentAlignment = Alignment.Center) {
                if (question is Question.MapPin) MapPinView(question.imageUrl, question.options, null, { _, _ -> }, Modifier.fillMaxSize())
                else AsyncImage(model = question.imageUrl, contentDescription = "Illustration de la question",
                    contentScale = ContentScale.Fit, modifier = Modifier.fillMaxSize())
            }
        }
        Column(Modifier.weight(1f).fillMaxHeight(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            val team = session.answerTimerTeamId?.let { id -> session.teams.find { it.id == id } }
            if (session.answerTimerRunning) Text("${team?.name.orEmpty()} À LA PAROLE · ${session.answerTimerRemainingSeconds ?: session.answerTimeSeconds} s",
                color = Color(0xFFFFD700), fontSize = 24.sp, fontWeight = FontWeight.Bold)
            else {
                val seconds = (session.timingConfig.secondsPerFlip - session.elapsedSecondsInFlip).coerceAtLeast(0)
                val points = session.timingConfig.calculateScore(question.basePoints, session.currentFlipNumber, session.elapsedSecondsInFlip)
                Text(if (session.questionReading) "Lecture · réponses fermées" else "$seconds s · $points pts", color = Color(0xFFFFD700), fontSize = 24.sp)
            }
            Column(Modifier.weight(1f).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(question.activePrompt(session.currentFlipNumber),
                    fontSize = if (question is Question.GuessWho && question.clues.size >= 4) 20.sp else 24.sp,
                    fontWeight = FontWeight.Bold, color = Color.White)
                com.example.triviaparty.ui.host.SpectatorChoices(question, columns = if (question.imageUrl.isNullOrBlank()) 2 else 1)
            }
        }
    }
}

@Composable
private fun CategoryIntroTvView(session: GameSession) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("NOUVELLE CATÉGORIE", fontSize = 30.sp, fontWeight = FontWeight.Bold, color = Color(0xFFFFD700))
        Text(session.currentCategory.orEmpty(), fontSize = 38.sp, fontWeight = FontWeight.Black, color = Color.White)
        Text("${session.currentCategoryQuestionCount} questions", fontSize = 26.sp, color = Color.White)
        Text("Types : ${session.currentCategoryQuestionTypes.joinToString(" · ")}", fontSize = 20.sp, color = Color.LightGray)
        Text("Mode : ${session.currentCategoryAnswerMode?.label().orEmpty()}", fontSize = 20.sp, color = Color.LightGray)
    }
}

@Composable
private fun TeamScoreTicker(session: GameSession) {
    LazyRow(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFF1E1E2C), shape = RoundedCornerShape(12.dp))
            .padding(horizontal = 10.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        items(session.teams) { team ->
            val locked = session.submissions[team.id]?.isLocked == true
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(team.name, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
                Text(" ${team.score} pts", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color(0xFFFFD700))
                if (session.state == GameState.QUESTION_ACTIVE) Text(if (locked) " 🔒" else " ✍️", fontSize = 14.sp)
            }
        }
    }
}

@Composable
private fun RevealAnswerTvView(session: GameSession) {
    val question = session.currentQuestion ?: return
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "RÉPONSE RÉVÉLÉE !",
            fontSize = 36.sp,
            fontWeight = FontWeight.Black,
            color = Color(0xFFFFD700)
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = question.revealPrompt(),
            fontSize = 18.sp,
            color = Color.White,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(24.dp))

        Box(
            modifier = Modifier
                .background(Color(0xFF1B4D3E), shape = RoundedCornerShape(16.dp))
                .border(2.dp, Color(0xFF4CAF50), shape = RoundedCornerShape(16.dp))
                .padding(24.dp)
        ) {
            val answerText = when (question) {
                is Question.MultipleChoice -> question.options.getOrNull(question.correctOptionIndex) ?: ""
                is Question.Ordering -> question.correctOrderIds.mapNotNull { id -> question.items.find { it.id == id }?.text }.joinToString(" → ")
                is Question.TextAnswer -> question.acceptableAnswers.firstOrNull() ?: ""
                is Question.GuessWho -> question.acceptableAnswers.firstOrNull() ?: ""
                is Question.MapPin -> question.options.getOrNull(question.correctOptionIndex)?.label ?: "Réponse sur la carte"
                is Question.Wager -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex) ?: ""
                is Question.SpeedRace -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex) ?: ""
            }
            Text(
                text = "Bonne réponse :\n$answerText",
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun RoundSummaryTvView(session: GameSession) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "CLASSEMENT APRÈS LA QUESTION ${session.roundNumber}",
            fontSize = 36.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFFD700)
        )
    }
}

@Composable
private fun GameEndedTvView(session: GameSession) {
    val winner = session.teams.maxByOrNull { it.score }?.takeIf { it.score > 0 }
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = if (winner != null) "🏆 GAGNANT 🏆" else "PARTIE TERMINÉE",
            fontSize = 44.sp,
            fontWeight = FontWeight.Black,
            color = Color(0xFFFFD700)
        )
        Text(
            text = winner?.name ?: "Bel effort !",
            fontSize = 36.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
        Text(
            text = "Score final : ${winner?.score ?: 0} pts",
            fontSize = 28.sp,
            color = Color.LightGray
        )
    }
}

