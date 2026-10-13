package com.example.triviaparty.util

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.withContext
import java.net.InetAddress
import java.net.Socket

data class DiscoveredDisplay(
    val ipAddress: String,
    val name: String,
    val webTvUrl: String
)

object DeviceScanner {

    /**
     * Scans local Wi-Fi subnet for responsive devices or active Web TV endpoints on port 8080.
     */
    suspend fun scanLocalSubnet(localIp: String): List<DiscoveredDisplay> = withContext(Dispatchers.IO) {
        val discovered = mutableListOf<DiscoveredDisplay>()
        if (localIp == "127.0.0.1") {
            discovered.add(DiscoveredDisplay("127.0.0.1", "Local Host Display", "http://127.0.0.1:8080/tv"))
            return@withContext discovered
        }

        val prefix = localIp.substringBeforeLast(".") + "."
        val tasks = (1..254).map { i ->
            async {
                val ip = "$prefix$i"
                try {
                    val address = InetAddress.getByName(ip)
                    if (address.isReachable(150)) {
                        // Check if port 8080 or port 80 is open
                        val isPortOpen = try {
                            Socket(ip, 8080).use { true }
                        } catch (e: Exception) {
                            false
                        }
                        if (isPortOpen || ip == localIp) {
                            DiscoveredDisplay(ip, "TV Display ($ip)", "http://$ip:8080/tv")
                        } else null
                    } else null
                } catch (e: Exception) {
                    null
                }
            }
        }

        val results = tasks.awaitAll().filterNotNull()
        discovered.addAll(results)
        if (discovered.none { it.ipAddress == localIp }) {
            discovered.add(0, DiscoveredDisplay(localIp, "This Device Display ($localIp)", "http://$localIp:8080/tv"))
        }
        discovered
    }
}
