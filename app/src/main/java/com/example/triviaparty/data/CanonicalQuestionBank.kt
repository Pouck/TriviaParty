package com.example.triviaparty.data

import com.example.triviaparty.model.CategoryAnswerMode
import com.example.triviaparty.model.CategoryQuestionFile
import com.example.triviaparty.model.Question
import com.example.triviaparty.model.ImageQuestionFacts
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*

/** Authoring storage is question-first. Category files below are transient game views. */
@Serializable
data class CanonicalQuestionBank(
    val schemaVersion: Int,
    val questions: List<BankQuestion>,
    val subjects: List<BankSubject> = emptyList(),
    val taxonomy: List<BankTaxonomyTag> = emptyList()
) {
    init {
        require(schemaVersion in 2..3)
        require(questions.map { it.id }.distinct().size == questions.size)
        val aliases = questions.flatMap { it.legacyIds }
        require(aliases.distinct().size == aliases.size)
        if (schemaVersion >= 3) {
            val subjectIds = subjects.map { it.id }.toSet()
            val tagIds = taxonomy.map { it.id }.toSet()
            require(subjectIds.size == subjects.size && subjectIds.isNotEmpty())
            require(tagIds.size == taxonomy.size)
            require(questions.all { question -> question.subjectIds.isNotEmpty() && question.subjectIds.all(subjectIds::contains) })
            require(subjects.flatMap { it.relations }.all { it.targetId in subjectIds })
            require(subjects.flatMap { it.tagIds }.all(tagIds::contains))
            require(taxonomy.all { it.parentId == null || it.parentId in tagIds })
        }
    }

    fun categoryViews(): List<CategoryQuestionFile> {
        val json = Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }
        val views = questions.flatMap { entry -> entry.presentations.map { entry to it } }
            .groupBy { (_, presentation) -> presentation.legacyCategory }
        return views.map { (category, records) ->
            val presentation = records.first().second
            CategoryQuestionFile(category = category, answerMode = presentation.answerMode,
                questionTypes = listOf(presentation.label), subject = presentation.topic,
                questions = records.map { (entry, variant) ->
                    val content = entry.content.toMutableMap().apply {
                        putAll(variant.content)
                        put("id", JsonPrimitive(entry.id))
                        put("category", JsonPrimitive(category))
                        putIfAbsent("prompt", JsonPrimitive(entry.prompt))
                        val kind = getValue("kind").jsonPrimitive.content
                        if (kind in setOf("textAnswer", "guessWho"))
                            putIfAbsent("acceptableAnswers", JsonArray(entry.answers.map(::JsonPrimitive)))
                        if (kind in setOf("multipleChoice", "textAnswer", "guessWho"))
                            put("conceptId", JsonPrimitive(entry.id))
                        entry.explanation?.let { putIfAbsent("explanation", JsonPrimitive(it)) }
                        entry.imageFacts?.let { put("imageFacts", json.encodeToJsonElement(it)) }
                        fun media(value: JsonElement?): JsonElement? = value?.jsonPrimitive?.contentOrNull?.let {
                            JsonPrimitive("local-media://canonical-bank/images/${it.removePrefix("media/")}")
                        }
                        media(get("imageUrl"))?.let { put("imageUrl", it) }
                        (get("subQuestion") as? JsonObject)?.let { sub ->
                            put("subQuestion", JsonObject(sub.toMutableMap().apply {
                                media(get("imageUrl"))?.let { put("imageUrl", it) }
                            }))
                        }
                    }
                    json.decodeFromJsonElement<Question>(JsonObject(content))
                })
        }
    }
}

@Serializable
data class BankQuestion(val id: String, val legacyIds: List<String>, val topics: List<String>,
    val prompt: String, val answers: List<String> = emptyList(), val content: JsonObject = JsonObject(emptyMap()),
    val explanation: String? = null, val presentations: List<BankPresentation>,
    val subjectIds: List<String> = emptyList(),
    val legacyReviews: List<BankLegacyReview> = emptyList(),
    val review: BankLegacyReview? = null,
    val imageFacts: ImageQuestionFacts? = null) {
    init {
        require(id in legacyIds && topics.isNotEmpty() && presentations.isNotEmpty())
        // A merged question may retain legacy aliases whose original presentations were
        // intentionally retired. Every active presentation must still have an alias.
        require(presentations.all { it.id in legacyIds })
    }
}

@Serializable
data class BankLegacyReview(val questionId: String, val rating: Int? = null)

@Serializable
data class BankSubject(
    val id: String,
    val type: String,
    val label: String,
    val aliases: List<String> = emptyList(),
    val tagIds: List<String> = emptyList(),
    val relations: List<BankSubjectRelation> = emptyList(),
    val facts: List<BankSubjectFact> = emptyList(),
    val chronologyEvidence: List<BankChronologyEvidence> = emptyList(),
    val sourceQuestionIds: List<String> = emptyList(),
    val identityStatus: String,
    val sources: List<String> = emptyList(),
    val candidateSubjectIds: List<String> = emptyList()
)

@Serializable
data class BankSubjectRelation(val type: String, val targetId: String, val role: String? = null)

@Serializable
data class BankSubjectFact(
    val kind: String,
    val value: String,
    val role: String? = null,
    val sourceUrl: String? = null
)

@Serializable
data class BankChronologyEvidence(
    val sourceQuestionId: String,
    val sourceSetId: String,
    val sourcePrompt: String,
    val position: Int? = null,
    val itemId: String? = null
)

@Serializable
data class BankTaxonomyTag(val id: String, val label: String, val parentId: String? = null)

@Serializable
data class BankPresentation(val id: String, val label: String, val answerMode: CategoryAnswerMode,
    val topic: String, val legacyCategory: String, val legacyPackageId: String, val content: JsonObject)
