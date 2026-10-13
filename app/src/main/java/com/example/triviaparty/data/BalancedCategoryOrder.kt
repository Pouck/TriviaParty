package com.example.triviaparty.data

import com.example.triviaparty.model.Question
import com.example.triviaparty.model.isChronologyQuestion
import kotlin.random.Random

enum class CategoryFormat { QCM, BUZZER, GUESS_WHO, WRITTEN, CHRONOLOGY, SPEED_RACE, MIXED }

data class CategoryProfile(val format: CategoryFormat, val subject: String)

fun categoryFormatFor(question: Question): CategoryFormat = when {
    question is Question.Wager -> categoryFormatFor(question.subQuestion)
    question is Question.GuessWho -> CategoryFormat.GUESS_WHO
    question.isChronologyQuestion() -> CategoryFormat.CHRONOLOGY
    question is Question.TextAnswer -> CategoryFormat.BUZZER
    question is Question.SpeedRace -> CategoryFormat.SPEED_RACE
    else -> CategoryFormat.QCM
}

fun categoryProfileFor(category: String): CategoryProfile {
    val formats = QuestionBankRepository.getQuestionsForCategory(category).map(::categoryFormatFor).distinct()
    val metadata = QuestionBankRepository.getCategoryPackage(category)
    val subject = metadata?.subject?.takeIf { it.isNotBlank() } ?: subjectGroup(category).let { inferred ->
        if (inferred != "Autres") inferred else GamePackageRepository.packages.firstOrNull {
            category in GamePackageRepository.categoryNamesFor(it)
        }?.browseGroup() ?: inferred
    }
    return CategoryProfile(if(metadata?.answerMode==com.example.triviaparty.model.CategoryAnswerMode.WRITTEN) CategoryFormat.WRITTEN else formats.singleOrNull() ?: CategoryFormat.MIXED, subject)
}

/**
 * Schedule whole categories, balancing both format and subject. The bounded search keeps
 * alternative paths so a locally attractive choice does not immediately exhaust a separator.
 * Repetitions come first, long runs second, then proportional spread throughout the game.
 * Random ties and shuffled buckets give a fresh order each game without changing package rules.
 */
fun balancedCategoryOrder(
    categories: List<String>,
    profileFor: (String) -> CategoryProfile,
    random: Random = Random.Default
): List<String> {
    val unique = categories.distinct()
    if (unique.size < 2) return unique
    val buckets = unique.groupBy { category ->
        val profile = profileFor(category)
        profile.copy(subject = searchablePackageText(profile.subject.trim()))
    }.entries.shuffled(random)
    val profiles = buckets.map { it.key }
    val queues = buckets.map { it.value.shuffled(random) }
    val totals = queues.map { it.size }
    val formatTotals = profiles.indices.groupBy { profiles[it].format }
        .mapValues { (_, indices) -> indices.sumOf { totals[it] } }
    val subjectTotals = profiles.indices.groupBy { profiles[it].subject }
        .mapValues { (_, indices) -> indices.sumOf { totals[it] } }
    val formatIndices = profiles.map { formatTotals.keys.indexOf(it.format) }
    val subjectIndices = profiles.map { subjectTotals.keys.indexOf(it.subject) }
    data class Path(
        val order: List<Int>, val used: List<Int>, val formatUsed: List<Int>, val subjectUsed: List<Int>,
        val last: Int = -1, val formatRun: Int = 0, val subjectRun: Int = 0,
        val repetitions: Int = 0, val runCost: Int = 0, val spreadCost: Double = 0.0
    )
    data class Key(val used: List<Int>, val last: Int, val formatRun: Int, val subjectRun: Int)
    val comparator = compareBy<Path>({ it.repetitions }, { it.runCost }, { it.spreadCost })
    var paths = listOf(Path(emptyList(), List(buckets.size) { 0 },
        List(formatTotals.size) { 0 }, List(subjectTotals.size) { 0 }))
    repeat(unique.size) { step ->
        val next = HashMap<Key, Path>()
        paths.forEach { previous ->
            profiles.indices.filter { previous.used[it] < totals[it] }.forEach { index ->
                val sameFormat = previous.last >= 0 && profiles[previous.last].format == profiles[index].format
                val sameSubject = previous.last >= 0 && profiles[previous.last].subject == profiles[index].subject
                val formatRun = if (sameFormat) previous.formatRun + 1 else 1
                val subjectRun = if (sameSubject) previous.subjectRun + 1 else 1
                val used = previous.used.toMutableList().apply { this[index]++ }
                val formatUsed = previous.formatUsed.toMutableList().apply { this[formatIndices[index]]++ }
                val subjectUsed = previous.subjectUsed.toMutableList().apply { this[subjectIndices[index]]++ }
                val fraction = (step + 1).toDouble() / unique.size
                fun deviation(counts: List<Int>, axisTotals: Collection<Int>): Double =
                    counts.zip(axisTotals).sumOf { (count, total) ->
                        val error = count - total * fraction
                        error * error
                    }
                val candidate = Path(previous.order + index, used, formatUsed, subjectUsed, index,
                    formatRun, subjectRun,
                    previous.repetitions + (if (sameFormat) 1 else 0) + (if (sameSubject) 1 else 0),
                    previous.runCost + (if (sameFormat) formatRun else 0) + (if (sameSubject) subjectRun else 0),
                    previous.spreadCost + deviation(formatUsed, formatTotals.values) + deviation(subjectUsed, subjectTotals.values))
                val key = Key(used, index, formatRun, subjectRun)
                val existing = next[key]
                if (existing == null || comparator.compare(candidate, existing) < 0) next[key] = candidate
            }
        }
        // Shuffle before the stable sort so equal-quality plans do not depend on map iteration.
        paths = next.values.shuffled(random).sortedWith(comparator).take(64)
    }
    val best = paths.minWith(comparator)
    val offsets = IntArray(buckets.size)
    return best.order.map { index -> queues[index][offsets[index]++] }
}
