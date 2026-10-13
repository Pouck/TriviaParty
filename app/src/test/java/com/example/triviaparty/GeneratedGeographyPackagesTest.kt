package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameServer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class GeneratedGeographyPackagesTest {
    private val json = Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }

    @Test
    fun allSixGeographyArchivesImportWithExpectedQuestionsAndRules() {
        val archives = File("../package-examples/geographie-2026-10-10")
        val counts = mapOf("afrique" to 4, "asie" to 4, "amerique-du-sud" to 2,
            "etats-unis" to 3, "europe" to 4, "capitales" to 9)
        val destination = Files.createTempDirectory("geography-import-").toFile()
        val ids = mutableSetOf<String>()
        try {
            counts.forEach { (region, count) ->
                val filename = if (region == "capitales") "geographie-capitales-v2.zip" else "geographie-$region.zip"
                val zip = File(archives, filename)
                assertTrue("Missing archive: $zip", zip.isFile)
                val imported = GamePackageImportRepository.importArchive(zip.inputStream(), destination)
                val pack = imported.gamePackage
                assertEquals(10, pack.answerTimeSeconds)
                assertEquals(5, pack.timingConfig.secondsPerFlip)
                assertEquals(2, pack.timingConfig.maxFlips)
                assertEquals(5, pack.timingConfig.pointsDecayPerFlip)
                assertEquals(listOf(15, 10, 5), (0..2).map { pack.timingConfig.calculateScore(15, it) })
                val category = json.decodeFromString<CategoryQuestionFile>(
                    File(imported.directory, "question-bank/${pack.categoryPackages.single()}.json").readText())
                assertEquals(count, category.questions.size)
                assertEquals(if (region == "capitales") CategoryAnswerMode.BUZZER else CategoryAnswerMode.SIMULTANEOUS,
                    category.answerMode)
                category.questions.forEach { question ->
                    assertTrue("Duplicate id", ids.add(question.id))
                    assertEquals(15, question.basePoints)
                    assertEquals(0, question.penaltyPoints)
                    assertTrue(File(imported.directory, question.imageUrl!!).isFile)
                    if (region == "capitales") {
                        assertTrue(question is Question.TextAnswer)
                        assertTrue((question as Question.TextAnswer).acceptableAnswers.isNotEmpty())
                    } else {
                        assertTrue(question is Question.MultipleChoice)
                        val choice = question as Question.MultipleChoice
                        assertEquals(listOf("A", "B", "C", "D"), choice.options)
                        assertTrue(choice.correctOptionIndex in 0..3)
                        assertTrue(choice.randomVariants.isNotEmpty())
                        assertEquals(choice.randomVariants.size, choice.randomVariants.map { it.correctOptionIndex }.distinct().size)
                        assertTrue(choice.randomVariants.all { it.correctOptionIndex in 0..3 && it.prompt.isNotBlank() })
                        if (choice.id == "geo-asie-20261010-03") assertFalse(choice.randomVariants.any { it.correctOptionIndex == 2 })
                        if (choice.id == "geo-europe-20261010-04") assertFalse(choice.randomVariants.any { it.correctOptionIndex == 3 })
                        if (choice.id == "geo-europe-20261010-03") assertEquals(listOf(3), choice.randomVariants.map { it.correctOptionIndex })
                        if (choice.id == "geo-amerique-du-sud-20261010-02") assertFalse(choice.randomVariants.any { it.correctOptionIndex == 3 })
                    }
                }
                if (region == "capitales") {
                    val answers = category.questions.map { (it as Question.TextAnswer).acceptableAnswers.first() }
                    assertTrue(answers.containsAll(listOf("Addis-Abeba", "Saint-Marin", "Port-au-Prince")))
                }
            }
            assertEquals(26, ids.size)
        } finally { destination.deleteRecursively() }
    }

    @Test
    @Suppress("UNCHECKED_CAST")
    fun geographyQuestionActuallyExpiresAfterFifteenTimerTicks() {
        val server = GameServer()
        val field = GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible = true }
        val state = field.get(server) as MutableStateFlow<GameSession>
        val tick = GameServer::class.java.getDeclaredMethod("advanceQuestionTimer", HourglassConfig::class.java)
            .apply { isAccessible = true }
        val config = HourglassConfig(secondsPerFlip = 5, maxFlips = 2, pointsDecayPerFlip = 5)
        state.value = GameSession(roomId = "test", state = GameState.QUESTION_ACTIVE,
            timingConfig = config, currentQuestion = Question.MultipleChoice("map-test", "Test",
                "Quelle lettre ?", basePoints = 15, options = listOf("A", "B", "C", "D"), correctOptionIndex = 0))
        for (second in 1..14) {
            assertEquals(true, tick.invoke(server, config))
            assertEquals(GameState.QUESTION_ACTIVE, state.value.state)
            val expected = if (second < 5) 15 else if (second < 10) 10 else 5
            assertEquals(expected, config.calculateScore(15, state.value.currentFlipNumber))
        }
        assertEquals(false, tick.invoke(server, config))
        assertEquals(GameState.REVEAL_ANSWER, state.value.state)
    }
}
