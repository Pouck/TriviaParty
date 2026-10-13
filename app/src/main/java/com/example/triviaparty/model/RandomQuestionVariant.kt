package com.example.triviaparty.model

import kotlin.random.Random

/** Select once when a question starts; keep the chosen prompt and answer throughout the round. */
fun Question.withRandomVariant(random: Random = Random.Default): Question {
    if (this !is Question.MultipleChoice || randomVariants.isEmpty()) return this
    val variant = randomVariants.random(random)
    return copy(prompt = variant.prompt, correctOptionIndex = variant.correctOptionIndex,
        randomVariants = emptyList())
}
