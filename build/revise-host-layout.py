from pathlib import Path

path = Path('app/src/main/java/com/example/triviaparty/ui/host/HostScreen.kt')
text = path.read_text(encoding='utf-8-sig')
start = text.index('@Composable\nprivate fun ActiveQuestionPanel(')
end = text.index('@Composable\nprivate fun AnswerTimerControls', start)
text = text[:start] + '''@Composable
private fun ActiveQuestionPanel(
    game: GameSession, paused: Boolean, onPause: () -> Unit, onReveal: () -> Unit,
    onJudgeText: (String, Boolean) -> Unit
) {
    val question = game.currentQuestion ?: return
    val index = game.currentCategory?.let { category ->
        QuestionBankRepository.getQuestionsForCategory(category).count { it.id in game.playedQuestionIds }
    } ?: game.roundNumber
    Column(Modifier.fillMaxSize().padding(horizontal = 12.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)) {
        // Reserve the right side for JOINDRE / SCORE / FIN, on the same header line.
        Box(Modifier.fillMaxWidth().height(40.dp).padding(end = 250.dp), contentAlignment = Alignment.CenterStart) {
            Text("QUESTION $index/${game.currentCategoryQuestionCount}", color = HostGold,
                fontSize = 18.sp, fontWeight = FontWeight.Black)
        }
        val image = !question.imageUrl.isNullOrBlank()
        if (image) {
            Row(Modifier.weight(1f).fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(Modifier.weight(1.8f).fillMaxHeight(), contentAlignment = Alignment.Center) {
                    if (question is Question.MapPin) {
                        MapPinView(question.imageUrl, question.options, null, { _, _ -> }, Modifier.fillMaxSize())
                    } else AsyncImage(model = question.imageUrl, contentDescription = "Illustration de la question",
                        contentScale = ContentScale.Fit, modifier = Modifier.fillMaxSize())
                }
                QuestionControls(game, question, paused, onPause, onReveal, onJudgeText,
                    Modifier.weight(1f).fillMaxHeight(), compact = true)
            }
        } else QuestionControls(game, question, paused, onPause, onReveal, onJudgeText,
            Modifier.weight(1f).fillMaxWidth(), compact = false)
    }
}

@Composable
private fun QuestionControls(
    game: GameSession, question: Question, paused: Boolean, onPause: () -> Unit, onReveal: () -> Unit,
    onJudgeText: (String, Boolean) -> Unit, modifier: Modifier, compact: Boolean
) {
    val config = game.timingConfig
    val elapsed = game.elapsedSecondsInFlip.coerceIn(0, config.secondsPerFlip.coerceAtLeast(1))
    val points = config.calculateScore(question.basePoints, game.currentFlipNumber, elapsed)
    val answering = game.answerTimerTeamId?.let { id -> game.teams.find { it.id == id } }
        ?: game.submissions.values.firstOrNull { it.isLocked && it.isCorrect != false && it.isBuzz() }
            ?.let { submission -> game.teams.find { it.id == submission.teamId } }
    val buzzer = question is Question.TextAnswer || game.currentCategoryAnswerMode == com.example.triviaparty.model.CategoryAnswerMode.BUZZER
    Column(modifier, verticalArrangement = Arrangement.spacedBy(6.dp)) {
        if (game.answerTimerRunning) AnswerTimerControls(game, compact)
        else Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("$points pts", color = HostGold, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            LinearProgressIndicator(progress = { 1f - elapsed.toFloat() / config.secondsPerFlip.coerceAtLeast(1) },
                modifier = Modifier.weight(1f).height(8.dp), color = HostGold, trackColor = HostBackground)
            Text("${(config.secondsPerFlip - elapsed).coerceAtLeast(0)} s", color = Color.White)
        }
        if (buzzer) {
            Text(answering?.let { "${it.name} A LA PAROLE" } ?: "En attente d’un buzzer",
                color = if (answering != null) HostGold else Color.LightGray, fontWeight = FontWeight.Black,
                fontSize = if (compact) 18.sp else 22.sp,
                modifier = Modifier.fillMaxWidth().background(HostBackground, RoundedCornerShape(8.dp)).padding(8.dp))
        }
        Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(question.prompt, color = Color.White, fontWeight = FontWeight.Bold,
                fontSize = if (compact) 19.sp else 23.sp)
            SpectatorChoices(question, columns = if (compact) 1 else 2)
        }
        answering?.let { team ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { onJudgeText(team.id, true) }, modifier = Modifier.weight(1f),
                    contentPadding = PaddingValues(6.dp)) { Text("Bonne réponse", fontSize = 13.sp) }
                Button(onClick = { onJudgeText(team.id, false) }, modifier = Modifier.weight(1f),
                    contentPadding = PaddingValues(6.dp)) { Text("Mauvaise réponse", fontSize = 13.sp) }
            }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            OutlinedButton(onClick = onPause, enabled = !game.answerTimerRunning,
                contentPadding = PaddingValues(8.dp)) { Text(if (paused) "Reprendre" else "Pause") }
            val connected = game.teams.filter { it.isConnected }
            val allAnswered = connected.isEmpty() || connected.all { game.submissions[it.id]?.isLocked == true }
            if (answering == null && allAnswered) {
                Button(onClick = onReveal, modifier = Modifier.weight(1f), contentPadding = PaddingValues(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = HostGold, contentColor = Color.Black)) {
                    Text("RÉVÉLER LA RÉPONSE", fontWeight = FontWeight.Black, fontSize = 13.sp)
                }
            } else if (answering == null) Text("En attente des réponses…", color = Color.LightGray, fontSize = 13.sp)
        }
    }
}

/** Fixed public list; never follows a player's private ordering draft. */
@Composable
internal fun SpectatorChoices(question: Question, columns: Int = 2) {
    val choices = when (question) {
        is Question.MultipleChoice -> question.options
        is Question.SpeedRace -> question.subQuestion.options
        is Question.Wager -> question.subQuestion.options
        is Question.Ordering -> question.items.map { it.text }
        is Question.MapPin -> question.options.map { it.label }
        else -> emptyList()
    }
    CompactGrid(choices, columns) { value ->
        Text(value, color = Color.White, fontSize = 17.sp,
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

''' + text[end:]
start = text.index('@Composable\nprivate fun RevealPanel(')
end = text.index('@Composable\nprivate fun EndPanel', start)
text = text[:start] + '''@Composable
private fun RevealPanel(game: GameSession, categoryQuestionIndex: Int, hasMore: Boolean, isLastQuestion: Boolean, onNext: () -> Unit) {
    val question = game.currentQuestion
    val answer = when (question) {
        is Question.MultipleChoice -> question.options.getOrNull(question.correctOptionIndex).orEmpty()
        is Question.Ordering -> question.correctOrderIds.mapNotNull { id -> question.items.find { it.id == id }?.text }.joinToString(" → ")
        is Question.TextAnswer -> question.acceptableAnswers.firstOrNull().orEmpty()
        is Question.MapPin -> question.options.getOrNull(question.correctOptionIndex)?.label.orEmpty()
        is Question.Wager -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex).orEmpty()
        is Question.SpeedRace -> question.subQuestion.options.getOrNull(question.subQuestion.correctOptionIndex).orEmpty()
        null -> ""
    }
    Column(Modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(Modifier.fillMaxWidth().height(40.dp).padding(end = 250.dp), contentAlignment = Alignment.CenterStart) {
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
                    Text(question?.prompt.orEmpty(), color = Color.LightGray, fontSize = 18.sp)
                    Text(answer, color = Color.White, fontSize = 26.sp, fontWeight = FontWeight.Black,
                        modifier = Modifier.fillMaxWidth().background(Color(0xFF173D30), RoundedCornerShape(8.dp)).padding(12.dp))
                }
            }
            Leaderboard(game, Modifier.weight(1f).fillMaxHeight())
        }
        Button(onClick = onNext, modifier = Modifier.fillMaxWidth().height(48.dp),
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
            CompactGrid(game.teams.leadersWithTies()) { team ->
                val rank = 1 + game.teams.count { it.score > team.score }
                Column(Modifier.fillMaxWidth().background(HostBackground, RoundedCornerShape(8.dp)).padding(8.dp)) {
                    Text("$rank. ${team.name}", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Text("${team.score} pts", color = HostGold, fontSize = 18.sp)
                }
            }
        }
    }
}

@Composable
private fun WagerOfferPanel(game: GameSession, onStart: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(Modifier.fillMaxWidth().height(40.dp).padding(end = 250.dp), contentAlignment = Alignment.CenterStart) {
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
            Button(onClick = onStart) { Text("FERMER LES MISES ET COMMENCER") }
        }
    }
}

''' + text[end:]
path.write_text(text, encoding='utf-8')
