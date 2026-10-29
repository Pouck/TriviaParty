package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
data class CategoryWagerResult(val teamId: String, val teamName: String, val amount: Int,
    val correct: Boolean, val delta: Int)

@Serializable enum class CategoryWagerStatus { PENDING, ACCEPTED, REJECTED }

@Serializable
data class CategoryWagerProposal(
    val id:String,
    val amount:Int,
    val proposerPlayerId:String,
    /** Connected teammates captured when this proposal was made. */
    val eligiblePlayerIds:List<String>,
    val approvedPlayerIds:List<String> = emptyList(),
    val rejectedPlayerIds:List<String> = emptyList(),
    val status:CategoryWagerStatus = CategoryWagerStatus.PENDING
) {
    val approvalThreshold:Int get()=eligiblePlayerIds.size/2+1
}

fun categoryWagerLimit(score: Int, maximumReward: Int): Int =
    maxOf(score, maximumReward, 0)

/** Top three teams plus every team tied with the third team. */
fun List<Team>.leadersWithTies(): List<Team> {
    val sorted = sortedWith(compareByDescending<Team> { it.score }.thenBy { it.name })
    val cutoff = sorted.getOrNull(2)?.score ?: return sorted
    return sorted.takeWhile { it.score >= cutoff }
}

/** Called after ordinary question scoring; missing or incorrect answers lose the stake. */
fun GameSession.settleCategoryWagers(): GameSession {
    if (categoryWagerSettled || categoryWagerQuestionId == null || currentQuestion?.id != categoryWagerQuestionId) return this
    val results = teams.filter { it.id in categoryWagerLimits }.map { team ->
        val amount = (categoryWagers[team.id] ?: 0).coerceIn(0, categoryWagerLimits.getValue(team.id))
        val sub = submissions[team.id]
        val correct = sub?.questionId == categoryWagerQuestionId && sub.isLocked && sub.isCorrect == true
        CategoryWagerResult(team.id, team.name, amount, correct, if (correct) amount else -amount)
    }
    val deltas = results.associate { it.teamId to it.delta }
    return copy(teams = teams.map { it.copy(score = it.score + (deltas[it.id] ?: 0)) },
        categoryWagerResults = results, categoryWagerSettled = true)
}
