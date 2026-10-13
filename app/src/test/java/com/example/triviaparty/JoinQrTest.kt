package com.example.triviaparty

import com.example.triviaparty.util.JoinQrSvg
import com.example.triviaparty.cast.TvState
import com.example.triviaparty.model.GameSession
import com.google.zxing.common.BitMatrix
import com.google.zxing.qrcode.decoder.Decoder
import org.junit.Assert.*
import org.junit.Test

class JoinQrTest {
    @Test fun publicSvgDecodesToLocalPlayerPage() {
        val url = "http://192.168.86.47:8080/play"
        val svg = JoinQrSvg.render(url)
        val dimensions = Regex("viewBox=\"0 0 (\\d+) (\\d+)\"").find(svg)!!
        val matrix = BitMatrix(dimensions.groupValues[1].toInt(), dimensions.groupValues[2].toInt())
        Regex("<rect x=\"(\\d+)\" y=\"(\\d+)\"").findAll(svg).forEach {
            matrix.set(it.groupValues[1].toInt(), it.groupValues[2].toInt())
        }
        // Remove the four-module quiet zone for the QR decoder.
        val qr = BitMatrix(matrix.width - 8)
        for (y in 0 until qr.height) for (x in 0 until qr.width) if (matrix[x + 4, y + 4]) qr.set(x, y)
        assertEquals(url, Decoder().decode(qr).text)
    }
    @Test fun tvSnapshotIncludesOnlyPublicJoiningAndTimingDetails() {
        val state = TvState.from(GameSession(roomId = "1234", hostIpAddress = "192.168.86.47"))
        assertEquals("http://192.168.86.47:8080/play", state.joinUrl)
        assertEquals("http://192.168.86.47:8080/tv/join-qr.svg", state.joinQrUrl)
        assertFalse(state.encode().contains("judge#"))
        assertFalse(state.encode().contains("sessionToken"))
    }
}
