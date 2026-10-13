package com.example.triviaparty

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.model.*
import org.junit.Assert.*
import org.junit.Test

class TvStateTest {
    @Test fun lockedChoicesShowImmediateTvVerdictsWithoutEarlyPointsOrAnswerKey() {
        val q=Question.MultipleChoice("mc","Test","Question",options=listOf("A","B","C"),correctOptionIndex=1)
        fun submission(id:String,index:Int,qid:String="mc",locked:Boolean=true)=AnswerSubmission(id,qid,AnswerValue.MultipleChoiceSelection(index),locked,0,0)
        val session=GameSession(roomId="test",state=GameState.QUESTION_ACTIVE,currentQuestion=q,
            teams=listOf(Team("right","Right",10,sessionToken="r"),Team("wrong","Wrong",20,sessionToken="w"),Team("waiting","Waiting",30,sessionToken="n"),Team("draft","Draft",40,sessionToken="d"),Team("old","Old",50,sessionToken="o")),
            submissions=mapOf("right" to submission("right",1),"wrong" to submission("wrong",0),"draft" to submission("draft",1,locked=false),"old" to submission("old",1,qid="previous")))
        val tv=TvState.from(session)
        assertEquals(listOf(true,false,null,null,null),tv.teams.map { it.answerResult })
        assertEquals(listOf(10,20,30,40,50),tv.teams.map { it.score })
        assertNull(tv.question!!.answer);assertNull(tv.question.correctOptionIndex)
        assertTrue(session.submissions.values.all { it.isCorrect==null })
        assertTrue(TvState.from(session.copy(state=GameState.CATEGORY_INTRO)).teams.all { it.answerResult==null })
        val ordering=Question.Ordering("mc","Test","Order",items=listOf(Question.OrderItem("a","A"),Question.OrderItem("b","B")),correctOrderIds=listOf("a","b"))
        assertTrue(TvState.from(session.copy(currentQuestion=ordering)).teams.all { it.answerResult==null })
    }
    private val question = Question.MultipleChoice(
        id = "q", category = "Science", prompt = "Red planet?",
        options = listOf("Venus", "Mars"), correctOptionIndex = 1
    )
    private fun game(phase: GameState) = GameSession(
        roomId = "1234", state = phase, currentQuestion = question,
        teams = listOf(Team("team", "Wizards", sessionToken = "private-token"))
    )

    @Test fun activeQuestionDoesNotExposeAnswersOrCredentials() {
        val state = TvState.from(game(GameState.QUESTION_ACTIVE))
        assertNull(state.question!!.answer)
        assertNull(state.question.correctOptionIndex)
        assertEquals(question.options, state.question.options)
        val encoded = state.encode()
        assertFalse(encoded.contains("correctOptionIndex"))
        assertFalse(encoded.contains("private-token"))
        assertFalse(encoded.contains("sessionToken"))
        assertFalse(encoded.contains("submissions"))
        assertTrue(encoded.contains("\"version\":1"))
        assertTrue(encoded.contains("\"type\":\"state\""))
    }

    @Test fun answerIsVisibleOnlyDuringRevealAndSummary() {
        for (phase in GameState.entries) {
            val state = TvState.from(game(phase))
            if (phase == GameState.REVEAL_ANSWER || phase == GameState.ROUND_SUMMARY) {
                assertEquals("Mars", state.question!!.answer)
                assertEquals(1, state.question.correctOptionIndex)
            } else {
                assertNull(state.question?.answer)
            }
        }
    }

    @Test fun teamVerdictsArePublicOnlyOnRevealAndOnlyForTheCurrentQuestion() {
        val teams = listOf("right", "wrong", "missing", "pending", "old").map { Team(it, it, sessionToken = "private-$it") }
        fun submission(id: String, correct: Boolean?, questionId: String = "q") =
            AnswerSubmission(id, questionId, AnswerValue.MultipleChoiceSelection(1), true, 0, 0, isCorrect = correct)
        val session = game(GameState.QUESTION_ACTIVE).copy(teams = teams, submissions = mapOf(
            "right" to submission("right", true), "wrong" to submission("wrong", false),
            "pending" to submission("pending", null), "old" to submission("old", true, "previous")))
        for (phase in GameState.entries) {
            val tv = TvState.from(session.copy(state = phase))
            val expected = phase in setOf(GameState.REVEAL_ANSWER, GameState.ROUND_SUMMARY)
            assertEquals(expected, tv.teams.first { it.name == "right" }.correct)
            assertTrue(tv.teams.filter { it.name != "right" }.none { it.correct })
        }
        assertTrue(TvState.from(session.copy(state = GameState.REVEAL_ANSWER, currentQuestion = null)).teams.none { it.correct })
    }

    @Test fun validatedBuzzerVerdictHighlightsOnlyTheAcceptedTeam() {
        val buzz = Question.GuessWho("buzz", "Test", clues = listOf("Indice"), acceptableAnswers = listOf("Réponse"))
        val session = game(GameState.REVEAL_ANSWER).copy(currentQuestion = buzz, teams = listOf(Team("a", "A", sessionToken = "private-a"), Team("b", "B", sessionToken = "private-b")),
            submissions = mapOf("a" to AnswerSubmission("a", "buzz", AnswerValue.TextSelection("BUZZ"), true, 0, 0, isCorrect = true)))
        assertEquals(listOf(true, false), TvState.from(session).teams.map { it.correct })
        assertTrue(TvState.from(session.copy(state = GameState.QUESTION_ACTIVE)).teams.none { it.correct })
    }

    @Test fun mapTargetStaysHiddenUntilReveal() {
        val map = Question.MapPin("map", "Geography", "Pin it", "https://example.com/map.png",
            target = Question.MapTarget.CenterRadius(0.5f, 0.5f, 0.1f))
        val active = game(GameState.QUESTION_ACTIVE).copy(currentQuestion = map)
        assertNull(TvState.from(active).question!!.mapTarget)
        assertEquals(map.target, TvState.from(active.copy(state = GameState.REVEAL_ANSWER)).question!!.mapTarget)
    }

    @Test fun wrappedQuestionAndTimerAreConverted() {
        val wager = Question.Wager("w", "Science", "Make your wager", subQuestion = question)
        val state = TvState.from(game(GameState.QUESTION_ACTIVE).copy(
            currentQuestion = wager, elapsedSecondsInFlip = 25, currentFlipNumber = 1
        ))
        assertEquals(question.options, state.question!!.options)
        assertEquals(0, state.secondsRemaining)
        assertEquals(90, state.points)
    }

    @Test fun categoryIntroductionCarriesCategoryRulesAndQuestionCount() {
        val state = TvState.from(game(GameState.CATEGORY_INTRO).copy(
            currentCategory = "Geography",
            currentCategoryAnswerMode = CategoryAnswerMode.SIMULTANEOUS,
            currentCategoryQuestionTypes = listOf("Map", "Ordering"),
            currentCategoryQuestionCount = 5
        ))
        assertNull(state.question)
        assertEquals("Geography", state.category)
        assertEquals(5, state.categoryQuestionCount)
        assertEquals(listOf("Map", "Ordering"), state.categoryQuestionTypes)
        assertEquals(CategoryAnswerMode.SIMULTANEOUS, state.categoryAnswerMode)
    }
}
