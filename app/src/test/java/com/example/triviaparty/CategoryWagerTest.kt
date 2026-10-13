package com.example.triviaparty

import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameEvent
import com.example.triviaparty.network.GameServer
import kotlinx.coroutines.flow.MutableStateFlow
import org.junit.Assert.*
import org.junit.Test

class CategoryWagerTest {
    private fun team(id: String, score: Int) = Team(id, id, score, sessionToken = "token-$id")
    private val question = Question.MultipleChoice("first", "Test", "Question", basePoints = 15,
        options = listOf("A", "B", "C", "D"), correctOptionIndex = 1)
    private fun submission(id: String, correct: Boolean) = AnswerSubmission(id, "first",
        AnswerValue.MultipleChoiceSelection(if (correct) 1 else 0), true, 0, 0, isCorrect = correct)

    @Test
    fun limitsUseCurrentScoreOrMaximumCategoryReward() {
        assertEquals(100, categoryWagerLimit(100, 15))
        assertEquals(15, categoryWagerLimit(5, 15))
        assertEquals(15, categoryWagerLimit(14, 15))
        assertEquals(15, categoryWagerLimit(15, 15))
        assertEquals(20, categoryWagerLimit(20, 15))
        assertEquals(15, categoryWagerLimit(0, 15))
        assertEquals(15, categoryWagerLimit(-20, 15))
        assertEquals(0, categoryWagerLimit(-20, -5))
        assertEquals(5, categoryWagerLimit(5, -5))
    }

    @Test
    fun settlementHandlesCorrectWrongMissingAndZeroStakesExactlyOnce() {
        val session = GameSession("test", currentQuestion = question,
            teams = listOf(team("a", 115), team("b", 0), team("c", 10), team("d", -5)),
            categoryWagerQuestionId = "first",
            categoryWagerLimits = mapOf("a" to 100, "b" to 15, "c" to 10, "d" to 15),
            categoryWagers = mapOf("a" to 50, "b" to 15, "c" to 10, "d" to 0),
            submissions = mapOf("a" to submission("a", true), "b" to submission("b", false)))
        val settled = session.settleCategoryWagers()
        assertEquals(listOf(165, -15, 0, -5), settled.teams.map { it.score })
        assertEquals(listOf(50, -15, -10, 0), settled.categoryWagerResults.map { it.delta })
        assertSame(settled, settled.settleCategoryWagers())
        val second = session.copy(currentQuestion = question.copy(id = "second"))
        assertSame(second, second.settleCategoryWagers())
    }

    @Test
    fun leaderboardIncludesAllTiesAtThirdTeamCutoff() {
        val teams = listOf(team("a", 40), team("b", 30), team("c", 20), team("d", 20), team("e", 10))
        assertEquals(listOf("a", "b", "c", "d"), teams.reversed().leadersWithTies().map { it.id })
        assertEquals(5, teams.map { it.copy(score = 0) }.leadersWithTies().size)
        assertTrue(emptyList<Team>().leadersWithTies().isEmpty())
    }

    @Test
    @Suppress("UNCHECKED_CAST")
    fun serverClosesWagersScoresFirstQuestionAndShowsResultsBeforeAdvancing() {
        val server = GameServer()
        val state = GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible = true }
            .get(server) as MutableStateFlow<GameSession>
        fun invoke(name: String, arg: Any? = null) {
            val method = if (arg == null) GameServer::class.java.getDeclaredMethod(name)
                else GameServer::class.java.getDeclaredMethod(name, arg.javaClass)
            method.isAccessible = true
            if (arg == null) method.invoke(server) else method.invoke(server, arg)
        }
        state.value = GameSession("test", state = GameState.CATEGORY_INTRO, currentCategory = "Test",
            currentQuestion = question, teams = listOf(team("a", 100), team("b", 5)), totalRounds = 1)
        try {
            invoke("offerCategoryWager")
            assertEquals(GameState.WAGER_OPEN, state.value.state)
            assertEquals(mapOf("a" to 100, "b" to 15), state.value.categoryWagerLimits)
            invoke("handleCategoryWager", GameEvent.SubmitCategoryWager("a", "first", 101))
            invoke("handleCategoryWager", GameEvent.SubmitCategoryWager("b", "stale", 15))
            assertTrue(state.value.categoryWagers.isEmpty())
            invoke("handleCategoryWager", GameEvent.SubmitCategoryWager("b", "first", 16))
            assertTrue(state.value.categoryWagers.isEmpty())
            invoke("handleCategoryWager", GameEvent.SubmitCategoryWager("a", "first", 50))
            invoke("handleCategoryWager", GameEvent.SubmitCategoryWager("a", "first", 10))
            assertEquals(50,state.value.categoryWagers["a"])
            invoke("handleCategoryWager", GameEvent.SubmitCategoryWager("b", "first", 15))
            invoke("handleHostNextQuestion", GameEvent.HostNextQuestion())
            assertEquals(GameState.QUESTION_ACTIVE, state.value.state)
            invoke("handleCategoryWager", GameEvent.SubmitCategoryWager("a", "first", 100))
            assertEquals(50, state.value.categoryWagers["a"])
            state.value = state.value.copy(submissions = mapOf("a" to submission("a", true), "b" to submission("b", false)))
            invoke("evaluateQuestionScoresAndReveal")
            assertEquals(GameState.REVEAL_ANSWER, state.value.state)
            assertEquals(listOf(165, -10), state.value.teams.map { it.score })
            invoke("handleHostNextQuestion", GameEvent.HostNextQuestion())
            assertEquals(GameState.WAGER_RESULTS, state.value.state)
            invoke("handleHostNextQuestion", GameEvent.HostNextQuestion())
            assertEquals(GameState.GAME_ENDED, state.value.state)
            assertEquals(listOf(165, -10), state.value.teams.map { it.score })
        } finally { server.stop() }
    }
}
