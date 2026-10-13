package com.example.triviaparty

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameServer
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test

class OrderingBrowserStateTest {
    @Test fun spectatorListsOmitRepeatedChronologyPermutationsAndBareMapLetters() {
        val chronology = Question.MultipleChoice("timeline", "Chronologie", "Quel ordre ?\n• Cabot\n• Cartier\n• Champlain",
            options = listOf("A — Cabot → Cartier → Champlain", "B — Cartier → Cabot → Champlain"), correctOptionIndex = 0)
        assertTrue(chronology.spectatorOptions().isEmpty())
        assertTrue(TvState.from(GameSession("1234", state = GameState.QUESTION_ACTIVE, currentQuestion = chronology)).question!!.options.isEmpty())
        val map = chronology.copy(id = "map", prompt = "Quel repère correspond au pays ?", options = listOf("a", "b", "c", "d"))
        assertTrue(map.spectatorOptions().isEmpty())
        assertEquals(listOf("a", "b", "c", "d"), map.options)
        val named = map.copy(options = listOf("A — France", "B — Italie", "C — Espagne", "D — Allemagne"))
        assertEquals(named.options, named.spectatorOptions())
        val order = Question.Ordering("order", "Chronologie", "Classez les événements",
            items = listOf(Question.OrderItem("c", "Champlain"), Question.OrderItem("a", "Cabot"), Question.OrderItem("b", "Cartier")),
            correctOrderIds = listOf("a", "b", "c"))
        assertTrue(order.spectatorOptions().isEmpty())
    }

    @Test fun playerReceivesCardsAndOwnDraftButNotQuestionOrCorrectOrder() {
        val items = listOf(Question.OrderItem("opaque-z", "Troisième événement"), Question.OrderItem("opaque-x", "Premier événement"), Question.OrderItem("opaque-y", "Deuxième événement"))
        val question = Question.Ordering("order", "Chronologie", "Question réservée à l’hôte", items = items,
            correctOrderIds = listOf("opaque-x", "opaque-y", "opaque-z"))
        val draft = AnswerSubmission("a", "order", AnswerValue.OrderingSelection(listOf("opaque-y", "opaque-x", "opaque-z")), false, 0, 0)
        val state = GameSession("1234", state = GameState.QUESTION_ACTIVE, currentQuestion = question,
            submissions = mapOf("a" to draft, "b" to draft.copy(teamId = "b")))
        val method = GameServer::class.java.getDeclaredMethod("browserStateText", GameSession::class.java, String::class.java)
        method.isAccessible = true
        val server = GameServer(0)
        val encoded = method.invoke(server, state, "a") as String
        val player = Json.parseToJsonElement(encoded).jsonObject["session"]!!.jsonObject
        val publicQuestion = player["currentQuestion"]!!.jsonObject
        assertEquals(setOf("id", "type", "items"), publicQuestion.keys)
        assertEquals("ordering", publicQuestion["type"]!!.jsonPrimitive.content)
        assertEquals(items.map { it.id }, publicQuestion["items"]!!.jsonArray.map { it.jsonObject["id"]!!.jsonPrimitive.content })
        assertFalse(encoded.contains("correctOrderIds"))
        assertFalse(encoded.contains(question.prompt))
        assertEquals(setOf("a"), player["submissions"]!!.jsonObject.keys)
        val tv = TvState.from(state)
        assertTrue(tv.question!!.options.isEmpty())
        assertEquals(question.prompt+"\n"+items.joinToString("\n") { "• ${it.text}" },tv.question!!.prompt)
        assertNull(tv.question!!.answer)
        val revealed = TvState.from(state.copy(state = GameState.REVEAL_ANSWER))
        assertEquals("Premier événement → Deuxième événement → Troisième événement", revealed.question!!.answer)
    }

    @Test fun mapChoicesPublishCoordinatesWithoutTheSolution() {
        val q = Question.MapPin("map", "Test", "Secret prompt", options = listOf(
            Question.MapPinOption("A", .2f, .3f), Question.MapPinOption("B", .5f, .6f)), correctOptionIndex = 1)
        val method = GameServer::class.java.getDeclaredMethod("browserStateText", GameSession::class.java, String::class.java).apply { isAccessible = true }
        val encoded = method.invoke(GameServer(0), GameSession("1234", state = GameState.QUESTION_ACTIVE, currentQuestion = q), "a") as String
        val question = Json.parseToJsonElement(encoded).jsonObject["session"]!!.jsonObject["currentQuestion"]!!.jsonObject
        assertEquals(listOf("A", "B"), question["options"]!!.jsonArray.map { it.jsonPrimitive.content })
        assertEquals(.5f, question["mapOptions"]!!.jsonArray[1].jsonObject["xRatio"]!!.jsonPrimitive.float)
        assertFalse(question.containsKey("correctOptionIndex"))
        assertFalse(encoded.contains("Secret prompt"))
    }
    @Test fun chronologyRevealKeepsEventListForReceiverReconnect() {
        val q = Question.Ordering("order", "Test", "Classez les nombres.", items = listOf(
            Question.OrderItem("3", "Trois"), Question.OrderItem("1", "Un"), Question.OrderItem("2", "Deux")), correctOrderIds = listOf("1", "2", "3")).withChronologyCards()
        val active = GameSession("1234", state = GameState.QUESTION_ACTIVE, currentQuestion = q)
        assertEquals(TvState.from(active).question!!.prompt, TvState.from(active.copy(state = GameState.REVEAL_ANSWER)).question!!.prompt)
        assertNull(TvState.from(active).question!!.answer)
        assertTrue(TvState.from(active.copy(state = GameState.REVEAL_ANSWER)).question!!.answer!!.contains("Un → Deux → Trois"))
    }
}
