package com.example.triviaparty.model

enum class BuzzerStatus(val label: String) {
    WAITING("En attente"), READY("À vous de jouer"), PRESSED("Vous avez la parole"),
    BLOCKED("Une autre équipe répond"), INCORRECT("Mauvaise réponse · désactivé"),
    CORRECT("Bonne réponse"), ENDED("Partie terminée"), DISCONNECTED("Reconnexion…")
}

fun GameSession.usesPlayerBuzzer(): Boolean {
    if(currentCategoryAnswerMode==CategoryAnswerMode.WRITTEN) return false
    if (currentQuestion is Question.MultipleChoice || currentQuestion is Question.SpeedRace) return false
    return currentQuestion?.isOralBuzzerQuestion() == true || currentCategoryAnswerMode == CategoryAnswerMode.BUZZER ||
        (currentQuestion == null && currentCategoryAnswerMode == null)
}

fun GameSession.buzzerStatus(teamId: String, connected: Boolean, pressed: Boolean = false): BuzzerStatus {
    if (!connected) return BuzzerStatus.DISCONNECTED
    if (state == GameState.GAME_ENDED) return BuzzerStatus.ENDED
    val own = submissions[teamId]
    if (own?.isCorrect == false || teamId in textBuzzedTeamIds) return BuzzerStatus.INCORRECT
    if (own?.isCorrect == true) return BuzzerStatus.CORRECT
    if (state != GameState.QUESTION_ACTIVE || questionReading || currentQuestion == null) return BuzzerStatus.WAITING
    if (own?.isLocked == true || pressed) return BuzzerStatus.PRESSED
    if (submissions.values.any { it.isLocked && it.isCorrect != false && it.isBuzz() }) return BuzzerStatus.BLOCKED
    return BuzzerStatus.READY
}
