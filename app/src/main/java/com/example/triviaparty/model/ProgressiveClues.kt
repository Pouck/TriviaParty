package com.example.triviaparty.model

/** Oral questions use the host's judgment and the existing buzzer answer timer. */
fun Question.isOralBuzzerQuestion(): Boolean = this is Question.TextAnswer || this is Question.GuessWho

/** First clue immediately; each completed scoring segment adds one, retaining earlier clues. */
fun Question.activePrompt(flipNumber: Int): String {
    if (this !is Question.GuessWho) return prompt
    val visible = clues.take(flipNumber.coerceIn(0, clues.lastIndex) + 1)
    return prompt + "\n\n" + visible.mapIndexed { index, clue -> "${index + 1}. $clue" }.joinToString("\n")
}
