package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
data class GamePackage(
    val id: String,
    val name: String,
    val description: String,
    val categoryPackages: List<String>,
    val timingConfig: HourglassConfig,
    val answerTimeSeconds: Int = 10
)
