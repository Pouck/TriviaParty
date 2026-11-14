package com.example.triviaparty.ui.cast

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.mediarouter.app.MediaRouteButton
import androidx.mediarouter.media.MediaRouteSelector
import com.example.triviaparty.R
import com.example.triviaparty.cast.GoogleCastController
import com.google.android.gms.cast.framework.CastButtonFactory
import com.google.android.gms.cast.framework.CastContext

@Composable
fun GoogleCastButton(modifier: Modifier = Modifier) {
    AndroidView(
        factory = { viewContext ->
            val activity = viewContext.findFragmentActivity()
            MediaRouteButton(activity).also { button ->
                CastButtonFactory.setUpMediaRouteButton(viewContext.applicationContext, button)
                try {
                    CastContext.getSharedInstance(activity).mergedSelector?.let {
                        button.routeSelector = it
                    }
                } catch (_: Exception) {}
                button.contentDescription = "Choisir un téléviseur Cast"
            }
        },
        modifier = modifier
    )
}

private fun android.content.Context.findFragmentActivity(): androidx.fragment.app.FragmentActivity = when (this) {
    is androidx.fragment.app.FragmentActivity -> this
    is android.content.ContextWrapper -> baseContext.findFragmentActivity()
    else -> error("Cast button requires a FragmentActivity context")
}

@Composable
fun GoogleCastDeviceStatus(controller: GoogleCastController) {
    val status by controller.status.collectAsState()
    Text(
        if (status.connected) status.message else "Aucun téléviseur connecté. Utilisez le bouton Cast pour choisir votre téléviseur.",
        style = MaterialTheme.typography.bodyMedium
    )
    status.error?.let {
        Text(it, color = MaterialTheme.colorScheme.error)
    }
    if (status.connecting) {
        LinearProgressIndicator(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp))
    }
    if (status.connected) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TextButton(onClick = controller::resend) { Text("Resend game") }
            TextButton(onClick = controller::stopCasting) { Text("Stop casting") }
        }
    }
}
