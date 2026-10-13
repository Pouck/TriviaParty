package com.example.triviaparty

import com.example.triviaparty.model.*
import com.example.triviaparty.network.*
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test
import java.net.ServerSocket

class InstantChoiceTvTest {
    @Test fun selectingChoicesBroadcastsGreenRedBeforeLastPlayerAndScoresOnlyAtReveal()=runBlocking {
        val port=ServerSocket(0).use { it.localPort };val server=GameServer(port)
        val client=HttpClient(CIO) { install(WebSockets) }
        val q=Question.MultipleChoice("instant","Test","Question",basePoints=15,options=listOf("Wrong","Right"),correctOptionIndex=1)
        @Suppress("UNCHECKED_CAST")
        val state=GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible=true }.get(server) as MutableStateFlow<GameSession>
        state.value=GameSession(roomId="test",state=GameState.QUESTION_ACTIVE,currentQuestion=q,
            teams=listOf(Team("a","A",sessionToken="a"),Team("b","B",sessionToken="b"),Team("c","C",sessionToken="c")),
            timingConfig=HourglassConfig(secondsPerFlip=5,maxFlips=2,pointsDecayPerFlip=5))
        val lock=GameServer::class.java.getDeclaredMethod("handleLockAnswer",GameEvent.LockAnswer::class.java).apply { isAccessible=true }
        suspend fun WebSocketSession.snapshot(predicate:(JsonObject)->Boolean):JsonObject {
            while(true) {val frame=incoming.receive();if(frame is Frame.Text) {val data=Json.parseToJsonElement(frame.readText()).jsonObject;if(predicate(data))return data}}
        }
        try {
            server.start()
            withTimeout(10000) {
                val tv=client.webSocketSession(host="127.0.0.1",port=port,path="/tv/ws")
                try {
                    tv.snapshot { true }
                    lock.invoke(server,GameEvent.LockAnswer("a",q.id,AnswerValue.MultipleChoiceSelection(1)))
                    val first=tv.snapshot { it["teams"]!!.jsonArray[0].jsonObject["answerResult"]==JsonPrimitive(true) }
                    assertEquals("QUESTION_ACTIVE",first["phase"]!!.jsonPrimitive.content)
                    assertEquals(JsonNull,first["question"]!!.jsonObject["answer"])
                    assertFalse(first["question"]!!.jsonObject.containsKey("correctOptionIndex"))
                    lock.invoke(server,GameEvent.LockAnswer("b",q.id,AnswerValue.MultipleChoiceSelection(0)))
                    val second=tv.snapshot { it["teams"]!!.jsonArray[1].jsonObject["answerResult"]==JsonPrimitive(false) }
                    assertEquals("QUESTION_ACTIVE",second["phase"]!!.jsonPrimitive.content)
                    assertTrue(state.value.teams.all { it.score==0 });assertEquals(0,state.value.answerSoundId)
                    assertTrue(state.value.submissions.values.all { it.isCorrect==null })
                    lock.invoke(server,GameEvent.LockAnswer("c",q.id,AnswerValue.MultipleChoiceSelection(1)))
                    tv.snapshot { it["phase"]==JsonPrimitive("REVEAL_ANSWER") }
                    assertEquals(listOf(15,0,15),state.value.teams.map { it.score })
                } finally {tv.close()}
            }
        } finally {client.close();server.stop()}
    }
}
