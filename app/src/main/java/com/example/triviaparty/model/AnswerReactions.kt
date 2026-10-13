package com.example.triviaparty.model

import kotlin.random.Random

/** Recorded clips, shared by the local TV page and Cast receiver. */
object AnswerReactions {
    fun clips(outcome: String): List<String> = when(outcome) {
        "good" -> (1..26).map { n -> "good-" + n.toString().padStart(2,'0') + ".wav" }
        "bad" -> (1..20).map { n -> "bad-" + n.toString().padStart(2,'0') + ".wav" }
        else -> emptyList()
    }
    fun isAllowed(file: String?): Boolean = file in clips("good") + clips("bad") + listOf("good.wav","bad.wav","buzzer.wav","enabled.wav","good-ping.wav","bad-ping.wav","game-end.wav","good-02.mp3","good-26.mp3","bad-04.mp3","bad-14.mp3")
    fun choose(outcome: String, previous: String?, random: Random = Random.Default): String {
        val candidates=clips(outcome).filter { it!=previous }
        require(candidates.isNotEmpty())
        return candidates[random.nextInt(candidates.size)]
    }
}
