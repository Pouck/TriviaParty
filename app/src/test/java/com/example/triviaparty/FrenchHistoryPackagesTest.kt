package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class FrenchHistoryPackagesTest {
    @Test fun fivePackagesImportWithReviewedAnswersAndBalancedChoices() {
        val root = Files.createTempDirectory("french-history-").toFile()
        val expected = mapOf(
            "moyen-age-reperes" to listOf("Gaule", "Carcassonne", "Gothique", "La Sorbonne", "Une épée pouvant être maniée à une ou deux mains", "La Loire"),
            "moyen-age-vie-quotidienne" to listOf("Des animaux", "La peste noire", "Les lois somptuaires", "Le palais de la Cité", "Les communautés de métiers", "La dîme"),
            "renaissance-chronologie" to listOf("François Ier → Arrivée de Léonard → Chambord", "Gargantua → Villers-Cotterêts → Défense et illustration", "Wassy → Amboise → Saint-Barthélemy", "Marignan → Assassinat d’Henri III → Édit de Nantes"),
            "renaissance-rois-et-arts" to listOf("Léonard de Vinci", "Catherine de Médicis", "Chenonceau", "Le Louvre"),
            "renaissance-lettres-et-savoirs" to listOf("Ambroise Paré", "Michel de Montaigne", "L’emploi du français dans les actes judiciaires à la place du latin", "La vénalité des offices"))
        val ids = mutableSetOf<String>()
        val counts = IntArray(4)
        try {
            expected.forEach { (slug, answers) ->
                val archive = File("../package-examples/histoire-france-2026-10-10/histoire-france-$slug.zip")
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5, game.timingConfig.secondsPerFlip)
                assertEquals(2, game.timingConfig.maxFlips)
                assertEquals(listOf(15, 10, 5), (0..2).map { game.timingConfig.calculateScore(15, it) })
                val category = Json { classDiscriminator = "kind" }.decodeFromString<CategoryQuestionFile>(File(imported.directory, "question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                assertEquals(answers, category.questions.map { question ->
                    val q = question as Question.MultipleChoice
                    assertTrue(ids.add(q.id))
                    assertEquals(15, q.basePoints)
                    assertEquals(0, q.penaltyPoints)
                    assertEquals(4, q.options.distinct().size)
                    q.options.forEachIndexed { i, option -> assertTrue(option.startsWith("${"ABCD"[i]} — ")) }
                    counts[q.correctOptionIndex]++
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
            }
            assertEquals(24, ids.size)
            assertEquals(listOf(6, 6, 6, 6), counts.toList())
        } finally { root.deleteRecursively() }
    }
}
