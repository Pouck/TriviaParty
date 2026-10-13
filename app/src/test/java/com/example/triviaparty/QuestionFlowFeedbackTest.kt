package com.example.triviaparty

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.model.*
import com.example.triviaparty.network.*
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test
import java.net.ServerSocket

class QuestionFlowFeedbackTest {
    private val json=Json { encodeDefaults=true }
    @Suppress("UNCHECKED_CAST")
    private fun state(server: GameServer)=GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible=true }.get(server) as MutableStateFlow<GameSession>
    private fun start(server: GameServer,q: Question)=GameServer::class.java.getDeclaredMethod("startQuestion",Question::class.java,String::class.java).apply { isAccessible=true }.invoke(server,q,q.category)
    private fun tick(server: GameServer)=GameServer::class.java.getDeclaredMethod("advanceQuestionTimer",HourglassConfig::class.java).apply { isAccessible=true }.invoke(server,server.gameSession.value.timingConfig)
    private fun buzz(server: GameServer,q: Question): Any? {
        if(server.gameSession.value.questionReading && q is Question.GuessWho) {
            GameServer::class.java.getDeclaredMethod("handleHostStartQuestionTimer").apply {isAccessible=true}.invoke(server)
        }
        return GameServer::class.java.getDeclaredMethod("handleLockAnswer",GameEvent.LockAnswer::class.java).apply { isAccessible=true }.invoke(server,GameEvent.LockAnswer("a",q.id,AnswerValue.TextSelection("BUZZ")))
    }
    private suspend fun WebSocketSession.snapshot(predicate: (JsonObject)->Boolean): JsonObject {
        while (true) { val f=incoming.receive(); if (f is Frame.Text) { val data=Json.parseToJsonElement(f.readText()).jsonObject; if (predicate(data)) return data } }
    }
    private suspend fun WebSocketSession.control(event: GameEvent,q: String) {
        val fields=json.encodeToJsonElement(GameEvent.serializer(),event).jsonObject + ("questionId" to JsonPrimitive(q))
        send(Frame.Text(JsonObject(fields).toString()))
    }
    @Test fun chronologyWaitsForExplicitStartAndPauseResetsForNextQuestion()=runBlocking {
        val port=ServerSocket(0).use { it.localPort }; val server=GameServer(port)
        val client=HttpClient(CIO) { install(WebSockets) }
        val chrono=Question.MultipleChoice("chronology","Test","Ordre ?",basePoints=15,options=listOf("A — X → Y → Z","B — Y → Z → X","C — Z → X → Y","D — Z → Y → X"),correctOptionIndex=0)
        try { server.start(); withTimeout(10000) {
            val host=client.webSocketSession(host="127.0.0.1",port=port,path="/ws")
            host.snapshot { true }
            state(server).value=server.gameSession.value.copy(teams=listOf(Team("a","A",0,sessionToken="a")),timingConfig=HourglassConfig(secondsPerFlip=5,maxFlips=3,pointsDecayPerFlip=5))
            start(server,chrono); repeat(40) { tick(server) }
            assertTrue(server.gameSession.value.currentQuestion is Question.Ordering)
            assertTrue(server.gameSession.value.timingConfig.secondsPerFlip*(server.gameSession.value.timingConfig.maxFlips+1)>=45)
            assertTrue(server.gameSession.value.questionReading)
            assertEquals(0,server.gameSession.value.elapsedSecondsInFlip)
            GameServer::class.java.getDeclaredMethod("handleLockAnswer",GameEvent.LockAnswer::class.java).apply { isAccessible=true }.invoke(server,GameEvent.LockAnswer("a",chrono.id,AnswerValue.MultipleChoiceSelection(0)))
            assertTrue(server.gameSession.value.submissions.isEmpty())
            assertTrue(TvState.from(server.gameSession.value).questionReading)
            host.send(Frame.Text(json.encodeToString<GameEvent>(GameEvent.HostStartQuestionTimer)))
            host.snapshot { it["session"]?.jsonObject?.get("questionReading")==JsonPrimitive(false) && it["session"]?.jsonObject?.get("currentQuestion")?.jsonObject?.get("id")==JsonPrimitive(chrono.id) }
            tick(server); assertEquals(1,server.gameSession.value.elapsedSecondsInFlip)
            host.send(Frame.Text(json.encodeToString<GameEvent>(GameEvent.HostPauseTimer)))
            host.snapshot { it["session"]?.jsonObject?.get("timerPaused")==JsonPrimitive(true) }
            tick(server); assertEquals(1,server.gameSession.value.elapsedSecondsInFlip)
            start(server,chrono.copy(id="ordinary",options=listOf("A","B","C","D")))
            assertFalse(server.gameSession.value.timerPaused); assertFalse(server.gameSession.value.questionReading)
            assertEquals(15,server.gameSession.value.timingConfig.secondsPerFlip)
            tick(server); assertEquals(1,server.gameSession.value.elapsedSecondsInFlip)
            host.close()
        } } finally { client.close(); server.stop() }
    }
    @Test fun privateJudgeNeedsSecretAndWrongAnswersReopenOnNextClue()=runBlocking {
        val port=ServerSocket(0).use { it.localPort }; val server=GameServer(port)
        val client=HttpClient(CIO) { install(WebSockets) }
        val q=Question.GuessWho("secret-question","Test",basePoints=20,clues=listOf("Indice 1","Indice 2","Indice 3","Indice 4"),acceptableAnswers=listOf("Réponse secrète"))
        try { server.start(); withTimeout(10000) {
            val denied=client.webSocketSession(host="127.0.0.1",port=port,path="/judge/ws?token=invalid")
            assertEquals(1008,denied.closeReason.await()!!.code.toInt())
            val key=server.privateJudgeUrl().substringAfter('#')
            val judge=client.webSocketSession(host="127.0.0.1",port=port,path="/judge/ws?token=$key")
            judge.snapshot { true }
            state(server).value=server.gameSession.value.copy(teams=listOf(Team("a","A",0,sessionToken="a")),timingConfig=HourglassConfig(secondsPerFlip=5,maxFlips=3,pointsDecayPerFlip=5))
            start(server,q)
            judge.snapshot { it["answer"]==JsonPrimitive("Réponse secrète") }
            assertEquals(20,server.gameSession.value.timingConfig.secondsPerFlip)
            assertFalse(TvState.from(server.gameSession.value).encode().contains("Réponse secrète"))
            val public=GameServer::class.java.getDeclaredMethod("browserStateText",GameSession::class.java,String::class.java).apply { isAccessible=true }.invoke(server,server.gameSession.value,"a").toString()
            assertFalse(public.contains("Réponse secrète")); assertFalse(public.contains(key))
            buzz(server,q); judge.snapshot { it["answering"]==JsonPrimitive(true) }
            assertEquals(1,server.gameSession.value.buzzerSoundId)
            buzz(server,q);assertEquals(1,server.gameSession.value.buzzerSoundId)
            judge.control(GameEvent.HostJudgeTextBuzz("a",false),q.id)
            judge.snapshot { it["answering"]==JsonPrimitive(false) && it["penalty"]==JsonPrimitive(5) }
            assertEquals(-5,server.gameSession.value.teams.single().score)
            assertEquals("bad",server.gameSession.value.answerSound)
            assertTrue(server.gameSession.value.answerSoundClip in AnswerReactions.clips("bad"))
            assertEquals(1,server.gameSession.value.answerSoundId)
            buzz(server,q); assertFalse(server.gameSession.value.answerTimerRunning)
            repeat(20) { tick(server) }
            assertEquals(1,server.gameSession.value.currentFlipNumber)
            assertTrue(server.gameSession.value.submissions.isEmpty()); assertTrue(server.gameSession.value.textBuzzedTeamIds.isEmpty())
            buzz(server,q); judge.snapshot { it["answering"]==JsonPrimitive(true) }
            assertEquals(2,server.gameSession.value.buzzerSoundId)
            judge.control(GameEvent.HostJudgeTextBuzz("a",true),q.id)
            judge.snapshot { it["phase"]==JsonPrimitive("REVEAL_ANSWER") }
            assertEquals(10,server.gameSession.value.teams.single().score)
            assertEquals("good",server.gameSession.value.answerSound)
            assertTrue(server.gameSession.value.answerSoundClip in AnswerReactions.clips("good"))
            assertEquals(2,server.gameSession.value.answerSoundId)
            judge.close()
        } } finally { client.close(); server.stop() }
    }
    @Test fun chronologyArchivesUseCardsWithoutLosingCorrectOrderOrLeakingItInIds() {
        val q=Question.Ordering("old","Histoire","Classez",items=listOf(Question.OrderItem("c","Troisième"),Question.OrderItem("a","Premier"),Question.OrderItem("b","Deuxième")),correctOrderIds=listOf("a","b","c"))
        assertEquals(q,q.withChronologyCards())
        val mc=Question.MultipleChoice("mc","Histoire","Quel ordre ?\n• Troisième\n• Premier\n• Deuxième",basePoints=15,
            options=listOf("A — Premier → Deuxième → Troisième","B — Deuxième → Premier → Troisième",
                "C — Troisième → Premier → Deuxième","D — Troisième → Deuxième → Premier"),correctOptionIndex=0)
        val cards=mc.withChronologyCards() as Question.Ordering
        assertEquals(listOf("Troisième","Premier","Deuxième"),cards.items.map { it.text })
        assertEquals(listOf("event-0","event-1","event-2"),cards.items.map { it.id })
        assertEquals(listOf("event-1","event-2","event-0"),cards.correctOrderIds)
        assertEquals(15,cards.basePoints)
        assertTrue(cards.spectatorOptions().isEmpty())
        assertEquals(mc.copy(options=listOf("A","B","C","D")),mc.copy(options=listOf("A","B","C","D")).withChronologyCards())
        val malformed=mc.copy(options=mc.options.dropLast(1)+"D — Premier → Inconnu → Troisième")
        assertEquals(malformed,malformed.withChronologyCards())
    }
    @Test fun convertedChronologyScoresTheLockedOrderAndRejectsChangesAfterSubmission() {
        val server=GameServer(0)
        val q=Question.MultipleChoice("drag","Test","Classez",basePoints=15,
            options=listOf("A — X → Y → Z","B — Y → Z → X","C — Z → X → Y","D — Z → Y → X"),correctOptionIndex=0)
        val lock=GameServer::class.java.getDeclaredMethod("handleLockAnswer",GameEvent.LockAnswer::class.java).apply { isAccessible=true }
        try {
            state(server).value=server.gameSession.value.copy(teams=listOf(Team("a","A",0,sessionToken="a"),Team("b","B",0,sessionToken="b")),
                timingConfig=HourglassConfig(secondsPerFlip=10,maxFlips=2,pointsDecayPerFlip=5))
            start(server,q)
            val cards=server.gameSession.value.currentQuestion as Question.Ordering
            lock.invoke(server,GameEvent.LockAnswer("a",q.id,AnswerValue.OrderingSelection(cards.correctOrderIds)))
            assertTrue(server.gameSession.value.submissions.isEmpty())
            state(server).value=server.gameSession.value.copy(questionReading=false,currentFlipNumber=1)
            lock.invoke(server,GameEvent.LockAnswer("a",q.id,AnswerValue.OrderingSelection(cards.correctOrderIds)))
            lock.invoke(server,GameEvent.LockAnswer("a",q.id,AnswerValue.OrderingSelection(cards.correctOrderIds.reversed())))
            lock.invoke(server,GameEvent.LockAnswer("b",q.id,AnswerValue.OrderingSelection(cards.correctOrderIds.reversed())))
            val result=server.gameSession.value
            assertEquals(GameState.REVEAL_ANSWER,result.state)
            assertEquals(listOf(10,0),result.teams.map { it.score })
            assertEquals(true,result.submissions["a"]!!.isCorrect)
            assertEquals(false,result.submissions["b"]!!.isCorrect)
        } finally { server.stop() }
    }
    @Test fun hostCanRevealChronologyBeforeEveryTeamSubmits() {
        val server=GameServer(0)
        val q=Question.Ordering("reveal","Test","Classez",basePoints=15,
            items=listOf(Question.OrderItem("b","B"),Question.OrderItem("a","A"),Question.OrderItem("c","C")),correctOrderIds=listOf("a","b","c"))
        try {
            state(server).value=server.gameSession.value.copy(teams=listOf(Team("a","A",0,sessionToken="a"),Team("b","B",0,sessionToken="b")),
                timingConfig=HourglassConfig(secondsPerFlip=5,maxFlips=2,pointsDecayPerFlip=5))
            start(server,q)
            val reveal=GameServer::class.java.getDeclaredMethod("handleHostRevealAnswer").apply { isAccessible=true }
            reveal.invoke(server)
            assertEquals(GameState.QUESTION_ACTIVE,server.gameSession.value.state)
            state(server).value=server.gameSession.value.copy(questionReading=false,
                submissions=mapOf("a" to AnswerSubmission("a",q.id,AnswerValue.OrderingSelection(q.correctOrderIds),true,0,0)))
            reveal.invoke(server)
            assertEquals(GameState.REVEAL_ANSWER,server.gameSession.value.state)
            assertEquals(listOf(15,0),server.gameSession.value.teams.map { it.score })
            assertEquals(true,server.gameSession.value.submissions["a"]!!.isCorrect)
        } finally { server.stop() }
    }
    @Test fun unansweredBuzzCostsOneShareAndAllowsRetryOnlyAtNextClue()=runBlocking {
        val port=ServerSocket(0).use { it.localPort }; val server=GameServer(port)
        val client=HttpClient(CIO) { install(WebSockets) }
        val q=Question.GuessWho("timeout","Test",basePoints=20,clues=listOf("Un","Deux","Trois","Quatre"),acceptableAnswers=listOf("Solution"))
        try { server.start(); withTimeout(10000) {
            val judge=client.webSocketSession(host="127.0.0.1",port=port,path="/judge/ws?token=${server.privateJudgeUrl().substringAfter('#')}")
            judge.snapshot { true }
            state(server).value=server.gameSession.value.copy(teams=listOf(Team("a","A",0,sessionToken="a")),answerTimeSeconds=1,
                timingConfig=HourglassConfig(secondsPerFlip=5,maxFlips=3,pointsDecayPerFlip=5))
            start(server,q); judge.snapshot { it["answer"]==JsonPrimitive("Solution") }
            buzz(server,q); judge.snapshot { it["answering"]==JsonPrimitive(true) }
            judge.snapshot { it["answering"]==JsonPrimitive(false) && server.gameSession.value.submissions["a"]?.isCorrect==false }
            assertEquals(-5,server.gameSession.value.teams.single().score)
            assertEquals(BuzzerStatus.INCORRECT,server.gameSession.value.buzzerStatus("a",true))
            assertEquals(server.gameSession.value,server.gameSession.value.rejectOralAnswer("a"))
            repeat(20) { tick(server) }
            assertEquals(BuzzerStatus.WAITING,server.gameSession.value.buzzerStatus("a",true))
            GameServer::class.java.getDeclaredMethod("handleHostStartQuestionTimer").apply {isAccessible=true}.invoke(server)
            assertEquals(BuzzerStatus.READY,server.gameSession.value.buzzerStatus("a",true))
            assertEquals(-5,server.gameSession.value.teams.single().score)
            judge.close()
        } } finally { client.close(); server.stop() }
    }
}
