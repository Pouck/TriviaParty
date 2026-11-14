package com.example.triviaparty.ui.host

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.ui.Alignment
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.triviaparty.data.*
import com.example.triviaparty.model.*
import com.example.triviaparty.ui.player.components.OrderingView
import com.example.triviaparty.cast.GoogleCastController
import com.example.triviaparty.ui.cast.GoogleCastButton
import com.example.triviaparty.ui.cast.GoogleCastDeviceStatus
import com.example.triviaparty.network.GameServer
import com.example.triviaparty.util.NetworkUtils
import java.io.File

internal fun reviewAnswer(question: Question): String = when(question) {
    is Question.MultipleChoice -> question.options.getOrNull(question.correctOptionIndex).orEmpty()
    is Question.Ordering -> question.correctOrderIds.mapNotNull { id -> question.items.find { it.id==id }?.text }.joinToString(" → ")
    is Question.TextAnswer -> question.acceptableAnswers.firstOrNull().orEmpty()
    is Question.GuessWho -> question.acceptableAnswers.firstOrNull().orEmpty()
    is Question.MapPin -> question.options.getOrNull(question.correctOptionIndex)?.label ?: "Emplacement attendu sur la carte"
    is Question.Wager -> reviewAnswer(question.subQuestion)
    is Question.SpeedRace -> reviewAnswer(question.subQuestion)
}

@Composable internal fun SoloReviewScreen(categories: List<String>, server: GameServer, googleCast: GoogleCastController, close: () -> Unit) {
    val context=LocalContext.current
    val store=remember { HostReviewStore(File(context.filesDir,"host-review.json")) }
    val questions=remember(categories) { categories.distinct().flatMap { QuestionBankRepository.getQuestionsForCategory(it) }
        .distinctBy { it.id }.map { it.withRandomVariant().withChronologyCards() } }
    var index by remember { mutableIntStateOf(0) }
    val question=questions.getOrNull(index)
    if(question==null) { Column(Modifier.fillMaxSize().padding(24.dp)) { Text("Aucune question à revoir"); Button(onClick=close) { Text("Retour") } }; return }
    val saved=remember(question.id) { store.read().reviews[question.id] }
    var revealed by remember(question.id) { mutableStateOf(false) }
    var difficulty by remember(question.id) { mutableStateOf(saved?.difficulty) }
    var comment by remember(question.id) { mutableStateOf(saved?.comment.orEmpty()) }
    var clue by remember(question.id) { mutableIntStateOf(0) }
    var selected by remember(question.id) { mutableStateOf<Int?>(null) }
    var spoken by remember(question.id) { mutableStateOf("") }
    var items by remember(question.id) { mutableStateOf((question as? Question.Ordering)?.items.orEmpty()) }
    var result by remember(question.id) { mutableStateOf<Boolean?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    val scroll=rememberScrollState()
    val tone=remember { android.media.ToneGenerator(android.media.AudioManager.STREAM_MUSIC,65) }
    var showCastDialog by remember { mutableStateOf(false) }
    val castStatus by googleCast.status.collectAsState()
    DisposableEffect(tone) { onDispose { tone.release() } }
    DisposableEffect(googleCast) { onDispose { googleCast.clearReviewPreview() } }
    LaunchedEffect(Unit) { server.start() }
    LaunchedEffect(question.id) { scroll.scrollTo(0) }
    val reviewMode = QuestionBankRepository.getCategoryPackage(question.category)?.answerMode
        ?: if(question is Question.GuessWho) CategoryAnswerMode.BUZZER else CategoryAnswerMode.SIMULTANEOUS
    val preview = remember(question.id, clue, revealed, reviewMode, index) {
        GameSession(roomId="review", hostIpAddress=NetworkUtils.getLocalIpAddress(), state=if(revealed) GameState.REVEAL_ANSWER else GameState.QUESTION_ACTIVE,
            currentCategory=question.category, currentCategoryAnswerMode=reviewMode, currentCategoryQuestionTypes=listOf("Révision"),
            currentCategoryQuestionCount=questions.size, availableCategories=listOf(question.category), currentQuestion=question,
            currentFlipNumber=clue, roundNumber=index+1, totalRounds=questions.size,
            timingConfig=HourglassConfig(secondsPerFlip=20, maxFlips=2, pointsDecayPerFlip=5))
    }
    LaunchedEffect(preview) { googleCast.showReviewPreview(preview) }
    fun judge(correct: Boolean) { result=correct; tone.startTone(if(correct) android.media.ToneGenerator.TONE_PROP_ACK else android.media.ToneGenerator.TONE_PROP_NACK,300) }
    fun save(): Boolean = runCatching {
        if(revealed && (comment.isNotBlank() || difficulty!=null || saved!=null)) store.saveReview(QuestionReview(question.id,question.category,
            question.prompt + if(question is Question.GuessWho) "\n"+question.clues.joinToString("\n") else "",comment,difficulty))
    }.onFailure { error=it.message }.isSuccess
    BackHandler { if(save()) close() }
    val choices=when(question) {
        is Question.MultipleChoice -> question.options
        is Question.Wager -> question.subQuestion.options
        is Question.SpeedRace -> question.subQuestion.options
        is Question.MapPin -> question.options.map { it.label }
        else -> emptyList()
    }
    val correctIndex=when(question) {
        is Question.MultipleChoice -> question.correctOptionIndex
        is Question.Wager -> question.subQuestion.correctOptionIndex
        is Question.SpeedRace -> question.subQuestion.correctOptionIndex
        is Question.MapPin -> question.correctOptionIndex
        else -> -1
    }
    val image=question.imageUrl?.let { url ->
        if(url.startsWith("local-media://")) {
            val parts=url.removePrefix("local-media://").split('/',limit=2)
            if(parts.size==2) GamePackageImportRepository.mediaFile(File(context.filesDir,"game-packages"),parts[0],parts[1]) else null
        } else url
    }
    MaterialTheme(colorScheme=darkColorScheme(primary=Color(0xFFFFD54F),onPrimary=Color(0xFF19191F),surface=Color(0xFF232333),onSurface=Color.White)) {
    Column(Modifier.fillMaxSize().background(Color(0xFF12121D)).padding(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
        Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween, verticalAlignment=Alignment.CenterVertically) {
            Text("Révision ${index+1}/${questions.size}",color=Color.White,fontSize=22.sp,fontWeight=FontWeight.Bold)
            Row(verticalAlignment=Alignment.CenterVertically) {
                GoogleCastButton(Modifier.size(width=44.dp, height=44.dp))
                if (castStatus.connected) TextButton(onClick={ showCastDialog=true }) { Text("Son") }
                TextButton(onClick={ if(save()) close() }) { Text("Fermer") }
            }
        }
        Column(Modifier.weight(1f).verticalScroll(scroll),verticalArrangement=Arrangement.spacedBy(16.dp)) {
            Text(question.category,color=Color(0xFFFFD54F),fontSize=16.sp)
            if(image!=null) AsyncImage(model=image,contentDescription="Illustration de la question",contentScale=ContentScale.Fit,
                modifier=Modifier.fillMaxWidth().heightIn(min=180.dp,max=300.dp))
            Text(question.activePrompt(clue),color=Color.White,fontSize=24.sp,lineHeight=30.sp)
            if(question is Question.GuessWho && !revealed && clue<question.clues.lastIndex) {
                OutlinedButton(onClick={ clue++ }) { Text("Indice suivant (${clue+1}/${question.clues.size})") }
            }
            choices.forEachIndexed { choice,text ->
                val color=if(revealed && choice==correctIndex) Color(0xFF246541) else if(selected==choice) Color(0xFF3C5275) else Color(0xFF2A2A3C)
                Button(onClick={ selected=choice; revealed=true; judge(choice==correctIndex) },enabled=!revealed,
                    colors=ButtonDefaults.buttonColors(containerColor=color,disabledContainerColor=color,disabledContentColor=Color.White),modifier=Modifier.fillMaxWidth()) {
                    Text(text,fontSize=19.sp,lineHeight=25.sp)
                }
            }
            if(question is Question.Ordering && !revealed) OrderingView(items,onReorder={ items=it })
            if(choices.isEmpty() && question !is Question.Ordering && !revealed) OutlinedTextField(value=spoken,onValueChange={ spoken=it },
                label={ Text("Votre réponse (facultatif)") },modifier=Modifier.fillMaxWidth())
            if(!revealed) Button(onClick={ revealed=true; if(question is Question.Ordering) judge(items.map { it.id }==question.correctOrderIds) },modifier=Modifier.fillMaxWidth()) { Text("Révéler la réponse") }
            if(revealed) {
                Surface(color=Color(0xFF173E30),shape=androidx.compose.foundation.shape.RoundedCornerShape(12.dp)) {
                    Column(Modifier.fillMaxWidth().padding(16.dp),verticalArrangement=Arrangement.spacedBy(8.dp)) {
                        Text("Réponse",color=Color(0xFFA6ECC3))
                        Text(reviewAnswer(question),color=Color.White,fontSize=26.sp,lineHeight=32.sp,fontWeight=FontWeight.Bold)
                    }
                }
                if(result==null) Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                    Button(onClick={ judge(true) }) { Text("Bonne réponse") }
                    OutlinedButton(onClick={ judge(false) }) { Text("Mauvaise réponse") }
                } else Text(if(result==true) "Bonne réponse !" else "Mauvaise réponse",color=if(result==true) Color(0xFFA6ECC3) else Color(0xFFFF9D9D))
                Text("Difficulté · 1 facile — 5 difficile",color=Color.White)
                FilterChip(selected=difficulty==0,onClick={ difficulty=if(difficulty==0) null else 0 },label={ Text("0 — À réviser") })
                Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) { (1..5).forEach { rating ->
                    FilterChip(selected=difficulty==rating,onClick={ difficulty=if(difficulty==rating) null else rating },label={ Text("$rating") })
                } }
                OutlinedTextField(value=comment,onValueChange={ comment=it },label={ Text("Commentaire / correction") },modifier=Modifier.fillMaxWidth(),minLines=3)
                Text("Notes enregistrées en passant à la question suivante ou en fermant.",color=Color.LightGray,fontSize=13.sp)
                TextButton(onClick={ save() }) { Text("Enregistrer maintenant") }
            }
            error?.let { Text(it,color=Color(0xFFFF9D9D)) }
        }
        Button(onClick={ if(save()) { if(index<questions.lastIndex) index++ else close() } },enabled=revealed,modifier=Modifier.fillMaxWidth()) {
            Text(if(index<questions.lastIndex) "Question suivante" else "Terminer la révision")
        }
    }
    }
    if (showCastDialog) {
        AlertDialog(onDismissRequest={ showCastDialog=false }, title={ Text("Diffuser la révision") },
            text={ Column(Modifier.heightIn(max=360.dp).verticalScroll(rememberScrollState())) {
                Text("La question affichée sur le téléphone est envoyée au téléviseur. Révélez la réponse sur le téléphone quand vous êtes prêt.")
                GoogleCastDeviceStatus(googleCast)
                Button(onClick = { googleCast.testAudio() }) { Text("Tester le son TV") }
                castStatus.audioStatus?.let { Text(it, fontSize = 14.sp) }
            } }, confirmButton={ TextButton(onClick={ showCastDialog=false }) { Text("Fermer") } })
    }
}
