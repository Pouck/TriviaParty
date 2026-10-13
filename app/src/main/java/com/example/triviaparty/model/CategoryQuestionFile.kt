package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
enum class CategoryAnswerMode { SIMULTANEOUS, BUZZER, WRITTEN }

fun CategoryAnswerMode.label(): String = when (this) {
    CategoryAnswerMode.SIMULTANEOUS -> "Réponses simultanées"
    CategoryAnswerMode.BUZZER -> "Buzzer"
    CategoryAnswerMode.WRITTEN -> "Réponses écrites"
}

/** One editable JSON file per category in app/src/main/assets/question-bank/. */
@Serializable
data class CategoryQuestionFile(
    val category: String,
    val answerMode: CategoryAnswerMode = CategoryAnswerMode.SIMULTANEOUS,
    val answerTimeSeconds: Int = 0,
    val questionTypes: List<String> = emptyList(),
    val questions: List<Question>,
    val subject: String? = null
) {
    init {
        require(questions.isNotEmpty()) { "Category '$category' must contain at least one question" }
        require(questions.map { it::class }.distinct().size == 1) {
            "All questions in category '$category' must use the same format"
        }
        require(questionTypes.size == 1) {
            "Category '$category' must declare exactly one question type"
        }
        require(answerTimeSeconds >= 0) { "Category '$category' cannot have a negative answer timer" }
        require(questions.none { it is Question.GuessWho } || answerMode in setOf(CategoryAnswerMode.BUZZER,CategoryAnswerMode.WRITTEN)) {
            "Qui suis-je ? doit utiliser le mode Buzzer ou Réponses écrites."
        }
        require(answerMode!=CategoryAnswerMode.WRITTEN || questions.all { it is Question.TextAnswer || it is Question.GuessWho }) { "Les réponses écrites nécessitent des questions à réponse libre." }
    }
}
