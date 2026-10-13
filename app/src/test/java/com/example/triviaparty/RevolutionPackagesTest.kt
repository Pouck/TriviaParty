package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class RevolutionPackagesTest {
    @Test fun threePackagesImportWithReviewedAnswersAndScoring() {
        val root = Files.createTempDirectory("revolution-packages-").toFile()
        val expected = mapOf(
            "chronologie" to listOf("Serment du Jeu de paume → Prise de la Bastille → Marche des femmes sur Versailles", "Fuite à Varennes → Abolition de la royauté → Exécution de Louis XVI", "Marie-Antoinette → Danton → Robespierre", "Mise en place du Directoire → Coup d’État du 18 Brumaire → Sacre de Napoléon"),
            "politique-et-personnages" to listOf("Les paysans, les artisans et les bourgeois non nobles", "Le club des Jacobins", "Charlotte Corday", "Le Comité de salut public"),
            "culture-et-mobilisation" to listOf("Des pantalons courts s’arrêtant au genou", "10 jours", "La Marseillaise", "La mobilisation de la population pour soutenir l’effort de guerre"))
        val ids = mutableSetOf<String>()
        val json = Json { classDiscriminator = "kind" }
        try {
            expected.forEach { (slug, answers) ->
                val archive = File("../package-examples/revolution-francaise-2026-10-10/revolution-francaise-$slug.zip")
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5, game.timingConfig.secondsPerFlip)
                assertEquals(2, game.timingConfig.maxFlips)
                assertEquals(listOf(15, 10, 5), (0..2).map { game.timingConfig.calculateScore(15, it) })
                val category = json.decodeFromString<CategoryQuestionFile>(File(imported.directory,"question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                val questions = category.questions.map { it as Question.MultipleChoice }
                assertEquals(answers, questions.map { q ->
                    assertTrue(ids.add(q.id))
                    assertEquals(15, q.basePoints)
                    assertEquals(0, q.penaltyPoints)
                    assertEquals(4, q.options.distinct().size)
                    q.options.forEachIndexed { i, option -> assertTrue(option.startsWith("${"ABCD"[i]} — ")) }
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
                assertEquals(setOf(0,1,2,3), questions.map { it.correctOptionIndex }.toSet())
                if (slug == "chronologie") assertTrue(questions.all { it.spectatorOptions().isEmpty() })
            }
            assertEquals(12, ids.size)
        } finally { root.deleteRecursively() }
    }
}
