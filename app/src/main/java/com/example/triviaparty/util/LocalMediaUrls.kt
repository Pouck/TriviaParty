package com.example.triviaparty.util

import com.example.triviaparty.model.GameSession
import com.example.triviaparty.model.Question

object LocalMediaUrls {
    private const val PREFIX = "local-media://"

    fun resolve(value: String?, hostIp: String, port: Int = 8080): String? {
        if (value.isNullOrBlank()) return null
        if (!value.startsWith(PREFIX)) return value
        val path = value.removePrefix(PREFIX)
        if (path.split('/').any { it.isBlank() || it == "." || it == ".." }) return null
        return "http://$hostIp:$port/media/$path"
    }

    fun networkSession(session: GameSession, port: Int = 8080): GameSession = session.copy(
        currentQuestion = session.currentQuestion?.resolveLocalMedia(session.hostIpAddress, port)
    )

    private fun Question.resolveLocalMedia(hostIp: String, port: Int): Question {
        fun resolved(value: String?): String? = resolve(value, hostIp, port)
        return when (this) {
            is Question.MultipleChoice -> copy(imageUrl = resolved(imageUrl))
            is Question.Ordering -> copy(imageUrl = resolved(imageUrl))
            is Question.TextAnswer -> copy(imageUrl = resolved(imageUrl))
            is Question.GuessWho -> copy(imageUrl = resolved(imageUrl))
            is Question.MapPin -> copy(imageUrl = resolved(imageUrl).orEmpty())
            is Question.Wager -> copy(imageUrl = resolved(imageUrl), subQuestion = subQuestion.copy(imageUrl = resolved(subQuestion.imageUrl)))
            is Question.SpeedRace -> copy(imageUrl = resolved(imageUrl), subQuestion = subQuestion.copy(imageUrl = resolved(subQuestion.imageUrl)))
        }
    }
}
