package com.example.triviaparty

import com.example.triviaparty.model.*
import org.junit.Assert.assertEquals
import org.junit.Test

class BuzzerStatusTest {
    @Test
    fun onlyBuzzerQuestionsShowThePlayerBuzzer() {
        val choice = Question.MultipleChoice("q", "C", "Prompt", options = listOf("A", "B"), correctOptionIndex = 0)
        val game = GameSession("1234", currentCategoryAnswerMode = CategoryAnswerMode.SIMULTANEOUS)
        assertEquals(false, game.copy(currentQuestion = choice).usesPlayerBuzzer())
        assertEquals(false, game.copy(currentQuestion = Question.SpeedRace("s", "C", "Prompt", subQuestion = choice)).usesPlayerBuzzer())
        assertEquals(false, game.copy(currentQuestion = Question.Ordering("o", "C", "Prompt", items = emptyList(), correctOrderIds = emptyList())).usesPlayerBuzzer())
        assertEquals(false, game.copy(currentQuestion = Question.MapPin("m", "C", "Prompt")).usesPlayerBuzzer())
        assertEquals(false, game.copy(currentQuestion = Question.Wager("w", "C", "Prompt", subQuestion = choice)).usesPlayerBuzzer())
        assertEquals(true, game.copy(currentQuestion = Question.TextAnswer("t", "C", "Prompt", acceptableAnswers = listOf("A"))).usesPlayerBuzzer())
    }

    @Test
    fun buzzerStateTransitionsAndResetsForNextQuestion() {
        val question = Question.MultipleChoice("q", "C", "Hidden prompt", options = listOf("A", "B"), correctOptionIndex = 0)
        var game = GameSession("1234")
        assertEquals(BuzzerStatus.WAITING, game.buzzerStatus("a", true))
        game = game.copy(state = GameState.QUESTION_ACTIVE, currentQuestion = question)
        assertEquals(BuzzerStatus.READY, game.buzzerStatus("a", true))
        assertEquals(BuzzerStatus.PRESSED, game.buzzerStatus("a", true, true))
        val buzz = AnswerSubmission("a", "q", AnswerValue.TextSelection("BUZZ"), true, 0, 0)
        game = game.copy(submissions = mapOf("a" to buzz))
        assertEquals(BuzzerStatus.PRESSED, game.buzzerStatus("a", true))
        assertEquals(BuzzerStatus.BLOCKED, game.buzzerStatus("b", true))
        game = game.copy(submissions = mapOf("a" to buzz.copy(isCorrect = false)), textBuzzedTeamIds = listOf("a"))
        assertEquals(BuzzerStatus.INCORRECT, game.buzzerStatus("a", true))
        assertEquals(BuzzerStatus.READY, game.buzzerStatus("b", true))
        assertEquals(BuzzerStatus.DISCONNECTED, game.buzzerStatus("a", false))
        game = game.copy(currentQuestion = question.copy(id = "next"), submissions = emptyMap(), textBuzzedTeamIds = emptyList())
        assertEquals(BuzzerStatus.READY, game.buzzerStatus("a", true))
        game = game.copy(state = GameState.GAME_ENDED)
        assertEquals(BuzzerStatus.ENDED, game.buzzerStatus("a", true))
    }
}
