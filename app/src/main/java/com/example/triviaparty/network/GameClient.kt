package com.example.triviaparty.network

import com.example.triviaparty.model.GameSession
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

enum class ClientConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    ERROR
}

class GameClient {

    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    private val client = HttpClient(CIO) {
        install(WebSockets)
    }

    private var session: DefaultClientWebSocketSession? = null
    private val clientScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val _connectionState = MutableStateFlow(ClientConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ClientConnectionState> = _connectionState.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _gameSession = MutableStateFlow<GameSession?>(null)
    val gameSession: StateFlow<GameSession?> = _gameSession.asStateFlow()

    private val _joinResponse = MutableStateFlow<GameEvent.JoinResponse?>(null)
    val joinResponse: StateFlow<GameEvent.JoinResponse?> = _joinResponse.asStateFlow()

    fun connect(hostIp: String = "127.0.0.1", port: Int = 8080, onConnected: () -> Unit = {}) {
        _connectionState.value = ClientConnectionState.CONNECTING
        _errorMessage.value = null

        clientScope.launch {
            try {
                client.webSocket(host = hostIp, port = port, path = "/ws") {
                    session = this
                    _connectionState.value = ClientConnectionState.CONNECTED
                    onConnected()
                    for (frame in incoming) {
                        if (frame is Frame.Text) {
                            handleServerMessage(frame.readText())
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
                _connectionState.value = ClientConnectionState.ERROR
                _errorMessage.value = "Could not connect to Host at $hostIp:$port. Make sure the Host Room is active!"
            } finally {
                session = null
                if (_connectionState.value != ClientConnectionState.ERROR) {
                    _connectionState.value = ClientConnectionState.DISCONNECTED
                }
            }
        }
    }

    fun disconnect() {
        clientScope.launch {
            try {
                session?.close()
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                session = null
                _connectionState.value = ClientConnectionState.DISCONNECTED
            }
        }
    }

    fun sendEvent(event: GameEvent) {
        val currentSession = session
        if (currentSession != null) {
            clientScope.launch {
                try {
                    val text = json.encodeToString(event)
                    currentSession.send(Frame.Text(text))
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }

    private fun handleServerMessage(text: String) {
        try {
            val event = json.decodeFromString<GameEvent>(text)
            when (event) {
                is GameEvent.RoomStateBroadcast -> {
                    _gameSession.value = event.session
                }
                is GameEvent.JoinResponse -> {
                    _joinResponse.value = event
                }
                else -> {}
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
