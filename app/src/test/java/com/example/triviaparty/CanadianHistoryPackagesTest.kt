package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class CanadianHistoryPackagesTest {
    @Test fun bothTimelinePackagesImportWithCorrectChronologies() {
        val root = Files.createTempDirectory("canadian-history-").toFile()
        val expected = mapOf(
            "facile" to listOf("Cabot → Cartier → Champlain", "Déportation des Acadiens → Plaines d’Abraham → Traité de Paris", "Rébellions → Charlottetown → Confédération", "Rivière-Rouge → Dernier crampon → Or au Klondike", "Citoyenneté canadienne → Drapeau à la feuille d’érable → Rapatriement"),
            "moins-facile" to listOf("Alberta et Saskatchewan → Empress of Ireland → Vimy", "Hong Kong → Dieppe → Juno Beach", "Terre-Neuve → Voie maritime → Expo 67", "Crise d’Octobre → Attentat d’Air India → Crise d’Oka", "Échec de Meech → Référendum québécois → Nunavut"))
        val ids = mutableSetOf<String>()
        try {
            expected.forEach { (slug, answers) ->
                val archive = File("../package-examples/histoire-canada-2026-10-10/histoire-canada-chronologie-$slug.zip")
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5, game.timingConfig.secondsPerFlip)
                assertEquals(2, game.timingConfig.maxFlips)
                assertEquals(listOf(15, 10, 5), (0..2).map { game.timingConfig.calculateScore(15, it) })
                val category = Json { classDiscriminator = "kind" }.decodeFromString<CategoryQuestionFile>(
                    File(imported.directory, "question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                assertEquals(5, category.questions.size)
                val questions = category.questions.map { it as Question.MultipleChoice }
                assertEquals(answers, questions.map { q ->
                    assertTrue(ids.add(q.id))
                    assertEquals(15, q.basePoints)
                    assertEquals(0, q.penaltyPoints)
                    assertEquals(4, q.options.distinct().size)
                    q.options.forEachIndexed { i, option -> assertTrue(option.startsWith("${"ABCD"[i]} — ")) }
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
                val counts = (0..3).map { position -> questions.count { it.correctOptionIndex == position } }
                assertEquals(listOf(1, 1, 1, 2), counts.sorted())
            }
            assertEquals(10, ids.size)
        } finally { root.deleteRecursively() }
    }
}
