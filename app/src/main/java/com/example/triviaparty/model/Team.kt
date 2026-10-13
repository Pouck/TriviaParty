package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
data class Team(
    val id: String,
    val name: String,
    val score: Int = 0,
    val isConnected: Boolean = true,
    val sessionToken: String
)
