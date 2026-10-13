const fs = require('node:fs');
const base = 'app/src/main/java/com/example/triviaparty/';
function edit(file, fn) { fs.writeFileSync(file, fn(fs.readFileSync(file, 'utf8'))); }
edit(base+'ui/player/PlayerScreen.kt', s => {
  s=s.replace('    var draftAnswerValue by remember { mutableStateOf<AnswerValue?>(null) }','');
  const start=s.indexOf('                val mySub =');
  const end=s.indexOf('\n@Composable\nprivate fun PlayerJoinForm');
  s=s.slice(0,start)+`                var pressed by remember(currentSession.currentQuestion?.id) { mutableStateOf(false) }
                val status = currentSession.buzzerStatus(myTeamId!!, connState == ClientConnectionState.CONNECTED, pressed)
                LaunchedEffect(pressed, currentSession.submissions, currentSession.state, connState) {
                    if (pressed) { kotlinx.coroutines.delay(1200); pressed = false }
                }
                Column(Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
                    PlayerHeader(myTeam?.name.orEmpty(), myTeam?.score ?: 0, true)
                    Spacer(Modifier.weight(1f))
                    val color = when (status) {
                        BuzzerStatus.READY -> Color(0xFFFFD54F)
                        BuzzerStatus.PRESSED -> Color(0xFF4DA3FF)
                        BuzzerStatus.INCORRECT -> Color(0xFFE45B67)
                        BuzzerStatus.CORRECT -> Color(0xFF70D69B)
                        else -> Color(0xFF55556D)
                    }
                    Button(
                        enabled = status == BuzzerStatus.READY,
                        onClick = {
                            currentSession.currentQuestion?.let { question ->
                                pressed = true
                                client.sendEvent(GameEvent.LockAnswer(myTeamId!!, question.id, AnswerValue.TextSelection("BUZZ")))
                            }
                        },
                        modifier = Modifier.fillMaxWidth().heightIn(min = 180.dp),
                        shape = RoundedCornerShape(28.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = color, contentColor = Color(0xFF12121D),
                            disabledContainerColor = color, disabledContentColor = Color.White)
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("BUZZER", fontSize = 36.sp, fontWeight = FontWeight.Black)
                            Text(status.label, fontSize = 16.sp, textAlign = TextAlign.Center)
                        }
                    }
                    Spacer(Modifier.weight(1f))
                }
            }
        }
    }
}
`+s.slice(end);
  const interactive=s.indexOf('\n@Composable\nprivate fun PlayerInteractiveQuestion');
  s=s.slice(0,interactive);
  return s.replace(/^import com.example.triviaparty.ui.player.components.*\r?\n/gm,'');
});
edit(base+'network/GameServer.kt',s=>{
  s=s.replace('if (question is Question.TextAnswer) {\n            if (event.teamId', 'if (question is Question.TextAnswer || (event.answer as? AnswerValue.TextSelection)?.text == "BUZZ") {\n            if (event.teamId');
  s=s.replace(/session\.currentQuestion as\? Question\.TextAnswer \?: return/g,'session.currentQuestion ?: return');
  s=s.replace('val unansweredBuzz = session.currentQuestion is Question.TextAnswer &&','val unansweredBuzz =');
  s=s.replace('else sub.copy(isCorrect = evaluateAnswer(question, sub.answer))','else if ((sub.answer as? AnswerValue.TextSelection)?.text == "BUZZ") sub.copy(isCorrect = sub.isCorrect ?: false)\n            else sub.copy(isCorrect = evaluateAnswer(question, sub.answer))');
  s=s.replace('if (question is Question.TextAnswer) return@map team','if (question is Question.TextAnswer || (sub.answer as? AnswerValue.TextSelection)?.text == "BUZZ") return@map team');
  s=s.replace('val teamId = requestingTeamId ?: return','val teamId = requestingTeamId');
  s=s.replace('if (teamId != currentSession.pickerTeamId) return','if (teamId != null && teamId != currentSession.pickerTeamId) return');
  s=s.replace('if (currentSession.teams.find { it.id == teamId }?.score != highestScore) return','if (teamId != null && currentSession.teams.find { it.id == teamId }?.score != highestScore) return');
  const start=s.indexOf('        fun redactQuestion(');
  const end=s.indexOf('        val stateJson =',start);
  s=s.slice(0,start)+s.slice(end);
  s=s.replace('stateJson["currentQuestion"]?.let { stateJson["currentQuestion"] = redactQuestion(it) }','stateJson["currentQuestion"] = state.currentQuestion?.let { JsonObject(mapOf("id" to JsonPrimitive(it.id))) } ?: kotlinx.serialization.json.JsonNull');
  return s;
});
edit(base+'ui/host/HostScreen.kt',s=>{
  s=s.replace('CategorySelectionPanel(game, leader)','CategorySelectionPanel(game, leader, client)');
  s=s.replace('private fun CategorySelectionPanel(game: GameSession, leader: Team?)','private fun CategorySelectionPanel(game: GameSession, leader: Team?, client: GameClient)');
  s=s.replace('choisit sur son téléphone','choisit avec l’hôte');
  s=s.replace('Text("Choix proposés :', 'game.availableCategories.forEach { category ->\n            Button(onClick = { client.sendEvent(GameEvent.HostSelectCategory(category)) }) { Text(category) }\n        }\n        Text("Choix proposés :');
  s=s.replace(/if \(question is Question.TextAnswer\) \{/g,'if (question != null) {');
  s=s.replace(/val waitingForTextJudgment = question is Question.TextAnswer &&/g,'val waitingForTextJudgment =');
  s=s.replace('game.currentQuestion as? Question.TextAnswer ?: return','game.currentQuestion ?: return');
  return s;
});
