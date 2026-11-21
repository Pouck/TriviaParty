package com.example.triviaparty

import com.example.triviaparty.util.NetworkUtils
import org.junit.Assert.*
import org.junit.Test

class NetworkUtilsTest {

    @Test
    fun testGetLocalIpAddressReturnsValidFormatOrFallback() {
        val ip = NetworkUtils.getLocalIpAddress()
        assertNotNull(ip)
        assertTrue(
            "IP address should be valid IPv4 or 127.0.0.1, got: $ip",
            ip == "127.0.0.1" || ip.matches(Regex("""\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"""))
        )
    }
}
