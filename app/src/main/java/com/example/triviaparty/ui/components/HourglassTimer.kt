package com.example.triviaparty.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.clipPath
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.triviaparty.model.HourglassConfig

@Composable
fun HourglassTimer(
    currentFlipNumber: Int,
    elapsedSecondsInFlip: Int,
    config: HourglassConfig,
    basePoints: Int,
    modifier: Modifier = Modifier
) {
    val sandProgress by animateFloatAsState(
        targetValue = (elapsedSecondsInFlip.toFloat() / config.secondsPerFlip.coerceAtLeast(1)).coerceIn(0f, 1f),
        animationSpec = tween(durationMillis = 500), label = "sandProgress")

    val remainingSeconds = (config.secondsPerFlip - elapsedSecondsInFlip).coerceAtLeast(0)
    val currentPointsReward = config.calculateScore(basePoints, currentFlipNumber,elapsedSecondsInFlip)

    Column(
        modifier = modifier
            .background(Color(0xFF1E1E2C), shape = RoundedCornerShape(16.dp))
            .padding(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Hourglass Visual
        Box(
            modifier = Modifier
                .size(width = 54.dp, height = 72.dp),
            contentAlignment = Alignment.Center
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val w = size.width
                val h = size.height

                val glassPath = Path().apply {
                    moveTo(w * .18f, h * .12f)
                    lineTo(w * .82f, h * .12f)
                    cubicTo(w * .82f, h * .36f, w * .53f, h * .40f, w * .53f, h * .50f)
                    cubicTo(w * .53f, h * .60f, w * .82f, h * .64f, w * .82f, h * .88f)
                    lineTo(w * .18f, h * .88f)
                    cubicTo(w * .18f, h * .64f, w * .47f, h * .60f, w * .47f, h * .50f)
                    cubicTo(w * .47f, h * .40f, w * .18f, h * .36f, w * .18f, h * .12f)
                    close()
                }
                val sand = Color(0xFFFFD15C)
                drawPath(glassPath, Color(0xFF91CCE3).copy(alpha = .18f))
                clipPath(glassPath) {
                    val upperHeight = h * .36f * kotlin.math.sqrt(1f - sandProgress)
                    drawRect(sand, Offset(0f, h * .48f - upperHeight), Size(w, upperHeight))
                    val lowerHeight = h * .36f * kotlin.math.sqrt(sandProgress)
                    drawRect(sand, Offset(0f, h * .88f - lowerHeight), Size(w, lowerHeight))
                    if (sandProgress < 1f) drawLine(sand, Offset(w * .5f, h * .48f), Offset(w * .5f, h * .88f - lowerHeight), w * .025f)
                }
                drawPath(glassPath, Color(0xFFB5DFEA), style = androidx.compose.ui.graphics.drawscope.Stroke(width = 1.5.dp.toPx()))
                val wood = Color(0xFFB88335)
                drawLine(wood, Offset(w * .08f, h * .08f), Offset(w * .92f, h * .08f), 5.dp.toPx())
                drawLine(wood, Offset(w * .08f, h * .92f), Offset(w * .92f, h * .92f), 5.dp.toPx())
                drawLine(wood, Offset(w * .1f, h * .08f), Offset(w * .1f, h * .92f), 2.dp.toPx())
                drawLine(wood, Offset(w * .9f, h * .08f), Offset(w * .9f, h * .92f), 2.dp.toPx())
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Timer text
        Text(
            text = if(config.pointsDecayPerSecond!=null) "$currentPointsReward pts" else "${remainingSeconds}s",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFFD700)
        )

        Spacer(modifier = Modifier.height(4.dp))

        // Point Reward Indicator
        Text(
            text = "$currentPointsReward pts",
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium,
            color = Color.White
        )

        Text(
            text = "Palier ${currentFlipNumber + 1}/${config.maxFlips + 1}",
            fontSize = 12.sp,
            color = Color.Gray
        )
    }
}
