package com.example.triviaparty.ui.host

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.platform.LocalContext
import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.data.GamePackageRepository
import com.example.triviaparty.data.QuestionBankRepository
import com.example.triviaparty.model.CategoryGameRules
import com.example.triviaparty.model.HourglassConfig
import com.example.triviaparty.data.combineGamePackages
import com.example.triviaparty.data.browseGroup
import com.example.triviaparty.data.isTestPackage
import com.example.triviaparty.data.searchablePackageText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun GameSetupScreen(
    onStartGame: (selectedCategories: List<String>, totalRounds: Int, timingConfig: HourglassConfig, answerTimeSeconds: Int, categoryRules: Map<String, CategoryGameRules>, voteSettings: com.example.triviaparty.model.VoteSettings?, allAudiencesOnly: Boolean) -> Unit,
    onSoloReview: (List<String>) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val audioPreferences=remember { context.getSharedPreferences("host-audio",android.content.Context.MODE_PRIVATE) }
    var allAudiencesOnly by remember { mutableStateOf(audioPreferences.getBoolean("all-audiences",false)) }
    val packagesDirectory = File(context.filesDir, "game-packages")
    val importedIds = GamePackageImportRepository.importedDirectories(packagesDirectory).map { it.name }.toSet()
    var packageToUpdate by remember { mutableStateOf<String?>(null) }
    var packageToRemove by remember { mutableStateOf<com.example.triviaparty.model.GamePackage?>(null) }
    val selectedIds = remember { mutableStateListOf<String>() }
    var search by remember { mutableStateOf("") }
    val expandedGroups = remember { mutableStateListOf<String>() }
    val reviewStore = remember { com.example.triviaparty.data.HostReviewStore(File(context.filesDir,"host-review.json")) }
    var usage by remember { mutableStateOf(reviewStore.read().usage) }
    var selectionMode by remember { mutableStateOf("Aléatoire") }
    var randomCount by remember { mutableStateOf("6") }
    var voteCount by remember { mutableStateOf("5") }
    var setsPerSubject by remember { mutableStateOf("1") }
    val selectedSubjects = remember { mutableStateListOf<String>() }
    var showReviews by remember { mutableStateOf(false) }
    val exportReviews = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        if(uri!=null) context.contentResolver.openOutputStream(uri)?.use { output ->
            val source=File(context.filesDir,"host-review.json")
            output.write(if(source.exists()) source.readBytes() else "{\"reviews\":{},\"usage\":{}}".toByteArray())
        }
    }
    var resetStats by remember { mutableStateOf(false) }
    var drawing by remember { mutableStateOf(false) }
    var drawError by remember { mutableStateOf<String?>(null) }
    var toolsOpen by remember { mutableStateOf(false) }
    var editCounts by remember { mutableStateOf(false) }
    var manualSubject by remember { mutableStateOf("Tous") }
    var draftCount by remember { mutableStateOf("6") }
    var draftSets by remember { mutableStateOf("1") }
    var showSelection by remember { mutableStateOf(false) }
    val accent = Color(0xFFFFD54F)
    val panel = Color(0xFF232333)
    val setupColors = darkColorScheme(primary=accent,onPrimary=Color(0xFF19191F),
        surface=panel,onSurface=Color(0xFFF1F1F5),surfaceVariant=Color(0xFF303040),
        onSurfaceVariant=Color(0xFFBEBECF),background=Color(0xFF12121D),
        secondaryContainer=Color(0xFF4A4229),onSecondaryContainer=accent)
    if(showReviews) ReviewListDialog(reviewStore) { showReviews=false }
    if(resetStats) AlertDialog(onDismissRequest={ resetStats=false },title={ Text("Réinitialiser l’utilisation ?") },
        text={ Text("Les compteurs de parties et les dernières utilisations seront effacés. Les commentaires sont conservés.") },
        confirmButton={ TextButton(onClick={ reviewStore.resetUsage(); usage=emptyMap(); resetStats=false }) { Text("Réinitialiser") } },
        dismissButton={ TextButton(onClick={ resetStats=false }) { Text("Annuler") } })
    fun eligiblePackages() = GamePackageRepository.packages.filter { pack ->
        !pack.isTestPackage() && GamePackageRepository.categoryNamesFor(pack).any { QuestionBankRepository.getQuestionsForCategory(it).isNotEmpty() }
    }
    val voteSets=setsPerSubject.toIntOrNull()?.coerceIn(1,50) ?: 1
    val votePool=if(selectionMode=="Vote") eligiblePackages().groupBy { it.browseGroup() }.filterValues { it.size>=voteSets }.values.flatten() else emptyList()
    val voteSubjects=votePool.map { it.browseGroup() }.distinct().size
    val voteNumber=(voteCount.toIntOrNull()?.coerceIn(1,50) ?: 5).coerceAtMost(voteSubjects)
    fun drawPackages() {
        if(drawing) return
        val mode=selectionMode
        val subjects=selectedSubjects.toSet()
        val count=if(mode=="Sujets") subjects.size else randomCount.toIntOrNull()?.coerceIn(1,50) ?: 6
        val sets=setsPerSubject.toIntOrNull()?.coerceIn(1,50) ?: 1
        val stats=usage
        drawing=true; drawError=null
        scope.launch {
        val result=runCatching { withContext(Dispatchers.Default) {
        val packs = eligiblePackages().filter { mode != "Sujets" || it.browseGroup() in subjects }
        val byId = packs.associateBy { it.id }
        com.example.triviaparty.data.selectBalancedCategorySets(packs.map { it.id },count,sets,
            stats, { id ->
                val pack=byId.getValue(id)
                val formats=GamePackageRepository.categoryNamesFor(pack).map { com.example.triviaparty.data.categoryProfileFor(it).format }.distinct()
                com.example.triviaparty.data.CategoryProfile(formats.singleOrNull() ?: com.example.triviaparty.data.CategoryFormat.MIXED,pack.browseGroup())
            })
        } }
        result.onSuccess { ids ->
            if(selectionMode==mode && selectedSubjects.toSet()==subjects && (setsPerSubject.toIntOrNull()?.coerceIn(1,50) ?: 1)==sets) { selectedIds.clear(); selectedIds.addAll(ids);if(ids.isEmpty()) drawError="Aucun sujet ne contient $sets forfaits disponibles. Réduisez le nombre de forfaits par catégorie." }
        }.onFailure { drawError=it.message ?: "Tirage impossible" }
        drawing=false
        }
    }
    val selectedPackages = selectedIds.mapNotNull { id -> GamePackageRepository.packages.firstOrNull { it.id == id } }
    val combined = combineGamePackages(selectedPackages, GamePackageRepository::categoryNamesFor) {
        QuestionBankRepository.getQuestionsForCategory(it).size
    }
    fun togglePackage(id: String) {
        if (id in selectedIds) selectedIds.remove(id) else selectedIds.add(id)
    }
    var importMessage by remember { mutableStateOf<String?>(null) }
    var importSucceeded by remember { mutableStateOf(false) }
    val importLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        val updateId = packageToUpdate
        packageToUpdate = null
        if (uri != null) {
            scope.launch {
                val result = runCatching {
                    withContext(Dispatchers.IO) {
                        val packagesDirectory = File(context.filesDir, "game-packages")
                        val newPackage = GamePackageImportRepository.importZip(context.contentResolver, uri, packagesDirectory, updateId)
                        try {
                            val imported = GamePackageImportRepository.importedDirectories(packagesDirectory)
                            QuestionBankRepository.reloadImportedPackages(imported)
                            GamePackageRepository.reloadImportedPackages(imported)
                        } catch (error: Exception) {
                            GamePackageImportRepository.rollbackImport(newPackage)
                            val restored = GamePackageImportRepository.importedDirectories(packagesDirectory)
                            runCatching {
                                QuestionBankRepository.reloadImportedPackages(restored)
                                GamePackageRepository.reloadImportedPackages(restored)
                            }
                            throw error
                        }
                        GamePackageImportRepository.confirmImport(newPackage)
                    }
                }
                importSucceeded = result.isSuccess
                importMessage = result.fold(
                    onSuccess = { if (updateId != null) "Forfait mis à jour." else "Forfait importé avec succès." },
                    onFailure = { it.message ?: "Impossible d’importer ce fichier ZIP." }
                )
            }
        }
    }

    packageToRemove?.let { pack ->
        AlertDialog(
            onDismissRequest = { packageToRemove = null },
            title = { Text("Supprimer ce forfait ?") },
            text = { Text(pack.name) },
            confirmButton = { TextButton(onClick = {
                packageToRemove = null
                scope.launch {
                    val result = runCatching {
                        withContext(Dispatchers.IO) {
                            GamePackageImportRepository.removePackage(packagesDirectory, pack.id)
                            val imported = GamePackageImportRepository.importedDirectories(packagesDirectory)
                            QuestionBankRepository.reloadImportedPackages(imported)
                            GamePackageRepository.reloadImportedPackages(imported)
                        }
                    }
                    if (result.isSuccess) selectedIds.remove(pack.id)
                    importSucceeded = result.isSuccess
                    importMessage = result.fold({ "Forfait supprimé." }, { it.message ?: "Suppression impossible." })
                }
            }) { Text("Supprimer") } },
            dismissButton = { TextButton(onClick = { packageToRemove = null }) { Text("Annuler") } }
        )
    }

    MaterialTheme(colorScheme=setupColors) {
    if(editCounts) AlertDialog(onDismissRequest={ editCounts=false },title={ Text("Format de la partie") },
        text={ Column(verticalArrangement=Arrangement.spacedBy(12.dp)) {
            if(selectionMode!="Sujets") OutlinedTextField(value=draftCount,onValueChange={ draftCount=it.filter(Char::isDigit).take(2) },label={ Text("Nombre de catégories") },singleLine=true)
            OutlinedTextField(value=draftSets,onValueChange={ draftSets=it.filter(Char::isDigit).take(2) },label={ Text("Forfaits par catégorie") },singleLine=true)
        } },
        confirmButton={ TextButton(enabled=(selectionMode=="Sujets" || (draftCount.toIntOrNull() ?: 0) in 1..50) && (draftSets.toIntOrNull() ?: 0) in 1..50,onClick={
            if(selectionMode=="Vote") voteCount=draftCount else if(selectionMode=="Aléatoire") randomCount=draftCount
            setsPerSubject=draftSets;selectedIds.clear();editCounts=false
        }) { Text("Appliquer") } },dismissButton={ TextButton(onClick={ editCounts=false }) { Text("Annuler") } })
    Column(
        modifier = modifier.fillMaxSize().background(Color(0xFF12121D)).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        horizontalAlignment = Alignment.Start
    ) {
        Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.SpaceBetween) {
            Text("Nouvelle partie", fontSize=26.sp,fontWeight=FontWeight.Bold,color=Color.White)
            Box {
                TextButton(onClick={ toolsOpen=true }) { Text("Outils ⋮") }
                DropdownMenu(expanded=toolsOpen,onDismissRequest={ toolsOpen=false }) {
                    DropdownMenuItem(text={ Text("Importer un forfait") },onClick={
                        toolsOpen=false; packageToUpdate=null
                        importLauncher.launch(arrayOf("application/zip","application/x-zip-compressed","application/octet-stream"))
                    })
                    DropdownMenuItem(text={ Text("Gérer les forfaits") },onClick={ toolsOpen=false; selectionMode="Manuel" })
                    DropdownMenuItem(text={ Text("Questions à revoir") },onClick={ toolsOpen=false; showReviews=true })
                    DropdownMenuItem(text={ Text("Exporter notes et statistiques") },onClick={ toolsOpen=false; exportReviews.launch("trivia-commentaires.json") })
                    DropdownMenuItem(text={ Text("Réinitialiser les statistiques") },onClick={ toolsOpen=false; resetStats=true })
                }
            }
        }
        FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(0.dp)) {
            listOf("Aléatoire" to "Tirage", "Sujets" to "Sujets", "Vote" to "Vote", "Tout" to "Tout", "Manuel" to "Manuel", "Révision" to "Révision", "Tests" to "Tests").forEach { (mode,label) ->
                FilterChip(selected=selectionMode==mode,enabled=!drawing,onClick={
                    showSelection=false;drawError=null
                    if(selectionMode!=mode) {
                        selectionMode=mode;selectedIds.clear()
                        if(mode=="Tout") selectedIds.addAll(eligiblePackages().map { it.id })
                        if(mode=="Tests") selectedIds.addAll(GamePackageRepository.packages.filter { pack ->
                            pack.isTestPackage() && GamePackageRepository.categoryNamesFor(pack).any { QuestionBankRepository.getQuestionsForCategory(it).isNotEmpty() }
                        }.map { it.id })
                    }
                },label={ Text(label,fontSize=15.sp) })
            }
        }
        importMessage?.let { message ->
            Text(message, color = if (importSucceeded) Color(0xFF8EE6A2) else Color(0xFFFF8A80))
        }

        Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            if(selectionMode=="Vote") {
                Text("Les joueurs rejoignent le salon, puis votent sur leur téléphone. Les sujets sont affichés sur la TV.",color=MaterialTheme.colorScheme.onSurfaceVariant)
                Text("$voteSubjects sujets disponibles pour $voteSets forfait${if(voteSets==1) "" else "s"} chacun. Les forfaits sont tirés après le vote, avec des formats variés.",color=MaterialTheme.colorScheme.onSurfaceVariant)
            }
            if(selectionMode=="Révision") Text("Choisissez les forfaits à revoir. Jouez seul, révélez la réponse, puis notez et commentez la question. Sans chrono.",color=MaterialTheme.colorScheme.onSurfaceVariant)
            if(selectionMode in listOf("Aléatoire","Sujets","Vote")) Surface(color=panel,shape=RoundedCornerShape(12.dp),modifier=Modifier.fillMaxWidth()) {
                Row(Modifier.padding(horizontal=14.dp,vertical=4.dp),verticalAlignment=Alignment.CenterVertically) {
                    val count=when(selectionMode) { "Vote" -> voteCount; "Sujets" -> selectedSubjects.size.toString(); else -> randomCount }
                    Text("$count × $voteSets",fontSize=23.sp,fontWeight=FontWeight.Bold,color=Color.White)
                    Text("  catégories × forfaits",modifier=Modifier.weight(1f),fontSize=13.sp,color=MaterialTheme.colorScheme.onSurfaceVariant)
                    TextButton(enabled=!drawing,onClick={ draftCount=if(selectionMode=="Vote") voteCount else randomCount;draftSets=setsPerSubject;editCounts=true }) { Text("Modifier") }
                }
            }
            if(selectionMode=="Sujets") {
                Text("Choisissez les sujets. Les formats sont mélangés.",color=MaterialTheme.colorScheme.onSurfaceVariant)
                FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(0.dp)) {
                eligiblePackages().map { it.browseGroup() }.distinct().sorted().forEach { subject ->
                    FilterChip(selected=subject in selectedSubjects,enabled=!drawing,onClick={
                        if(subject in selectedSubjects) selectedSubjects.remove(subject) else selectedSubjects.add(subject)
                        selectedIds.clear()
                    },label={ Text(subject) })
                }
                }
            }
            if(selectionMode=="Tests") Text("Tous les forfaits de test et démonstration sont sélectionnés.",color=MaterialTheme.colorScheme.onSurfaceVariant)
            if(selectionMode=="Tout") Text("Toute la bibliothèque, sauf les tests et démonstrations.",color=MaterialTheme.colorScheme.onSurfaceVariant)
            if(selectionMode in listOf("Aléatoire","Sujets")) Button(onClick={ drawPackages() },
                colors=ButtonDefaults.buttonColors(containerColor=Color(0xFF75D7CB),contentColor=Color(0xFF102724)),
                modifier=Modifier.fillMaxWidth(),shape=RoundedCornerShape(12.dp),
                enabled=!drawing && (selectionMode!="Sujets" || selectedSubjects.isNotEmpty())) { Text(if(drawing) "Tirage en cours…" else if(selectedIds.isEmpty()) "Tirer les forfaits" else "Nouveau tirage") }
            if(drawing) LinearProgressIndicator(Modifier.fillMaxWidth())
            drawError?.let { Text(it,color=Color(0xFFFF8A80)) }
            if(selectionMode in listOf("Aléatoire","Sujets")) Text("Sujets et formats équilibrés · priorité aux moins joués",color=MaterialTheme.colorScheme.onSurfaceVariant,fontSize=13.sp)
            if(selectionMode !in listOf("Manuel","Révision","Vote") && selectedPackages.isNotEmpty()) {
                TextButton(onClick={ showSelection=!showSelection },contentPadding=PaddingValues(0.dp)) {
                    Text(if(showSelection) "Masquer la sélection ▴" else "Voir les ${selectedPackages.size} forfaits ▾")
                }
                if(showSelection) selectedPackages.forEach { pack ->
                    Surface(color=panel,shape=RoundedCornerShape(10.dp),modifier=Modifier.fillMaxWidth()) {
                        Text(pack.name,modifier=Modifier.padding(12.dp),color=Color.White,fontSize=15.sp)
                    }
                }
            }
            if(selectionMode in listOf("Manuel","Révision")) {
            OutlinedTextField(value=search,onValueChange={ search=it },singleLine=true,
                label={ Text("Rechercher un forfait") },modifier=Modifier.fillMaxWidth())
            FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                (listOf("Tous")+GamePackageRepository.packages.map { it.browseGroup() }.distinct().sorted()).forEach { subject ->
                    FilterChip(selected=manualSubject==subject,onClick={ manualSubject=subject },label={ Text(subject) })
                }
            }
            GamePackageRepository.packages.filter {
                (manualSubject=="Tous" || it.browseGroup()==manualSubject) && searchablePackageText(it.name).contains(searchablePackageText(search.trim()))
            }.groupBy { it.browseGroup() }.toSortedMap().forEach { (group,packs) ->
                val selectable=packs.filter { pack -> GamePackageRepository.categoryNamesFor(pack).any { QuestionBankRepository.getQuestionsForCategory(it).isNotEmpty() } }
                val allSelected=selectable.isNotEmpty() && selectable.all { it.id in selectedIds }
                Row(verticalAlignment=Alignment.CenterVertically,modifier=Modifier.fillMaxWidth()) {
                    TextButton(onClick={ if(group in expandedGroups) expandedGroups.remove(group) else expandedGroups.add(group) },modifier=Modifier.weight(1f),contentPadding=PaddingValues(horizontal=0.dp,vertical=2.dp)) {
                        Text("${if(group in expandedGroups || search.isNotBlank() || manualSubject!="Tous") "▾" else "▸"} $group · ${packs.size}",color=accent,modifier=Modifier.fillMaxWidth(),fontWeight=FontWeight.Bold)
                    }
                    TextButton(enabled=selectable.isNotEmpty(),onClick={
                        if(allSelected) selectedIds.removeAll(selectable.map { it.id }.toSet())
                        else selectable.forEach { if(it.id !in selectedIds) selectedIds.add(it.id) }
                    }) { Text(if(allSelected) "Tout retirer" else "Tout sélectionner",fontSize=12.sp) }
                }
                if (group in expandedGroups || search.isNotBlank() || manualSubject!="Tous") packs.sortedBy { it.name }.forEach { gamePackage ->
                val categories = GamePackageRepository.categoryNamesFor(gamePackage)
                val count = categories.sumOf { QuestionBankRepository.getQuestionsForCategory(it).size }
                Card(
                    onClick = { togglePackage(gamePackage.id) },
                    enabled = categories.isNotEmpty() && count > 0,
                    border = if (gamePackage.id in selectedIds) BorderStroke(1.dp, accent) else null,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(8.dp),
                    colors = CardDefaults.cardColors(containerColor = panel)
                ) {
                    Column(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
                        verticalArrangement = Arrangement.spacedBy(0.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Checkbox(
                                checked = gamePackage.id in selectedIds,
                                onCheckedChange = { togglePackage(gamePackage.id) },
                                enabled = categories.isNotEmpty() && count > 0,
                                colors = CheckboxDefaults.colors(checkedColor = accent, checkmarkColor = Color.Black)
                            )
                            Column(Modifier.weight(1f)) {
                                Text(gamePackage.name, color = Color.White,
                                    fontWeight = FontWeight.Bold, fontSize = 16.sp,
                                    maxLines = 1, overflow = TextOverflow.Ellipsis)
                                val clueQuestion = categories.any { category -> QuestionBankRepository.getQuestionsForCategory(category).any { it is com.example.triviaparty.model.Question.GuessWho } }
                                val timing = if (clueQuestion) gamePackage.timingConfig.copy(secondsPerFlip=20) else gamePackage.timingConfig
                                val usesBuzzer = categories.any {
                                    QuestionBankRepository.getCategoryPackage(it)?.answerMode == com.example.triviaparty.model.CategoryAnswerMode.BUZZER
                                }
                                val summary = "$count questions · ${timing.secondsPerFlip * (timing.maxFlips + 1)} s" +
                                    (if (usesBuzzer) " · Réponse : ${gamePackage.answerTimeSeconds} s" else "") +
                                    " · ${usage[gamePackage.id]?.plays ?: 0} partie(s)"
                                Text(summary,
                                    color = Color.LightGray, fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            }
                            if (gamePackage.id in importedIds) {
                                var menuOpen by remember(gamePackage.id) { mutableStateOf(false) }
                                Box {
                                    TextButton(onClick = { menuOpen = true }, contentPadding = PaddingValues(0.dp),
                                        modifier = Modifier.width(48.dp).semantics { contentDescription = "Gérer ${gamePackage.name}" }) {
                                        Text("⋮", color = Color.White, fontSize = 24.sp)
                                    }
                                    DropdownMenu(expanded = menuOpen, onDismissRequest = { menuOpen = false }) {
                                        DropdownMenuItem(text = { Text("Mettre à jour") }, onClick = {
                                            menuOpen = false
                                            packageToUpdate = gamePackage.id
                                            importLauncher.launch(arrayOf("application/zip", "application/x-zip-compressed", "application/octet-stream"))
                                        })
                                        DropdownMenuItem(text = { Text("Supprimer") }, onClick = {
                                            menuOpen = false
                                            packageToRemove = gamePackage
                                        })
                                    }
                                }
                            }
                        }
                    }
                }
                }
            }
            }
        }
        if(selectionMode!="Révision") Row(verticalAlignment=Alignment.CenterVertically) {
            Switch(checked=allAudiencesOnly,onCheckedChange={ allAudiencesOnly=it;audioPreferences.edit().putBoolean("all-audiences",it).apply() })
            Text("Répliques tout public uniquement",color=Color.White,modifier=Modifier.padding(start=10.dp))
        }
        if (combined.conflictingCategories.isNotEmpty()) {
            Text("Catégories communes : règles du premier forfait sélectionné pour " +
                combined.conflictingCategories.joinToString(" · "), color = Color(0xFFFFD700), fontSize = 12.sp)
        }
        Text(if(selectionMode=="Vote") "$voteNumber catégories · ${voteNumber*voteSets} forfaits après le vote" else "${selectedPackages.size} forfait${if(selectedPackages.size==1) "" else "s"} · ${combined.totalQuestions} questions",
            color = Color.LightGray, fontSize = 14.sp)
        Button(
            onClick = {
                if(selectionMode=="Révision") onSoloReview(combined.categories)
                else {
                    val packs=if(selectionMode=="Vote") votePool else selectedPackages
                    val setup=if(selectionMode=="Vote") combineGamePackages(packs,GamePackageRepository::categoryNamesFor) { QuestionBankRepository.getQuestionsForCategory(it).size } else combined
                    val first=packs.first()
                    onStartGame(setup.categories,setup.totalQuestions,first.timingConfig,first.answerTimeSeconds,setup.categoryRules,
                        if(selectionMode=="Vote") com.example.triviaparty.model.VoteSettings(voteNumber,voteSets) else null,allAudiencesOnly)
                }
            },
            enabled = !drawing && (if(selectionMode=="Vote") voteNumber>0 else selectedPackages.isNotEmpty() && combined.totalQuestions>0),
            modifier = Modifier.fillMaxWidth().height(48.dp),shape=RoundedCornerShape(12.dp),
            contentPadding = PaddingValues(horizontal=16.dp,vertical=8.dp)
        ) { Text(when(selectionMode) { "Vote"->"Ouvrir le salon"; "Révision"->"Commencer la révision"; else->"Préparer la partie" }, fontWeight = FontWeight.Bold,fontSize=17.sp) }

    }
    }
}
