package com.example.triviaparty.data

import com.example.triviaparty.model.CategoryAnswerMode
import com.example.triviaparty.model.CategoryQuestionFile
import com.example.triviaparty.model.Question
import kotlin.random.Random
import java.text.Normalizer

data class DynamicPackagePlan(
    val packages: List<CategoryQuestionFile>,
    val requestedQuestionsPerPackage: Int
) {
    val categories: List<String> get() = packages.map { it.category }
    val totalQuestions: Int get() = packages.sumOf { it.questions.size }
}

/** Builds one-format packages from the larger topic bank and balances formats across packages. */
fun planDynamicPackages(
    source: Collection<CategoryQuestionFile>,
    topics: List<String>,
    packagesPerTopic: Int,
    questionsPerPackage: Int,
    random: Random = Random.Default,
    difficultyForQuestionId: (String) -> Int? = { null }
): DynamicPackagePlan {
    if (topics.isEmpty() || packagesPerTopic <= 0 || questionsPerPackage <= 0) {
        return DynamicPackagePlan(emptyList(), questionsPerPackage.coerceAtLeast(1))
    }

    data class Format(val label: String, val mode: CategoryAnswerMode, val questionClass: String) {
        val key = "$label|$mode|$questionClass"
        val balanceKey = "$label|$mode"
    }
    data class Candidate(val sourceCategory: String, val question: Question)

    val pools = linkedMapOf<String, LinkedHashMap<String, MutableList<Candidate>>>()
    val formats = linkedMapOf<String, Format>()

    fun add(topic: String, format: Format, sourceCategory: String, question: Question) {
        formats.putIfAbsent(format.key, format)
        pools.getOrPut(topic) { linkedMapOf() }
            .getOrPut(format.key) { mutableListOf() }
            .add(Candidate(sourceCategory, question))
    }

    source.forEach { file ->
        val topic = file.subject?.trim()?.takeIf(String::isNotEmpty) ?: subjectGroup(file.category)
        val originalType = file.questionTypes.firstOrNull() ?: "Questions variées"
        file.questions.forEach questionLoop@ { question ->
            when (question) {
                is Question.MultipleChoice -> {
                    add(topic, Format(originalType, file.answerMode, question::class.qualifiedName.orEmpty()), file.category, question)
                    // Keep the authored choices for QCM, hide them for free response.
                    // Variants with changing answers and prompts referring to choices need those choices.
                    if (question.randomVariants.isEmpty() && !Regex("(?i)parmi|suivant|ci-dessous|lequel|laquelle").containsMatchIn(question.prompt)) {
                        val answer = question.options.getOrNull(question.correctOptionIndex)?.withoutChoiceLabel().orEmpty()
                        if (answer.isNotBlank()) {
                            val open = Question.TextAnswer(question.id, question.category, question.prompt,
                                question.imageUrl, question.basePoints, question.penaltyPoints,
                                listOf(answer), conceptId = question.conceptId, explanation = question.explanation)
                            add(topic, Format("Buzzer", CategoryAnswerMode.BUZZER, open::class.qualifiedName.orEmpty()), file.category, open)
                            add(topic, Format("Réponses écrites", CategoryAnswerMode.WRITTEN, open::class.qualifiedName.orEmpty()), file.category, open)
                        }
                    }
                }
                is Question.TextAnswer -> {
                    add(topic, Format("Buzzer", CategoryAnswerMode.BUZZER, question::class.qualifiedName.orEmpty()), file.category, question)
                    add(topic, Format("Réponses écrites", CategoryAnswerMode.WRITTEN, question::class.qualifiedName.orEmpty()), file.category, question)
                }
                is Question.GuessWho -> {
                    add(topic, Format("Qui suis-je ?", CategoryAnswerMode.BUZZER, question::class.qualifiedName.orEmpty()), file.category, question)
                    add(topic, Format("Qui suis-je ? écrit", CategoryAnswerMode.WRITTEN, question::class.qualifiedName.orEmpty()), file.category, question)
                }
                else -> add(topic, Format(originalType, file.answerMode, question::class.qualifiedName.orEmpty()), file.category, question)
            }
        }
    }

    val slots = topics.flatMap { topic -> List(packagesPerTopic) { topic } }
    val useCounts = mutableMapOf<String, Int>()
    val topicUseCounts = mutableMapOf<Pair<String, String>, Int>()
    val sameFormatIndex = mutableMapOf<Pair<String, String>, Int>()
    val usedQuestionIds = mutableSetOf<String>()
    val usedConcepts = mutableSetOf<String>()
    val packages = mutableListOf<CategoryQuestionFile>()
    slots.forEach { topic ->
        val topicPools = pools[topic].orEmpty()
        val remaining = topicPools.mapValues { (_, candidates) -> candidates.filter {
            it.question.id !in usedQuestionIds && it.question.semanticKey() !in usedConcepts
        }.shuffled(random).distinctBy { it.question.semanticKey() } }
        val options = remaining.filterValues { it.isNotEmpty() }.keys
        if (options.isEmpty()) return@forEach
        val fullPackages = options.filter { key -> remaining.getValue(key).distinctBy { it.question.id }.size >= questionsPerPackage }
        val largestRemaining = options.maxOf { remaining.getValue(it).size }
        val eligibleFormats = fullPackages.ifEmpty { options.filter { remaining.getValue(it).size == largestRemaining } }
        val chosen = eligibleFormats.shuffled(random).minWithOrNull(
            compareBy<String>({ useCounts[formats.getValue(it).balanceKey] ?: 0 },
                { topicUseCounts[topic to formats.getValue(it).balanceKey] ?: 0 })
        ) ?: return@forEach
        val formatKey = chosen
        val format = formats.getValue(formatKey)
        useCounts[format.balanceKey] = (useCounts[format.balanceKey] ?: 0) + 1
        topicUseCounts[topic to format.balanceKey] = (topicUseCounts[topic to format.balanceKey] ?: 0) + 1
        val available = remaining.getValue(formatKey)
        val unique = available.distinctBy { it.question.id }
        if (unique.isEmpty()) return@forEach
        val selected = mutableListOf<Candidate>()
        var easyCount = 0
        var hardCount = 0
        val ordered = unique.shuffled(random).toMutableList()
        while (selected.size < questionsPerPackage && ordered.isNotEmpty()) {
            val eligibleIndex = ordered.indexOfFirst { candidate ->
                val rating = difficultyForQuestionId(candidate.question.id)
                (rating != 1 || easyCount == 0) && (rating != 5 || hardCount == 0)
            }
            if (eligibleIndex < 0) break
            val candidate = ordered.removeAt(eligibleIndex)
            selected += candidate
            when (difficultyForQuestionId(candidate.question.id)) {
                1 -> easyCount++
                5 -> hardCount++
            }
        }
        if (selected.isEmpty()) return@forEach

        val indexKey = topic to formatKey
        val index = (sameFormatIndex[indexKey] ?: 0) + 1
        sameFormatIndex[indexKey] = index
        val title = if (index == 1) "$topic — ${format.label}" else "$topic — ${format.label} $index"
        val questions = selected.map { it.question.withCategory(title) }
        usedQuestionIds += selected.map { it.question.id }
        usedConcepts += selected.map { it.question.semanticKey() }
        packages += CategoryQuestionFile(
            category = title,
            answerMode = format.mode,
            questionTypes = listOf(format.label),
            questions = questions,
            subject = topic
        )
    }
    return DynamicPackagePlan(packages, questionsPerPackage)
}

private fun String.withoutChoiceLabel(): String = replace(Regex("^[A-Z]\\s*[—–:.)-]\\s*"), "").trim()

private fun Question.semanticKey(): String {
    fun norm(value: String) = Normalizer.normalize(value.lowercase(), Normalizer.Form.NFD)
        .replace(Regex("\\p{Mn}+"), "").replace(Regex("[^a-z0-9]+"), " ").trim()
    val concept = when (this) {
        is Question.MultipleChoice -> conceptId
        is Question.TextAnswer -> conceptId
        is Question.GuessWho -> conceptId
        else -> null
    }
    if (!concept.isNullOrBlank()) return "concept:$concept"
    val answer = when (this) {
        is Question.MultipleChoice -> options.getOrNull(correctOptionIndex).orEmpty().withoutChoiceLabel()
        is Question.Ordering -> correctOrderIds.mapNotNull { id -> items.firstOrNull { it.id == id }?.text }.joinToString(" ")
        is Question.TextAnswer -> acceptableAnswers.firstOrNull().orEmpty()
        is Question.GuessWho -> acceptableAnswers.firstOrNull().orEmpty()
        is Question.MapPin -> prompt
        is Question.Wager -> subQuestion.prompt
        is Question.SpeedRace -> subQuestion.prompt
    }
    val questionText = if (this is Question.GuessWho) clues.joinToString(" ") else prompt
    val family = if (this is Question.MultipleChoice || this is Question.TextAnswer) "direct" else this::class.simpleName
    return "$family|${norm(questionText)}|${norm(answer)}"
}

private fun Question.withCategory(category: String): Question = when (this) {
    is Question.MultipleChoice -> copy(category = category)
    is Question.Ordering -> copy(category = category)
    is Question.TextAnswer -> copy(category = category)
    is Question.GuessWho -> copy(category = category)
    is Question.MapPin -> copy(category = category)
    is Question.Wager -> copy(category = category, subQuestion = subQuestion.copy(category = category))
    is Question.SpeedRace -> copy(category = category, subQuestion = subQuestion.copy(category = category))
}
