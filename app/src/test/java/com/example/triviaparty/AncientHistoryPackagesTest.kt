package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class AncientHistoryPackagesTest {
    @Test fun greekAndRomanPackagesImportWithCorrectChronologies() {
        val root = Files.createTempDirectory("ancient-history-").toFile()
        val expected = mapOf(
            "grece-antique" to listOf("Premiers Jeux olympiques antiques traditionnellement datés", "Bataille de Marathon", "Début de l’épidémie dite « peste d’Athènes »", "Naissance de Socrate", "Traversée de l’Hellespont vers l’Asie"),
            "rome-antique" to listOf("Jules César franchit le Rubicon", "Hannibal traverse les Alpes", "Grand incendie de Rome sous Néron", "Mise en place de la tétrarchie par Dioclétien", "Sac de Rome par les Wisigoths d’Alaric"))
        val ids = mutableSetOf<String>()
        val json = Json { classDiscriminator = "kind" }
        try {
            expected.forEach { (slug, answers) ->
                val archive = File("../package-examples/histoire-antique-2026-10-10/histoire-chronologie-$slug.zip")
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5, game.timingConfig.secondsPerFlip)
                assertEquals(2, game.timingConfig.maxFlips)
                assertEquals(listOf(15, 10, 5), (0..2).map { game.timingConfig.calculateScore(15, it) })
                val category = json.decodeFromString<CategoryQuestionFile>(File(imported.directory, "question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                val questions = category.questions.map { it as Question.MultipleChoice }
                assertEquals(answers, questions.map { q ->
                    assertTrue(ids.add(q.id))
                    assertEquals(15, q.basePoints)
                    assertEquals(0, q.penaltyPoints)
                    assertEquals(4,q.options.distinct().size)
                    assertTrue(q.spectatorOptions().isEmpty())
                    q.options[q.correctOptionIndex].substringAfter(" — ").substringBefore(" → ")
                })
                assertEquals(listOf("Choix multiples"), category.questionTypes)
            }
            assertEquals(10, ids.size)
        } finally { root.deleteRecursively() }
    }
}
