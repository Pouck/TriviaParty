package com.example.triviaparty

import com.example.triviaparty.model.*
import kotlin.random.Random
import org.junit.Assert.*
import org.junit.Test

class RandomQuestionVariantTest {
    @Test
    fun variantsKeepPromptAndAnswerTogetherAndDoNotChangeDuringTheRound() {
        val variants = listOf(Question.MultipleChoiceVariant("Cameroun ?", 0),
            Question.MultipleChoiceVariant("Angola ?", 1), Question.MultipleChoiceVariant("Mozambique ?", 3))
        val question = Question.MultipleChoice("map", "Afrique", "Original", "map.png", 15, 0,
            listOf("A", "B", "C", "D"), 1, variants)
        val random = Random(42)
        val selected = (1..100).map { question.withRandomVariant(random) as Question.MultipleChoice }
        assertEquals(variants.toSet(), selected.map { Question.MultipleChoiceVariant(it.prompt, it.correctOptionIndex) }.toSet())
        selected.forEach {
            assertEquals(question.id, it.id)
            assertEquals(question.imageUrl, it.imageUrl)
            assertEquals(question.options, it.options)
            assertEquals(15, it.basePoints)
            assertTrue(it.randomVariants.isEmpty())
            assertSame(it, it.withRandomVariant(random))
        }
        assertEquals(variants, question.randomVariants)
        val fixed = question.copy(randomVariants = emptyList())
        assertSame(fixed, fixed.withRandomVariant(random))
    }
}
