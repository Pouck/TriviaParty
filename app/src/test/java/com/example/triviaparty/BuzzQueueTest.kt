package com.example.triviaparty

import com.example.triviaparty.model.*
import com.example.triviaparty.network.*
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.net.ServerSocket

class BuzzQueueTest {
    private val question = Question.TextAnswer("q", "Test", "Question", acceptableAnswers=listOf("Answer"))
    private fun game() = GameSession("room", state=GameState.QUESTION_ACTIVE, currentQuestion=question,
        currentCategoryAnswerMode=CategoryAnswerMode.BUZZER, teams=listOf("a","b","c").map {Team(it,it,sessionToken=it)})

    @Test fun pressesAreOrderedOnceAndOnlyOnePlayerHasTheFloor() {
        var state=game().recordBuzz("a",30).recordBuzz("b",20).recordBuzz("c",10)
        assertEquals(listOf("a","b","c"),state.buzzQueue.map {it.teamId}) // Arrival, not client clocks.
        assertEquals("a",state.answerTimerTeamId)
        assertEquals(setOf("a"),state.submissions.keys)
        assertEquals(BuzzerStatus.QUEUED,state.buzzerStatus("b",true))
        assertEquals(state,state.recordBuzz("b",50))
        state=state.rejectOralAnswer("a").advanceBuzzQueue()
        assertEquals("b",state.answerTimerTeamId)
        assertEquals(20L,state.submissions["b"]!!.timestamp)
        assertEquals(BuzzerStatus.INCORRECT,state.buzzerStatus("a",true))
        state=state.rejectOralAnswer("b").advanceBuzzQueue()
        assertEquals("c",state.answerTimerTeamId)
        assertEquals(1,state.submissions.values.count {it.isCorrect != false})
    }

    @Test fun closedReadingForeignAndDuplicatePressesCannotEnterTheQueue() {
        assertEquals(game(),game().recordBuzz("unknown",0))
        val reading=game().copy(questionReading=true)
        assertEquals(reading,reading.recordBuzz("a",0))
        val closed=game().copy(state=GameState.REVEAL_ANSWER)
        assertEquals(closed,closed.recordBuzz("a",0))
        val disconnected=game().copy(teams=game().teams.map {it.copy(isConnected=false)})
        assertEquals(disconnected,disconnected.recordBuzz("a",0))
        val once=game().recordBuzz("a",1)
        assertEquals(once,once.recordBuzz("a",2))
        val written=game().copy(currentCategoryAnswerMode=CategoryAnswerMode.WRITTEN)
        assertEquals(written,written.recordBuzz("a",0))
    }

    @Test fun categorySoundsStayInTheBundledBankAndChangeOnNewCategory() {
        repeat(50) {assertTrue(CategoryBuzzerSounds.choose("wolf") in CategoryBuzzerSounds.ids.filter {it!="wolf"})}
    }

    @Test fun serverHandsOffOnWrongAnswerAndTimeoutAndRejectsOutOfTurnJudgement() = runBlocking {
        val port=ServerSocket(0).use {it.localPort};val server=GameServer(port)
        val client=HttpClient(CIO) {install(WebSockets)}
        try {server.start();withTimeout(10000) {
            @Suppress("UNCHECKED_CAST")
            val state=GameServer::class.java.getDeclaredField("_gameSession").apply {isAccessible=true}.get(server) as MutableStateFlow<GameSession>
            state.value=game().copy(answerTimeSeconds=1)
            val host=client.webSocketSession(host="127.0.0.1",port=port,path="/ws")
            val lock=GameServer::class.java.getDeclaredMethod("handleLockAnswer",GameEvent.LockAnswer::class.java).apply {isAccessible=true}
            for(id in listOf("a","b","c","b"))lock.invoke(server,GameEvent.LockAnswer(id,question.id,AnswerValue.TextSelection("BUZZ")))
            assertEquals(3,state.value.buzzQueue.size)
            assertEquals("a",state.value.answerTimerTeamId)
            host.send(Frame.Text(Json.encodeToString<GameEvent>(GameEvent.HostJudgeTextBuzz("c",true))))
            host.send(Frame.Text(Json.encodeToString<GameEvent>(GameEvent.HostJudgeTextBuzz("a",false))))
            state.first {it.answerTimerTeamId=="b"}
            state.first {it.answerTimerTeamId=="c"}
            assertEquals(false,state.value.submissions["b"]!!.isCorrect)
            host.send(Frame.Text(Json.encodeToString<GameEvent>(GameEvent.HostJudgeTextBuzz("c",true))))
            state.first {it.state==GameState.REVEAL_ANSWER}
            assertEquals(true,state.value.submissions["c"]!!.isCorrect)
            assertEquals(listOf("a","b","c"),state.value.buzzQueue.map {it.teamId})
            host.close()
        }} finally {client.close();server.stop()}
    }
}
