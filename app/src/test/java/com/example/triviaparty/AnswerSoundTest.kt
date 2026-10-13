package com.example.triviaparty

import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameServer
import com.example.triviaparty.cast.TvState
import com.example.triviaparty.ui.host.reviewAnswer
import kotlinx.coroutines.flow.MutableStateFlow
import org.junit.Assert.*
import org.junit.Test

class AnswerSoundTest {
    @Test @Suppress("UNCHECKED_CAST") fun judgementsEmitOneCueAndTicksDoNotRepeatIt() {
        val server=GameServer()
        val state=GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible=true }.get(server) as MutableStateFlow<GameSession>
        val broadcast=GameServer::class.java.getDeclaredMethod("broadcastState").apply { isAccessible=true }
        val question=Question.TextAnswer("q","Test","Qui ?",acceptableAnswers=listOf("Platon"))
        state.value=GameSession("room",state=GameState.QUESTION_ACTIVE,currentQuestion=question)
        try {
            broadcast.invoke(server)
            val wrong=AnswerSubmission("a","q",AnswerValue.TextSelection("BUZZ"),true,0,0,isCorrect=false)
            state.value=state.value.copy(submissions=mapOf("a" to wrong)); broadcast.invoke(server)
            assertEquals("bad",state.value.answerSound); assertEquals(1,state.value.answerSoundId)
            broadcast.invoke(server); assertEquals(1,state.value.answerSoundId)
            state.value=state.value.copy(submissions=state.value.submissions+("b" to wrong.copy(teamId="b",isCorrect=true)),state=GameState.REVEAL_ANSWER)
            broadcast.invoke(server)
            assertEquals("good",state.value.answerSound); assertEquals(2,TvState.from(state.value).answerSoundId)
            broadcast.invoke(server); assertEquals(2,state.value.answerSoundId)
        } finally { server.stop() }
    }
    @Test fun reviewRevealsCanonicalAnswerAndChronologicalOrder() {
        assertEquals("Platon",reviewAnswer(Question.TextAnswer("q","Test","Qui ?",acceptableAnswers=listOf("Platon","Plato"))))
        assertEquals("A → B → C",reviewAnswer(Question.Ordering("q","Test","Ordre ?",items=listOf(Question.OrderItem("c","C"),Question.OrderItem("a","A"),Question.OrderItem("b","B")),correctOrderIds=listOf("a","b","c"))))
    }
}
