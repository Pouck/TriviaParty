package com.example.triviaparty

import com.example.triviaparty.data.QuestionBankRepository
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
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.net.ServerSocket
import java.io.File
import java.net.URL
import java.net.HttpURLConnection
import kotlin.io.path.createTempDirectory

class TvBroadcastTest {
    @Test
    fun importedImagesAreServedOnlyFromPackageImageFolders() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val packageRoot = createTempDirectory("tv-media-").toFile()
        val image = File(packageRoot, "charades/images/nun-ace.png")
        image.parentFile?.mkdirs()
        val imageBytes = byteArrayOf(1, 2, 3, 4)
        image.writeBytes(imageBytes)
        val server = GameServer(port, importedPackagesDirectory = packageRoot)
        try {
            server.start()
            withTimeout(10_000) {
                val response = URL("http://127.0.0.1:$port/media/charades/images/nun-ace.png")
                    .openConnection() as HttpURLConnection
                try {
                    assertEquals(200, response.responseCode)
                    assertTrue(response.contentType.startsWith("image/png"))
                    assertTrue(response.inputStream.use { it.readBytes().contentEquals(imageBytes) })
                } finally {
                    response.disconnect()
                }
                val missing = URL("http://127.0.0.1:$port/media/charades/question-bank/game.json")
                    .openConnection() as HttpURLConnection
                try {
                    assertEquals(404, missing.responseCode)
                } finally {
                    missing.disconnect()
                }
            }
        } finally {
            server.stop()
            packageRoot.deleteRecursively()
        }
    }

    @Test
    fun startingANewGameClearsPreviousPlayersAndAssignsANewRoomCode() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(10_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val player = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                try {
                    host.receiveState()
                    player.receiveState()
                    val categories = QuestionBankRepository.sampleCategories
                    val firstStart: GameEvent = GameEvent.HostStartGame(categories)
                    host.send(Frame.Text(Json.encodeToString(firstStart)))
                    val firstGame = host.receiveState().session
                    player.receiveState()
                    val join: GameEvent = GameEvent.JoinRoom(firstGame.roomId, "Old Team", "old-token")
                    player.send(Frame.Text(Json.encodeToString(join)))
                    assertTrue((player.receiveEvent() as GameEvent.JoinResponse).success)
                    player.receiveState()
                    val joined = host.receiveState().session
                    val team = joined.teams.single()

                    val score: GameEvent = GameEvent.HostSetScore(team.id, 900)
                    host.send(Frame.Text(Json.encodeToString(score)))
                    assertEquals(900, host.receiveState().session.teams.single().score)

                    val secondStart: GameEvent = GameEvent.HostStartGame(categories)
                    host.send(Frame.Text(Json.encodeToString(secondStart)))
                    val secondGame = host.receiveState().session
                    assertNotEquals(firstGame.roomId, secondGame.roomId)
                    assertTrue(secondGame.teams.isEmpty())
                    assertTrue(secondGame.pendingJoinRequests.isEmpty())
                } finally {
                    host.close()
                    player.close()
                }
            }
        } finally {
            client.close()
            server.stop()
        }
    }

    @Test
    fun hostAndTvReceiveUpdatesWithoutJoiningAsPlayers() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port)
        val client = HttpClient(CIO) { install(WebSockets) }
        try {
            server.start()
            withTimeout(10_000) {
                val host = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                val tv = client.webSocketSession(host = "127.0.0.1", port = port, path = "/ws")
                try {
                    host.receiveState()
                    tv.receiveState()
                    val expectedRounds = QuestionBankRepository.sampleCategories.sumOf {
                        QuestionBankRepository.getQuestionsForCategory(it).size
                    }
                    val start: GameEvent = GameEvent.HostStartGame(
                        categories = QuestionBankRepository.sampleCategories,
                        totalRounds = expectedRounds
                    )
                    host.send(Frame.Text(Json.encodeToString(start)))
                    assertEquals(expectedRounds, host.receiveState().session.totalRounds)
                    val tvState = tv.receiveState().session
                    assertEquals(expectedRounds, tvState.totalRounds)
                    assertTrue(tvState.teams.isEmpty())

                } finally {
                    host.close()
                    tv.close()
                }
            }
        } finally {
            client.close()
            server.stop()
        }
    }

    private suspend fun WebSocketSession.receiveState(): GameEvent.RoomStateBroadcast {
        return receiveEvent() as GameEvent.RoomStateBroadcast
    }

    private suspend fun WebSocketSession.receiveEvent(): GameEvent {
        val frame = incoming.receive() as Frame.Text
        return Json.decodeFromString(frame.readText())
    }
}
