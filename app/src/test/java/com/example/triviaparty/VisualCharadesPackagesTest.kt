package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.CategoryAnswerMode
import com.example.triviaparty.model.CategoryQuestionFile
import com.example.triviaparty.model.Question
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class VisualCharadesPackagesTest {
    @Test fun allVisualCharadesImportWithShortRoundsAndBothAnswerModes() {
        val archives = File("../game-library/current").listFiles { f -> f.name.startsWith("charades-visuelles-") && f.extension == "zip" }.orEmpty()
        assertEquals(17, archives.size)
        val root = Files.createTempDirectory("visual-charades").toFile()
        val json = Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }
        val ids = mutableSetOf<String>()
        var buzzer = 0
        var written = 0
        try {
            archives.forEach { archive ->
                val imported = GamePackageImportRepository.importArchive(archive.inputStream(), root, enforceQuestionCount = true)
                val game = imported.gamePackage
                assertEquals(45, game.timingConfig.secondsPerFlip * (game.timingConfig.maxFlips + 1))
                val bank = json.decodeFromString<CategoryQuestionFile>(File(imported.directory, "question-bank/${game.id}.json").readText())
                when (bank.answerMode) {
                    CategoryAnswerMode.BUZZER -> buzzer++
                    CategoryAnswerMode.WRITTEN -> written++
                    else -> fail("Expected buzzer or written")
                }
                assertTrue(bank.questions.size in 5..7)
                bank.questions.forEach { question ->
                    assertTrue(ids.add(question.id))
                    assertTrue(question is Question.TextAnswer)
                    val q = question as Question.TextAnswer
                    assertTrue(q.acceptableAnswers.isNotEmpty())
                    assertTrue(q.acceptableAnswers.all { it.isNotBlank() })
                    assertTrue(q.imageUrl!!.matches(Regex("images/charade-[0-9]{2}\\.png")))
                    assertTrue(File(imported.directory, q.imageUrl!!).isFile)
                    assertEquals(bank.category, q.category)
                }
            }
            assertEquals(105, ids.size)
            assertEquals(9, buzzer)
            assertEquals(8, written)
        } finally { root.deleteRecursively() }
    }
}
