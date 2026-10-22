package com.example.triviaparty.model

import kotlin.random.Random

/** The host selects one 24-second ending for the entire game, shared by every TV. */
object GameEndingSounds {
    val files = listOf("zarathustra", "te-deum", "fireworks", "aida", "pomp", "kiev", "william-tell")
        .map { "game-end-$it.mp3" }
}

/** Play every ending before repeating; never repeat the previous game's ending. */
class GameEndingSoundPicker {
    private val remaining = mutableListOf<String>()
    private var previous: String? = null

    fun choose(random: Random = Random.Default): String {
        if (remaining.isEmpty()) remaining.addAll(GameEndingSounds.files.shuffled(random))
        val choices = remaining.filter { it != previous }.ifEmpty { remaining.toList() }
        val chosen = choices.random(random)
        remaining.remove(chosen)
        previous = chosen
        return chosen
    }
}
