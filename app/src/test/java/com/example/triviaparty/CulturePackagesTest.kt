package com.example.triviaparty

import com.example.triviaparty.cast.TvState
import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class CulturePackagesTest {
    @Test fun allNineteenArchivesImportWithReviewedAnswersAndProgressiveTiming() {
        val expectedClues = mapOf(
            "grece-figures-et-lieux" to listOf("Platon","Delphes","Alexandre le Grand","L’Acropole d’Athènes"),
            "grece-grandes-figures" to listOf("Thucydide","Hippocrate","Diogène de Sinope","Solon"),
            "rome-personnages" to listOf("Crassus","Marius","Caton le Jeune","Antonin le Pieux"),
            "rome-monuments-et-crises" to listOf("La colonne Trajane","Les réformes des Gracques","Le Panthéon de Rome","L’année des quatre empereurs"),
            "mythologie-grecque-dieux-et-mortels" to listOf("Dionysos","Dédale"),
            "mythologie-grecque-monstres-et-objets" to listOf("Méduse","Le bouclier d’Achille"),
            "mythologie-romaine-divinites" to listOf("Janus","Mars"),
            "mythologie-romaine-fondations" to listOf("Énée","Romulus et Rémus"),
            "litterature-francaise-oeuvres" to listOf("Les Misérables","Le Petit Prince"),
            "litterature-francaise-personnages" to listOf("Edmond Dantès","Emma Bovary"),
            "litterature-anglophone-oeuvres" to listOf("Frankenstein","Animal Farm"),
            "litterature-anglophone-personnages" to listOf("Miss Havisham","Elizabeth Bennet"),
            "litterature-americaine-oeuvres" to listOf("Moby-Dick","The Great Gatsby"),
            "litterature-americaine-personnages" to listOf("Atticus Finch","Holden Caulfield"))
        val expectedChoices = mapOf(
            "francaise-oeuvres" to listOf("Notre-Dame de Paris","La mort de sa mère","À la recherche du temps perdu","La Reine Margot","Le palais Garnier","Le Rouge et le Noir","Les mines de charbon","Candide","La Comédie humaine","La philosophie féministe"),
            "francaise-personnages" to listOf("D’Artagnan","Mathilde Loisel","Le vol d’un pain pour nourrir la famille de sa sœur","Erik","Tartuffe","Le renard","Eugène de Rastignac","Charles Bovary","Bernard Rieux","Roland"),
            "anglophone-oeuvres" to listOf("Londres et Paris","Wuthering Heights","Les Carpates","Lord of the Flies","Une réception en soirée","Paradise Lost","Le pôle Nord","Brave New World","Persuasion","The Canterbury Tales"),
            "anglophone-personnages" to listOf("Sherlock Holmes","Edward Rochester","Hamlet","Emma Woodhouse","Ebenezer Scrooge","La créature","Frodon Sacquet","Dorian Gray","Winston Smith","Alice"),
            "americaine-oeuvres" to listOf("Les puritains du Massachusetts au XVIIe siècle","The Grapes of Wrath","Brûler les livres interdits et les maisons qui en abritent","Beloved","Catch-22","New York","Walden","Un grand marlin","The Sound and the Fury","Le maccarthysme et la chasse aux communistes"))
        val root = Files.createTempDirectory("culture-packages-").toFile()
        val ids = mutableSetOf<String>()
        val json = Json { classDiscriminator = "kind" }
        val positions = mutableMapOf<Int,Int>()
        fun load(mode: String,slug: String): Pair<GamePackage,CategoryQuestionFile> {
            val imported = GamePackageImportRepository.importArchive(File("../package-examples/culture-2026-10-10/culture-$mode-$slug.zip").inputStream(),root)
            val game = imported.gamePackage
            assertEquals(10,game.answerTimeSeconds)
            assertEquals(if (mode=="qsj") 20 else 5,game.timingConfig.secondsPerFlip)
            val category = json.decodeFromString<CategoryQuestionFile>(File(imported.directory,"question-bank/${game.categoryPackages.single()}.json").readText())
            category.questions.forEach { assertTrue(ids.add(it.id)); assertEquals(if (mode=="qsj") 5 else 0,it.penaltyPoints) }
            return game to category
        }
        try {
            expectedClues.forEach { (slug,answers) ->
                val (game,category) = load("qsj",slug)
                assertEquals(CategoryAnswerMode.BUZZER,category.answerMode)
                assertEquals(3,game.timingConfig.maxFlips)
                assertEquals(listOf(20,15,10,5),(0..3).map { game.timingConfig.calculateScore(20,it) })
                val questions = category.questions.map { it as Question.GuessWho }
                assertEquals(answers,questions.map { it.acceptableAnswers.single() })
                questions.forEach { q ->
                    assertEquals(20,q.basePoints)
                    assertEquals(4,q.clues.distinct().size)
                    assertTrue(q.clues.all { it.isNotBlank() })
                    for (flip in 0..3) {
                        val tv = TvState.from(GameSession("1234",state=GameState.QUESTION_ACTIVE,currentQuestion=q,currentFlipNumber=flip,timingConfig=game.timingConfig,currentCategoryAnswerMode=CategoryAnswerMode.BUZZER))
                        q.clues.forEachIndexed { i,clue -> assertEquals(i<=flip,tv.question!!.prompt.contains(clue)) }
                        assertNull(tv.question!!.answer)
                        assertEquals(listOf(20,15,10,5)[flip],tv.points)
                    }
                }
            }
            expectedChoices.forEach { (slug,answers) ->
                val (game,category) = load("qcm",slug)
                assertEquals(CategoryAnswerMode.SIMULTANEOUS,category.answerMode)
                assertEquals(2,game.timingConfig.maxFlips)
                assertEquals(listOf(15,10,5),(0..2).map { game.timingConfig.calculateScore(15,it) })
                val questions = category.questions.map { it as Question.MultipleChoice }
                assertEquals(answers,questions.map { q ->
                    assertEquals(15,q.basePoints)
                    assertEquals(4,q.options.distinct().size)
                    q.options.forEachIndexed { i,o -> assertTrue(o.startsWith("${"ABCD"[i]} — ")) }
                    positions[q.correctOptionIndex] = positions.getOrDefault(q.correctOptionIndex,0)+1
                    q.options[q.correctOptionIndex].substringAfter(" — ")
                })
                assertEquals(listOf(2,2,3,3),questions.groupingBy { it.correctOptionIndex }.eachCount().values.sorted())
            }
            assertEquals(86,ids.size)
            assertEquals(mapOf(0 to 13,1 to 13,2 to 12,3 to 12),positions)
        } finally { root.deleteRecursively() }
    }
}
