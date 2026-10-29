package com.example.triviaparty.model

import kotlinx.serialization.Serializable

/** A phone/player identity that contributes answers to a shared scored team. */
@Serializable
data class Player(
    val id: String,
    val name: String,
    val teamId: String,
    val sessionToken: String,
    val isConnected: Boolean = true
)
