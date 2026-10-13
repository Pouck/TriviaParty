from pathlib import Path
path = Path('app/src/main/java/com/example/triviaparty/ui/cast/CastTvScreen.kt')
text = path.read_text(encoding='utf-8-sig')
start = text.index('@Composable\nprivate fun ActiveQuestionTvView(')
end = text.index('@Composable\nprivate fun CategoryIntroTvView(', start)
text = text[:start] + '''@Composable
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
            if (session.answerTimerRunning) Text("${team?.name.orEmpty()} A LA PAROLE · ${session.answerTimerRemainingSeconds ?: session.answerTimeSeconds} s",
                color = Color(0xFFFFD700), fontSize = 24.sp, fontWeight = FontWeight.Bold)
            else {
                val seconds = (session.timingConfig.secondsPerFlip - session.elapsedSecondsInFlip).coerceAtLeast(0)
                val points = session.timingConfig.calculateScore(question.basePoints, session.currentFlipNumber, session.elapsedSecondsInFlip)
                Text("$seconds s · $points pts", color = Color(0xFFFFD700), fontSize = 24.sp)
            }
            Column(Modifier.weight(1f).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(question.prompt, fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.White)
                com.example.triviaparty.ui.host.SpectatorChoices(question, columns = if (question.imageUrl.isNullOrBlank()) 2 else 1)
            }
        }
    }
}

''' + text[end:]
text = text.replace('is Question.Ordering -> question.items.joinToString(" → ") { it.text }',
    'is Question.Ordering -> question.correctOrderIds.mapNotNull { id -> question.items.find { it.id == id }?.text }.joinToString(" → ")')
# Keep ties in the visible grid rather than hiding them beyond a horizontal ticker.
start = text.index('                LazyRow(horizontalArrangement = Arrangement.spacedBy(20.dp)) {')
end = text.index('\n            }', start)
text = text[:start] + '''                Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    session.teams.leadersWithTies().chunked(3).forEach { row ->
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            row.forEach { team ->
                                val rank = 1 + session.teams.count { it.score > team.score }
                                Text("$rank. ${team.name} · ${team.score} pts", color = Color(0xFFFFD700), fontSize = 20.sp,
                                    modifier = Modifier.weight(1f))
                            }
                        }
                    }
                }''' + text[end:]
path.write_text(text.replace('A LA PAROLE', 'À LA PAROLE'), encoding='utf-8')
host = Path('app/src/main/java/com/example/triviaparty/ui/host/HostScreen.kt')
host.write_text(host.read_text(encoding='utf-8').replace('A LA PAROLE', 'À LA PAROLE'), encoding='utf-8')
