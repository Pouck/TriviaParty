package com.example.triviaparty

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class MoviePackagesTest {
    @Test fun allTenCinemaPackagesImportWithCorrectFormatsTimingAndRevealPrivacy() {
        val archives = File("../package-examples/cinema-2026-10-11").listFiles { f -> f.extension == "zip" }.orEmpty()
        assertEquals(10, archives.size)
        val directory = Files.createTempDirectory("movie-packages-").toFile()
        val ids = mutableSetOf<String>()
        val modes = mutableMapOf<String, Int>()
        val json = Json { classDiscriminator = "kind" }
        try {
            archives.forEach { archive ->
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), directory)
                val game = imported.gamePackage
                val category = json.decodeFromString<CategoryQuestionFile>(
                    File(imported.directory, "question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals("Cinéma", category.subject)
                assertEquals(10, game.answerTimeSeconds)
                assertTrue(category.questions.size in 5..10)
                val mode = when {
                    "-chronologie-" in game.id -> "chronologie"
                    "-qsj-" in game.id -> "qsj"
                    "-buzzer-" in game.id -> "buzzer"
                    else -> "qcm"
                }
                modes[mode] = modes.getOrDefault(mode, 0) + 1
                assertEquals(if (mode == "qsj") 20 else if (mode == "chronologie") 10 else 5, game.timingConfig.secondsPerFlip)
                assertEquals(if (mode == "qsj") CategoryAnswerMode.BUZZER else if (mode == "buzzer") CategoryAnswerMode.BUZZER else CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                assertEquals(if (mode == "qsj") listOf(20,15,10,5) else listOf(15,10,5),
                    (0..game.timingConfig.maxFlips).map { game.timingConfig.calculateScore(if (mode == "qsj") 20 else 15, it) })
                category.questions.forEach { q ->
                    assertTrue(ids.add(q.id))
                    assertEquals(category.category, q.category)
                    assertNull(q.imageUrl)
                    assertEquals(if (mode == "qsj") 5 else 0, q.penaltyPoints)
                    if (q is Question.GuessWho) {
                        assertEquals(4, q.clues.distinct().size)
                        assertTrue(q.acceptableAnswers.all { it.isNotBlank() })
                    }
                    if (q is Question.MultipleChoice) {
                        assertEquals(4, q.options.distinct().size)
                        assertEquals(mode == "chronologie", q.isChronologyQuestion())
                        assertTrue(q.correctOptionIndex in 0..3)
                        if (mode == "chronologie") {
                            val displayed = q.prompt.lines().drop(1).map { it.removePrefix("• ") }
                            val ordered = q.options[q.correctOptionIndex].substringAfter(" — ").split(" → ")
                            assertEquals(3, displayed.distinct().size)
                            assertEquals(displayed.toSet(), ordered.toSet())
                            assertNotEquals(displayed, ordered)
                        }
                    }
                    val active = GameSession("1234", state=GameState.QUESTION_ACTIVE, currentQuestion=q,
                        timingConfig=game.timingConfig, currentCategoryAnswerMode=category.answerMode)
                    val tv = TvState.from(active)
                    assertNull(tv.question!!.answer)
                    if (mode == "chronologie") assertTrue(tv.question.options.isEmpty())
                    assertNotNull(TvState.from(active.copy(state=GameState.REVEAL_ANSWER)).question!!.answer)
                }
                val choices = category.questions.filterIsInstance<Question.MultipleChoice>()
                if (choices.isNotEmpty()) {
                    val positions = (0..3).map { p -> choices.count { it.correctOptionIndex == p } }.sorted()
                    assertEquals(if (mode == "qcm") listOf(2,2,2,2) else listOf(1,1,2,2), positions)
                }
            }
            assertEquals(70, ids.size)
            assertEquals(mapOf("qcm" to 3, "buzzer" to 3, "qsj" to 2, "chronologie" to 2), modes)
        } finally { directory.deleteRecursively() }
    }
}
