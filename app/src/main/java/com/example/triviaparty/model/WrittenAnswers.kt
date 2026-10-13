package com.example.triviaparty.model

fun GameSession.pendingWrittenAnswers(): List<AnswerSubmission> = submissions.values.filter {
    it.questionId==currentQuestion?.id && it.isLocked && it.isCorrect==null && it.answer is AnswerValue.TextSelection
}.sortedWith(compareBy({it.timestamp},{it.teamId}))
