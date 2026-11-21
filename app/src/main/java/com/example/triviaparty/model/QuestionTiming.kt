package com.example.triviaparty.model

/**
 * Shortest time a question may run. The in-round soundtrack for "Qui suis-je ?" is Anitra's
 * intro (4.125 s) plus the cat theme (9.874 s), about 14 s, the shortest soundtrack in the game.
 * A question timer below that cuts the music off mid-phrase, so packages or questions that
 * specify a shorter time are raised to this floor.
 */
object QuestionTiming {
    const val MIN_QUESTION_SECONDS = 15
}

/** This config with its per-step time raised to [QuestionTiming.MIN_QUESTION_SECONDS] if shorter. */
fun HourglassConfig.withMinimumQuestionTime(): HourglassConfig =
    if (secondsPerFlip >= QuestionTiming.MIN_QUESTION_SECONDS) this
    else copy(secondsPerFlip = QuestionTiming.MIN_QUESTION_SECONDS)
