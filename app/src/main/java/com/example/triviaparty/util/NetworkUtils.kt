package com.example.triviaparty.util

import java.net.Inet4Address
import java.net.NetworkInterface

object NetworkUtils {

    /**
     * Finds the local IPv4 Wi-Fi/LAN IP address of the device.
     * Prioritizes standard local subnet prefixes (`192.168.`, `10.`, `172.`)
     * and skips VPN / virtual network adapters (such as Tailscale `100.`, etc.).
     * Falls back to any non-loopback IPv4 address, and finally to "127.0.0.1" if offline.
     */
    fun getLocalIpAddress(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces() ?: return "127.0.0.1"
            
            val candidates = mutableListOf<String>()

            for (networkInterface in interfaces) {
                if (networkInterface.isLoopback || !networkInterface.isUp) continue
                
                val name = networkInterface.name.lowercase()
                val displayName = networkInterface.displayName.lowercase()
                
                // Skip common VPN / virtual network adapters (e.g. tailscale, tun, tap, vpn, ppp)
                if (name.contains("tun") || name.contains("tap") || name.contains("ppp") || name.contains("vpn") ||
                    name.contains("tailscale") || name.contains("rmnet") || name.contains("vbox") ||
                    displayName.contains("tun") || displayName.contains("tap") || displayName.contains("vpn") ||
                    displayName.contains("tailscale")) {
                    continue
                }

                val addresses = networkInterface.inetAddresses
                for (address in addresses) {
                    if (!address.isLoopbackAddress && address is Inet4Address) {
                        val host = address.hostAddress
                        if (host != null && !host.startsWith("127.")) {
                            // Check if it's Tailscale (100.64.0.0/10 or similar 100.x)
                            if (host.startsWith("100.")) {
                                continue
                            }
                            candidates.add(host)
                        }
                    }
                }
            }

            // 1. Priority: standard LAN / Wi-Fi subnets (192.168., 10., 172.16-31.)
            for (ip in candidates) {
                if (ip.startsWith("192.168.") || ip.startsWith("10.")) {
                    return ip
                }
                if (ip.startsWith("172.")) {
                    // Check standard private 172.16.0.0 to 172.31.255.255
                    val parts = ip.split(".")
                    if (parts.size >= 2) {
                        val secondOctet = parts[1].toIntOrNull() ?: 0
                        if (secondOctet in 16..31) {
                            return ip
                        }
                    }
                }
            }

            // 2. Fallback: any other non-loopback, non-VPN IPv4 address found
            if (candidates.isNotEmpty()) {
                return candidates.first()
            }

            // 3. Fallback check across all interfaces without strict VPN filtering if none found
            for (networkInterface in NetworkInterface.getNetworkInterfaces() ?: return "127.0.0.1") {
                if (networkInterface.isLoopback || !networkInterface.isUp) continue
                val addresses = networkInterface.inetAddresses
                for (address in addresses) {
                    if (!address.isLoopbackAddress && address is Inet4Address) {
                        val host = address.hostAddress
                        if (host != null && !host.startsWith("127.") && !host.startsWith("100.")) {
                            return host
                        }
                    }
                }
            }

        } catch (e: Exception) {
            e.printStackTrace()
        }
        return "127.0.0.1"
    }
}
