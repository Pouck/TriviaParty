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
    @Test fun audienceOptionRoundTripsAndLegacyGamesKeepFullBank() {
        val json=kotlinx.serialization.json.Json { encodeDefaults=true }
        val event=com.example.triviaparty.network.GameEvent.HostStartGame(listOf("Test"),allAudiencesOnly=true)
        val encoded=json.encodeToString(com.example.triviaparty.network.GameEvent.HostStartGame.serializer(),event)
        assertTrue(json.decodeFromString(com.example.triviaparty.network.GameEvent.HostStartGame.serializer(),encoded).allAudiencesOnly)
        assertFalse(json.decodeFromString(com.example.triviaparty.network.GameEvent.HostStartGame.serializer(),"""{"categories":["Test"]}""").allAudiencesOnly)
        assertTrue(TvState.from(GameSession(roomId="test")).encode().contains("\"answerSoundClip\":null"))
    }

    @Test fun audienceFilterExcludesRestrictedAndUnreviewedWithoutFallback() {
        val clips=listOf(
            com.example.triviaparty.model.ReactionClip("good-01.wav","good","A","Bravo",audience="all"),
            com.example.triviaparty.model.ReactionClip("good-02.wav","good","B","Adult",audience="mature"),
            com.example.triviaparty.model.ReactionClip("bad-01.wav","bad","C","Unknown",audience="unreviewed"))
        val filtered=com.example.triviaparty.model.AnswerReactionPicker(clips,true)
        repeat(20) { assertEquals("good-01.wav",filtered.chooseOrNull("good",null)) }
        assertNull(filtered.chooseOrNull("bad",null))
        val full=com.example.triviaparty.model.AnswerReactionPicker(clips,false)
        assertEquals(setOf("good-01.wav","good-02.wav"),(1..2).map {full.choose("good",null)}.toSet())
        assertEquals("bad-01.wav",full.choose("bad",null))
    }

    @Test fun selectedClipReachesTvAndAllRecordingsAreServedWithTheirAudioType() {
        val state=TvState.from(GameSession(roomId="test",answerSoundId=3,answerSound="bad",answerSoundClip="bad-04.mp3",buzzerSoundId=2))
        assertEquals("bad-04.mp3",state.answerSoundClip)
        assertEquals(2,state.buzzerSoundId)
        assertTrue(state.encode().contains("bad-04.mp3"))
        val port=ServerSocket(0).use { it.localPort }
        val server=GameServer(port,readTvAsset={path -> File("src/main/assets/tv",path).readText()},readTvBinaryAsset={ path -> File("src/main/assets/tv",path).readBytes() })
        try {
            server.start()
            for(file in AnswerReactions.clips("good")+AnswerReactions.clips("bad")+listOf("buzzer.wav","enabled.wav","good-ping.wav","bad-ping.wav","game-end.wav")+(1..10).map {"buzzer-%02d.wav".format(it)}) {
                val connection=URL("http://127.0.0.1:$port/tv/sounds/$file").openConnection() as HttpURLConnection
                try {
                    assertEquals(200,connection.responseCode)
                    assertTrue(connection.contentType.startsWith(if(file.endsWith("mp3")) "audio/mpeg" else "audio/wav"))
                    assertArrayEquals(File("src/main/assets/tv/sounds",file).readBytes(),connection.inputStream.use { it.readBytes() })
                } finally {connection.disconnect()}
            }
            assertTrue(URL("http://127.0.0.1:$port/tv/buzzer-sampler").readText().contains("Mini boing"))
            val denied=URL("http://127.0.0.1:$port/tv/sounds/reactions.json").openConnection() as HttpURLConnection
            try {assertEquals(404,denied.responseCode)} finally {denied.disconnect()}
        } finally {server.stop()}
    }
    @Test fun everySelectableClipExistsWithTheCorrectOutcomeAndSeveralVoices() {
        val folder=File("src/main/assets/tv/sounds")
        val records=Json.parseToJsonElement(File(folder,"reactions.json").readText().removePrefix("\uFEFF")).jsonArray.map { it.jsonObject }
        assertTrue(records.size in setOf(46,100))
        assertEquals(AnswerReactions.clips("good").toSet()+AnswerReactions.clips("bad").toSet(),records.map { it["file"]!!.jsonPrimitive.content }.toSet())
        records.forEach { record ->
            val file=record["file"]!!.jsonPrimitive.content
            assertTrue(file.startsWith(record["outcome"]!!.jsonPrimitive.content+"-"))
            assertTrue("Empty recording: $file",File(folder,file).length()>1000)
        }
        assertEquals(if(records.size==100) setOf("fr","en","de","es") else setOf("fr","en","de","ru"),records.map { it["language"]!!.jsonPrimitive.content }.toSet())
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
    @Test fun shuffleBankExhaustsClipsAndVariesAvailableSpeakersAndPhrases() {
        val clips=(0 until 12).map { com.example.triviaparty.model.ReactionClip("good-$it.wav","good","speaker-${it%3}","Phrase $it") }
        val picker=com.example.triviaparty.model.AnswerReactionPicker(clips);val random=Random(13)
        var previous:String?=null;var voice:String?=null
        repeat(4) {
            val round=mutableSetOf<String>()
            repeat(12) {
                val next=picker.choose("good",previous,random);assertTrue(round.add(next));assertNotEquals(previous,next)
                val speaker=clips.first {it.file==next}.voice
                // Prefer a different available speaker; do not fake extra voices if only one remains.
                if(clips.filter {it.file !in round || it.file==next}.any {it.voice!=voice}) assertNotEquals(voice,speaker)
                previous=next;voice=speaker
            }
            assertEquals(12,round.size)
        }
    }

    @Test fun privateReactionsVaryFilmsAsWellAsVoicesWithoutRepeatingClips() {
        val catalogue=(0..7).map { com.example.triviaparty.model.ReactionClip("good-$it.wav","good","actor-$it","Distinct line $it",if(it<4) "Film A" else "Film B") }
        val picker=com.example.triviaparty.model.AnswerReactionPicker(catalogue)
        var previous:String?=null;var lastFilm:String?=null
        repeat(3) {
            val drawn=mutableSetOf<String>()
            repeat(8) {
                val file=picker.choose("good",previous,Random(19+it));assertTrue(drawn.add(file))
                val source=catalogue.first {it.file==file}.source
                assertNotEquals(lastFilm,source);lastFilm=source;previous=file
            }
        }
    }

}
