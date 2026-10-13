package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class RiverPackageTest {
    @Test
    fun islandsDesertsAndWaterArchivesImportWithFourQuestionsEach() {
        val root = Files.createTempDirectory("geography-sets-").toFile()
        val expected = mapOf(
            "iles-et-archipels" to listOf("B — Honshu", "C — Oahu", "C — Sri Lanka", "B — Sicile"),
            "deserts-et-paysages-arides" to listOf("B — Désert des Mojaves", "B — Désert d’Atacama", "B — Désert de Gobi", "B — Désert d’Arabie"),
            "lacs-mers-et-golfes" to listOf("B — Mer du Nord", "B — Lac Victoria", "B — Mer Caspienne", "B — Lac Michigan"))
        val json = Json { classDiscriminator = "kind" }
        val questionIds = mutableSetOf<String>()
        try {
            expected.forEach { (slug, answers) ->
                val archive = File("../package-examples/geographie-2026-10-10/geographie-$slug.zip")
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5, game.timingConfig.secondsPerFlip)
                assertEquals(2, game.timingConfig.maxFlips)
                assertEquals(listOf(15, 10, 5), (0..2).map { game.timingConfig.calculateScore(15, it) })
                val category = json.decodeFromString<CategoryQuestionFile>(
                    File(imported.directory, "question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                assertEquals(4, category.questions.size)
                assertVariedPositions(category)
                assertEquals(answers.map { it.substringAfter(" — ") }, category.questions.map {
                    val q = it as Question.MultipleChoice
                    assertTrue(questionIds.add(q.id))
                    assertEquals(15, q.basePoints)
                    assertEquals(0, q.penaltyPoints)
                    assertEquals(4, q.options.size)
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
            }
        } finally { root.deleteRecursively() }
    }

    @Test
    fun bothFrenchMountainPackagesImportWithTheirSixAnswers() {
        val root = Files.createTempDirectory("mountain-packages-").toFile()
        val expected = mapOf(
            "sommets-et-volcans" to listOf("B — Mont Fuji", "C — Vésuve", "B — Montagne de la Table", "B — Tupungato", "C — Mont Rainier", "B — Corcovado"),
            "chaines-de-montagnes" to listOf("B — Apennins", "C — Pyrénées", "B — Oural", "C — Montagnes Rocheuses", "A — Andes", "B — Alpes"))
        val json = Json { classDiscriminator = "kind" }
        try {
            expected.forEach { (slug, answers) ->
                val archive = File("../package-examples/geographie-2026-10-10/geographie-$slug.zip")
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5, game.timingConfig.secondsPerFlip)
                assertEquals(2, game.timingConfig.maxFlips)
                assertEquals(listOf(15, 10, 5), (0..2).map { game.timingConfig.calculateScore(15, it) })
                val category = json.decodeFromString<CategoryQuestionFile>(
                    File(imported.directory, "question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                assertEquals(6, category.questions.size)
                assertVariedPositions(category)
                assertEquals(answers.map { it.substringAfter(" — ") }, category.questions.map {
                    val q = it as Question.MultipleChoice
                    assertEquals(15, q.basePoints)
                    assertEquals(0, q.penaltyPoints)
                    assertEquals(4, q.options.size)
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
            }
        } finally { root.deleteRecursively() }
    }

    @Test
    fun frenchRiverArchiveImportsWithAllTwelveAnswersAndGeographyRules() {
        val root = Files.createTempDirectory("river-package-").toFile()
        try {
            val archive = File("../package-examples/geographie-2026-10-10/geographie-fleuves-et-rivieres.zip")
            val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
            val game = imported.gamePackage
            assertEquals(5, game.timingConfig.secondsPerFlip)
            assertEquals(2, game.timingConfig.maxFlips)
            assertEquals(listOf(15, 10, 5), (0..2).map { game.timingConfig.calculateScore(15, it) })
            val category = Json { classDiscriminator = "kind" }.decodeFromString<CategoryQuestionFile>(
                File(imported.directory, "question-bank/${game.categoryPackages.single()}.json").readText())
            assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
            assertEquals(12, category.questions.size)
            val answers = category.questions.map {
                val question = it as Question.MultipleChoice
                assertEquals(15, question.basePoints)
                assertEquals(0, question.penaltyPoints)
                assertEquals(4, question.options.size)
                assertNull(question.imageUrl)
                question.options[question.correctOptionIndex].substringAfter(" — ")
            }
            assertEquals(listOf("Tigre", "Nil", "Seine", "Tibre", "Tamise", "Danube",
                "Neva", "Liffey", "Swan", "Huangpu", "Tage", "Congo"), answers)
            assertVariedPositions(category)
        } finally { root.deleteRecursively() }
    }

    private fun assertVariedPositions(category: CategoryQuestionFile) {
        val questions = category.questions.map { it as Question.MultipleChoice }
        val counts = (0..3).map { index -> questions.count { it.correctOptionIndex == index } }
        assertTrue(counts.all { it > 0 })
        assertTrue(counts.max() - counts.min() <= 1)
        questions.forEach { q ->
            q.options.forEachIndexed { index, option -> assertTrue(option.startsWith("${"ABCD"[index]} — ")) }
        }
    }
}
