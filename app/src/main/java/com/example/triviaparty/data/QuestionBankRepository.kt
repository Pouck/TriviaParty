package com.example.triviaparty.data

import com.example.triviaparty.model.Question
import com.example.triviaparty.model.CategoryQuestionFile
import kotlinx.serialization.json.Json

object QuestionBankRepository {

    private val json = Json { ignoreUnknownKeys = true; classDiscriminator = "kind"; encodeDefaults = true }
    @Volatile private var fileQuestions: List<Question>? = null
    @Volatile private var categoryMetadata: Map<String, CategoryQuestionFile> = emptyMap()
    val sampleCategories: List<String>
        get() = sampleQuestions.map { it.category }.distinct().sorted()

    val sampleQuestions: List<Question>
        get() = fileQuestions ?: builtInQuestions

    private val builtInQuestions: List<Question> = listOf(
        // --- Gaming History ---
        Question.MultipleChoice(
            id = "q1",
            category = "Gaming History",
            prompt = "In which year was the original Nintendo Entertainment System (NES) released in North America?",
            basePoints = 100,
            options = listOf("1983", "1985", "1987", "1989"),
            correctOptionIndex = 1,
        ),
        Question.SpeedRace(
            id = "q2",
            category = "Gaming History",
            prompt = "RACE QUESTION! First correct answer wins bonus points! Who created the iconic Mario franchise?",
            basePoints = 200,
            subQuestion = Question.MultipleChoice(
                id = "q2_sub",
                category = "Gaming History",
                prompt = "Who created Mario?",
                options = listOf("Hideo Kojima", "Shigeru Miyamoto", "Satoru Iwata", "Gabe Newell"),
                correctOptionIndex = 1
            ),
        ),
        Question.Wager(
            id = "q6",
            category = "Gaming History",
            prompt = "WAGER QUESTION! Choose how many points to wager, then answer: What was the best-selling game on the Game Boy?",
            basePoints = 100,
            subQuestion = Question.MultipleChoice(
                id = "q6_sub",
                category = "Gaming History",
                prompt = "Best selling Game Boy title?",
                options = listOf("Super Mario Land", "Tetris", "Pokémon Red & Blue", "Donkey Kong"),
                correctOptionIndex = 1
            )
        ),
        Question.MultipleChoice(
            id = "q7",
            category = "Gaming History",
            prompt = "What was the world's first commercial home video game console, released in 1972?",
            basePoints = 100,
            options = listOf("Atari 2600", "Magnavox Odyssey", "ColecoVision", "Fairchild Channel F"),
            correctOptionIndex = 1
        ),
        Question.TextAnswer(
            id = "q8",
            category = "Gaming History",
            prompt = "In what year was Minecraft officially released out of beta (Version 1.0)?",
            basePoints = 100,
            acceptableAnswers = listOf("2011"),
            allowFuzzyMatch = false
        ),

        // --- World Geography ---
        Question.MapPin(
            id = "q3",
            category = "World Geography",
            prompt = "On the map, choose the marker for France.",
            imageUrl = "",
            basePoints = 150,
            target = Question.MapTarget.CenterRadius(xRatio = 0.38f, yRatio = 0.62f, maxDistanceRatio = 0.08f),
            options = listOf(
                Question.MapPinOption("A", 0.38f, 0.62f),
                Question.MapPinOption("B", 0.29f, 0.42f),
                Question.MapPinOption("C", 0.55f, 0.48f),
                Question.MapPinOption("D", 0.61f, 0.75f)
            ),
            correctOptionIndex = 0,
        ),
        Question.MultipleChoice(
            id = "q9",
            category = "World Geography",
            prompt = "What is the capital city of Australia?",
            basePoints = 100,
            options = listOf("Sydney", "Melbourne", "Canberra", "Brisbane"),
            correctOptionIndex = 2
        ),
        Question.Ordering(
            id = "q10",
            category = "World Geography",
            prompt = "Order these countries by land area from largest to smallest:",
            basePoints = 150,
            items = listOf(
                Question.OrderItem(id = "c_rus", text = "Russia"),
                Question.OrderItem(id = "c_can", text = "Canada"),
                Question.OrderItem(id = "c_usa", text = "United States"),
                Question.OrderItem(id = "c_bra", text = "Brazil")
            ),
            correctOrderIds = listOf("c_rus", "c_can", "c_usa", "c_bra")
        ),
        Question.TextAnswer(
            id = "q11",
            category = "World Geography",
            prompt = "Which river is traditionally considered the longest in the world?",
            basePoints = 100,
            acceptableAnswers = listOf("Nile", "Nile River", "The Nile"),
            allowFuzzyMatch = true
        ),
        Question.Wager(
            id = "q12",
            category = "World Geography",
            prompt = "WAGER QUESTION! What mountain peak is furthest from the Earth's center due to the equatorial bulge?",
            basePoints = 100,
            subQuestion = Question.MultipleChoice(
                id = "q12_sub",
                category = "World Geography",
                prompt = "Furthest peak from Earth's center?",
                options = listOf("Mount Everest", "K2", "Mount Chimborazo", "Kilimanjaro"),
                correctOptionIndex = 2
            )
        ),

        // --- Pop Culture ---
        Question.Ordering(
            id = "q4",
            category = "Pop Culture",
            prompt = "Order these iconic gaming consoles chronologically by release date (oldest to newest):",
            basePoints = 150,
            items = listOf(
                Question.OrderItem(id = "item_ps2", text = "PlayStation 2"),
                Question.OrderItem(id = "item_n64", text = "Nintendo 64"),
                Question.OrderItem(id = "item_xbox360", text = "Xbox 360"),
                Question.OrderItem(id = "item_switch", text = "Nintendo Switch")
            ),
            correctOrderIds = listOf("item_n64", "item_ps2", "item_xbox360", "item_switch")
        ),
        Question.MultipleChoice(
            id = "q13",
            category = "Pop Culture",
            prompt = "Which film currently holds the record for highest-grossing film of all time worldwide?",
            basePoints = 100,
            options = listOf("Avengers: Endgame", "Titanic", "Avatar", "Star Wars: The Force Awakens"),
            correctOptionIndex = 2
        ),
        Question.SpeedRace(
            id = "q14",
            category = "Pop Culture",
            prompt = "RACE QUESTION! Which British rock band recorded the 1975 hit song 'Bohemian Rhapsody'?",
            basePoints = 200,
            subQuestion = Question.MultipleChoice(
                id = "q14_sub",
                category = "Pop Culture",
                prompt = "Band that sang Bohemian Rhapsody?",
                options = listOf("The Beatles", "Queen", "Led Zeppelin", "The Rolling Stones"),
                correctOptionIndex = 1
            ),
        ),
        Question.TextAnswer(
            id = "q15",
            category = "Pop Culture",
            prompt = "What superhero identity does Tony Stark assume in the Marvel Cinematic Universe?",
            basePoints = 100,
            acceptableAnswers = listOf("Iron Man", "Ironman"),
            allowFuzzyMatch = true
        ),
        Question.MultipleChoice(
            id = "q16",
            category = "Pop Culture",
            prompt = "Which music artist performed at the 2021 Super Bowl halftime show and sang 'Blinding Lights'?",
            basePoints = 100,
            options = listOf("Bruno Mars", "The Weeknd", "Usher", "Justin Timberlake"),
            correctOptionIndex = 1
        ),

        // --- Science & Tech ---
        Question.TextAnswer(
            id = "q5",
            category = "Science & Tech",
            prompt = "What is the name of the programming language created by James Gosling at Sun Microsystems in 1995?",
            basePoints = 100,
            acceptableAnswers = listOf("Java", "java"),
            allowFuzzyMatch = true
        ),
        Question.MultipleChoice(
            id = "q17",
            category = "Science & Tech",
            prompt = "What is the chemical symbol for Gold on the Periodic Table?",
            basePoints = 100,
            options = listOf("Ag", "Au", "Fe", "Gd"),
            correctOptionIndex = 1
        ),
        Question.MultipleChoice(
            id = "q18",
            category = "Science & Tech",
            prompt = "Which tech company became the first publicly traded U.S. company to reach a $1 trillion market cap in 2018?",
            basePoints = 100,
            options = listOf("Microsoft", "Amazon", "Apple", "Google"),
            correctOptionIndex = 2
        ),
        Question.Ordering(
            id = "q19",
            category = "Science & Tech",
            prompt = "Order these electromagnetic spectrum waves by frequency (lowest to highest):",
            basePoints = 150,
            items = listOf(
                Question.OrderItem(id = "em_radio", text = "Radio Waves"),
                Question.OrderItem(id = "em_infra", text = "Infrared"),
                Question.OrderItem(id = "em_visible", text = "Visible Light"),
                Question.OrderItem(id = "em_uv", text = "Ultraviolet")
            ),
            correctOrderIds = listOf("em_radio", "em_infra", "em_visible", "em_uv")
        ),
        Question.SpeedRace(
            id = "q20",
            category = "Science & Tech",
            prompt = "RACE QUESTION! Which planet in our solar system is closest to the Sun?",
            basePoints = 200,
            subQuestion = Question.MultipleChoice(
                id = "q20_sub",
                category = "Science & Tech",
                prompt = "Planet closest to the Sun?",
                options = listOf("Venus", "Mercury", "Mars", "Earth"),
                correctOptionIndex = 1
            )
        ),

        // --- Video Game Maps ---
        Question.MapPin(
            id = "q21",
            category = "Video Game Maps",
            prompt = "Choose the marker for western France.",
            imageUrl = "",
            basePoints = 150,
            target = Question.MapTarget.CenterRadius(xRatio = 0.35f, yRatio = 0.60f, maxDistanceRatio = 0.08f),
            options = listOf(
                Question.MapPinOption("A", 0.35f, 0.60f),
                Question.MapPinOption("B", 0.29f, 0.42f),
                Question.MapPinOption("C", 0.55f, 0.48f),
                Question.MapPinOption("D", 0.61f, 0.75f)
            ),
            correctOptionIndex = 0
        ),
        Question.TextAnswer(
            id = "q22",
            category = "Video Game Maps",
            prompt = "What is the name of the fictional fantasy kingdom setting in The Legend of Zelda series?",
            basePoints = 100,
            acceptableAnswers = listOf("Hyrule"),
            allowFuzzyMatch = true
        ),
        Question.MultipleChoice(
            id = "q23",
            category = "Video Game Maps",
            prompt = "In Fortnite Chapter 1, what was the codename of the original Battle Royale island map?",
            basePoints = 100,
            options = listOf("Apollo", "Athena", "Artemis", "Asteria"),
            correctOptionIndex = 1
        ),
        Question.Ordering(
            id = "q24",
            category = "Video Game Maps",
            prompt = "Order these famous video game worlds by their release year (oldest to newest):",
            basePoints = 150,
            items = listOf(
                Question.OrderItem(id = "map_kanto", text = "Kanto (Pokémon Red/Blue)"),
                Question.OrderItem(id = "map_sanandreas", text = "San Andreas (GTA)"),
                Question.OrderItem(id = "map_skyrim", text = "Skyrim (The Elder Scrolls V)"),
                Question.OrderItem(id = "map_elden", text = "The Lands Between (Elden Ring)")
            ),
            correctOrderIds = listOf("map_kanto", "map_sanandreas", "map_skyrim", "map_elden")
        ),
        Question.Wager(
            id = "q25",
            category = "Video Game Maps",
            prompt = "WAGER QUESTION! What is the name of the futuristic metropolis setting in Cyberpunk 2077?",
            basePoints = 100,
            subQuestion = Question.MultipleChoice(
                id = "q25_sub",
                category = "Video Game Maps",
                prompt = "Futuristic city in Cyberpunk 2077?",
                options = listOf("Raccoon City", "Night City", "Neo-Tokyo", "Gotham City"),
                correctOptionIndex = 1
            )
        )
    )

    fun getQuestionsForCategory(category: String): List<Question> {
        return sampleQuestions.filter { it.category.equals(category, ignoreCase = true) }
    }

    fun getCategoryPackage(category: String): CategoryQuestionFile? =
        categoryMetadata[category.lowercase()]

    fun reloadImportedPackages(packageDirectories: List<java.io.File>) {
        val imported = packageDirectories.flatMap { packageDirectory ->
            val categoryDirectory = java.io.File(packageDirectory, "question-bank")
            categoryDirectory.listFiles { file -> file.isFile && file.extension.equals("json", true) }
                .orEmpty().sortedBy { it.name }.map { file ->
                    val category = json.decodeFromString<CategoryQuestionFile>(file.readText(Charsets.UTF_8))
                    require(category.questions.all { it.category == category.category }) {
                        "Questions in ${file.name} must use category '${category.category}'"
                    }
                    category.copy(questions = category.questions.map { question ->
                        question.withImportedImagePrefix(packageDirectory.name)
                    })
                }
        }
        val categories = imported
        val loaded = categories.flatMap { it.questions }
        require(loaded.map { it.id }.distinct().size == loaded.size) { "Question IDs must be unique across category files" }
        require(categories.map { it.category.lowercase() }.distinct().size == categories.size) {
            "Imported categories must have names that are unique"
        }
        categoryMetadata = categories.associateBy { it.category.lowercase() }
        fileQuestions = loaded
    }

    private fun Question.withImportedImagePrefix(packageId: String): Question {
        fun local(path: String?): String? = path?.takeIf { it.isNotBlank() }?.let {
            if (it.startsWith("local-media://")) it else "local-media://$packageId/$it"
        }
        return when (this) {
            is Question.MultipleChoice -> copy(imageUrl = local(imageUrl))
            is Question.Ordering -> copy(imageUrl = local(imageUrl))
            is Question.TextAnswer -> copy(imageUrl = local(imageUrl))
            is Question.GuessWho -> copy(imageUrl = local(imageUrl))
            is Question.MapPin -> copy(imageUrl = local(imageUrl).orEmpty())
            is Question.Wager -> copy(imageUrl = local(imageUrl), subQuestion = subQuestion.copy(imageUrl = local(subQuestion.imageUrl)))
            is Question.SpeedRace -> copy(imageUrl = local(imageUrl), subQuestion = subQuestion.copy(imageUrl = local(subQuestion.imageUrl)))
        }
    }
}
