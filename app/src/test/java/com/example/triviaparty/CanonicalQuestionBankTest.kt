package com.example.triviaparty

import com.example.triviaparty.data.*
import com.example.triviaparty.model.*
import java.io.File
import kotlin.random.Random
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test

class CanonicalQuestionBankTest {
    private val json = Json { ignoreUnknownKeys = true }
    private fun bank() = json.decodeFromString<CanonicalQuestionBank>(File("../game-library/bank/questions.json").readText(Charsets.UTF_8))

    @Test fun migrationKeepsEveryLegacyQuestionAndPresentationUnderOneEntry() {
        val bank = bank()
        val bankLegacy = bank.questions.flatMap { it.legacyIds }
        assertEquals(bankLegacy.size, bankLegacy.distinct().size)
        val old = File("../game-library/current/sources").walkTopDown()
            .filter { it.isFile && it.parentFile?.name == "question-bank" && it.extension == "json" }
            .flatMap { file -> Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }
                .decodeFromString<CategoryQuestionFile>(file.readText(Charsets.UTF_8)).questions.asSequence() }.map { it.id }.toSet()
        val oldCanonical = old.filter { it in bankLegacy.toSet() }.toSet()
        assertTrue(oldCanonical.isNotEmpty())
        assertTrue(bank.questions.size < bank.questions.sumOf { it.presentations.size })
        val presentationIds = bank.questions.flatMap { it.presentations.map { p -> p.id } }
        assertEquals(presentationIds.size, presentationIds.distinct().size)
        assertTrue(bank.questions.all { q -> q.presentations.all { it.id in q.legacyIds } })
        assertEquals(bank.questions.size, bank.questions.map { it.id }.distinct().size)
    }

    @Test fun qcmDirectAndProgressiveCluesArePresentationsOfTheSameQuestion() {
        val bank = bank()
        val entry = bank.questions.single { "lib-qcm-inventions-canada-20261012-02" in it.legacyIds }
        assertTrue("lib-qsj-inventions-canada-20261012-03" in entry.legacyIds)
        val views = bank.categoryViews()
        val questions = views.flatMap { it.questions }.filter { it.id == entry.id }
        assertTrue(questions.any { it is Question.MultipleChoice })
        assertTrue(questions.any { it is Question.TextAnswer })
        assertTrue(questions.any { it is Question.GuessWho })
        for (seed in 0..15) {
            val plan = planDynamicPackages(views.filter { file -> file.questions.any { it.id == entry.id } }
                .map { file -> file.copy(questions = file.questions.filter { it.id == entry.id }) },
                entry.topics, 5, 6, Random(seed))
            assertEquals(1, plan.totalQuestions)
        }
    }

    @Test fun homonymsRemainSeparateAndBankProjectsWithoutAnyLegacyPackageFiles() {
        val bank = bank()
        val building = bank.questions.single { "architecture-qsj-sacre-20261011-01" in it.legacyIds }
        val novel = bank.questions.single { "culture-qcm-francaise-oeuvres-20261010-01" in it.legacyIds }
        assertNotEquals(building.id, novel.id)
        val views = bank.categoryViews()
        assertTrue(views.isNotEmpty())
        assertTrue(views.flatMap { it.questions }.all { it.id in bank.questions.map { entry -> entry.id }.toSet() })
        val images = views.flatMap { it.questions }.mapNotNull { it.imageUrl }.filter { it.isNotBlank() }
        assertTrue(images.all { it.startsWith("local-media://canonical-bank/images/") })
    }
}
