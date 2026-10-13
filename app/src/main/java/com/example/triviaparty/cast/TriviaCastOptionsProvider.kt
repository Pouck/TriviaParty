package com.example.triviaparty.cast

import android.content.Context
import com.example.triviaparty.R
import com.google.android.gms.cast.framework.CastOptions
import com.google.android.gms.cast.framework.OptionsProvider
import com.google.android.gms.cast.framework.SessionProvider

const val TRIVIA_CAST_NAMESPACE = "urn:x-cast:com.example.triviaparty"

class TriviaCastOptionsProvider : OptionsProvider {
    override fun getCastOptions(context: Context): CastOptions = CastOptions.Builder()
        .setReceiverApplicationId(context.getString(R.string.cast_receiver_application_id))
        .setResumeSavedSession(false) // A fresh app process has no previous host room to restore.
        .setStopReceiverApplicationWhenEndingSession(true)
        .build()

    override fun getAdditionalSessionProviders(context: Context): List<SessionProvider>? = null
}
