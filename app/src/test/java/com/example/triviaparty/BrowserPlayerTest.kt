package com.example.triviaparty

import com.example.triviaparty.model.AnswerValue
import com.example.triviaparty.model.GameState
import com.example.triviaparty.network.GameEvent
import com.example.triviaparty.network.GameServer
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.WebSockets
import io.ktor.client.plugins.websocket.webSocketSession
import io.ktor.websocket.Frame
import io.ktor.websocket.WebSocketSession
import io.ktor.websocket.close
import io.ktor.websocket.readText
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.net.ServerSocket
import java.net.URL

class BrowserPlayerTest {
    @Test
    fun categoryWagersArePrivateBoundToPlayerAndOnlyAffectFirstQuestion() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port, rotateQuestions = false)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(15_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                host.nextEvent()
                host.sendEvent(GameEvent.HostStartGame(listOf("Gaming History"), totalRounds = 5))
                val room = host.stateWhere { it["state"]!!.jsonPrimitive.content == "LOBBY" }["roomId"]!!.jsonPrimitive.content
                val a = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                val b = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                a.nextEvent(); b.nextEvent()
                a.sendEvent(GameEvent.JoinRoom(room, "A", "a-token"))
                val aId = a.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                b.sendEvent(GameEvent.JoinRoom(room, "B", "b-token"))
                val bId = b.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                host.sendEvent(GameEvent.HostSetScore(aId, 100))
                host.stateWhere { it["teams"]!!.jsonArray.any { team -> team.jsonObject["score"]!!.jsonPrimitive.int == 100 } }
                host.sendEvent(GameEvent.HostBeginCategorySelect)
                host.stateWhere { it["state"]!!.jsonPrimitive.content == "CATEGORY_INTRO" }
                host.sendEvent(GameEvent.HostOfferCategoryWager)
                val offered = a.stateWhere { it["state"]!!.jsonPrimitive.content == "WAGER_OPEN" }
                assertEquals(JsonNull, offered["currentQuestion"])
                assertEquals(setOf(aId), offered["categoryWagerLimits"]!!.jsonObject.keys)
                val questionId = offered["categoryWagerQuestionId"]!!.jsonPrimitive.content
                a.sendEvent(GameEvent.SubmitCategoryWager(bId, questionId, 15))
                a.sendEvent(GameEvent.SubmitCategoryWager(aId, questionId, 50))
                host.stateWhere { it["categoryWagers"]!!.jsonObject[aId]?.jsonPrimitive?.int == 50 }
                assertFalse(server.gameSession.value.categoryWagers.containsKey(bId))
                b.sendEvent(GameEvent.SubmitCategoryWager(bId, questionId, 15))
                val privateB = b.stateWhere { it["categoryWagers"]!!.jsonObject[bId]?.jsonPrimitive?.int == 15 }
                assertEquals(setOf(bId), privateB["categoryWagers"]!!.jsonObject.keys)
                host.sendEvent(GameEvent.HostNextQuestion())
                a.stateWhere { it["state"]!!.jsonPrimitive.content == "QUESTION_ACTIVE" }
                val question = server.gameSession.value.currentQuestion as com.example.triviaparty.model.Question.MultipleChoice
                a.sendEvent(GameEvent.SubmitCategoryWager(aId, questionId, 100))
                a.sendEvent(GameEvent.LockAnswer(aId, questionId, AnswerValue.MultipleChoiceSelection(question.correctOptionIndex)))
                host.stateWhere { it["submissions"]!!.jsonObject[aId]?.jsonObject?.get("isLocked")?.jsonPrimitive?.boolean == true }
                assertEquals(50, server.gameSession.value.categoryWagers[aId])
                b.sendEvent(GameEvent.LockAnswer(bId, questionId, AnswerValue.MultipleChoiceSelection((question.correctOptionIndex + 1) % question.options.size)))
                host.stateWhere { it["state"]!!.jsonPrimitive.content == "REVEAL_ANSWER" }
                assertEquals(250, server.gameSession.value.teams.first { it.id == aId }.score)
                assertEquals(-15, server.gameSession.value.teams.first { it.id == bId }.score)
                host.sendEvent(GameEvent.HostNextQuestion())
                host.stateWhere { it["state"]!!.jsonPrimitive.content == "WAGER_RESULTS" }
                host.sendEvent(GameEvent.HostNextQuestion())
                host.stateWhere { it["state"]!!.jsonPrimitive.content == "QUESTION_ACTIVE" && it["currentQuestion"]!!.jsonObject["id"]!!.jsonPrimitive.content != questionId }
                assertTrue(server.gameSession.value.categoryWagers.isEmpty())
                assertNull(server.gameSession.value.categoryWagerQuestionId)
                a.close(); b.close(); host.close()
            }
        } finally { client.close(); server.stop() }
    }

    @Test
    fun buzzAutomaticallyPausesQuestionTimerAndStartsPackageAnswerCountdown() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port, rotateQuestions = false)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(15_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val player = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                host.nextEvent(); player.nextEvent()
                host.sendEvent(GameEvent.HostStartGame(emptyList(), answerTimeSeconds = 2))
                val setup = host.stateWhere { it["answerTimeSeconds"]!!.jsonPrimitive.int == 2 }
                player.sendEvent(GameEvent.JoinRoom(setup["roomId"]!!.jsonPrimitive.content, "Timer", "timer-token"))
                val teamId = player.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                host.sendEvent(GameEvent.HostNextQuestion())
                val active = host.stateWhere { it["state"]!!.jsonPrimitive.content == "QUESTION_ACTIVE" }
                val questionId = active["currentQuestion"]!!.jsonObject["id"]!!.jsonPrimitive.content
                player.sendEvent(GameEvent.LockAnswer(teamId, questionId, AnswerValue.TextSelection("BUZZ")))
                val buzz = player.stateWhere { it["answerTimerRunning"]!!.jsonPrimitive.boolean }
                assertEquals(2, buzz["answerTimerRemainingSeconds"]!!.jsonPrimitive.int)
                val countdown = player.stateWhere { it["answerTimerRemainingSeconds"] == JsonPrimitive(1) }
                assertEquals(buzz["elapsedSecondsInFlip"], countdown["elapsedSecondsInFlip"])
                assertEquals(buzz["currentFlipNumber"], countdown["currentFlipNumber"])
                val tv = com.example.triviaparty.cast.TvState.from(server.gameSession.value)
                assertEquals(1, tv.answerSecondsRemaining)
                val expired = player.stateWhere { it["answerTimerRemainingSeconds"] == JsonPrimitive(0) }
                assertFalse(expired["answerTimerRunning"]!!.jsonPrimitive.boolean)
                assertFalse(expired["submissions"]!!.jsonObject[teamId]!!.jsonObject["isCorrect"]!!.jsonPrimitive.boolean)
                assertEquals(buzz["elapsedSecondsInFlip"], expired["elapsedSecondsInFlip"])
                player.stateWhere { it["elapsedSecondsInFlip"]!!.jsonPrimitive.int > expired["elapsedSecondsInFlip"]!!.jsonPrimitive.int }
                player.close(); host.close()
            }
        } finally { client.close(); server.stop() }
    }

    @Test
    fun preparedQuestionIsWithheldFromBrowserUntilPlayStarts() {
        val server = GameServer()
        val snapshot = GameServer::class.java.getDeclaredMethod("browserStateText",
            com.example.triviaparty.model.GameSession::class.java, String::class.java)
        snapshot.isAccessible = true
        val question = com.example.triviaparty.model.Question.MultipleChoice(
            id = "prepared", category = "Test", prompt = "Question", options = listOf("A", "B"), correctOptionIndex = 0)
        for (phase in listOf(GameState.LOBBY, GameState.CATEGORY_SELECT, GameState.CATEGORY_INTRO,
            GameState.QUESTION_ACTIVE, GameState.REVEAL_ANSWER)) {
            val state = com.example.triviaparty.model.GameSession(roomId = "1234", state = phase, currentQuestion = question)
            val safe = json.parseToJsonElement(snapshot.invoke(server, state, null) as String)
                .jsonObject["session"]!!.jsonObject["currentQuestion"]
            if (phase in listOf(GameState.QUESTION_ACTIVE, GameState.REVEAL_ANSWER)) {
                assertEquals(2, safe!!.jsonObject["options"]!!.jsonArray.size)
            } else {
                assertEquals(JsonNull, safe)
            }
        }
    }

    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }

    @Test
    fun servesBundledBrowserAssets() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val assets = File("src/main/assets/player")
        val server = GameServer(port, rotateQuestions = false, readPlayerAsset = { File(assets, it).readText() })
        try {
            server.start()
            for ((path, file) in listOf("/play?room=1234" to "index.html", "/play/player.css" to "player.css", "/play/player.js" to "player.js")) {
                assertEquals(File(assets, file).readText(), URL("http://127.0.0.1:$port$path").readText())
            }
        } finally { server.stop() }
    }

    @Test
    fun browserProtocolSupportsBuzzLockoutAndReconnectionWithoutExposingSecrets() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port, rotateQuestions = false)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(15_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val a = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                val b = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                val room = server.gameSession.value.roomId
                a.nextEvent(); b.nextEvent(); host.nextEvent()
                // An unjoined browser must never gain host privileges.
                a.sendEvent(GameEvent.HostStartGame(listOf("Gaming History")))
                a.send(Frame.Text("""{"type":"com.example.triviaparty.network.GameEvent.JoinRoom","roomId":"wrong","teamName":"A","sessionToken":"a-token"}"""))
                assertFalse(a.nextEvent()["success"]!!.jsonPrimitive.boolean)
                assertEquals(room, server.gameSession.value.roomId)
                a.sendEvent(GameEvent.JoinRoom(room, "A", "a-token"))
                val aId = a.nextEvent()["teamId"]!!.jsonPrimitive.content
                b.sendEvent(GameEvent.JoinRoom(room, "B", "b-token"))
                val bId = b.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                val lobby = b.stateWhere { it["teams"]!!.jsonArray.size == 2 }
                assertFalse(lobby.toString().contains("sessionToken"))
                // Advance through the built-in category to its spoken-answer question.
                // HostNextQuestion currently advances sequentially regardless of questionId.
                for (id in listOf("q1", "q2", "q6", "q7", "q8")) {
                    host.sendEvent(GameEvent.HostNextQuestion())
                    host.stateWhere { (it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content == id }
                }
                val question = a.stateWhere { (it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content == "q8" }
                assertFalse(question.toString().contains("acceptableAnswers"))
                assertFalse(question.toString().contains("2011"))
                a.sendEvent(GameEvent.LockAnswer(aId, "q8", AnswerValue.TextSelection("BUZZ")))
                b.stateWhere { it["buzzActiveTeamId"]?.jsonPrimitive?.content == aId }
                b.sendEvent(GameEvent.LockAnswer(bId, "q8", AnswerValue.TextSelection("BUZZ")))
                b.sendEvent(GameEvent.UpdateDraftAnswer(bId, "q8", AnswerValue.TextSelection("draft")))
                host.stateWhere { it["submissions"]!!.jsonObject.containsKey(bId) }
                assertEquals(1, server.gameSession.value.submissions.values.count { it.isLocked })
                val safeB = b.stateWhere { it["submissions"]!!.jsonObject.containsKey(bId) }
                assertFalse(safeB["submissions"]!!.jsonObject.containsKey(aId))
                b.sendEvent(GameEvent.HostSetScore(bId, 999))
                b.sendEvent(GameEvent.UpdateDraftAnswer(bId, "q8", AnswerValue.TextSelection("barrier")))
                host.stateWhere { it["submissions"]!!.jsonObject[bId]?.jsonObject?.get("answer")?.jsonObject?.get("text")?.jsonPrimitive?.content == "barrier" }
                assertEquals(0, server.gameSession.value.teams.first { it.id == bId }.score)
                host.sendEvent(GameEvent.HostJudgeTextBuzz(aId, false))
                b.stateWhere { it["textBuzzedTeamIds"]!!.jsonArray.any { id -> id.jsonPrimitive.content == aId } }
                b.sendEvent(GameEvent.LockAnswer(bId, "q8", AnswerValue.TextSelection("BUZZ")))
                b.stateWhere { it["buzzActiveTeamId"]?.jsonPrimitive?.content == bId }
                assertEquals(bId, server.gameSession.value.answerTimerTeamId)
                a.close()
                host.stateWhere { state -> state["teams"]!!.jsonArray.any { it.jsonObject["id"]!!.jsonPrimitive.content == aId && !it.jsonObject["isConnected"]!!.jsonPrimitive.boolean } }
                val restored = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                restored.nextEvent()
                restored.sendEvent(GameEvent.JoinRoom(room, "A", "a-token"))
                assertEquals(aId, restored.nextEvent()["teamId"]!!.jsonPrimitive.content)
                assertEquals(2, server.gameSession.value.teams.size)
                restored.close(); b.close(); host.close()
            }
        } finally { client.close(); server.stop() }
    }

    @Test
    fun approvalBindsTheWaitingPlayerRatherThanTheHost() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port, rotateQuestions = false)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(10_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val player = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                host.nextEvent(); player.nextEvent()
                host.sendEvent(GameEvent.HostSetValidationMode(true))
                player.stateWhere { it["requireHostValidation"]!!.jsonPrimitive.boolean }
                player.sendEvent(GameEvent.JoinRoom(server.gameSession.value.roomId, "Approved", "saved-token"))
                assertTrue(player.eventOf("JoinResponse")["requiresHostApproval"]!!.jsonPrimitive.boolean)
                host.stateWhere { it["pendingJoinRequests"]!!.jsonArray.isNotEmpty() }
                host.sendEvent(GameEvent.HostValidateTeam("Approved", true))
                val response = player.eventOf("JoinResponse")
                assertTrue(response["success"]!!.jsonPrimitive.boolean)
                val teamId = response["teamId"]!!.jsonPrimitive.content
                host.sendEvent(GameEvent.HostSetScore(teamId, 42))
                player.stateWhere { it["teams"]!!.jsonArray.single().jsonObject["score"]!!.jsonPrimitive.int == 42 }
                assertEquals("saved-token", server.gameSession.value.teams.single().sessionToken)
                assertEquals(GameState.LOBBY, server.gameSession.value.state)
                player.close(); host.close()
            }
        } finally { client.close(); server.stop() }
    }

    private suspend fun WebSocketSession.sendEvent(event: GameEvent) { send(Frame.Text(json.encodeToString(event))) }

    @Test
    fun choiceQuestionsAcceptBuzzesAndHostJudgingFromBrowserAndAndroidPlayers() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port, rotateQuestions = false)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(10_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val browser = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                val android = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                host.nextEvent(); browser.nextEvent(); android.nextEvent()
                val room = server.gameSession.value.roomId
                browser.sendEvent(GameEvent.JoinRoom(room, "Browser", "browser-token"))
                val a = browser.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                android.sendEvent(GameEvent.JoinRoom(room, "Android", "android-token"))
                val b = android.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                host.sendEvent(GameEvent.HostNextQuestion())
                val safe = browser.stateWhere { (it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content == "q1" }
                assertEquals(setOf("id", "type", "options"), safe["currentQuestion"]!!.jsonObject.keys)
                browser.sendEvent(GameEvent.LockAnswer(a, "q1", AnswerValue.TextSelection("BUZZ")))
                host.stateWhere { it["submissions"]!!.jsonObject[a]?.jsonObject?.get("isLocked")?.jsonPrimitive?.boolean == true }
                assertTrue(server.gameSession.value.answerTimerRunning)
                host.sendEvent(GameEvent.HostJudgeTextBuzz(a, true))
                browser.stateWhere { it["state"]!!.jsonPrimitive.content == "REVEAL_ANSWER" }
                assertFalse(server.gameSession.value.answerTimerRunning)
                assertEquals(100, server.gameSession.value.teams.first { it.id == a }.score)
                host.sendEvent(GameEvent.HostNextQuestion())
                browser.stateWhere { (it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content == "q2" }
                browser.sendEvent(GameEvent.LockAnswer(a, "q2", AnswerValue.TextSelection("BUZZ")))
                host.stateWhere { (it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content == "q2" && it["submissions"]!!.jsonObject[a]?.jsonObject?.get("isLocked")?.jsonPrimitive?.boolean == true }
                host.sendEvent(GameEvent.HostJudgeTextBuzz(a, false))
                android.stateWhere { it["textBuzzedTeamIds"]!!.jsonArray.any { id -> id.jsonPrimitive.content == a } }
                assertFalse(server.gameSession.value.answerTimerRunning)
                android.sendEvent(GameEvent.LockAnswer(b, "q2", AnswerValue.TextSelection("BUZZ")))
                host.stateWhere { it["submissions"]!!.jsonObject[b]?.jsonObject?.get("isLocked")?.jsonPrimitive?.boolean == true }
                host.sendEvent(GameEvent.HostJudgeTextBuzz(b, true))
                browser.stateWhere { it["state"]!!.jsonPrimitive.content == "REVEAL_ANSWER" && (it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content == "q2" }
                assertEquals(200, server.gameSession.value.teams.first { it.id == b }.score)
                host.close(); browser.close(); android.close()
            }
        } finally { client.close(); server.stop() }
    }
    private suspend fun WebSocketSession.nextEvent(): JsonObject = json.parseToJsonElement((incoming.receive() as Frame.Text).readText()).jsonObject

    @Test
    fun oneTapChoiceAnswersLockIndependentlyAndScoreWithoutHostApproval() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port, rotateQuestions = false)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(10_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val browser = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                val android = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                host.nextEvent(); browser.nextEvent(); android.nextEvent()
                val room = server.gameSession.value.roomId
                browser.sendEvent(GameEvent.JoinRoom(room, "Browser", "token-a"))
                val a = browser.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                android.sendEvent(GameEvent.JoinRoom(room, "Android", "token-b"))
                val b = android.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                host.sendEvent(GameEvent.HostNextQuestion())
                val safe = browser.stateWhere { (it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content == "q1" }
                val question = safe["currentQuestion"]!!.jsonObject
                assertEquals(4, question["options"]!!.jsonArray.size)
                assertFalse(question.containsKey("prompt"))
                assertFalse(question.containsKey("correctOptionIndex"))
                assertFalse(question.containsKey("imageUrl"))
                browser.sendEvent(GameEvent.LockAnswer(a, "q1", AnswerValue.MultipleChoiceSelection(1)))
                browser.sendEvent(GameEvent.LockAnswer(a, "q1", AnswerValue.MultipleChoiceSelection(0)))
                host.stateWhere { it["submissions"]!!.jsonObject[a]?.jsonObject?.get("isLocked")?.jsonPrimitive?.boolean == true }
                val locked = browser.stateWhere { it["submissions"]!!.jsonObject[a]?.jsonObject?.get("isLocked")?.jsonPrimitive?.boolean == true }
                assertFalse(locked.containsKey("buzzActiveTeamId"))
                android.sendEvent(GameEvent.LockAnswer(b, "q1", AnswerValue.MultipleChoiceSelection(0)))
                host.stateWhere { it["state"]!!.jsonPrimitive.content == "REVEAL_ANSWER" }
                assertEquals(100, server.gameSession.value.teams.first { it.id == a }.score)
                assertEquals(0, server.gameSession.value.teams.first { it.id == b }.score)
                assertEquals(AnswerValue.MultipleChoiceSelection(1), server.gameSession.value.submissions[a]?.answer)
                host.close(); browser.close(); android.close()
            }
        } finally { client.close(); server.stop() }
    }
    private suspend fun WebSocketSession.eventOf(name: String): JsonObject {
        while (true) { val event = nextEvent(); if (event["type"]!!.jsonPrimitive.content.endsWith(".$name")) return event }
    }
    private suspend fun WebSocketSession.stateWhere(predicate: (JsonObject) -> Boolean): JsonObject {
        while (true) { val state = eventOf("RoomStateBroadcast")["session"]!!.jsonObject; if (predicate(state)) return state }
    }
}
