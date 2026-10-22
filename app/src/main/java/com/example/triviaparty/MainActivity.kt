package com.example.triviaparty

import android.os.Bundle
import android.os.Build
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ActivityInfo
import android.net.Uri
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.triviaparty.data.QuestionBankRepository
import com.example.triviaparty.data.GamePackageRepository
import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.cast.GoogleCastController
import com.example.triviaparty.model.CategoryGameRules
import com.example.triviaparty.model.HourglassConfig
import com.example.triviaparty.network.GameClient
import com.example.triviaparty.network.GameServer
import com.example.triviaparty.ui.host.GameSetupScreen
import com.example.triviaparty.ui.host.HostScreen
import com.example.triviaparty.ui.theme.TriviaPartyTheme
import java.io.File

enum class AppRole { HOST_SETUP, HOST_DASHBOARD, SOLO_REVIEW }

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val packagesDirectory = File(filesDir, "game-packages")
        com.example.triviaparty.data.OriginalPackageMigration.seed(packagesDirectory,
            assets.list("original-packages").orEmpty().filter { it.endsWith(".zip") }.map { file ->
                file.removeSuffix(".zip") to { assets.open("original-packages/$file") }
            })
        val importedPackages = GamePackageImportRepository.importedDirectories(packagesDirectory)
        QuestionBankRepository.reloadImportedPackages(importedPackages)
        GamePackageRepository.reloadImportedPackages(importedPackages)
        enableEdgeToEdge()
        setContent {
            TriviaPartyTheme {
                LocalNetworkPermissionGate { TriviaPartyApp() }
            }
        }
    }
}

@Composable
private fun LocalNetworkPermissionGate(content: @Composable () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val permission = "android.permission.ACCESS_LOCAL_NETWORK"
    fun hasPermission() = Build.VERSION.SDK_INT < 37 ||
        ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED

    var granted by remember { mutableStateOf(hasPermission()) }
    var requested by remember { mutableStateOf(false) }
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {
        granted = it
        requested = true
    }
    DisposableEffect(lifecycleOwner, context) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) granted = hasPermission()
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    if (granted) {
        content()
    } else {
        Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFF0F0F1A)) {
            Column(
                modifier = Modifier.fillMaxSize().systemBarsPadding().padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("Connexion à la partie", color = Color.White, fontSize = 24.sp)
                Spacer(Modifier.height(16.dp))
                Text(
                    "Allow nearby device access so Trivia Party can find your TV and connect players on your Wi-Fi network.",
                    color = Color.LightGray
                )
                Spacer(Modifier.height(16.dp))
                Button(onClick = { launcher.launch(permission) }) { Text("Autoriser les appareils à proximité") }
                if (requested) {
                    Text("If no prompt appears, enable Nearby devices in app settings.", color = Color.LightGray)
                    TextButton(onClick = {
                        context.startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                            Uri.parse("package:${context.packageName}")))
                    }) { Text("Ouvrir les paramètres") }
                }
            }
        }
    }
}

@Composable
fun TriviaPartyApp() {
    var currentRole by remember { mutableStateOf(AppRole.HOST_SETUP) }
    var hostSelectedCategories by remember { mutableStateOf<List<String>>(QuestionBankRepository.sampleCategories) }
    var hostTotalRounds by remember { mutableStateOf(5) }
    var hostTimingConfig by remember { mutableStateOf(HourglassConfig()) }
    var hostCategoryRules by remember { mutableStateOf<Map<String, CategoryGameRules>>(emptyMap()) }
    var hostAnswerTimeSeconds by remember { mutableStateOf(10) }
    var hostSessionStarted by remember { mutableStateOf(false) }
    var hostAllAudiencesOnly by remember { mutableStateOf(false) }
    var hostVoteSettings by remember { mutableStateOf<com.example.triviaparty.model.VoteSettings?>(null) }
    val activity = LocalContext.current as? ComponentActivity
    DisposableEffect(activity, currentRole) {
        activity?.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
        onDispose {
            activity?.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
        }
    }

    val appContext = LocalContext.current.applicationContext
    val importedPackagesDirectory = remember(appContext) { File(appContext.filesDir, "game-packages") }
    val gameServer = remember(appContext) {
        val preview=com.example.triviaparty.model.PrivateReactionBank.load(File(appContext.filesDir,"reaction-preview"))
        GameServer(privateReactions=preview,readTvAsset = { assetName ->
            appContext.assets.open("tv/$assetName").bufferedReader().use { it.readText() }
        }, importedPackagesDirectory = importedPackagesDirectory, readPlayerAsset = { assetName ->
            appContext.assets.open("player/$assetName").bufferedReader().use { it.readText() }
        }, readTvBinaryAsset = { assetName ->
            appContext.assets.open("tv/$assetName").use { it.readBytes() }
        })
    }
    val gameClient = remember { GameClient() }
    val context = LocalContext.current
    val googleCast = remember { GoogleCastController(context, gameServer.gameSession) }
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(googleCast) {
        googleCast.start()
        onDispose { googleCast.close() }
    }
    DisposableEffect(googleCast, lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) googleCast.onAppResumed()
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    Scaffold(containerColor = Color(0xFF0F0F1A)) { innerPadding ->
        Box(Modifier.fillMaxSize().padding(innerPadding)) {
            when (currentRole) {
                AppRole.HOST_SETUP -> GameSetupScreen(
                    onStartGame = { categories, rounds, timingConfig, answerTimeSeconds, categoryRules, voteSettings, allAudiencesOnly ->
                        hostSelectedCategories = categories
                        hostTotalRounds = rounds
                        hostTimingConfig = timingConfig
                        hostAnswerTimeSeconds = answerTimeSeconds
                        hostCategoryRules = categoryRules
                        hostSessionStarted = false
                        hostVoteSettings=voteSettings
                        hostAllAudiencesOnly=allAudiencesOnly
                        currentRole = AppRole.HOST_DASHBOARD
                    },
                    onSoloReview={ categories -> hostSelectedCategories=categories; currentRole=AppRole.SOLO_REVIEW }
                )
                AppRole.HOST_DASHBOARD -> HostScreen(
                    server = gameServer,
                    client = gameClient,
                    googleCast = googleCast,
                    selectedCategories = hostSelectedCategories,
                    totalRounds = hostTotalRounds,
                    timingConfig = hostTimingConfig,
                    answerTimeSeconds = hostAnswerTimeSeconds,
                    categoryRules = hostCategoryRules,
                    voteSettings=hostVoteSettings,
                    allAudiencesOnly=hostAllAudiencesOnly,
                    startNewGame = !hostSessionStarted,
                    onGameStarted = { hostSessionStarted = true },
                    onBackToMain = {
                        hostSessionStarted = false
                        currentRole = AppRole.HOST_SETUP
                    }
                )
                AppRole.SOLO_REVIEW -> com.example.triviaparty.ui.host.SoloReviewScreen(hostSelectedCategories, gameServer, googleCast) { currentRole=AppRole.HOST_SETUP }
            }
        }
    }
}
