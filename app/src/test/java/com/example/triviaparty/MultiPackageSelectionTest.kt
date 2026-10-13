package com.example.triviaparty

import com.example.triviaparty.data.combineGamePackages
import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameServer
import kotlinx.coroutines.flow.MutableStateFlow
import org.junit.Assert.*
import org.junit.Test

class MultiPackageSelectionTest {
    @Test
    @Suppress("UNCHECKED_CAST")
    fun categoriesAdvanceInSelectedOrderAndFinishAfterAllQuestions() {
        val bank = com.example.triviaparty.data.QuestionBankRepository
        val categories = bank.sampleCategories.filter { bank.getQuestionsForCategory(it).isNotEmpty() }.take(3).reversed()
        assertEquals(3, categories.size)
        val server = GameServer()
        val state = GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible = true }
            .get(server) as MutableStateFlow<GameSession>
        val advance = GameServer::class.java.getDeclaredMethod("handleHostBeginCategorySelect").apply { isAccessible = true }
        state.value = GameSession(roomId = "test", state = GameState.LOBBY, masterCategories = categories,
            totalRounds = categories.sumOf { bank.getQuestionsForCategory(it).size })
        try {
            categories.forEach { category ->
                advance.invoke(server)
                assertEquals(GameState.CATEGORY_INTRO, state.value.state)
                assertEquals(category, state.value.currentQuestion!!.category)
                state.value = state.value.copy(state = GameState.REVEAL_ANSWER,
                    playedQuestionIds = state.value.playedQuestionIds + bank.getQuestionsForCategory(category).map { it.id })
            }
            advance.invoke(server)
            assertEquals(GameState.GAME_ENDED, state.value.state)
        } finally { server.stop() }
    }

    private val fast = GamePackage("fast", "Rapide", "", listOf("a", "b"),
        HourglassConfig(secondsPerFlip = 5, maxFlips = 2, pointsDecayPerFlip = 5), answerTimeSeconds = 10)
    private val slow = GamePackage("slow", "Long", "", listOf("b", "c"),
        HourglassConfig(secondsPerFlip = 8, maxFlips = 3), answerTimeSeconds = 20)
    private val counts = mapOf("a" to 4, "b" to 9, "c" to 3)

    @Test
    fun combinesPackagesWithoutRepeatingSharedCategoriesAndKeepsTheirRules() {
        val result = combineGamePackages(listOf(fast, slow), { it.categoryPackages }) { counts.getValue(it) }
        assertEquals(listOf("a", "b", "c"), result.categories)
        assertEquals(16, result.totalQuestions)
        assertEquals(fast.timingConfig, result.categoryRules.getValue("a").timingConfig)
        assertEquals(10, result.categoryRules.getValue("b").answerTimeSeconds)
        assertEquals(slow.timingConfig, result.categoryRules.getValue("c").timingConfig)
        assertEquals(20, result.categoryRules.getValue("c").answerTimeSeconds)
        assertEquals(listOf("b"), result.conflictingCategories)
        val reversed = combineGamePackages(listOf(slow, fast), { it.categoryPackages }) { counts.getValue(it) }
        assertEquals(20, reversed.categoryRules.getValue("b").answerTimeSeconds)
    }

    @Test
    fun identicalRulesDoNotRaiseConflictsAndEmptySelectionHasNoQuestions() {
        val other = fast.copy(id = "other", categoryPackages = listOf("b"))
        val combined = combineGamePackages(listOf(fast, other), { it.categoryPackages }) { counts.getValue(it) }
        assertEquals(13, combined.totalQuestions)
        assertTrue(combined.conflictingCategories.isEmpty())
        val empty = combineGamePackages(emptyList(), { it.categoryPackages }) { counts.getValue(it) }
        assertEquals(0, empty.totalQuestions)
        assertTrue(empty.categories.isEmpty())
    }

    @Test
    @Suppress("UNCHECKED_CAST")
    fun serverSwitchesTimingAndAnswerDurationWhenChangingPackageCategory() {
        val server = GameServer()
        val stateField = GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible = true }
        val state = stateField.get(server) as MutableStateFlow<GameSession>
        val introduce = GameServer::class.java.getDeclaredMethod("introduceCategory", Question::class.java, String::class.java)
            .apply { isAccessible = true }
        val start = GameServer::class.java.getDeclaredMethod("startQuestion", Question::class.java, String::class.java)
            .apply { isAccessible = true }
        val combined = combineGamePackages(listOf(fast, slow), { it.categoryPackages }) { counts.getValue(it) }
        state.value = GameSession(roomId = "test", categoryRules = combined.categoryRules)
        try {
            for (category in listOf("a", "c", "b")) {
                val question = Question.TextAnswer("q-$category", category, "Question", acceptableAnswers = listOf("Réponse"))
                val expected = combined.categoryRules.getValue(category)
                introduce.invoke(server, question, category)
                assertEquals(GameState.CATEGORY_INTRO, state.value.state)
                assertEquals(expected.answerTimeSeconds, state.value.currentCategoryAnswerTimeSeconds)
                start.invoke(server, question, category)
                assertEquals(GameState.QUESTION_ACTIVE, state.value.state)
                assertEquals(expected.timingConfig, state.value.timingConfig)
                assertEquals(expected.answerTimeSeconds, state.value.answerTimeSeconds)
                assertEquals(0, state.value.elapsedSecondsInFlip)
            }
        } finally { server.stop() }
    }
}
