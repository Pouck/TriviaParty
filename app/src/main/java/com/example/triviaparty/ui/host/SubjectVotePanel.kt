package com.example.triviaparty.ui.host

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.triviaparty.model.GameSession
import com.example.triviaparty.network.GameEvent

@OptIn(ExperimentalLayoutApi::class)
@Composable internal fun SubjectVotePanel(game: GameSession, send: (GameEvent) -> Unit) {
    val vote=game.subjectVoting ?: return
    val selected=remember(vote.round) { mutableStateListOf<String>() }
    val totals=vote.totals()
    Text(if(vote.hostTieBreak) "Égalité persistante · choix de l’hôte" else if(vote.round==1) "Vote des catégories" else "Second vote · égalités",color=Color.White)
    if(vote.selected.isNotEmpty()) Text("Déjà retenus : ${vote.selected.joinToString(" · ")}",color=Color(0xFFA6ECC3))
    Text("${vote.remainingSlots} place(s) · ${vote.ballots.size}/${game.teams.count { it.isConnected }} équipes ont voté",color=Color.LightGray)
    if(vote.hostTieBreak) {
        Text("Choisissez exactement ${vote.remainingSlots} sujet(s).",color=Color.LightGray)
        FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
            vote.candidates.forEach { subject -> FilterChip(selected=subject in selected,onClick={
                if(subject in selected) selected.remove(subject) else if(selected.size<vote.remainingSlots) selected.add(subject)
            },label={ Text(subject) }) }
        }
        Button(onClick={ send(GameEvent.HostBreakSubjectTie(selected.toList())) },enabled=selected.size==vote.remainingSlots) { Text("CONFIRMER LES SUJETS") }
    } else {
        vote.candidates.sortedByDescending { totals[it] }.forEach { Text("$it · ${totals[it] ?: 0} vote(s)",color=Color.White) }
        Text("Fermer le vote accepte aussi les abstentions.",color=Color.LightGray)
        Button(onClick={ send(GameEvent.HostCloseSubjectVote) }) { Text("FERMER LE VOTE") }
    }
}
