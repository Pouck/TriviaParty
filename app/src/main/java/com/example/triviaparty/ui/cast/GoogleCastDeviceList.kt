package com.example.triviaparty.ui.cast

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.triviaparty.cast.GoogleCastController

@Composable
fun GoogleCastDeviceList(controller: GoogleCastController, scanning: Boolean) {
    val devices by controller.devices.collectAsState()
    val status by controller.status.collectAsState()

    Text(status.message, style = MaterialTheme.typography.titleMedium)
    status.error?.let {
        Text(it, color = MaterialTheme.colorScheme.error)
    }
    if (status.connecting) {
        LinearProgressIndicator(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp))
    }
    if (status.connected || status.connecting) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (status.connected) {
                TextButton(onClick = controller::resend) { Text("Resend game") }
            }
            TextButton(onClick = controller::stopCasting) {
                Text(if (status.connected) "Stop casting" else "Cancel")
            }
        }
    } else {
        if (devices.isEmpty()) {
            Text(if (scanning) "Looking for TVs on your Wi-Fi…" else
                "No compatible TVs found yet. Check your TV is on the same Wi-Fi and retry discovery.")
        }
        devices.forEach { device ->
            OutlinedButton(
                onClick = { controller.connect(device.id) },
                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                contentPadding = PaddingValues(16.dp)
            ) {
                Text(device.name, modifier = Modifier.weight(1f))
                Text("Cast")
            }
        }
    }
}
