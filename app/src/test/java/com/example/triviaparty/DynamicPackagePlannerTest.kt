package com.example.triviaparty

import com.example.triviaparty.data.planDynamicPackages
import com.example.triviaparty.model.CategoryAnswerMode
import com.example.triviaparty.model.CategoryQuestionFile
import com.example.triviaparty.model.Question
import kotlinx.serialization.json.Json
import java.io.File
import kotlin.random.Random
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class DynamicPackagePlannerTest {
    @Test fun currentSubjectBanksGenerateDistinctSixQuestionPackagesWithVariedFormats() {
        val json = Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }
        val source = File("../game-library/current/sources").walkTopDown()
            .filter { it.isFile && it.parentFile?.name == "question-bank" && it.extension.equals("json", true) }
            .map { json.decodeFromString<CategoryQuestionFile>(it.readText(Charsets.UTF_8)) }.toList()

        val plan = planDynamicPackages(source, listOf("Histoire", "Cinéma", "Arts"),
            packagesPerTopic = 1, questionsPerPackage = 6, random = Random(2026))

        assertEquals(3, plan.packages.size)
        assertTrue(plan.packages.all { it.questions.size == 6 })
        assertTrue(plan.packages.all { it.questions.map { q -> q::class }.distinct().size == 1 })
        assertEquals(18, plan.packages.flatMap { it.questions }.map { it.id }.distinct().size)
        assertTrue("Expected varied announced formats", plan.packages.map { it.questionTypes.single() }.distinct().size >= 2)
    }

    @Test fun keepsEachPackageFocusedAndBalancesFormatsAcrossPackages() {
        val source = listOf(
            textFile("topic-a", "History", "A", 4),
            textFile("topic-b", "History", "B", 4),
            qcmFile("topic-c", "History", "C", 4),
            qcmFile("topic-d", "History", "D", 4),
            chronologyFile("topic-e", "History", "E", 4)
        )

        val plan = planDynamicPackages(source, listOf("History"), packagesPerTopic = 5,
            questionsPerPackage = 3, random = Random(41))

        assertEquals(5, plan.packages.size)
        assertTrue(plan.packages.all { it.questions.size == 3 })
        assertTrue(plan.packages.all { it.questions.map { q -> q::class }.distinct().size == 1 })
        assertTrue(plan.packages.map { it.questionTypes.single() }.distinct().size >= 3)
        assertTrue(plan.packages.groupBy { it.questionTypes.single() }.values.map { it.size }.max() -
            plan.packages.groupBy { it.questionTypes.single() }.values.map { it.size }.min() <= 1)
        assertEquals(15, plan.packages.flatMap { it.questions }.map { it.id }.distinct().size)
    }

    @Test fun letsFreeResponseQuestionsMoveBetweenBuzzerAndWrittenPackages() {
        val source = listOf(textFile("written", "Cinema", "W", 10, CategoryAnswerMode.WRITTEN))
        val plan = planDynamicPackages(source, listOf("Cinema"), packagesPerTopic = 2,
            questionsPerPackage = 5, random = Random(9))

        assertEquals(setOf(CategoryAnswerMode.BUZZER, CategoryAnswerMode.WRITTEN), plan.packages.map { it.answerMode }.toSet())
        assertEquals(5, plan.packages[0].questions.size)
        assertEquals(5, plan.packages[1].questions.size)
        assertEquals(10, plan.packages.flatMap { it.questions }.map { it.id }.distinct().size)
    }

    @Test fun capsPackageSizeAtAvailableQuestionsAndSkipsTopicsWithoutQuestions() {
        val plan = planDynamicPackages(listOf(qcmFile("small", "Arts", "A", 2)),
            listOf("Arts", "Missing"), packagesPerTopic = 1, questionsPerPackage = 6,
            random = Random(2))
        assertEquals(1, plan.packages.size)
        assertEquals(2, plan.totalQuestions)
    }

    @Test fun includesExtremesSparinglyWithoutRequiringThem() {
        val source = listOf(textFile("rated", "Arts", "A", 8))
        val ratings = (1..8).associate { "rated-$it" to when (it) { 1, 2 -> 1; 3, 4 -> 5; else -> 3 } }
        val plan = planDynamicPackages(source, listOf("Arts"), 1, 8, Random(7), ratings::get)
        val selectedRatings = plan.packages.single().questions.mapNotNull { ratings[it.id] }
        assertTrue(selectedRatings.count { it == 1 } <= 1)
        assertTrue(selectedRatings.count { it == 5 } <= 1)
        assertEquals(6, selectedRatings.size)
    }

    @Test fun sharedConceptCannotRepeatAcrossFormatsOrTopicsButKeepsAuthoredVariants() {
        val choice = qcmFile("choice", "History", "QCM", 1).let { file ->
            file.copy(questions = listOf((file.questions.single() as Question.MultipleChoice).copy(
                prompt = "Qui fonde Québec en 1608 ?", options = listOf("A — Champlain", "B — Cartier"),
                conceptId = "quebec-founder")))
        }
        val written = textFile("written", "Canada", "Written", 1).let { file ->
            file.copy(questions = listOf((file.questions.single() as Question.TextAnswer).copy(
                prompt = "Quel Français fonde Québec ?", acceptableAnswers = listOf("Champlain"),
                conceptId = "quebec-founder")))
        }
        val observed = mutableSetOf<Class<out Question>>()
        for (seed in 0..40) {
            val plan = planDynamicPackages(listOf(choice, written), listOf("History", "Canada"), 3, 1, Random(seed))
            assertEquals(1, plan.totalQuestions)
            observed += plan.packages.single().questions.single().javaClass
        }
        assertEquals(setOf(Question.MultipleChoice::class.java, Question.TextAnswer::class.java), observed)
    }

    @Test fun exactQuestionDeduplicationIgnoresChoiceLabelsAndResponseType() {
        val choice = qcmFile("choice", "History", "QCM", 1).let { file ->
            file.copy(questions = listOf((file.questions.single() as Question.MultipleChoice).copy(
                prompt = "Qui fonde Québec ?", options = listOf("A — Champlain", "B — Cartier"))))
        }
        val text = textFile("text", "History", "Text", 1).let { file ->
            file.copy(questions = listOf((file.questions.single() as Question.TextAnswer).copy(
                prompt = "Qui fonde Québec ?", acceptableAnswers = listOf("Champlain"))))
        }
        val otherFact = text.copy(questions = listOf((text.questions.single() as Question.TextAnswer).copy(
            id = "different-fact", prompt = "Qui explore le lac portant son nom ?")))
        assertEquals(2, planDynamicPackages(listOf(choice, text, otherFact), listOf("History"), 6, 1, Random(8)).totalQuestions)
    }

    private fun textFile(id: String, subject: String, sourceName: String, count: Int,
        answerMode: CategoryAnswerMode = CategoryAnswerMode.BUZZER): CategoryQuestionFile {
        val category = "$sourceName — ${if (answerMode == CategoryAnswerMode.WRITTEN) "Réponses écrites" else "Buzzer"}"
        return CategoryQuestionFile(
        category = category,
        answerMode = answerMode,
        questionTypes = listOf(if (answerMode == CategoryAnswerMode.WRITTEN) "Réponses écrites" else "Buzzer"),
        subject = subject,
        questions = (1..count).map { n -> Question.TextAnswer("$id-$n", category, "Question $id $n", acceptableAnswers = listOf("A$id$n")) }
    )
    }

    private fun qcmFile(id: String, subject: String, sourceName: String, count: Int): CategoryQuestionFile {
        val category = "$sourceName — Choix multiples"
        return CategoryQuestionFile(
        category = category, answerMode = CategoryAnswerMode.SIMULTANEOUS,
        questionTypes = listOf("Choix multiples"), subject = subject,
        questions = (1..count).map { n -> Question.MultipleChoice("$id-$n", category, "Question $id $n", options = listOf("A", "B"), correctOptionIndex = 0) }
    )
    }

    private fun chronologyFile(id: String, subject: String, sourceName: String, count: Int): CategoryQuestionFile {
        val category = "$sourceName — Chronologie"
        return CategoryQuestionFile(
        category = category, answerMode = CategoryAnswerMode.SIMULTANEOUS,
        questionTypes = listOf("Chronologie"), subject = subject,
        questions = (1..count).map { n -> Question.Ordering("$id-$n", category, "Question $id $n", items = listOf(Question.OrderItem("a", "A"), Question.OrderItem("b", "B")), correctOrderIds = listOf("a", "b")) }
    )
    }
}
