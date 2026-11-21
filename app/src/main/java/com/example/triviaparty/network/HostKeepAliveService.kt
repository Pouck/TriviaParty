package com.example.triviaparty.network

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.net.wifi.WifiManager
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.example.triviaparty.MainActivity
import com.example.triviaparty.R

/**
 * Keeps the process, CPU and Wi-Fi radio alive while a host game is running, so the
 * local web server keeps answering players and the Cast receiver when the host
 * switches apps or the screen turns off.
 */
class HostKeepAliveService : Service() {
    private var wakeLock: PowerManager.WakeLock? = null
    private var wifiLock: WifiManager.WifiLock? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(CHANNEL_ID, "Partie en cours", NotificationManager.IMPORTANCE_LOW)
        )
        val open = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle("Trivia Party")
            .setContentText("Partie en cours — les joueurs et la TV restent connectés")
            .setOngoing(true)
            .setContentIntent(open)
            .build()
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
        acquireLocks()
        return START_NOT_STICKY
    }

    @Suppress("DEPRECATION")
    private fun acquireLocks() {
        if (wakeLock == null) {
            wakeLock = getSystemService(PowerManager::class.java)
                .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "TriviaParty:host").apply {
                    setReferenceCounted(false); acquire(MAX_HOLD_MS)
                }
        }
        if (wifiLock == null) {
            val mode = if (Build.VERSION.SDK_INT >= 29) WifiManager.WIFI_MODE_FULL_LOW_LATENCY
            else WifiManager.WIFI_MODE_FULL_HIGH_PERF
            wifiLock = applicationContext.getSystemService(WifiManager::class.java)
                .createWifiLock(mode, "TriviaParty:host").apply { setReferenceCounted(false); acquire() }
        }
    }

    override fun onDestroy() {
        wakeLock?.takeIf { it.isHeld }?.release(); wakeLock = null
        wifiLock?.takeIf { it.isHeld }?.release(); wifiLock = null
        super.onDestroy()
    }

    companion object {
        private const val CHANNEL_ID = "host-game"
        private const val NOTIFICATION_ID = 8080
        private const val MAX_HOLD_MS = 6 * 60 * 60 * 1000L

        fun start(context: Context) {
            try {
                ContextCompat.startForegroundService(context, Intent(context, HostKeepAliveService::class.java))
            } catch (_: Exception) { /* Never block hosting if the system refuses a foreground start. */ }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, HostKeepAliveService::class.java))
        }
    }
}
