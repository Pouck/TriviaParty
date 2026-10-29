package com.example.triviaparty.model

/** Chronology choices need a reading phase before any answer can be submitted. */
fun Question.isChronologyQuestion(): Boolean = this is Question.Ordering ||
    (this is Question.MultipleChoice && options.size == 4 && options.all { "→" in it })

/** Existing chronology ZIPs become draggable cards without changing their answer keys. */
fun Question.withChronologyCards(): Question {
    if (this !is Question.MultipleChoice || !isChronologyQuestion()) return this
    fun events(option: String) = option.replace(Regex("^[A-D]\\s*[—.)\\-:]\\s*"), "")
        .split("→").map { it.trim() }
    val correct = options.getOrNull(correctOptionIndex)?.let(::events) ?: return this
    if (correct.size < 2 || correct.any { it.isBlank() } || correct.distinct().size != correct.size ||
        options.any { events(it).size != correct.size || events(it).toSet() != correct.toSet() }) return this
    val listed = prompt.lines().drop(1).map { it.trim().removePrefix("•").trim() }.filter { it.isNotEmpty() }
    var display = if (listed.size == correct.size && listed.toSet() == correct.toSet()) listed
        else correct.shuffled(kotlin.random.Random(id.hashCode()))
    if (display == correct) display = display.drop(1) + display.first()
    // IDs follow the public display order, never the secret chronological order.
    val cards = display.mapIndexed { index, text -> Question.OrderItem("event-$index", text) }
    val heading = prompt.substringBefore('\n')
        .replace(Regex("^Quel (?:est l’ordre chronologique|ordre va),? du plus ancien au plus récent,? pour "), "Classez ")
        .replace(Regex("^Quel ordre va du plus ancien au plus récent pour "), "Classez ")
        .replace(Regex("\\s*— du plus ancien au plus récent\\s*:?") , "")
        .trim().removeSuffix("?").removeSuffix(":").trim()
    return Question.Ordering(id, category, heading, imageUrl, basePoints, penaltyPoints,
        cards, correct.map { text -> cards.first { it.text == text }.id })
}

/** A rejected clue costs one equal share of the initial reward. */
fun Question.GuessWho.wrongAnswerPenalty(): Int =
    if (penaltyPoints > 0) penaltyPoints else
        (basePoints / if (imageRevealMode == ImageRevealMode.NONE) clues.size else imageRevealSteps).coerceAtLeast(1)

fun GameSession.rejectOralAnswer(teamId: String): GameSession {
    val submission = submissions[teamId] ?: return this
    if (!submission.isLocked || submission.isCorrect != null) return this
    val penalty = (currentQuestion as? Question.GuessWho)?.wrongAnswerPenalty() ?: 0
    return copy(
        teams = teams.map { if (it.id == teamId) it.copy(score=it.score-penalty) else it },
        submissions = submissions + (teamId to submission.copy(isCorrect=false)),
        textBuzzedTeamIds = (textBuzzedTeamIds + teamId).distinct(),
        answerTimerTeamId=null,answerTimerRemainingSeconds=null,answerTimerRunning=false)
}


/** Derive public format labels from actual questions, including legacy banks without metadata. */
fun Question.publicFormatLabel(mode: CategoryAnswerMode?): String = when {
    isChronologyQuestion() -> "Chronologie"
    this is Question.GuessWho -> if(mode==CategoryAnswerMode.WRITTEN) "Qui suis-je ? — réponse écrite" else "Qui suis-je ?"
    this is Question.TextAnswer -> if(mode==CategoryAnswerMode.WRITTEN) "Réponse écrite" else "Buzzer"
    this is Question.MapPin -> "Carte — choix multiples"
    this is Question.Wager -> "Choix multiples avec mise"
    this is Question.SpeedRace -> "Choix multiples — rapidité"
    else -> "Choix multiples"
}
