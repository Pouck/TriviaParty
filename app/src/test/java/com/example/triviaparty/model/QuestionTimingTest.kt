package com.example.triviaparty.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertSame
import org.junit.Test

class QuestionTimingTest {
    @Test
    fun shorterTimesAreRaisedToTheFloor() {
        listOf(1, 5, 10, 14).forEach { seconds ->
            assertEquals(QuestionTiming.MIN_QUESTION_SECONDS, HourglassConfig(secondsPerFlip = seconds).withMinimumQuestionTime().secondsPerFlip)
        }
    }

    @Test
    fun timesAtOrAboveTheFloorAreUntouched() {
        val config = HourglassConfig(secondsPerFlip = QuestionTiming.MIN_QUESTION_SECONDS)
        assertSame(config, config.withMinimumQuestionTime())
        assertEquals(20, HourglassConfig(secondsPerFlip = 20).withMinimumQuestionTime().secondsPerFlip)
    }

    @Test
    fun onlyTheTimeChanges() {
        val original = HourglassConfig(secondsPerFlip = 5, maxFlips = 3, pointsDecayPerFlip = 4)
        val raised = original.withMinimumQuestionTime()
        assertEquals(original.copy(secondsPerFlip = QuestionTiming.MIN_QUESTION_SECONDS), raised)
    }

    @Test
    fun floorCoversTheShortestSoundtrack() {
        // Anitra's intro (4.125 s) + cat theme (9.874 s) is the shortest in-round soundtrack.
        assert(QuestionTiming.MIN_QUESTION_SECONDS >= 4.125 + 9.874)
    }
}
