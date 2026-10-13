package com.example.triviaparty.model

/** Shared choice grading for scoring and the TV's immediate submitted-card feedback. */
fun Question.choiceVerdict(answer: AnswerValue): Boolean? = when(this) {
    is Question.MultipleChoice -> (answer as? AnswerValue.MultipleChoiceSelection)?.optionIndex == correctOptionIndex
    is Question.SpeedRace -> (answer as? AnswerValue.MultipleChoiceSelection)?.optionIndex == subQuestion.correctOptionIndex
    is Question.Wager -> (answer as? AnswerValue.WagerSelection)?.subAnswerOptionIndex == subQuestion.correctOptionIndex
    is Question.MapPin -> if(options.isEmpty()) null else {
        val pin=answer as? AnswerValue.MapPinSelection
        pin!=null && options.indexOfFirst { kotlin.math.abs(it.xRatio-pin.xRatio)<0.001f && kotlin.math.abs(it.yRatio-pin.yRatio)<0.001f } == correctOptionIndex
    }
    else -> null
}
