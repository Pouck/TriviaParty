package com.example.triviaparty.data

import kotlinx.serialization.builtins.MapSerializer
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.json.Json
import java.io.File
import kotlin.random.Random

/**
 * How many times each question has been played across games, so new games prefer questions
 * that were seen least. Stored as a small JSON file next to the app's other host data; with
 * no file (unit tests) it is simply empty and ordering is purely random.
 */
class QuestionPlayHistory(private val file: File? = null) {
    private val counts = mutableMapOf<String, Int>()
    private val serializer = MapSerializer(String.serializer(), Int.serializer())

    init {
        runCatching {
            if (file?.isFile == true) counts.putAll(Json.decodeFromString(serializer, file.readText(Charsets.UTF_8)))
        }
    }

    @Synchronized fun count(questionId: String): Int = counts[questionId] ?: 0

    @Synchronized fun record(questionId: String) {
        counts[questionId] = (counts[questionId] ?: 0) + 1
        runCatching { file?.writeText(Json.encodeToString(serializer, counts), Charsets.UTF_8) }
    }
}

/**
 * Play order for one category in one game: shuffled with [seed] (stable for the whole game, so
 * repeated calls agree), then stably sorted so the least-played questions come first.
 */
fun <T> orderForPlay(items: List<T>, seed: Long, playCount: (T) -> Int): List<T> =
    items.shuffled(Random(seed)).sortedBy(playCount)
