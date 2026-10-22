package com.example.triviaparty

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.model.*
import kotlin.random.Random
import org.junit.Assert.*
import org.junit.Test

class GameEndingSoundsTest {
    @Test fun randomRotationUsesEveryEndingAndDoesNotRepeatAtCycleBoundaries() {
        val picker = GameEndingSoundPicker()
        val random = Random(17)
        val choices = List(70) { picker.choose(random) }
        choices.chunked(7).forEach { assertEquals(GameEndingSounds.files.toSet(), it.toSet()) }
        assertTrue(choices.zipWithNext().all { (a, b) -> a != b })
    }

    @Test fun chosenMusicStaysWithTheGameAndIsSentToEveryWinnerScreen() {
        val clip = GameEndingSoundPicker().choose(Random(3))
        val game = GameSession(roomId = "room", gameEndSoundClip = clip)
        for (phase in GameState.entries) {
            val tv = TvState.from(game.copy(state = phase))
            assertEquals(clip, tv.gameEndSoundClip)
            assertTrue(tv.encode().contains("\"gameEndSoundClip\":\"$clip\""))
        }
        assertTrue(GameEndingSounds.files.all { AnswerReactions.isAllowed(it) })
        assertFalse(AnswerReactions.isAllowed("game-end-unknown.mp3"))
        assertFalse(AnswerReactions.isAllowed("../game-end-aida.mp3"))
    }
}
