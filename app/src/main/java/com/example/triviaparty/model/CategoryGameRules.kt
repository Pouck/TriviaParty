package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
data class CategoryGameRules(
    val timingConfig: HourglassConfig,
    val answerTimeSeconds: Int
)
