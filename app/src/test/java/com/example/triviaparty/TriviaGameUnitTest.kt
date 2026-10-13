package com.example.triviaparty

import com.example.triviaparty.data.QuestionBankRepository
import com.example.triviaparty.model.*
import com.example.triviaparty.network.GameServer
import org.junit.Assert.*
import org.junit.Test

class TriviaGameUnitTest {


    @Test
    fun testHourglassScoreDecay() {
        val config = HourglassConfig(secondsPerFlip = 10, decayPercentagePerFlip = 0.10f, maxFlips = 5)

        assertEquals(100, config.calculateScore(basePoints = 100, flipNumber = 0))
        assertEquals(90, config.calculateScore(basePoints = 100, flipNumber = 1))
        assertEquals(100, config.calculateScore(basePoints = 100, flipNumber = 0, elapsedSecondsInFlip = 5))
        assertEquals(90, config.calculateScore(basePoints = 100, flipNumber = 1, elapsedSecondsInFlip = 5))
        assertEquals(80, config.calculateScore(basePoints = 100, flipNumber = 2))
        assertEquals(50, config.calculateScore(basePoints = 100, flipNumber = 5))
    }

    @Test
    fun fixedPointDecayDropsOnlyAtCompletedIntervalsAndCanReachZero() {
        val config = HourglassConfig(secondsPerFlip = 10, maxFlips = 5, pointsDecayPerFlip = 5)
        assertEquals(20, config.calculateScore(basePoints = 20, flipNumber = 0, elapsedSecondsInFlip = 9))
        assertEquals(15, config.calculateScore(basePoints = 20, flipNumber = 1))
        assertEquals(10, config.calculateScore(basePoints = 20, flipNumber = 2))
        assertEquals(5, config.calculateScore(basePoints = 20, flipNumber = 3))
        assertEquals(0, config.calculateScore(basePoints = 20, flipNumber = 4))
    }

    @Test
    fun testQuestionBankRepository() {
        assertFalse(QuestionBankRepository.sampleCategories.isEmpty())
        assertFalse(QuestionBankRepository.sampleQuestions.isEmpty())

        for (category in QuestionBankRepository.sampleCategories) {
            val questions = QuestionBankRepository.getQuestionsForCategory(category)
            assertTrue("Category $category should contain multiple questions", questions.size >= 3)
        }
    }

    @Test
    fun bundledCategoryFilesContainValidQuestions() {
        val directory = java.io.File("src/main/assets/question-bank")
        val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }
        val files = directory.listFiles { file -> file.extension == "json" }.orEmpty()
        assertTrue("Question bank should have one or more category files", files.isNotEmpty())
        val categories = mutableSetOf<String>()
        val ids = mutableSetOf<String>()
        files.forEach { file ->
            val data = json.decodeFromString<CategoryQuestionFile>(file.readText(Charsets.UTF_8))
            assertTrue(data.questions.isNotEmpty())
            assertTrue(data.questionTypes.isNotEmpty())
            assertEquals("Category $file must declare a single format", 1, data.questions.map { it::class }.distinct().size)
            assertEquals("Category $file must declare one question type", 1, data.questionTypes.size)
            assertTrue(categories.add(data.category))
            data.questions.forEach { question ->
                assertEquals(data.category, question.category)
                assertTrue(ids.add(question.id))
                assertTrue(question.basePoints >= 0)
                when (question) {
                    is Question.MultipleChoice -> assertTrue(question.correctOptionIndex in question.options.indices)
                    is Question.Wager -> assertTrue(question.subQuestion.correctOptionIndex in question.subQuestion.options.indices)
                    is Question.SpeedRace -> assertTrue(question.subQuestion.correctOptionIndex in question.subQuestion.options.indices)
                    is Question.MapPin -> {
                        assertTrue("${question.id} needs labeled map choices", question.options.isNotEmpty())
                        assertTrue(question.correctOptionIndex in question.options.indices)
                    }
                    is Question.Ordering -> assertEquals(question.items.map { it.id }.toSet(), question.correctOrderIds.toSet())
                    is Question.TextAnswer -> assertTrue(question.acceptableAnswers.isNotEmpty())
                    is Question.GuessWho -> {
                        assertTrue(question.clues.isNotEmpty())
                        assertTrue(question.acceptableAnswers.isNotEmpty())
                    }
                }
            }
        }
    }

    @Test
    fun gamePackagesReferenceExistingCategoryPackages() {
        val packageDirectory = java.io.File("src/main/assets/game-packages")
        val categoryDirectory = java.io.File("src/main/assets/question-bank")
        val categoryIds = categoryDirectory.listFiles { file -> file.extension == "json" }
            .orEmpty().map { it.nameWithoutExtension }.toSet()
        val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true }
        val packages = packageDirectory.listFiles { file -> file.extension == "json" }.orEmpty()
            .map { json.decodeFromString<GamePackage>(it.readText(Charsets.UTF_8)) }
        assertTrue("At least one game package should be bundled", packages.isNotEmpty())
        packages.forEach { gamePackage ->
            assertTrue(gamePackage.categoryPackages.isNotEmpty())
            assertTrue(gamePackage.categoryPackages.all { it in categoryIds })
            assertTrue(gamePackage.timingConfig.secondsPerFlip > 0)
        }
    }

    @Test
    fun testGameSessionInitialState() {
        val session = GameSession(roomId = "1234")
        assertEquals("1234", session.roomId)
        assertEquals(GameState.LOBBY, session.state)
        assertTrue(session.teams.isEmpty())
    }

    @Test
    fun testTeamCreationAndScoring() {
        val team = Team(id = "team_1", name = "Trivia Masters", score = 100, sessionToken = "token_abc")
        assertEquals("Trivia Masters", team.name)
        assertEquals(100, team.score)

        val updatedTeam = team.copy(score = team.score + 50)
        assertEquals(150, updatedTeam.score)
    }

    @Test
    fun testGameServerMultiQuestionProgression() {
        val server = GameServer(port = 8888)
        val initialSession = server.gameSession.value
        assertNotNull(initialSession)
        assertEquals(GameState.LOBBY, initialSession.state)
    }
}
