package com.example.triviaparty.util

import android.content.Context
import android.hardware.display.DisplayManager
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class DiscoveredTvDevice(
    val id: String,
    val name: String,
    val type: String, // "Chromecast/Smart TV", "Secondary Display", "Web Display"
    val address: String? = null
)

object TvCastManager {

    private val _discoveredTvs = MutableStateFlow<List<DiscoveredTvDevice>>(emptyList())
    val discoveredTvs: StateFlow<List<DiscoveredTvDevice>> = _discoveredTvs.asStateFlow()
    private val _discoveryError = MutableStateFlow<String?>(null)
    val discoveryError: StateFlow<String?> = _discoveryError.asStateFlow()
    private val handler = Handler(Looper.getMainLooper())
    private var generation = 0

    private var nsdManager: NsdManager? = null
    private var discoveryListener: NsdManager.DiscoveryListener? = null

    fun startDiscovery(context: Context) {
        stopDiscovery()
        val currentGeneration = generation
        _discoveryError.value = null
        val devices = mutableListOf<DiscoveredTvDevice>()

        // 1. Check for physical or wireless secondary displays (HDMI, DeX, Miracast)
        val displayManager = context.getSystemService(Context.DISPLAY_SERVICE) as? DisplayManager
        val displays = displayManager?.getDisplays(DisplayManager.DISPLAY_CATEGORY_PRESENTATION) ?: emptyArray()
        displays.forEach { display ->
            devices.add(
                DiscoveredTvDevice(
                    id = "display_${display.displayId}",
                    name = display.name ?: "Connected Secondary Display",
                    type = "Physical/Wireless Display"
                )
            )
        }

        // 2. Discover Chromecast & Smart TV services on Wi-Fi network via NSD (mDNS)
        nsdManager = context.getSystemService(Context.NSD_SERVICE) as? NsdManager
        if (nsdManager == null) {
            _discoveredTvs.value = devices
            _discoveryError.value = "Network discovery is unavailable on this device."
            return
        }
        discoveryListener = object : NsdManager.DiscoveryListener {
            override fun onDiscoveryStarted(regType: String) {}

            override fun onServiceFound(service: NsdServiceInfo) {
                handler.post {
                    if (currentGeneration != generation) return@post
                    val serviceName = service.serviceName ?: "Smart TV"
                    val dev = DiscoveredTvDevice(
                        id = serviceName,
                        name = serviceName,
                        type = "Google Cast / Smart TV"
                    )
                    if (_discoveredTvs.value.none { it.id == dev.id }) {
                        _discoveredTvs.value = _discoveredTvs.value + dev
                    }
                }
            }

            override fun onServiceLost(service: NsdServiceInfo) {
                handler.post {
                    if (currentGeneration != generation) return@post
                    _discoveredTvs.value = _discoveredTvs.value.filter { it.id != service.serviceName }
                }
            }

            override fun onDiscoveryStopped(serviceType: String) {}
            override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) {
                handler.post {
                    if (currentGeneration == generation) {
                        _discoveryError.value = "TV discovery failed (code $errorCode). Check Nearby devices permission and your Wi-Fi connection, then retry."
                    }
                }
            }
            override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {}
        }

        _discoveredTvs.value = devices
        try {
            nsdManager?.discoverServices("_googlecast._tcp.", NsdManager.PROTOCOL_DNS_SD, discoveryListener)
        } catch (e: Exception) {
            _discoveryError.value = if (e is SecurityException) {
                "Nearby devices permission is required to discover TVs. Enable it in app settings."
            } else {
                "Could not start TV discovery. Check your Wi-Fi connection and retry."
            }
            e.printStackTrace()
        }
    }

    fun stopDiscovery() {
        generation++
        try {
            if (nsdManager != null && discoveryListener != null) {
                nsdManager?.stopServiceDiscovery(discoveryListener)
            }
        } catch (e: Exception) {
            // Ignore
        }
        discoveryListener = null
        nsdManager = null
    }
}
