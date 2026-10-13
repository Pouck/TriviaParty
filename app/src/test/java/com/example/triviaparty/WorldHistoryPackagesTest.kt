package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class WorldHistoryPackagesTest {
    @Test fun archivesImportWithCorrectAnswersAndTiming() {
        val root = Files.createTempDirectory("world-history-").toFile()
        val expected = mapOf(
            "chronologie-1" to listOf("Bataille de Waterloo → Restauration de Meiji → Proclamation de l’Empire allemand", "Naufrage du Titanic → Début de la Première Guerre mondiale → Abdication de Nicolas II", "Lancement de Spoutnik 1 → Début de la construction du mur de Berlin → Crise des missiles de Cuba", "Chute du mur de Berlin → Libération de Nelson Mandela → Dissolution de l’Union soviétique"),
            "xixe-empires-et-industrie" to listOf("Le congrès de Vienne", "L’Inde", "Le canal de Suez", "Fixer des règles entre puissances pour l’expansion coloniale en Afrique"),
            "xxe-conflits-et-transformations" to listOf("La Société des Nations", "Le projet Manhattan", "La partition de l’Inde", "Lech Wałęsa"),
            "chronologie-2" to listOf("Campagne de Russie de Napoléon → Convention de Seneca Falls → Publication de L’Origine des espèces", "Ouverture du central téléphonique commercial de New Haven → Premier vol motorisé et contrôlé des frères Wright → Pandémie de grippe dite « espagnole »", "Attaque de Pearl Harbor → Début de la bataille de Stalingrad → Adoption de la Déclaration universelle des droits de l’homme", "Premier alunissage humain, avec Apollo 11 → Chute de la monarchie en Iran → Catastrophe nucléaire de Tchernobyl"),
            "xixe-revoltes-et-unifications" to listOf("Les guerres de l’opium", "Matthew Perry", "La révolte des Taiping", "Giuseppe Garibaldi"),
            "xxe-guerres-et-reformes" to listOf("La bataille de Verdun", "Le plan Marshall", "Iouri Gagarine", "La glasnost"))
        val ids = mutableSetOf<String>()
        val json = Json { classDiscriminator = "kind" }
        try {
            expected.forEach { (slug, answers) ->
                val imported = GamePackageImportRepository.importArchive(File("../package-examples/histoire-mondiale-2026-10-10/histoire-mondiale-$slug.zip").inputStream(), root)
                val game = imported.gamePackage
                assertEquals(5,game.timingConfig.secondsPerFlip)
                assertEquals(2,game.timingConfig.maxFlips)
                assertEquals(listOf(15,10,5),(0..2).map { game.timingConfig.calculateScore(15,it) })
                val category = json.decodeFromString<CategoryQuestionFile>(File(imported.directory,"question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(CategoryAnswerMode.SIMULTANEOUS,category.answerMode)
                val questions = category.questions.map { it as Question.MultipleChoice }
                assertEquals(answers,questions.map { q ->
                    assertTrue(ids.add(q.id))
                    assertEquals(15,q.basePoints)
                    assertEquals(0,q.penaltyPoints)
                    assertEquals(4,q.options.distinct().size)
                    q.options.forEachIndexed { i,o -> assertTrue(o.startsWith("${"ABCD"[i]} — ")) }
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
                assertEquals(setOf(0,1,2,3),questions.map { it.correctOptionIndex }.toSet())
                if (slug.startsWith("chronologie")) assertTrue(questions.all { it.spectatorOptions().isEmpty() })
            }
            assertEquals(24,ids.size)
        } finally { root.deleteRecursively() }
    }
}
