package com.example.triviaparty.model

import kotlinx.serialization.Serializable

@Serializable
data class HourglassConfig(
    val secondsPerFlip: Int = 10,
    val decayPercentagePerFlip: Float = 0.10f,
    val maxFlips: Int = 5,
    /** Optional fixed points removed at each completed interval, instead of percentage decay. */
    val pointsDecayPerFlip: Int? = null,
    val pointsDecayPerSecond: Int? = null
) {
    /**
     * Calculates score awarded based on base points and current flip count.
     * Ensures correct answers always award at least 20% of base points.
     */
    fun calculateScore(basePoints: Int, flipNumber: Int, elapsedSecondsInFlip: Int = 0): Int {
        val clampedFlip = flipNumber.coerceIn(0, maxFlips)
        pointsDecayPerSecond?.let { drop ->
            return (basePoints-(clampedFlip*secondsPerFlip+elapsedSecondsInFlip.coerceAtLeast(0))*drop.coerceAtLeast(0)).coerceAtLeast(0)
        }
        pointsDecayPerFlip?.let { drop ->
            return (basePoints - clampedFlip * drop.coerceAtLeast(0)).coerceAtLeast(0)
        }
        // Reward changes only when a complete timer segment has elapsed.
        val remainingFactor = (1.0f - (clampedFlip * decayPercentagePerFlip)).coerceAtLeast(0.20f)
        return (basePoints * remainingFactor).toInt().coerceAtLeast(10)
    }
}
