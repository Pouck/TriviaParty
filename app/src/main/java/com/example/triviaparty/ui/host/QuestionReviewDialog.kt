package com.example.triviaparty.ui.host

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.triviaparty.data.*

@Composable internal fun QuestionReviewDialog(store: HostReviewStore, review: QuestionReview, close: () -> Unit) {
    var comment by remember(review.questionId) { mutableStateOf(review.comment) }
    var difficulty by remember(review.questionId) { mutableStateOf(review.difficulty) }
    var error by remember { mutableStateOf<String?>(null) }
    AlertDialog(onDismissRequest=close,title={ Text("Commenter la question") },text={
        Column(Modifier.heightIn(max=450.dp).verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)) {
            Text(review.category); Text(review.prompt)
            Text("Difficulté : 1 = facile · 5 = difficile")
            FilterChip(selected=difficulty==0,onClick={ difficulty=if(difficulty==0) null else 0 },label={ Text("0 — À réviser") })
            Row { (1..5).forEach { rating ->
                FilterChip(selected=difficulty==rating,onClick={ difficulty=if(difficulty==rating) null else rating },label={ Text("$rating") })
            } }
            OutlinedTextField(value=comment,onValueChange={ comment=it },label={ Text("Commentaire / correction à revoir") },modifier=Modifier.fillMaxWidth(),minLines=3)
            error?.let { Text(it) }
        }
    },confirmButton={ TextButton(onClick={
        runCatching { store.saveReview(review.copy(comment=comment,difficulty=difficulty)) }.onSuccess { close() }.onFailure { error=it.message }
    }) { Text("Enregistrer") } },dismissButton={ TextButton(onClick=close) { Text("Annuler") } })
}

@Composable internal fun ReviewListDialog(store: HostReviewStore, close: () -> Unit) {
    var editing by remember { mutableStateOf<QuestionReview?>(null) }
    var revision by remember { mutableIntStateOf(0) }
    var onlyFlagged by remember { mutableStateOf(false) }
    val reviews = remember(revision) { store.read().reviews.values.sortedByDescending { it.updatedAt } }
    val visible=if(onlyFlagged) reviews.filter { it.difficulty==0 } else reviews
    AlertDialog(onDismissRequest=close,title={ Text("Questions à revoir (${reviews.size})") },text={
        Column(Modifier.heightIn(max=450.dp).verticalScroll(rememberScrollState())) {
            FilterChip(selected=onlyFlagged,onClick={ onlyFlagged=!onlyFlagged },label={ Text("À réviser (${reviews.count { it.difficulty==0 }})") })
            if(visible.isEmpty()) Text(if(onlyFlagged) "Aucune question marquée à réviser." else "Aucun commentaire enregistré.")
            visible.forEach { review -> TextButton(onClick={ editing=review }) {
                Text("${review.category}\n${review.prompt}\n${if(review.difficulty==0) "0 — À réviser" else "Difficulté : ${review.difficulty ?: "—"}"} · ${review.comment}")
            } }
        }
    },confirmButton={ TextButton(onClick=close) { Text("Fermer") } })
    editing?.let { QuestionReviewDialog(store,it) { editing=null; revision++ } }
}
