package com.example.triviaparty

import com.example.triviaparty.model.AnswerReactions
import kotlinx.serialization.json.*
import java.io.File
import kotlin.random.Random
import org.junit.Assert.*
import org.junit.Test
import com.example.triviaparty.cast.TvState
import com.example.triviaparty.model.GameSession
import com.example.triviaparty.network.GameServer
import java.net.ServerSocket
import java.net.URL
import java.net.HttpURLConnection

class AnswerReactionsTest {
    @Test fun selectedClipReachesTvAndAllRecordingsAreServedWithTheirAudioType() {
        val state=TvState.from(GameSession(roomId="test",answerSoundId=3,answerSound="bad",answerSoundClip="bad-04.mp3",buzzerSoundId=2))
        assertEquals("bad-04.mp3",state.answerSoundClip)
        assertEquals(2,state.buzzerSoundId)
        assertTrue(state.encode().contains("bad-04.mp3"))
        val port=ServerSocket(0).use { it.localPort }
        val server=GameServer(port,readTvBinaryAsset={ path -> File("src/main/assets/tv",path).readBytes() })
        try {
            server.start()
            for(file in AnswerReactions.clips("good")+AnswerReactions.clips("bad")+listOf("buzzer.wav","enabled.wav","good-ping.wav","bad-ping.wav","game-end.wav")) {
                val connection=URL("http://127.0.0.1:$port/tv/sounds/$file").openConnection() as HttpURLConnection
                try {
                    assertEquals(200,connection.responseCode)
                    assertTrue(connection.contentType.startsWith(if(file.endsWith("mp3")) "audio/mpeg" else "audio/wav"))
                    assertArrayEquals(File("src/main/assets/tv/sounds",file).readBytes(),connection.inputStream.use { it.readBytes() })
                } finally {connection.disconnect()}
            }
            val denied=URL("http://127.0.0.1:$port/tv/sounds/reactions.json").openConnection() as HttpURLConnection
            try {assertEquals(404,denied.responseCode)} finally {denied.disconnect()}
        } finally {server.stop()}
    }
    @Test fun everySelectableClipExistsWithTheCorrectOutcomeAndSeveralVoices() {
        val folder=File("src/main/assets/tv/sounds")
        val records=Json.parseToJsonElement(File(folder,"reactions.json").readText().removePrefix("\uFEFF")).jsonArray.map { it.jsonObject }
        assertEquals(46,records.size)
        assertEquals(AnswerReactions.clips("good").toSet()+AnswerReactions.clips("bad").toSet(),records.map { it["file"]!!.jsonPrimitive.content }.toSet())
        records.forEach { record ->
            val file=record["file"]!!.jsonPrimitive.content
            assertTrue(file.startsWith(record["outcome"]!!.jsonPrimitive.content+"-"))
            assertTrue("Empty recording: $file",File(folder,file).length()>1000)
        }
        assertEquals(setOf("fr","en","de","ru"),records.map { it["language"]!!.jsonPrimitive.content }.toSet())
        assertTrue(records.map { it["voice"]!!.jsonPrimitive.content }.toSet().size>=5)
    }
    @Test fun randomDrawsStayInOutcomeAndAvoidThePreviousClip() {
        val random=Random(17)
        for(outcome in listOf("good","bad")) {
            var previous:String?=null;val selected=mutableSetOf<String>()
            repeat(300) { val next=AnswerReactions.choose(outcome,previous,random);assertNotEquals(previous,next);assertTrue(next in AnswerReactions.clips(outcome));selected+=next;previous=next }
            assertEquals(AnswerReactions.clips(outcome).toSet(),selected)
        }
        for(path in listOf("../good.wav","good-01.wav/../../secret","other.wav",null)) assertFalse(AnswerReactions.isAllowed(path))
    }
}
