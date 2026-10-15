package com.example.triviaparty.data

import java.io.File
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable data class QuestionReview(val questionId: String, val category: String, val prompt: String,
    val comment: String = "", val difficulty: Int? = null, val updatedAt: Long = 0)
@Serializable data class ResolvedQuestionReview(val review: QuestionReview, val resolvedAt: Long)
@Serializable data class PackageUsage(val plays: Int = 0, val lastPlayed: Long = 0)
@Serializable data class HostReviewData(val reviews: Map<String, QuestionReview> = emptyMap(),
    val usage: Map<String, PackageUsage> = emptyMap(), val countedSession: String = "",
    val countedPackages: Set<String> = emptySet(), val resolvedReviews: List<ResolvedQuestionReview> = emptyList())

/** Independent of package imports: corrections and updates retain notes and usage by stable ID. */
class HostReviewStore(private val file: File) {
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true }
    fun read(): HostReviewData = if (file.exists()) json.decodeFromString(file.readText()) else HostReviewData()
    private fun write(data: HostReviewData) {
        file.parentFile?.mkdirs()
        val temporary = File(file.parentFile, file.name + ".tmp")
        temporary.writeText(json.encodeToString(HostReviewData.serializer(), data))
        if(!temporary.renameTo(file)) {
            // Windows does not consistently replace an existing destination with renameTo.
            if(android.os.Build.VERSION.SDK_INT>=26 || System.getProperty("os.name").orEmpty().startsWith("Windows")) {
                replaceReviewFile(temporary,file)
            } else error("Impossible d’enregistrer les notes")
        }
    }
    fun saveReview(review: QuestionReview) {
        require(review.difficulty == null || review.difficulty in 0..5)
        val data = read()
        write(data.copy(reviews = data.reviews + (review.questionId to review.copy(updatedAt = System.currentTimeMillis()))))
    }
    /** Clear addressed feedback only; guard against clearing a newer comment. */
    fun resolveReview(questionId: String, expectedUpdatedAt: Long): Boolean {
        val data = read()
        val review = data.reviews[questionId] ?: return false
        if (review.updatedAt != expectedUpdatedAt) return false
        val retained = review.copy(comment = "", difficulty = review.difficulty?.takeIf { it > 0 }, updatedAt = System.currentTimeMillis())
        val reviews = if (retained.difficulty == null) data.reviews - questionId else data.reviews + (questionId to retained)
        write(data.copy(reviews = reviews, resolvedReviews = data.resolvedReviews + ResolvedQuestionReview(review, System.currentTimeMillis())))
        return true
    }
    fun recordPackages(ids: List<String>, sessionId: String? = null) {
        val data = read(); val now = System.currentTimeMillis()
        val counted = if(sessionId != null && sessionId==data.countedSession) data.countedPackages else emptySet()
        val fresh = ids.distinct().filter { it !in counted }
        write(data.copy(usage = data.usage + fresh.associateWith {
            PackageUsage((data.usage[it]?.plays ?: 0) + 1, now)
        }, countedSession=sessionId ?: "", countedPackages=counted + fresh))
    }
    fun resetUsage() = write(read().copy(usage = emptyMap(),countedSession="",countedPackages=emptySet()))
}

@android.annotation.SuppressLint("NewApi")
private fun replaceReviewFile(source: File,destination: File) {
    try { java.nio.file.Files.move(source.toPath(),destination.toPath(),java.nio.file.StandardCopyOption.REPLACE_EXISTING,java.nio.file.StandardCopyOption.ATOMIC_MOVE) }
    catch(_:java.nio.file.AtomicMoveNotSupportedException) { java.nio.file.Files.move(source.toPath(),destination.toPath(),java.nio.file.StandardCopyOption.REPLACE_EXISTING) }
}

/** Prefer least-played packages, then balance subject and format, then avoid recent repeats. */
fun selectBalancedPackages(ids: List<String>, count: Int, usage: Map<String, PackageUsage>,
    profile: (String) -> CategoryProfile, onePerSubject: Boolean = false,
    random: kotlin.random.Random = kotlin.random.Random.Default, subjectLimit: Int? = null): List<String> {
    val remaining = ids.distinct().shuffled(random).toMutableList()
    val profiles = remaining.associateWith(profile)
    val selected = mutableListOf<String>()
    val formats = mutableMapOf<CategoryFormat, Int>()
    val subjects = mutableMapOf<String, Int>()
    repeat(count.coerceIn(0, remaining.size)) {
        val candidates = remaining.filter { candidate ->
            val used = subjects[profiles.getValue(candidate).subject] ?: 0
            (!onePerSubject || used==0) && (subjectLimit==null || used<subjectLimit)
        }
        if (candidates.isEmpty()) return selected
        val choice = candidates.minWith(compareBy<String>(
            { usage[it]?.plays ?: 0 },
            { id -> profiles.getValue(id).let { (formats[it.format] ?: 0) + (subjects[it.subject] ?: 0) } },
            { usage[it]?.lastPlayed ?: 0 }))
        selected.add(choice); remaining.remove(choice)
        val chosen = profiles.getValue(choice)
        formats[chosen.format] = (formats[chosen.format] ?: 0) + 1
        subjects[chosen.subject] = (subjects[chosen.subject] ?: 0) + 1
    }
    return selected
}


/** Draw whole subject sets so “6 × 2” really yields six subjects with two packages each. */
fun selectBalancedCategorySets(ids: List<String>, subjectCount: Int, setsPerSubject: Int,
    usage: Map<String, PackageUsage>, profile: (String) -> CategoryProfile,
    random: kotlin.random.Random = kotlin.random.Random.Default): List<String> {
    val sets=setsPerSubject.coerceIn(1,50)
    val profiles=ids.distinct().associateWith(profile)
    val eligible=profiles.keys.groupBy { profiles.getValue(it).subject }.filterValues { it.size>=sets }.values.flatten()
    val representatives=selectBalancedPackages(eligible,subjectCount.coerceIn(1,50),usage,profiles::getValue,onePerSubject=true,random=random)
    val subjects=representatives.map { profiles.getValue(it).subject }.toSet()
    return selectBalancedPackages(eligible.filter { profiles.getValue(it).subject in subjects },subjects.size*sets,usage,profiles::getValue,random=random,subjectLimit=sets)
}
