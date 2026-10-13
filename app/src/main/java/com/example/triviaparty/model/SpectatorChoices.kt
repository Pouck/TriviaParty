package com.example.triviaparty.model

/** Keep the topic on reveal; the answer itself supplies the chronology's event list. */
fun Question.revealPrompt(): String {
    val chronologyChoices = this is Question.MultipleChoice &&
        prompt.lineSequence().count { it.trimStart().startsWith("•") } >= 2 &&
        options.isNotEmpty() && options.all { "→" in it }
    if (chronologyChoices) {
        val topic = prompt.substringBefore('\n').substringAfter("pour ", "").trim().removeSuffix("?").trim()
        return if (topic.isNotEmpty()) "Chronologie · $topic" else category
    }
    if (this is Question.Ordering && (category.contains("chronologie", ignoreCase = true) ||
            prompt.contains("plus ancien", ignoreCase = true))) {
        return prompt.substringAfter(": ", category).trim().removeSuffix(".")
    }
    return prompt
}

/** Chronology MC prompts already list the events; spectators need no repeated permutations. */
fun Question.spectatorOptions(): List<String> {
    val choices = when (this) {
    is Question.MultipleChoice -> {
        val listedEvents = prompt.lineSequence().count { it.trimStart().startsWith("•") } >= 2
        if (listedEvents && options.isNotEmpty() && options.all { "→" in it }) emptyList() else options
    }
    is Question.Ordering -> emptyList()
    is Question.SpeedRace -> subQuestion.options
    is Question.Wager -> subQuestion.options
    is Question.MapPin -> options.map { it.label }
    else -> emptyList()
    }
    val bareMapLetters = choices.size == 4 && choices.map { it.trim().uppercase() }.toSet() == setOf("A", "B", "C", "D")
    return if ((this is Question.MultipleChoice || this is Question.MapPin) && bareMapLetters) emptyList() else choices
}
