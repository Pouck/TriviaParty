package com.example.triviaparty.data

import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import kotlin.random.Random

class QuestionRotationTest {
    private fun installRealBank() {
        val source = File("../game-library/bank/questions.json").readText(Charsets.UTF_8)
        QuestionBankRepository.installCanonicalBank(source)
        GamePackageRepository.installBankViews(
            Json { ignoreUnknownKeys = true }.decodeFromString<CanonicalQuestionBank>(source)
        )
    }

    @Test
    fun orderIsStableForOneGameAndDiffersBetweenGames() {
        val items = (1..30).toList()
        assertEquals(orderForPlay(items, 7L) { 0 }, orderForPlay(items, 7L) { 0 })
        assertNotEquals(orderForPlay(items, 7L) { 0 }, orderForPlay(items, 8L) { 0 })
        // The old behaviour was a fixed order: the first six were always the same.
        val firstSixAcrossGames = (1L..20L).map { orderForPlay(items, it) { 0 }.take(6).toSet() }.toSet()
        assertTrue(firstSixAcrossGames.size > 10)
    }

    @Test
    fun leastPlayedQuestionsComeFirst() {
        val items = (1..10).toList()
        val playedBefore = setOf(1, 2, 3, 4, 5)
        repeat(20) { seed ->
            val order = orderForPlay(items, seed.toLong()) { if (it in playedBefore) 1 else 0 }
            assertEquals((6..10).toSet(), order.take(5).toSet())
        }
    }

    @Test
    fun historySurvivesARestart() {
        val file = File.createTempFile("question-history", ".json").apply { deleteOnExit() }
        val first = QuestionPlayHistory(file)
        first.record("q1"); first.record("q1"); first.record("q2")
        val reloaded = QuestionPlayHistory(file)
        assertEquals(2, reloaded.count("q1"))
        assertEquals(1, reloaded.count("q2"))
        assertEquals(0, reloaded.count("never-played"))
        assertEquals(0, QuestionPlayHistory(null).count("q1"))
    }

    @Test
    fun votePlanningPrefersQuestionsNotPlayedInEarlierGames() {
        installRealBank()
        val topics = listOf("Géographie", "Histoire", "Sciences", "Musique", "Cinéma")
        fun ids(plan: DynamicPackagePlan) = plan.packages.flatMap { it.questions }.map { it.id }.toSet()
        var withHistory = 0
        var withoutHistory = 0
        for (seed in 1..15) {
            val played = ids(QuestionBankRepository.generatePackages(topics, 1, 6, Random(seed)))
            withoutHistory += played.intersect(ids(QuestionBankRepository.generatePackages(topics, 1, 6, Random(seed + 100)))).size
            withHistory += played.intersect(ids(QuestionBankRepository.generatePackages(
                topics, 1, 6, Random(seed + 100), playCountForQuestionId = { if (it in played) 1 else 0 }))).size
        }
        assertTrue("repeats with history=$withHistory, without=$withoutHistory", withHistory < withoutHistory)
        QuestionBankRepository.resetGeneratedPackages()
    }

    @Test
    fun generatedPackagesShrinkTheCategoryListUntilReset() {
        installRealBank()
        val full = QuestionBankRepository.sampleCategories.size
        QuestionBankRepository.generatePackages(listOf("Nature", "Musique"), 1, 6)
        assertTrue(QuestionBankRepository.sampleCategories.size < full)
        QuestionBankRepository.resetGeneratedPackages()
        assertEquals(full, QuestionBankRepository.sampleCategories.size)
    }
}
