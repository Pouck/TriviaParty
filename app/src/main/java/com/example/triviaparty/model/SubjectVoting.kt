package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable data class VoteSettings(val categories: Int = 5, val setsPerCategory: Int = 1)
@Serializable data class SubjectVoting(
    val settings: VoteSettings,
    val candidates: List<String>,
    val selected: List<String> = emptyList(),
    val ballots: Map<String, List<String>> = emptyMap(),
    val round: Int = 1,
    val hostTieBreak: Boolean = false,
    val completed: Boolean = false
) {
    val remainingSlots: Int get() = (settings.categories - selected.size).coerceAtLeast(0)
    fun totals(): Map<String, Int> = candidates.associateWith { subject -> ballots.values.count { subject in it } }
}

/** Only the tie spanning the cutoff goes to another ballot, never the already elected subjects. */
fun SubjectVoting.closeRound(): SubjectVoting {
    if(completed || hostTieBreak) return this
    val totals = totals()
    val ranked = candidates.groupBy { totals[it] ?: 0 }.toSortedMap(compareByDescending { it })
    val elected = selected.toMutableList()
    for(group in ranked.values) {
        val slots = settings.categories - elected.size
        if(slots <= 0) break
        if(group.size <= slots) elected.addAll(group)
        else return copy(selected=elected,candidates=group,ballots=emptyMap(),
            round=round+1,hostTieBreak=round >= 2)
    }
    return copy(selected=elected,completed=true)
}
