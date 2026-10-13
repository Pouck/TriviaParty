package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class AmericanHistoryPackagesTest {
    @Test fun packagesImportWithCorrectAnswersAndBalancedPositions() {
        val root = Files.createTempDirectory("american-history-").toFile()
        val expected = mapOf(
            "chronologie" to listOf("Massacre de Boston → Boston Tea Party → Adoption de la Déclaration d’indépendance", "Adoption des Articles de la Confédération → Ratification de la Constitution → Ratification de la Déclaration des droits", "Achat de la Louisiane → Loi sur le déplacement des peuples autochtones → Début de la ruée vers l’or en Californie", "Attaque de Fort Sumter → Bataille de Gettysburg → Reddition de Lee à Appomattox"),
            "politique-et-grandes-figures" to listOf("Thomas Jefferson", "Sacagawea", "Antietam", "Marbury c. Madison"),
            "societe-crises-et-culture" to listOf("Le Chemin de fer clandestin", "La fabrication et la vente de boissons alcoolisées destinées à la consommation", "La convention de Seneca Falls", "La Grande Dépression"))
        val ids = mutableSetOf<String>()
        val json = Json { classDiscriminator = "kind" }
        try {
            expected.forEach { (slug, answers) ->
                val imported = GamePackageImportRepository.importArchive(File("../package-examples/histoire-etats-unis-2026-10-10/histoire-etats-unis-$slug.zip").inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5, game.timingConfig.secondsPerFlip)
                assertEquals(2, game.timingConfig.maxFlips)
                assertEquals(listOf(15,10,5), (0..2).map { game.timingConfig.calculateScore(15,it) })
                val category = json.decodeFromString<CategoryQuestionFile>(File(imported.directory,"question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS, category.answerMode)
                val questions = category.questions.map { it as Question.MultipleChoice }
                assertEquals(answers, questions.map { q ->
                    assertTrue(ids.add(q.id))
                    assertEquals(15, q.basePoints)
                    assertEquals(0, q.penaltyPoints)
                    assertEquals(4, q.options.distinct().size)
                    q.options.forEachIndexed { i,option -> assertTrue(option.startsWith("${"ABCD"[i]} — ")) }
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
                assertEquals(setOf(0,1,2,3), questions.map { it.correctOptionIndex }.toSet())
                if (slug == "chronologie") assertTrue(questions.all { it.spectatorOptions().isEmpty() })
            }
            assertEquals(12,ids.size)
        } finally { root.deleteRecursively() }
    }
}
