package com.example.triviaparty.model

import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName

@Serializable
enum class ImageRevealMode { NONE, PIXELATE, BLUR, SHUFFLE, UNCOVER }

/** Verified, reusable facts about the subject shown in an image question. */
@Serializable
data class ImageQuestionFacts(
    val subjectType: String,
    val subjectTitle: String? = null,
    val franchise: String? = null,
    val facts: List<ImageQuestionFact> = emptyList(),
    val sources: List<String> = emptyList()
)

@Serializable
data class ImageQuestionFact(
    val kind: String,
    val value: String,
    val role: String? = null,
    val sourceUrl: String? = null
)

@Serializable
sealed class Question {
    abstract val id: String
    abstract val category: String
    abstract val prompt: String
    abstract val imageUrl: String?
    abstract val basePoints: Int
    abstract val penaltyPoints: Int

    @Serializable
    @SerialName("multipleChoice")
    data class MultipleChoice(
        override val id: String,
        override val category: String,
        override val prompt: String,
        override val imageUrl: String? = null,
        override val basePoints: Int = 100,
        override val penaltyPoints: Int = 0,
        val options: List<String>,
        val correctOptionIndex: Int,
        val randomVariants: List<MultipleChoiceVariant> = emptyList(),
        val conceptId: String? = null,
        val explanation: String? = null
    ) : Question()

    @Serializable
    data class MultipleChoiceVariant(val prompt: String, val correctOptionIndex: Int)

    @Serializable
    data class OrderItem(val id: String, val text: String)

    @Serializable
    @SerialName("ordering")
    data class Ordering(
        override val id: String,
        override val category: String,
        override val prompt: String,
        override val imageUrl: String? = null,
        override val basePoints: Int = 100,
        override val penaltyPoints: Int = 0,
        val items: List<OrderItem>,
        val correctOrderIds: List<String>
    ) : Question()

    @Serializable
    @SerialName("textAnswer")
    data class TextAnswer(
        override val id: String,
        override val category: String,
        override val prompt: String,
        override val imageUrl: String? = null,
        override val basePoints: Int = 100,
        override val penaltyPoints: Int = 0,
        val acceptableAnswers: List<String>,
        val allowFuzzyMatch: Boolean = true,
        val conceptId: String? = null,
        val explanation: String? = null
    ) : Question()

    @Serializable
    @SerialName("guessWho")
    data class GuessWho(
        override val id: String,
        override val category: String,
        override val prompt: String = "Qui suis-je ?",
        override val imageUrl: String? = null,
        override val basePoints: Int = 15,
        override val penaltyPoints: Int = 0,
        val clues: List<String>,
        val acceptableAnswers: List<String>,
        val conceptId: String? = null,
        val imageRevealMode: ImageRevealMode = ImageRevealMode.NONE,
        val imageRevealSteps: Int = 5,
        val explanation: String? = null,
        val imageFacts: ImageQuestionFacts? = null
    ) : Question() {
        init {
            require((imageRevealMode != ImageRevealMode.NONE || clues.isNotEmpty()) && clues.all { it.isNotBlank() }) {
                "Qui suis-je ? nécessite des indices non vides."
            }
            require(imageRevealMode == ImageRevealMode.NONE || !imageUrl.isNullOrBlank()) {
                "Image reveal mode requires an image."
            }
            require(imageRevealSteps in 2..10) { "Image reveal steps must be between 2 and 10." }
            require(acceptableAnswers.isNotEmpty() && acceptableAnswers.all { it.isNotBlank() }) {
                "Qui suis-je ? nécessite au moins une réponse non vide."
            }
        }
    }

    @Serializable
    sealed class MapTarget {
        @Serializable
        @SerialName("centerRadius")
        data class CenterRadius(val xRatio: Float, val yRatio: Float, val maxDistanceRatio: Float) : MapTarget()

        @Serializable
        @SerialName("boundingBox")
        data class BoundingBox(val minXRatio: Float, val minYRatio: Float, val maxXRatio: Float, val maxYRatio: Float) : MapTarget()
    }

    @Serializable
    data class MapPinOption(val label: String, val xRatio: Float, val yRatio: Float)

    @Serializable
    @SerialName("mapChoice")
    data class MapPin(
        override val id: String,
        override val category: String,
        override val prompt: String,
        override val imageUrl: String = "",
        override val basePoints: Int = 100,
        override val penaltyPoints: Int = 0,
        val target: MapTarget? = null,
        val options: List<MapPinOption> = emptyList(),
        val correctOptionIndex: Int = 0
    ) : Question()

    @Serializable
    @SerialName("wager")
    data class Wager(
        override val id: String,
        override val category: String,
        override val prompt: String,
        override val imageUrl: String? = null,
        override val basePoints: Int = 100,
        override val penaltyPoints: Int = 0,
        val subQuestion: MultipleChoice
    ) : Question()

    @Serializable
    @SerialName("speedRace")
    data class SpeedRace(
        override val id: String,
        override val category: String,
        override val prompt: String,
        override val imageUrl: String? = null,
        override val basePoints: Int = 100,
        override val penaltyPoints: Int = 0,
        val subQuestion: MultipleChoice
    ) : Question()
}
