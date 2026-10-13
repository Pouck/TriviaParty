package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
sealed class AnswerValue {
    @Serializable
    data class MultipleChoiceSelection(val optionIndex: Int) : AnswerValue()

    @Serializable
    data class OrderingSelection(val orderedItemIds: List<String>) : AnswerValue()

    @Serializable
    data class TextSelection(val text: String) : AnswerValue()

    @Serializable
    data class MapPinSelection(val xRatio: Float, val yRatio: Float) : AnswerValue()

    @Serializable
    data class WagerSelection(val wageredAmount: Int, val subAnswerOptionIndex: Int) : AnswerValue()
}

@Serializable
data class AnswerSubmission(
    val teamId: String,
    val questionId: String,
    val answer: AnswerValue,
    val isLocked: Boolean,
    val timestamp: Long,
    val flipNumberWhenLocked: Int,
    val elapsedSecondsInFlipWhenLocked: Int = 0,
    val isCorrect: Boolean? = null
)

fun AnswerSubmission.isBuzz(): Boolean = (answer as? AnswerValue.TextSelection)?.text == "BUZZ"
