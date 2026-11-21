package com.example.triviaparty.ui.host

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.snapshots.SnapshotStateSet
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.platform.LocalContext
import com.example.triviaparty.data.BankTaxonomyTag
import com.example.triviaparty.data.HostReviewStore
import com.example.triviaparty.data.QuestionBankRepository
import com.example.triviaparty.data.GamePackageRepository
import com.example.triviaparty.data.browseGroup
import com.example.triviaparty.data.isTestPackage
import com.example.triviaparty.model.CategoryGameRules
import com.example.triviaparty.model.HourglassConfig
import com.example.triviaparty.model.VoteSettings
import java.io.File
import kotlin.random.Random

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun GameSetupScreen(
    onStartGame: (selectedCategories: List<String>, totalRounds: Int, timingConfig: HourglassConfig, answerTimeSeconds: Int, categoryRules: Map<String, CategoryGameRules>, voteSettings: VoteSettings?, allAudiencesOnly: Boolean, questionsPerPackage: Int, answerSoundsEnabled: Boolean, teamMode: Boolean, buzzerSoundsEnabled: Boolean, limitQuestionsPerCategory: Boolean) -> Unit,
    onSoloReview: (List<String>) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val audioPreferences = remember { context.getSharedPreferences("host-audio", Context.MODE_PRIVATE) }
    var allAudiencesOnly by remember { mutableStateOf(audioPreferences.getBoolean("all-audiences", false)) }
    var answerSoundsEnabled by remember { mutableStateOf(audioPreferences.getBoolean("answer-sounds-enabled", false)) }
    var buzzerSoundsEnabled by remember { mutableStateOf(audioPreferences.getBoolean("buzzer-sounds-enabled", false)) }
    var teamMode by remember { mutableStateOf(audioPreferences.getBoolean("team-mode-enabled", false)) }

    // A finished vote game leaves generated packages behind that shrink the list to a handful of
    // categories; start every setup from the full bank so the requested counts are achievable.
    val allCategories = remember {
        QuestionBankRepository.resetGeneratedPackages()
        QuestionBankRepository.sampleCategories
    }
    val canonicalSubjects = remember { QuestionBankRepository.canonicalSubjects }
    val canonicalSubjectNames = remember { canonicalSubjects.map { it.label }.distinct().sorted() }

    // Selection modes: "random", "vote", "topics"
    var selectionMode by remember { mutableStateOf("topics") }
    var randomCount by remember { mutableIntStateOf(minOf(5, allCategories.size)) }
    var voteCategoriesCount by remember { mutableIntStateOf(minOf(5, allCategories.size)) }

    val selectedCategories = remember { mutableStateListOf<String>() }
    var search by remember { mutableStateOf("") }
    var questionsPerCategory by remember { mutableIntStateOf(6) }
    var showReviews by remember { mutableStateOf(false) }
    val reviewStore = remember { HostReviewStore(File(context.filesDir, "host-review.json")) }

    val accent = Color(0xFFFFD54F)
    val panel = Color(0xFF232333)
    val setupColors = darkColorScheme(
        primary = accent, onPrimary = Color(0xFF19191F),
        surface = panel, onSurface = Color(0xFFF1F1F5), surfaceVariant = Color(0xFF303040),
        onSurfaceVariant = Color(0xFFBEBECF), background = Color(0xFF12121D),
        secondaryContainer = Color(0xFF46566C), onSecondaryContainer = Color.White
    )
    val categoryColors = FilterChipDefaults.filterChipColors(
        containerColor = Color(0xFF704D91), labelColor = Color.White,
        selectedContainerColor = Color(0xFFD6B4F5), selectedLabelColor = Color(0xFF341849)
    )

    if (showReviews) {
        ReviewListDialog(reviewStore) { showReviews = false }
    }

    val filteredCategories = allCategories.filter { it.contains(search, ignoreCase = true) }
    val totalQuestions = selectedCategories.sumOf { cat ->
        minOf(QuestionBankRepository.getQuestionsForCategory(cat).size, questionsPerCategory)
    }

    MaterialTheme(colorScheme = setupColors) {
        Column(
            modifier = modifier.fillMaxSize().background(Color(0xFF12121D)).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
            horizontalAlignment = Alignment.Start
        ) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Configuration de la Partie", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.White, softWrap = false)
            }

            // Selection Modes Row: Aléatoire, Vote, Sujets
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                Button(
                    onClick = { selectionMode = "random" },
                    colors = ButtonDefaults.buttonColors(containerColor = if (selectionMode == "random") accent else Color(0xFF303040)),
                    modifier = Modifier.weight(1f).height(46.dp),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text("Aléatoire", fontWeight = FontWeight.Bold, color = if (selectionMode == "random") Color(0xFF19191F) else Color.White, softWrap = false)
                }
                Button(
                    onClick = {
                        selectionMode = "vote"
                        if (selectedCategories.isEmpty()) selectedCategories.addAll(allCategories)
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = if (selectionMode == "vote") accent else Color(0xFF303040)),
                    modifier = Modifier.weight(1f).height(46.dp),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text("Vote", fontWeight = FontWeight.Bold, color = if (selectionMode == "vote") Color(0xFF19191F) else Color.White, softWrap = false)
                }
                Button(
                    onClick = { selectionMode = "topics" },
                    colors = ButtonDefaults.buttonColors(containerColor = if (selectionMode == "topics") accent else Color(0xFF303040)),
                    modifier = Modifier.weight(1f).height(46.dp),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text("Sujets", fontWeight = FontWeight.Bold, color = if (selectionMode == "topics") Color(0xFF19191F) else Color.White, softWrap = false)
                }
            }

            // Mode-specific configuration view
            when (selectionMode) {
                "random" -> {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E2C)),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Tirage aléatoire de forfaits", fontWeight = FontWeight.Bold, color = Color.White)
                            CountStepper("Nombre de catégories", randomCount, 1, minOf(20, allCategories.size)) { randomCount = it }
                            FilledTonalButton(
                                onClick = {
                                    val picked = allCategories.shuffled(Random(System.currentTimeMillis())).take(randomCount)
                                    selectedCategories.clear()
                                    selectedCategories.addAll(picked)
                                },
                                modifier = Modifier.fillMaxWidth().height(40.dp)
                            ) {
                                Text("TIRER LES FORFAITS", softWrap = false)
                            }
                        }
                    }
                }
                "vote" -> {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E2C)),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Vote des joueurs par sujets", fontWeight = FontWeight.Bold, color = Color.White)
                            CountStepper("Catégories à élire", voteCategoriesCount, 1, 20) { voteCategoriesCount = it }
                            Text(
                                "Les joueurs votent parmi les sujets des catégories sélectionnées (${voteSubjectCount(selectedCategories)} sujets proposés).",
                                color = Color.LightGray, fontSize = 12.sp
                            )
                            FilledTonalButton(
                                onClick = {
                                    // The vote elects subjects, so every category must be in the pool;
                                    // taking only the first few (alphabetical) offered a single subject.
                                    selectedCategories.clear()
                                    selectedCategories.addAll(allCategories)
                                },
                                modifier = Modifier.fillMaxWidth().height(40.dp)
                            ) {
                                Text("PRÉPARER LE VOTE (TOUS LES SUJETS)", softWrap = false)
                            }
                        }
                    }
                }
                else -> {
                    // Manual/Topics mode
                    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(
                            value = search,
                            onValueChange = { search = it },
                            singleLine = true,
                            label = { Text("Rechercher un sujet ou catégorie") },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            FilledTonalButton(
                                shape = RoundedCornerShape(10.dp),
                                onClick = {
                                    selectedCategories.clear()
                                    selectedCategories.addAll(allCategories)
                                },
                                modifier = Modifier.weight(1f).height(40.dp)
                            ) { Text("Tout sélectionner", softWrap = false) }
                            FilledTonalButton(
                                shape = RoundedCornerShape(10.dp),
                                onClick = { selectedCategories.clear() },
                                modifier = Modifier.weight(1f).height(40.dp)
                            ) { Text("Tout désélectionner", softWrap = false) }
                        }
                    }
                }
            }

            Column(
                Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                val taxonomyTags = remember { QuestionBankRepository.subjectTaxonomy }

                if (selectionMode == "topics" && taxonomyTags.isNotEmpty()) {
                    Text("Exploration hiérarchique des sujets (Tier 1 & 3)", color = accent, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    
                    val rootTags = remember(taxonomyTags) { taxonomyTags.filter { it.parentId == null } }
                    val expandedTagIds = remember { mutableStateSetOf<String>() }

                    rootTags.filter { tag ->
                        tag.label.contains(search, ignoreCase = true) || taxonomyTags.any { it.parentId == tag.id && it.label.contains(search, ignoreCase = true) }
                    }.forEach { rootTag ->
                        TaxonomyNodeView(
                            tag = rootTag,
                            depth = 0,
                            taxonomyTags = taxonomyTags,
                            expandedTagIds = expandedTagIds,
                            selectedCategories = selectedCategories,
                            categoryColors = categoryColors,
                            accent = accent
                        )
                    }
                } else if (selectionMode == "topics" && canonicalSubjectNames.isNotEmpty()) {
                    Text("Sujets canoniques", color = accent, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        canonicalSubjectNames.filter { it.contains(search, ignoreCase = true) }.forEach { subjectName ->
                            val matchingCats = allCategories.filter { it.contains(subjectName, ignoreCase = true) }
                            val isSelected = matchingCats.isNotEmpty() && matchingCats.all { it in selectedCategories }
                            FilterChip(
                                colors = categoryColors,
                                selected = isSelected,
                                onClick = {
                                    if (isSelected) {
                                        matchingCats.forEach { selectedCategories.remove(it) }
                                    } else {
                                        matchingCats.forEach { if (it !in selectedCategories) selectedCategories.add(it) }
                                    }
                                },
                                label = {
                                    Text("Sujet: $subjectName", textAlign = TextAlign.Center, softWrap = false)
                                }
                            )
                        }
                    }
                }
            }

            var gameSettingsExpanded by remember { mutableStateOf(false) }

            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "${selectedCategories.size} catégories sélectionnées · $totalQuestions questions au total",
                    color = Color.LightGray, fontSize = 13.sp, softWrap = false
                )
                TextButton(
                    onClick = { gameSettingsExpanded = !gameSettingsExpanded },
                    colors = ButtonDefaults.textButtonColors(contentColor = accent)
                ) {
                    Text(if (gameSettingsExpanded) "Paramètres ▲" else "Paramètres ▼", fontWeight = FontWeight.Bold, fontSize = 13.sp, softWrap = false)
                }
            }

            if (gameSettingsExpanded) {
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF262636)),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Paramètres de jeu", fontWeight = FontWeight.Bold, color = accent, fontSize = 14.sp)
                        HorizontalDivider(color = Color(0xFF38384E), thickness = 0.8.dp)
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Switch(
                                checked = allAudiencesOnly,
                                onCheckedChange = { allAudiencesOnly = it; audioPreferences.edit().putBoolean("all-audiences", it).apply() }
                            )
                            Text("Répliques tout public uniquement", color = Color.White, modifier = Modifier.padding(start = 10.dp), softWrap = false, fontSize = 13.sp)
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Switch(
                                checked = answerSoundsEnabled,
                                onCheckedChange = { answerSoundsEnabled = it; audioPreferences.edit().putBoolean("answer-sounds-enabled", it).apply() }
                            )
                            Text("Répliques parlées", color = Color.White, modifier = Modifier.padding(start = 10.dp), softWrap = false, fontSize = 13.sp)
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Switch(
                                checked = buzzerSoundsEnabled,
                                onCheckedChange = { buzzerSoundsEnabled = it; audioPreferences.edit().putBoolean("buzzer-sounds-enabled", it).apply() }
                            )
                            Text("Sons de buzzer", color = Color.White, modifier = Modifier.padding(start = 10.dp), softWrap = false, fontSize = 13.sp)
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Switch(
                                checked = teamMode,
                                onCheckedChange = { teamMode = it; audioPreferences.edit().putBoolean("team-mode-enabled", it).apply() }
                            )
                            Text("Mode équipes", color = Color.White, modifier = Modifier.padding(start = 10.dp), softWrap = false, fontSize = 13.sp)
                        }
                    }
                }
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Button(
                    onClick = { gameSettingsExpanded = !gameSettingsExpanded },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF38384E), contentColor = accent),
                    modifier = Modifier.weight(0.9f).height(48.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Paramètres", fontWeight = FontWeight.Bold, fontSize = 13.sp, softWrap = false)
                }
                Button(
                    onClick = { onSoloReview(selectedCategories.toList()) },
                    enabled = selectedCategories.isNotEmpty(),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF46566C), contentColor = Color.White),
                    modifier = Modifier.weight(1f).height(48.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Révision", fontWeight = FontWeight.Bold, fontSize = 13.sp, softWrap = false)
                }
                Button(
                    onClick = {
                        val categoryRules = selectedCategories.associateWith {
                            CategoryGameRules(HourglassConfig(), 20)
                        }
                        val voteSettings = if (selectionMode == "vote") VoteSettings(voteCategoriesCount, 1) else null
                        onStartGame(
                            selectedCategories.toList(),
                            selectedCategories.size,
                            HourglassConfig(),
                            20,
                            categoryRules,
                            voteSettings,
                            allAudiencesOnly,
                            questionsPerCategory,
                            answerSoundsEnabled,
                            teamMode,
                            buzzerSoundsEnabled,
                            true
                        )
                    },
                    enabled = selectedCategories.isNotEmpty() && totalQuestions > 0,
                    colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = Color(0xFF19191F)),
                    modifier = Modifier.weight(1.3f).height(48.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Commencer", fontWeight = FontWeight.Bold, fontSize = 13.sp, softWrap = false)
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun TaxonomyNodeView(
    tag: BankTaxonomyTag,
    depth: Int,
    taxonomyTags: List<BankTaxonomyTag>,
    expandedTagIds: SnapshotStateSet<String>,
    selectedCategories: SnapshotStateList<String>,
    categoryColors: SelectableChipColors,
    accent: Color
) {
    val childTags = remember(tag.id, taxonomyTags) { taxonomyTags.filter { it.parentId == tag.id } }
    val isExpanded = tag.id in expandedTagIds

    val subjectsForTag = remember(tag.id, isExpanded, childTags.isEmpty()) {
        if (isExpanded && childTags.isEmpty()) {
            QuestionBankRepository.subjectsForTaxonomyTagDirect(tag.id)
        } else {
            emptyList()
        }
    }

    val hasChildTags = childTags.isNotEmpty()
    val hasDirectSubjects = remember(tag.id) { QuestionBankRepository.subjectsForTaxonomyTagDirect(tag.id).isNotEmpty() }
    val hasChildren = hasChildTags || hasDirectSubjects

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = (depth * 12).dp, top = 4.dp, bottom = 4.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Surface(
            color = if (depth == 0) Color(0xFF1E1E2C) else Color(0xFF262638),
            shape = RoundedCornerShape(8.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(
                    Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.weight(1f)) {
                        Text(
                            tag.label,
                            fontWeight = if (depth == 0) FontWeight.Bold else FontWeight.SemiBold,
                            color = if (depth == 0) accent else Color(0xFFF1F1F5),
                            fontSize = if (depth == 0) 15.sp else 13.sp
                        )
                        if (hasChildren) {
                            Badge(
                                containerColor = Color(0xFF46566C),
                                modifier = Modifier.defaultMinSize(minWidth = 24.dp)
                            ) {
                                val count = if (hasChildTags) childTags.size else QuestionBankRepository.subjectsForTaxonomyTagDirect(tag.id).size
                                Text("$count", color = Color.White, fontSize = 10.sp, softWrap = false, textAlign = TextAlign.Center)
                            }
                        }
                    }

                    if (hasChildren) {
                        TextButton(
                            onClick = {
                                if (isExpanded) expandedTagIds.remove(tag.id)
                                else expandedTagIds.add(tag.id)
                            },
                            modifier = Modifier.height(32.dp)
                        ) {
                            Text(if (isExpanded) "Replier ▴" else "Explorer ▾", color = Color(0xFFD6B4F5), fontSize = 12.sp)
                        }
                    }
                }

                if (isExpanded) {
                    HorizontalDivider(color = Color(0xFF38384E), thickness = 0.8.dp)

                    if (hasChildTags) {
                        Text("Sous-catégories :", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                        childTags.forEach { child ->
                            TaxonomyNodeView(
                                tag = child,
                                depth = depth + 1,
                                taxonomyTags = taxonomyTags,
                                expandedTagIds = expandedTagIds,
                                selectedCategories = selectedCategories,
                                categoryColors = categoryColors,
                                accent = accent
                            )
                        }
                    } else if (subjectsForTag.isNotEmpty()) {
                        Text("Sujets (Feuilles) :", color = accent, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            subjectsForTag.forEach { subject ->
                                val questions = remember(subject.id) { QuestionBankRepository.questionsForCanonicalSubject(subject.id) }
                                val isSelected = questions.isNotEmpty() && questions.all { q -> selectedCategories.contains(q.category) }

                                FilterChip(
                                    colors = categoryColors,
                                    selected = isSelected,
                                    onClick = {
                                        val cats = questions.map { q -> q.category }.distinct()
                                        if (isSelected) {
                                            cats.forEach { cat -> selectedCategories.remove(cat) }
                                        } else {
                                            cats.forEach { cat -> if (cat !in selectedCategories) selectedCategories.add(cat) }
                                        }
                                    },
                                    label = { Text(subject.label, fontSize = 11.sp, softWrap = false) }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

/** Subjects players can vote on for the given categories (mirrors the host's vote candidates). */
private fun voteSubjectCount(categories: List<String>): Int =
    GamePackageRepository.packages
        .filter { pack -> !pack.isTestPackage() && GamePackageRepository.categoryNamesFor(pack).any { it in categories } }
        .map { it.browseGroup() }.distinct().size

@Composable
private fun CountStepper(label: String, value: Int, min: Int, max: Int, onChange: (Int) -> Unit) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("$label : $value", color = Color.LightGray, modifier = Modifier.weight(1f))
        FilledTonalButton(onClick = { onChange((value - 1).coerceAtLeast(min)) }, enabled = value > min,
            contentPadding = PaddingValues(0.dp), modifier = Modifier.size(40.dp)) { Text("−", fontSize = 18.sp) }
        FilledTonalButton(onClick = { onChange((value + 1).coerceAtMost(max)) }, enabled = value < max,
            contentPadding = PaddingValues(0.dp), modifier = Modifier.size(40.dp)) { Text("+", fontSize = 18.sp) }
    }
}
