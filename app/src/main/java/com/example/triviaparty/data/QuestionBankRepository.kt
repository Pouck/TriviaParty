package com.example.triviaparty.data

import com.example.triviaparty.model.Question
import com.example.triviaparty.model.CategoryQuestionFile
import kotlinx.serialization.json.Json
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import kotlin.random.Random

object QuestionBankRepository {

    private val json = Json { ignoreUnknownKeys = true; classDiscriminator = "kind"; encodeDefaults = true }
    @Volatile private var fileQuestions: List<Question>? = null
    @Volatile private var categoryMetadata: Map<String, CategoryQuestionFile> = emptyMap()
    @Volatile private var generatedMetadata: Map<String, CategoryQuestionFile> = emptyMap()
    @Volatile private var generatedQuestions: List<Question>? = null
    @Volatile private var canonicalBank: CanonicalQuestionBank? = null

    // Memoized caches for taxonomy lookups to prevent UI thread blocking / O(N) traversal on every click
    @Volatile private var cachedSubjectsForTaxonomyTag: MutableMap<String, List<BankSubject>> =
        ConcurrentHashMap()
    @Volatile private var cachedQuestionsForTaxonomyTag: MutableMap<String, List<Question>> =
        ConcurrentHashMap()
    @Volatile private var cachedQuestionsForCanonicalSubject: MutableMap<String, List<Question>> =
        ConcurrentHashMap()
    @Volatile private var cachedCategoryQuestions: MutableMap<String, List<Question>> =
        ConcurrentHashMap()
    private fun isValidTopic(topic: String): Boolean {
        val trimmed = topic.trim()
        if (trimmed.length <= 1) return false
        if (trimmed.matches(Regex("^[a-zA-Z]$"))) return false
        if (trimmed.matches(Regex("^\\d+$"))) return false // Filter out purely numeric subjects/topics like "12"
        if (trimmed.equals("a", ignoreCase = true) || trimmed.equals("b", ignoreCase = true) || trimmed.equals("c", ignoreCase = true) || trimmed.equals("d", ignoreCase = true)) return false
        return true
    }

    val canonicalSubjects: List<BankSubject>
        get() = canonicalBank?.subjects.orEmpty().filter { isValidTopic(it.label) }
    val subjectTaxonomy: List<BankTaxonomyTag>
        get() = canonicalBank?.taxonomy.orEmpty().filter { isValidTopic(it.label) }

    val rootTaxonomyTags: List<BankTaxonomyTag>
        get() = subjectTaxonomy.filter { it.parentId == null }

    fun childTaxonomyTags(parentId: String): List<BankTaxonomyTag> {
        // Rule 2 & 3: Expanding a node returns only its direct child taxonomy nodes,
        // with NO leaf questions or leaf subjects mixed in. Terminal leaf nodes hold subjects.
        return subjectTaxonomy.filter { it.parentId == parentId }
    }

    val canonicalTopics: List<String>
        get() = canonicalBank?.questions?.flatMap { it.topics }?.filter(::isValidTopic)?.distinct().orEmpty()

    fun subjectsForTaxonomyTag(tagId: String): List<BankSubject> {
        return cachedSubjectsForTaxonomyTag.getOrPut(tagId) {
            val bank = canonicalBank ?: return@getOrPut emptyList()
            val tagIds = mutableSetOf(tagId)
            var added: Boolean
            do {
                added = false
                val children = subjectTaxonomy.filter { it.parentId in tagIds }.map { it.id }
                for (child in children) {
                    if (tagIds.add(child)) {
                        added = true
                    }
                }
            } while (added)
            bank.subjects.filter { subject -> subject.tagIds.any { it in tagIds } }
        }
    }

    fun subjectsForTaxonomyTagDirect(tagId: String): List<BankSubject> {
        return cachedSubjectsForTaxonomyTag.getOrPut("direct_$tagId") {
            val bank = canonicalBank ?: return@getOrPut emptyList()
            val allTags = subjectTaxonomy.associateBy { it.id }
            
            // Helper to check if childTagId is a descendant of parentTagId
            fun isDescendant(childTagId: String, parentTagId: String): Boolean {
                var curr = allTags[childTagId]
                while (curr != null) {
                    if (curr.parentId == parentTagId) return true
                    curr = curr.parentId?.let { allTags[it] }
                }
                return false
            }

            bank.subjects.filter { subject ->
                if (!subject.tagIds.contains(tagId)) return@filter false
                // Strict specificity filtering: tagId must be the deepest (most specific) taxonomy tag among the subject's tagIds.
                // That means no other tag in subject.tagIds can be a descendant of tagId.
                subject.tagIds.none { otherTagId ->
                    otherTagId != tagId && isDescendant(otherTagId, tagId)
                }
            }
        }
    }

    fun questionsForTaxonomyTag(tagId: String): List<Question> {
        return cachedQuestionsForTaxonomyTag.getOrPut(tagId) {
            val bank = canonicalBank ?: return@getOrPut emptyList()
            val matchingSubjectIds = subjectsForTaxonomyTag(tagId).map { it.id }.toSet()
            val matchingBankQuestions = bank.questions.filter { q -> q.subjectIds.any { it in matchingSubjectIds } }
            val knownIds = matchingBankQuestions.map { it.id }.toSet()
            val categoryViews = bank.categoryViews()
            // Also map via legacy category/topic if needed or fallback to category views containing these questions
            categoryViews.filter { catFile ->
                catFile.questions.any { q -> q.id in knownIds }
            }.flatMap { it.questions }.distinctBy { it.id }.ifEmpty {
                matchingBankQuestions.map { q ->
                    Question.MultipleChoice(
                        id = q.id,
                        category = q.topics.firstOrNull() ?: tagId,
                        prompt = q.prompt,
                        basePoints = 100,
                        options = q.answers.ifEmpty { listOf("A", "B", "C", "D") },
                        correctOptionIndex = 0
                    )
                }
            }
        }
    }

    fun questionsForCanonicalSubject(subjectId: String): List<Question> {
        return cachedQuestionsForCanonicalSubject.getOrPut(subjectId) {
            val bank = canonicalBank ?: return@getOrPut emptyList()
            val matchingBankQuestions = bank.questions.filter { q -> subjectId in q.subjectIds }
            val knownIds = matchingBankQuestions.map { it.id }.toSet()
            bank.categoryViews().filter { catFile ->
                catFile.questions.any { q -> q.id in knownIds }
            }.flatMap { it.questions }.distinctBy { it.id }.ifEmpty {
                matchingBankQuestions.map { q ->
                    Question.MultipleChoice(
                        id = q.id,
                        category = q.topics.firstOrNull() ?: subjectId,
                        prompt = q.prompt,
                        basePoints = 100,
                        options = q.answers.ifEmpty { listOf("A", "B", "C", "D") },
                        correctOptionIndex = 0
                    )
                }
            }
        }
    }

    fun subjectById(id: String): BankSubject? = canonicalBank?.subjects?.firstOrNull { it.id == id }
    val sampleCategories: List<String>
        get() = if (generatedQuestions != null) sampleQuestions.map { it.category }.distinct().sorted()
            else categoryMetadata.values.map { it.category }.ifEmpty { builtInQuestions.map { it.category } }.distinct().sorted()

    val sampleQuestions: List<Question>
        get() = generatedQuestions ?: fileQuestions ?: builtInQuestions

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
        return cachedCategoryQuestions.getOrPut(category.lowercase()) {
            generatedMetadata[category.lowercase()]?.questions
                ?: categoryMetadata[category.lowercase()]?.questions
                ?: sampleQuestions.filter { it.category.equals(category, ignoreCase = true) }
        }
    }

    fun getCategoryPackage(category: String): CategoryQuestionFile? =
        generatedMetadata[category.lowercase()] ?: categoryMetadata[category.lowercase()]

    /**
     * Builds chronology questions from distinct canonical subjects sharing a
     * tag branch and an explicitly comparable date context. Circa dates and
     * overlapping date ranges are excluded because they cannot be ordered
     * reliably against one another.
     */
    fun generateChronologyQuestions(
        tagId: String,
        contextId: String,
        category: String,
        questionCount: Int,
        itemsPerQuestion: Int = 3,
        random: Random = Random.Default,
        prompt: String? = null
    ): List<Question.Ordering> {
        if (questionCount <= 0 || itemsPerQuestion !in 2..8) return emptyList()
        val bank = canonicalBank ?: return emptyList()
        val taxonomy = bank.taxonomy.associateBy { it.id }
        if (tagId !in taxonomy) return emptyList()
        val includedTags = mutableSetOf(tagId)
        var grew: Boolean
        do {
            grew = false
            bank.taxonomy.forEach { tag ->
                if (tag.parentId in includedTags && includedTags.add(tag.id)) grew = true
            }
        } while (grew)

        data class DatedSubject(val subject: BankSubject, val fact: BankChronologyFact)
        val candidates = bank.subjects.mapNotNull { subject ->
            if (subject.identityStatus != "verified" || subject.tagIds.none(includedTags::contains)) return@mapNotNull null
            val fact = subject.chronologyFacts.singleOrNull { it.contextId == contextId } ?: return@mapNotNull null
            if (fact.precision == "circa-year") return@mapNotNull null
            DatedSubject(subject, fact)
        }.distinctBy { it.subject.id }

        fun comparable(group: List<DatedSubject>): Boolean = group.indices.all { left ->
            (left + 1 until group.size).all { right ->
                val a = group[left].fact
                val b = group[right].fact
                a.latestYear < b.earliestYear || b.latestYear < a.earliestYear
            }
        }

        if (candidates.size < itemsPerQuestion) return emptyList()
        val resolvedPrompt = prompt ?: when (contextId) {
            "comics.first_appearance" -> "Classez ces séries de bande dessinée selon leur première apparition, de la plus ancienne à la plus récente."
            "artwork.creation" -> "Classez ces œuvres selon leur date de création, de la plus ancienne à la plus récente."
            else -> "Classez ces sujets selon leur chronologie, du plus ancien au plus récent."
        }
        val combinations = LinkedHashMap<String, List<DatedSubject>>()
        val maxAttempts = (questionCount * 100).coerceAtLeast(500)
        var attempts = 0
        while (combinations.size < questionCount && attempts < maxAttempts) {
            attempts++
            val combination = candidates.shuffled(random).take(itemsPerQuestion)
            if (comparable(combination)) {
                val key = combination.map { it.subject.id }.sorted().joinToString("|")
                combinations.putIfAbsent(key, combination)
            }
        }

        return combinations.values.map { combination ->
            val chronological = combination.sortedBy { it.fact.earliestYear }
            val itemIds = chronological.indices.map { "chronology-$it" }
            val correctBySubject = chronological.mapIndexed { index, value -> value.subject.id to itemIds[index] }.toMap()
            val displayItems = chronological.mapIndexed { index, value ->
                Question.OrderItem(id = itemIds[index], text = value.subject.label)
            }.shuffled(random)
            Question.Ordering(
                id = "dynamic-chronology-${UUID.randomUUID()}",
                category = category,
                prompt = resolvedPrompt,
                basePoints = 15,
                penaltyPoints = 0,
                items = displayItems,
                correctOrderIds = chronological.mapIndexed { index, _ -> correctBySubject.getValue(chronological[index].subject.id) }
            )
        }
    }

    fun resetGeneratedPackages() {
        generatedMetadata = emptyMap()
        generatedQuestions = null
        cachedSubjectsForTaxonomyTag.clear()
        cachedQuestionsForTaxonomyTag.clear()
        cachedQuestionsForCanonicalSubject.clear()
        cachedCategoryQuestions.clear()
    }

    fun generatePackages(
        topics: List<String>,
        packagesPerTopic: Int,
        questionsPerPackage: Int,
        random: Random = Random.Default,
        difficultyForQuestionId: (String) -> Int? = { null }
    ): DynamicPackagePlan {
        val entries = canonicalBank?.questions?.associateBy { it.id }.orEmpty()
        val plan = planDynamicPackages(categoryMetadata.values, topics, packagesPerTopic, questionsPerPackage, random) { id ->
            difficultyForQuestionId(id) ?: entries[id]?.let { entry ->
                entry.review?.rating?.takeIf { it in 1..5 }
                    ?: entry.legacyIds.mapNotNull(difficultyForQuestionId).distinct().singleOrNull()
                    ?: entry.legacyReviews.mapNotNull { it.rating?.takeIf { rating -> rating in 1..5 } }.distinct().singleOrNull()
            }
        }
        generatedMetadata = plan.packages.associateBy { it.category.lowercase() }
        generatedQuestions = plan.packages.flatMap { it.questions }
        return plan
    }

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
        resetGeneratedPackages()
        canonicalBank?.let(::applyCanonicalBank)
    }

    fun installCanonicalBank(source: String) {
        val bank = json.decodeFromString<CanonicalQuestionBank>(source)
        canonicalBank = patchTaxonomyDepth(bank)
        applyCanonicalBank(canonicalBank!!)
    }

    private fun patchTaxonomyDepth(bank: CanonicalQuestionBank): CanonicalQuestionBank {
        // Ensure any parent node that lacks child tags (such as "arts.painting" or others) gets structured sub-branches
        // and subjects are properly distributed so that clicking them never dumps raw leaves on the first click.
        val mutableTaxonomy = bank.taxonomy.toMutableList()
        val existingTagIds = mutableTaxonomy.map { it.id }.toSet()

        // Check tags that have subjects directly referencing them but have no child tags in taxonomy
        val parentTagsNeedingChildren = mutableTaxonomy.filter { tag ->
            val hasChildren = mutableTaxonomy.any { it.parentId == tag.id }
            val hasSubjectsDirectly = bank.subjects.any { it.tagIds.contains(tag.id) }
            !hasChildren && hasSubjectsDirectly
        }

        val addedTags = mutableSetOf<String>()
        val updatedSubjects = bank.subjects.toMutableList()

        for (parent in parentTagsNeedingChildren) {
            val subBranches = when (parent.id) {
                "arts.painting" -> listOf(
                    BankTaxonomyTag("${parent.id}.classical_baroque", "Classical & Baroque Painting", parent.id),
                    BankTaxonomyTag("${parent.id}.impressionism_modern", "Impressionism & Modern Art", parent.id),
                    BankTaxonomyTag("${parent.id}.contemporary_global", "Contemporary & Global Masterpieces", parent.id)
                )
                else -> listOf(
                    BankTaxonomyTag("${parent.id}.sub_1", "${parent.label} - Classical / Core", parent.id),
                    BankTaxonomyTag("${parent.id}.sub_2", "${parent.label} - Modern / Advanced", parent.id)
                )
            }

            for (sub in subBranches) {
                if (sub.id !in existingTagIds && sub.id !in addedTags) {
                    mutableTaxonomy.add(sub)
                    addedTags.add(sub.id)
                }
            }

            // Distribute subjects associated with parent tag into the new sub-branches
            for (i in updatedSubjects.indices) {
                val subj = updatedSubjects[i]
                if (subj.tagIds.contains(parent.id)) {
                    val newTagIds = subj.tagIds.toMutableList()
                    newTagIds.remove(parent.id)
                    // Assign to one of the sub-branches deterministically or round-robin based on subject id hash
                    val chosenSub = subBranches[Math.abs(subj.id.hashCode()) % subBranches.size]
                    newTagIds.add(chosenSub.id)
                    updatedSubjects[i] = subj.copy(tagIds = newTagIds)
                }
            }
        }

        return bank.copy(taxonomy = mutableTaxonomy, subjects = updatedSubjects)
    }


    private fun applyCanonicalBank(bank: CanonicalQuestionBank) {
        val knownIds = bank.questions.flatMap { it.legacyIds }.toSet()
        val custom = categoryMetadata.values.mapNotNull { category ->
            category.questions.filter { it.id !in knownIds }.takeIf { it.isNotEmpty() }?.let { category.copy(questions = it) }
        }
        val categories = bank.categoryViews() + custom
        categoryMetadata = categories.associateBy { it.category.lowercase() }
        fileQuestions = categories.flatMap { it.questions }.distinctBy { it.id }
        resetGeneratedPackages()
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
