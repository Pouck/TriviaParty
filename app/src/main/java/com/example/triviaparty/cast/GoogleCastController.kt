package com.example.triviaparty.cast

import android.content.Context
import androidx.mediarouter.media.MediaRouter
import com.example.triviaparty.R
import com.example.triviaparty.model.GameSession
import com.google.android.gms.cast.Cast
import com.google.android.gms.cast.CastDevice
import com.google.android.gms.cast.framework.CastContext
import com.google.android.gms.cast.framework.CastSession
import com.google.android.gms.cast.framework.SessionManagerListener
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import org.json.JSONObject

data class CastTv(val id: String, val name: String)
data class CastStatus(
    val message: String = "Choose a TV to start casting",
    val error: String? = null,
    val audioStatus: String? = null,
    val connected: Boolean = false,
    val connecting: Boolean = false
)

/** All SDK operations and callbacks are on the main thread. */
class GoogleCastController(context: Context, private val game: StateFlow<GameSession>) {
    private val appContext = context.applicationContext
    val configured = appContext.getString(R.string.cast_receiver_application_id).isNotBlank()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val _devices = MutableStateFlow<List<CastTv>>(emptyList())
    val devices = _devices.asStateFlow()
    private val _status = MutableStateFlow(CastStatus())
    val status = _status.asStateFlow()
    private var castContext: CastContext? = null
    private var router: MediaRouter? = null
    private var session: CastSession? = null
    private var discovering = false
    private var started = false
    private var generation = 0
    private var sending = false
    private var pending: String? = null
    private var reviewPreview: GameSession? = null
    private var latest = TvState.from(game.value).encode()

    private val routeCallback = object : MediaRouter.Callback() {
        override fun onRouteAdded(router: MediaRouter, route: MediaRouter.RouteInfo) = refreshDevices()
        override fun onRouteRemoved(router: MediaRouter, route: MediaRouter.RouteInfo) = refreshDevices()
        override fun onRouteChanged(router: MediaRouter, route: MediaRouter.RouteInfo) = refreshDevices()
    }

    private val sessionListener = object : SessionManagerListener<CastSession> {
        override fun onSessionStarting(session: CastSession) {
            _status.value = CastStatus("Connecting to TV…", connecting = true)
        }
        override fun onSessionStarted(session: CastSession, sessionId: String) = attach(session)
        override fun onSessionStartFailed(session: CastSession, error: Int) = connectionFailed(error)
        override fun onSessionEnding(session: CastSession) {
            detach()
            _status.value = CastStatus("Disconnecting…", connecting = true)
        }
        override fun onSessionEnded(session: CastSession, error: Int) {
            detach()
            _status.value = CastStatus("Casting stopped")
        }
        override fun onSessionResuming(session: CastSession, sessionId: String) {
            _status.value = CastStatus("Reconnecting to TV…", connecting = true)
        }
        override fun onSessionResumed(session: CastSession, wasSuspended: Boolean) = attach(session)
        override fun onSessionResumeFailed(session: CastSession, error: Int) = connectionFailed(error)
        override fun onSessionSuspended(session: CastSession, reason: Int) {
            detach()
            _status.value = CastStatus("TV connection interrupted. Reconnecting…", connecting = true)
        }
    }

    fun start() {
        if (started || !configured) return
        try {
            val sdk = CastContext.getSharedInstance(appContext)
            castContext = sdk
            router = MediaRouter.getInstance(appContext)
            sdk.sessionManager.addSessionManagerListener(sessionListener, CastSession::class.java)
            started = true
            sdk.sessionManager.currentCastSession?.takeIf { it.isConnected }?.let(::attach)
            scope.launch {
                game.collect {
                    latest = TvState.from(reviewPreview ?: it).encode()
                    sendLatest()
                }
            }
        } catch (e: Exception) {
            _status.value = CastStatus(error = "Google Cast could not start. Check Google Play services and retry.")
        }
    }

    /** Temporarily mirror the solo-review screen to the receiver without touching game state. */
    fun showReviewPreview(preview: GameSession) {
        reviewPreview = preview
        latest = TvState.from(preview).encode()
        sendLatest()
    }

    fun clearReviewPreview() {
        reviewPreview = null
        latest = TvState.from(game.value).encode()
        sendLatest()
    }

    fun startDiscovery() {
        start()
        val sdk = castContext ?: return
        val selector = sdk.mergedSelector ?: return
        if (!started || discovering) return
        try {
            router?.addCallback(selector, routeCallback, MediaRouter.CALLBACK_FLAG_REQUEST_DISCOVERY)
            discovering = true
            _status.value = _status.value.copy(error = null)
            refreshDevices()
        } catch (e: Exception) {
            _status.value = _status.value.copy(error = "Could not discover TVs. Check Nearby devices permission and Wi-Fi.")
        }
    }

    fun stopDiscovery() {
        router?.removeCallback(routeCallback)
        discovering = false
    }

    /** Reattach to the Cast session when Android returns this sender app to the foreground. */
    fun onAppResumed() {
        val activeSession = castContext?.sessionManager?.currentCastSession ?: return
        if (activeSession.isConnected && session !== activeSession) attach(activeSession)
    }

    private fun refreshDevices() {
        val selector = castContext?.mergedSelector ?: return
        _devices.value = router?.routes.orEmpty().filter { route ->
            route.isEnabled && !route.isDefault && route.matchesSelector(selector) &&
                CastDevice.getFromBundle(route.extras)?.hasCapability(CastDevice.CAPABILITY_VIDEO_OUT) == true
        }.map { CastTv(it.id, it.name) }.distinctBy { it.id }
    }

    fun connect(id: String) {
        if (_status.value.connecting) return
        val route = router?.routes?.find { it.id == id && it.isEnabled }
        if (route == null) {
            _status.value = _status.value.copy(error = "This TV is no longer available. Retry discovery.")
            return
        }
        try {
            _status.value = CastStatus("Connecting to ${route.name}…", connecting = true)
            router?.selectRoute(route)
        } catch (e: Exception) {
            connectionFailed(null)
        }
    }

    private fun attach(connectedSession: CastSession) {
        if (session === connectedSession && connectedSession.isConnected) {
            sendLatest()
            return
        }
        detach()
        session = connectedSession
        _status.value = CastStatus(
            message = "Casting to ${connectedSession.castDevice?.friendlyName ?: "TV"}",
            connected = true
        )
        try {
            connectedSession.setMessageReceivedCallbacks(TRIVIA_CAST_NAMESPACE) { _, _, message ->
                if (session === connectedSession) runCatching {
                    val payload = JSONObject(message)
                    when (payload.optString("type")) {
                        "ready" -> sendLatest()
                        "audio-status" -> _status.value = _status.value.copy(audioStatus = when (payload.optString("status")) {
                            "playing" -> "Son TV en lecture · vérifiez le volume du téléviseur si vous ne l’entendez pas."
                            "blocked" -> "Le téléviseur bloque le son. Reconnectez la diffusion puis réessayez."
                            else -> "Le téléviseur ne peut pas charger le son. Réessayez ou reconnectez la diffusion."
                        })
                    }
                }
            }
            sendLatest()
        } catch (e: Exception) {
            _status.value = _status.value.copy(error = "The TV receiver could not open the game channel. Reconnect to retry.")
        }
    }

    private fun sendLatest() {
        if (session?.isConnected != true) return
        pending = latest
        flush()
    }

    /** Keep only the newest snapshot while an earlier send is in flight. */
    private fun flush() {
        val active = session?.takeIf { it.isConnected } ?: return
        if (sending) return
        val payload = pending ?: return
        pending = null
        if (payload.toByteArray(Charsets.UTF_8).size > Cast.MAX_MESSAGE_LENGTH) {
            _status.value = _status.value.copy(error = "This game is too large to send to the TV.")
            return
        }
        val currentGeneration = generation
        sending = true
        try {
            active.sendMessage(TRIVIA_CAST_NAMESPACE, payload).setResultCallback { result ->
                if (generation == currentGeneration) {
                    sending = false
                    _status.value = _status.value.copy(error = if (result.isSuccess) null else
                        "TV update failed (${result.statusCode}). Tap Resend game or reconnect.")
                    flush()
                }
            }
        } catch (e: Exception) {
            sending = false
            _status.value = _status.value.copy(error = "TV update failed. Tap Resend game or reconnect.")
        }
    }

    fun testAudio() {
        val active = session?.takeIf { it.isConnected } ?: return
        _status.value = _status.value.copy(audioStatus = "Test du son TV…")
        try {
            active.sendMessage(TRIVIA_CAST_NAMESPACE, "{\"type\":\"audio-test\",\"version\":1}").setResultCallback { result ->
                if (!result.isSuccess) _status.value = _status.value.copy(audioStatus = "Le test audio n’a pas atteint le téléviseur. Reconnectez la diffusion.")
            }
        } catch (_: Exception) {
            _status.value = _status.value.copy(audioStatus = "Test audio impossible. Reconnectez la diffusion.")
        }
    }

    fun resend() = sendLatest()

    fun stopCasting() {
        detach()
        castContext?.sessionManager?.endCurrentSession(true)
        _status.value = CastStatus("Casting stopped")
    }

    private fun connectionFailed(code: Int?) {
        detach()
        _status.value = CastStatus(error = "Could not launch Trivia Party on the TV${code?.let { " (code $it)" } ?: ""}. Check the receiver setup and retry.")
    }

    private fun detach() {
        generation++
        runCatching { session?.removeMessageReceivedCallbacks(TRIVIA_CAST_NAMESPACE) }
        session = null
        pending = null
        sending = false
    }

    fun close() {
        stopDiscovery()
        detach()
        castContext?.sessionManager?.removeSessionManagerListener(sessionListener, CastSession::class.java)
        scope.cancel()
    }
}
