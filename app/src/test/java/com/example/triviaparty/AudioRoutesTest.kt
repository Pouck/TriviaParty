package com.example.triviaparty

import com.example.triviaparty.model.CategoryBuzzerSounds
import com.example.triviaparty.model.GameEndingSounds
import com.example.triviaparty.network.GameServer
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.net.HttpURLConnection
import java.net.ServerSocket
import java.net.URL

class AudioRoutesTest {
    @Test fun phoneAndTvSoundsAreServedAsAudioAndPlayerCodeCannotBeCached() {
        val port=ServerSocket(0).use {it.localPort}
        val server=GameServer(port,readPlayerAsset={File("src/main/assets/player",it).readText()},
            readTvBinaryAsset={File("src/main/assets/tv",it).readBytes()})
        try {
            server.start()
            for(id in CategoryBuzzerSounds.ids) {
                val connection=URL("http://127.0.0.1:$port/play/sounds/$id.mp3?v=2").openConnection() as HttpURLConnection
                assertEquals(200,connection.responseCode)
                assertEquals("audio/mpeg",connection.contentType)
                assertArrayEquals(File("src/main/assets/tv/phone-sounds/$id.mp3").readBytes(),connection.inputStream.use {it.readBytes()})
                connection.disconnect()
            }
            for(name in listOf("enabled.wav","good-ping.wav","bad-ping.wav","game-end.wav") + GameEndingSounds.files) {
                val connection=URL("http://127.0.0.1:$port/tv/sounds/$name").openConnection() as HttpURLConnection
                assertEquals(200,connection.responseCode);assertTrue(connection.contentType.startsWith("audio/"));assertTrue(connection.inputStream.use {it.readBytes()}.size>44)
                connection.disconnect()
            }
            val player=URL("http://127.0.0.1:$port/play/player.js?v=audio2").openConnection() as HttpURLConnection
            assertTrue(player.getHeaderField("Cache-Control").contains("no-store"));assertTrue(player.inputStream.bufferedReader().use {it.readText()}.contains("sound-button"));player.disconnect()
        } finally {server.stop()}
    }
}
