package com.example.triviaparty

import com.example.triviaparty.data.QuestionBankRepository
import com.example.triviaparty.network.*
import java.net.ServerSocket
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import org.junit.Assert.*
import org.junit.Test

class HostConnectionTest {
    @Test fun immediateDisconnectAndRetryKeepsTheReplacementConnectionUsable() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val server = GameServer(port)
        val client = GameClient()
        server.start()
        try {
            withTimeout(20000) {
                repeat(12) {
                    client.disconnect()
                    client.connect(port = port)
                    client.gameSession.first { it != null }
                    val previousRoom = server.gameSession.value.roomId
                    client.sendEvent(GameEvent.HostStartGame(QuestionBankRepository.sampleCategories.take(1)))
                    val room = client.gameSession.first { it != null && it.roomId != previousRoom }
                    assertEquals(ClientConnectionState.CONNECTED, client.connectionState.value)
                    assertEquals(server.gameSession.value.roomId, room!!.roomId)
                    client.sendEvent(GameEvent.HostBeginCategorySelect)
                    client.gameSession.first { it?.state == com.example.triviaparty.model.GameState.CATEGORY_INTRO }
                }
            }
        } finally {
            client.disconnect()
            server.stop()
        }
    }

    @Test fun retryCanReplaceAnInFlightFailedConnection() = runBlocking {
        val port = ServerSocket(0).use { it.localPort }
        val closedPort = ServerSocket(0).use { it.localPort }
        val server = GameServer(port)
        val client = GameClient()
        server.start()
        try {
            client.connect(port = closedPort)
            client.connect(port = port)
            withTimeout(5000) { client.gameSession.first { it != null } }
            assertEquals(ClientConnectionState.CONNECTED, client.connectionState.value)
            assertNull(client.errorMessage.value)
        } finally {
            client.disconnect()
            server.stop()
        }
    }
}
