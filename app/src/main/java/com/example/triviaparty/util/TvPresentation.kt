package com.example.triviaparty.util

import android.app.Presentation
import android.content.Context
import android.os.Bundle
import android.view.Display
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.ComposeView
import com.example.triviaparty.model.GameSession
import com.example.triviaparty.ui.cast.CastTvScreen
import com.example.triviaparty.ui.theme.TriviaPartyTheme
import kotlinx.coroutines.flow.StateFlow

class TvPresentation(
    context: Context,
    display: Display,
    private val sessionFlow: StateFlow<GameSession?>
) : Presentation(context, display) {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val composeView = ComposeView(context).apply {
            setContent {
                TriviaPartyTheme {
                    val sessionState by sessionFlow.collectAsState()
                    val session = sessionState
                    if (session != null) {
                        CastTvScreen(session = session)
                    }
                }
            }
        }
        setContentView(composeView)
    }
}
