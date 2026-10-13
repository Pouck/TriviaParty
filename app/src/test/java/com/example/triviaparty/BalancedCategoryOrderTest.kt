package com.example.triviaparty

import com.example.triviaparty.data.*
import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameServer
import com.example.triviaparty.network.GameEvent
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import kotlin.random.Random

class BalancedCategoryOrderTest {
    private fun order(profiles: List<CategoryProfile>, seed: Int = 0): List<CategoryProfile> {
        val ids = profiles.indices.map { "category-$it" }
        val result = balancedCategoryOrder(ids, { profiles[ids.indexOf(it)] }, Random(seed))
        assertEquals(ids.toSet(), result.toSet())
        assertEquals(ids.size, result.size)
        return result.map { profiles[ids.indexOf(it)] }
    }

    private fun repetitions(profiles: List<CategoryProfile>): Int = profiles.zipWithNext().sumOf { (a, b) ->
        (if (a.format == b.format) 1 else 0) + (if (a.subject == b.subject) 1 else 0)
    }

    @Test fun alternatesBothAxesForAllNineFormatSubjectCombinations() {
        val profiles = listOf(CategoryFormat.QCM, CategoryFormat.BUZZER, CategoryFormat.GUESS_WHO).flatMap { format ->
            listOf("Géographie", "Histoire", "Architecture").map { CategoryProfile(format, it) }
        }
        repeat(12) { seed -> assertEquals(0, repetitions(order(profiles, seed))) }
    }

    @Test fun mixesFormatsEvenWhenAllCategoriesHaveTheSameSubject() {
        val profiles = List(3) { CategoryProfile(CategoryFormat.QCM, "Architecture") } +
            List(3) { CategoryProfile(CategoryFormat.BUZZER, "Architecture") } +
            List(5) { CategoryProfile(CategoryFormat.GUESS_WHO, "Architecture") }
        repeat(8) { seed ->
            val result = order(profiles, seed)
            assertTrue(result.zipWithNext().all { (a, b) -> a.format != b.format })
        }
    }

    @Test fun mixesSubjectsEvenWhenEveryCategoryIsMultipleChoice() {
        val profiles = List(4) { CategoryProfile(CategoryFormat.QCM, "Géographie") } +
            List(3) { CategoryProfile(CategoryFormat.QCM, "Histoire") } +
            List(2) { CategoryProfile(CategoryFormat.QCM, "Littérature") }
        repeat(8) { seed -> assertTrue(order(profiles, seed).zipWithNext().all { (a, b) -> a.subject != b.subject }) }
    }

    @Test fun unavoidableRepeatsAreSpreadInsteadOfLeavingAMajorityAtTheEnd() {
        val profiles = List(8) { CategoryProfile(CategoryFormat.QCM, "Géographie") } +
            List(2) { CategoryProfile(CategoryFormat.BUZZER, "Histoire") } +
            List(2) { CategoryProfile(CategoryFormat.GUESS_WHO, "Littérature") }
        repeat(8) { seed ->
            val result = order(profiles, seed)
            assertEquals(3, result.zipWithNext().count { (a, b) -> a.format == b.format })
            assertTrue(result.windowed(3).none { trio -> trio.map { it.format }.distinct().size == 1 })
        }
    }

    @Test fun randomTiesAllowDifferentGamesAndSeededRunsAreReproducible() {
        val profiles = List(3) { CategoryProfile(CategoryFormat.QCM, "Géographie") } +
            List(3) { CategoryProfile(CategoryFormat.BUZZER, "Histoire") }
        val ids = profiles.indices.map { "category-$it" }
        fun schedule(seed: Int) = balancedCategoryOrder(ids, { profiles[ids.indexOf(it)] }, Random(seed))
        assertEquals(schedule(17), schedule(17))
        assertTrue((0..8).map(::schedule).distinct().size > 1)
    }

    @Test fun handlesEmptySingleAndDuplicateSelections() {
        val profile = CategoryProfile(CategoryFormat.BUZZER, "Architecture")
        assertTrue(balancedCategoryOrder(emptyList(), { error("No lookup needed") }).isEmpty())
        assertEquals(listOf("one"), balancedCategoryOrder(listOf("one", "one"), { profile }))
        val ids = listOf("a", "a", "b", "c", "b")
        assertEquals(setOf("a", "b", "c"), balancedCategoryOrder(ids, { profile }).toSet())
        assertEquals(3, balancedCategoryOrder(ids, { profile }).size)
    }

    @Test fun largeSelectionsStillAlternateWithoutDroppingCategories() {
        val profiles = listOf(CategoryFormat.QCM, CategoryFormat.BUZZER, CategoryFormat.GUESS_WHO, CategoryFormat.CHRONOLOGY)
            .flatMap { format -> (0..5).flatMap { subject -> List(5) { CategoryProfile(format, "Sujet $subject") } } }
        assertEquals(0, repetitions(order(profiles)))
    }

    @Test fun formatsComeFromQuestionsRatherThanPackageNames() {
        val mc = Question.MultipleChoice("m", "x", "Question", options = listOf("A", "B", "C", "D"), correctOptionIndex = 0)
        val chronology = mc.copy(options = listOf("A → B → C", "A → C → B", "B → A → C", "C → B → A"))
        assertEquals(CategoryFormat.QCM, categoryFormatFor(mc))
        assertEquals(CategoryFormat.CHRONOLOGY, categoryFormatFor(chronology))
        assertEquals(CategoryFormat.CHRONOLOGY, categoryFormatFor(Question.Ordering("o", "x", "Ordre",
            items = listOf(Question.OrderItem("a", "A")), correctOrderIds = listOf("a"))))
        assertEquals(CategoryFormat.BUZZER, categoryFormatFor(Question.TextAnswer("t", "x", "Question", acceptableAnswers = listOf("A"))))
        assertEquals(CategoryFormat.GUESS_WHO, categoryFormatFor(Question.GuessWho("g", "x", clues = listOf("Indice"), acceptableAnswers = listOf("A"))))
        assertEquals(CategoryFormat.QCM, categoryFormatFor(Question.Wager("w", "x", "Question", subQuestion = mc)))
        assertEquals(CategoryFormat.SPEED_RACE, categoryFormatFor(Question.SpeedRace("s", "x", "Question", subQuestion = mc)))
    }

    @Test fun subjectsRecognizeNewAndLegacyNamesAndOptionalMetadata() {
        assertEquals("Architecture", subjectGroup("Architecture — Merveilles antiques — Qui suis-je ?"))
        assertEquals("Arts", subjectGroup("Arts — Peintures de la Renaissance — QCM"))
        assertEquals("Arts", subjectGroup("Sculptures antiques"))
        assertEquals("Musique",subjectGroup("Musique — Films et comédies musicales — QCM"))
        assertEquals("BD et manga",subjectGroup("BD et manga — Classiques — Buzzer"))
        assertEquals("Super-héros",subjectGroup("Super-héros — Marvel — Qui suis-je ?"))
        assertEquals("Nature",subjectGroup("Nature — Oiseaux — QCM"))
        assertEquals("Cuisine",subjectGroup("Cuisine — Desserts — Buzzer"))
        assertEquals("Contes et légendes",subjectGroup("Contes et légendes — Traditions nommées — QCM"))
        assertEquals("Logique et énigmes",subjectGroup("Logique et énigmes — Défis rapides — QCM"))
        assertEquals("Histoire", subjectGroup("Canada — Bâtisseurs — Qui suis-je ?"))
        assertEquals("Sciences", subjectGroup("Inventions canadiennes — Médecine"))
        assertEquals("Géographie", subjectGroup("Géographie du Canada"))
        assertEquals("Littérature", subjectGroup("Qui suis-je ? — Littérature française"))
        assertEquals("Mythologie", subjectGroup("Mythologie grecque"))
        assertEquals("Jeux vidéo", subjectGroup("Gaming History"))
        assertEquals("Culture populaire", subjectGroup("Culture populaire"))
        assertEquals("Cinéma", subjectGroup("Cinéma — Films et personnages — QCM"))
        val json = Json { classDiscriminator = "kind" }
        val old = """{"category":"Mystères","questionTypes":["QCM"],"questions":[{"kind":"multipleChoice","id":"x","category":"Mystères","prompt":"?","options":["A","B","C","D"],"correctOptionIndex":0}]}"""
        assertNull(json.decodeFromString<CategoryQuestionFile>(old).subject)
        assertEquals("Architecture", json.decodeFromString<CategoryQuestionFile>(old.replace("\"category\":\"Mystères\",\"questionTypes\"", "\"category\":\"Mystères\",\"subject\":\"Architecture\",\"questionTypes\"")).subject)
    }

    @Test fun boundedSearchMatchesTheBestPossibleRepeatCountForATightlyCoupledSelection() {
        val profiles = listOf(CategoryProfile(CategoryFormat.QCM, "Géographie"),
            CategoryProfile(CategoryFormat.QCM, "Géographie"), CategoryProfile(CategoryFormat.QCM, "Histoire"),
            CategoryProfile(CategoryFormat.BUZZER, "Géographie"), CategoryProfile(CategoryFormat.BUZZER, "Histoire"),
            CategoryProfile(CategoryFormat.GUESS_WHO, "Histoire"))
        fun minimum(prefix: List<CategoryProfile>, remaining: List<CategoryProfile>): Int =
            if (remaining.isEmpty()) repetitions(prefix) else remaining.indices.minOf { i ->
                minimum(prefix + remaining[i], remaining.filterIndexed { index, _ -> index != i })
            }
        val optimum = minimum(emptyList(), profiles)
        repeat(8) { seed -> assertEquals(optimum, repetitions(order(profiles, seed))) }
    }

    @Test
    @Suppress("UNCHECKED_CAST")
    fun serverStoresBalancedOrderAndPlaysEveryCategoryWithItsOriginalRules() {
        val bank = QuestionBankRepository
        val questionField = bank::class.java.getDeclaredField("fileQuestions").apply { isAccessible = true }
        val metadataField = bank::class.java.getDeclaredField("categoryMetadata").apply { isAccessible = true }
        val oldQuestions = questionField.get(bank)
        val oldMetadata = metadataField.get(bank)
        val questions = listOf("Géographie", "Histoire", "Littérature").mapIndexed { i, subject ->
            Question.MultipleChoice("m$i", "$subject — QCM", "Question", options = listOf("A", "B", "C", "D"), correctOptionIndex = 0)
        } + listOf("Géographie", "Histoire", "Littérature").mapIndexed { i, subject ->
            Question.TextAnswer("b$i", "$subject — Buzzer", "Question", acceptableAnswers = listOf("A"))
        }
        val rules = questions.mapIndexed { i, q -> q.category to CategoryGameRules(
            HourglassConfig(secondsPerFlip = 5 + i), answerTimeSeconds = 10 + i) }.toMap()
        val server = GameServer()
        val state = GameServer::class.java.getDeclaredField("_gameSession").apply { isAccessible = true }.get(server) as MutableStateFlow<GameSession>
        val start = GameServer::class.java.getDeclaredMethod("handleHostStartGame", GameEvent.HostStartGame::class.java).apply { isAccessible = true }
        val advance = GameServer::class.java.getDeclaredMethod("handleHostBeginCategorySelect").apply { isAccessible = true }
        try {
            questionField.set(bank, questions)
            metadataField.set(bank, emptyMap<String, CategoryQuestionFile>())
            start.invoke(server, GameEvent.HostStartGame(questions.map { it.category }, questions.size,
                HourglassConfig(), 10, rules))
            val scheduled = state.value.masterCategories
            assertEquals(questions.map { it.category }.toSet(), scheduled.toSet())
            assertEquals(6, state.value.totalRounds)
            assertEquals(rules, state.value.categoryRules)
            assertEquals(0, repetitions(scheduled.map(::categoryProfileFor)))
            scheduled.forEach { category ->
                advance.invoke(server)
                assertEquals(category, state.value.currentQuestion!!.category)
                assertEquals(rules.getValue(category).answerTimeSeconds, state.value.currentCategoryAnswerTimeSeconds)
                state.value = state.value.copy(state = GameState.REVEAL_ANSWER,
                    playedQuestionIds = state.value.playedQuestionIds + bank.getQuestionsForCategory(category).map { it.id })
            }
            advance.invoke(server)
            assertEquals(GameState.GAME_ENDED, state.value.state)
        } finally {
            server.stop()
            questionField.set(bank, oldQuestions)
            metadataField.set(bank, oldMetadata)
        }
    }
}
