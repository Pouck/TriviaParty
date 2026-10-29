package com.example.triviaparty

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameEvent
import com.example.triviaparty.network.GameServer
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.WebSockets
import io.ktor.client.plugins.websocket.webSocketSession
import io.ktor.websocket.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test
import java.io.*
import java.net.ServerSocket
import java.nio.file.Files
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class ProgressiveCluesTest {
    private val question = Question.GuessWho("clues", "Test", clues = listOf("Indice initial", "Indice suivant", "Dernier indice"), acceptableAnswers = listOf("Solution privée"))
    private val config = HourglassConfig(secondsPerFlip = 5, maxFlips = 2, pointsDecayPerFlip = 5)
    private val json = Json { encodeDefaults = true; ignoreUnknownKeys = true }

    @Test fun cluesFollowPointBoundariesAndFutureCluesNeverReachTvOrPlayers() {
        val server = GameServer(0)
        val snapshot = GameServer::class.java.getDeclaredMethod("browserStateText", GameSession::class.java, String::class.java).apply { isAccessible = true }
        for (flip in 0..2) {
            val state = GameSession("1234", state = GameState.QUESTION_ACTIVE, currentQuestion = question,
                currentFlipNumber = flip, timingConfig = config, currentCategoryAnswerMode = CategoryAnswerMode.BUZZER)
            val tv = TvState.from(state)
            assertEquals(3, tv.clueCount)
            assertEquals(listOf(15, 10, 5)[flip], tv.points)
            question.clues.forEachIndexed { index, clue -> assertEquals(index <= flip, tv.question!!.prompt.contains(clue)) }
            assertNull(tv.question!!.answer)
            assertFalse(tv.encode().contains("Solution privée"))
            val atEndOfSegment = state.copy(elapsedSecondsInFlip = 4)
            assertEquals(tv.question, TvState.from(atEndOfSegment).question)
            assertEquals(tv.question, TvState.from(state.copy(answerTimerRunning = true, answerTimerRemainingSeconds = 5)).question)
            val playerJson = snapshot.invoke(server, state, "a") as String
            val publicQuestion = Json.parseToJsonElement(playerJson).jsonObject["session"]!!.jsonObject["currentQuestion"]!!.jsonObject
            assertEquals(setOf("id", "type"), publicQuestion.keys)
            assertEquals("guessWho", publicQuestion["type"]!!.jsonPrimitive.content)
            question.clues.forEach { assertFalse(playerJson.contains(it)) }
            assertFalse(playerJson.contains("Solution privée"))
            assertTrue(state.usesPlayerBuzzer())
        }
        val intro = TvState.from(GameSession("1234", state = GameState.CATEGORY_INTRO, currentQuestion = question))
        assertNull(intro.question)
        assertEquals(3, intro.clueCount)
        question.clues.forEach { assertFalse(intro.encode().contains(it)) }
        val revealed = TvState.from(GameSession("1234", state = GameState.REVEAL_ANSWER, currentQuestion = question))
        assertEquals("Qui suis-je ?", revealed.question!!.prompt)
        assertEquals("Solution privée", revealed.question!!.answer)
        assertEquals(question.activePrompt(2), question.activePrompt(Int.MAX_VALUE))
    }

    @Test fun demoImportsAndInvalidClueCountsOrCategoryModesAreRejected() {
        val root = Files.createTempDirectory("progressive-import-").toFile()
        try {
            val archive = File("../package-examples/qui-suis-je-demo/qui-suis-je-demo.zip")
            val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
            val category = Json { classDiscriminator = "kind" }.decodeFromString<CategoryQuestionFile>(File(imported.directory, "question-bank/qui-suis-je-demo.json").readText())
            assertTrue(category.questions.single() is Question.GuessWho)
            assertEquals(10, imported.gamePackage.answerTimeSeconds)
            assertEquals(3, (category.questions.single() as Question.GuessWho).clues.size)
            for (count in listOf(1, 2, 4)) {
                val source = File("../package-examples/qui-suis-je-demo/sources")
                val categoryJson = Json.parseToJsonElement(File(source, "question-bank/qui-suis-je-demo.json").readText()).jsonObject.toMutableMap()
                val q = categoryJson["questions"]!!.jsonArray.single().jsonObject.toMutableMap()
                q["clues"] = JsonArray((1..count).map { JsonPrimitive("Indice $it") })
                categoryJson["questions"] = JsonArray(listOf(JsonObject(q)))
                val bytes = ByteArrayOutputStream()
                ZipOutputStream(bytes).use { zip ->
                    for ((path, content) in mapOf("game.json" to File(source,"game.json").readText(), "question-bank/qui-suis-je-demo.json" to JsonObject(categoryJson).toString())) {
                        zip.putNextEntry(ZipEntry(path)); zip.write(content.toByteArray(Charsets.UTF_8)); zip.closeEntry()
                    }
                }
                val failure = runCatching { GamePackageImportRepository.importArchive(ByteArrayInputStream(bytes.toByteArray()), root, "qui-suis-je-demo") }.exceptionOrNull()
                assertNotNull(failure)
                assertTrue(failure!!.message.orEmpty().contains("indice par palier"))
            }
            assertTrue(runCatching { question.copy(clues = listOf(" ")) }.isFailure)
            assertTrue(runCatching { question.copy(acceptableAnswers = emptyList()) }.isFailure)
            assertTrue(runCatching { CategoryQuestionFile("Test", questionTypes = listOf("Qui suis-je ?"), questions = listOf(question)) }.isFailure)
            assertTrue(File(imported.directory,"game.json").isFile)
        } finally { root.deleteRecursively() }
    }

    @Test fun buzzingPausesCluesWrongAnswerResumesAndCorrectAnswerUsesBuzzReward() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(10_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val a = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                val b = client.webSocketSession(host = "127.0.0.1", port = port, path = "/play/ws")
                host.nextEvent(); a.nextEvent(); b.nextEvent()
                val room = server.gameSession.value.roomId
                a.sendEvent(GameEvent.JoinRoom(room, "A", "a-progressive"))
                val aId = a.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                b.sendEvent(GameEvent.JoinRoom(room, "B", "b-progressive"))
                val bId = b.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                @Suppress("UNCHECKED_CAST")
                val state = GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible = true }.get(server) as MutableStateFlow<GameSession>
                state.value = server.gameSession.value.copy(state = GameState.QUESTION_ACTIVE, currentQuestion = question,
                    currentCategoryAnswerMode = CategoryAnswerMode.BUZZER, timingConfig = config)
                val tick = GameServer::class.java.getDeclaredMethod("advanceQuestionTimer", HourglassConfig::class.java).apply { isAccessible = true }
                repeat(4) { tick.invoke(server, config) }
                assertFalse(TvState.from(server.gameSession.value).question!!.prompt.contains("Indice suivant"))
                a.sendEvent(GameEvent.LockAnswer(aId, question.id, AnswerValue.TextSelection("BUZZ")))
                host.stateWhere { it["answerTimerRunning"]!!.jsonPrimitive.boolean }
                repeat(5) { tick.invoke(server, config) }
                assertEquals(0, server.gameSession.value.currentFlipNumber)
                assertEquals(4, server.gameSession.value.elapsedSecondsInFlip)
                assertEquals(BuzzerStatus.PRESSED, server.gameSession.value.buzzerStatus(aId, true))
                host.sendEvent(GameEvent.HostJudgeTextBuzz(aId, false))
                host.stateWhere { it["submissions"]!!.jsonObject[aId]?.jsonObject?.get("isCorrect") == JsonPrimitive(false) }
                assertEquals(BuzzerStatus.INCORRECT, server.gameSession.value.buzzerStatus(aId, true))
                tick.invoke(server, config)
                assertEquals(1, server.gameSession.value.currentFlipNumber)
                assertTrue(TvState.from(server.gameSession.value).question!!.prompt.contains("Indice suivant"))
                host.sendEvent(GameEvent.HostStartQuestionTimer)
                host.stateWhere { it["questionReading"]==JsonPrimitive(false) }
                b.sendEvent(GameEvent.LockAnswer(bId, question.id, AnswerValue.TextSelection("BUZZ")))
                host.stateWhere { it["answerTimerTeamId"] == JsonPrimitive(bId) && it["answerTimerRunning"]!!.jsonPrimitive.boolean }
                repeat(7) { tick.invoke(server, config) }
                assertEquals(1, server.gameSession.value.currentFlipNumber)
                host.sendEvent(GameEvent.HostJudgeTextBuzz(bId, true))
                host.stateWhere { it["state"]!!.jsonPrimitive.content == "REVEAL_ANSWER" }
                assertEquals(10, server.gameSession.value.teams.first { it.id == bId }.score)
                assertEquals(-5, server.gameSession.value.teams.first { it.id == aId }.score)
                assertEquals("Solution privée", TvState.from(server.gameSession.value).question!!.answer)
                a.close(); b.close(); host.close()
            }
        } finally { client.close(); server.stop() }
    }

    private suspend fun WebSocketSession.sendEvent(event: GameEvent) = send(Frame.Text(json.encodeToString(event)))
    private suspend fun WebSocketSession.nextEvent(): JsonObject {
        while (true) {
            val frame = incoming.receive()
            if (frame is Frame.Text) return Json.parseToJsonElement(frame.readText()).jsonObject
        }
    }
    private suspend fun WebSocketSession.eventOf(type: String): JsonObject {
        while (true) { val event = nextEvent(); if (event["type"]!!.jsonPrimitive.content.endsWith(".$type")) return event }
    }
    private suspend fun WebSocketSession.stateWhere(predicate: (JsonObject) -> Boolean): JsonObject {
        while (true) {
            val event = eventOf("RoomStateBroadcast")
            val state = event["session"]!!.jsonObject
            if (predicate(state)) return state
        }
    }
}
