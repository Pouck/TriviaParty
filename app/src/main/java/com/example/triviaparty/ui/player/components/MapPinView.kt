package com.example.triviaparty.ui.player.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.triviaparty.model.Question

@Composable
fun MapPinView(
    imageUrl: String,
    options: List<Question.MapPinOption>,
    selectedPin: Pair<Float, Float>?,
    onPinSelected: (xRatio: Float, yRatio: Float) -> Unit,
    modifier: Modifier = Modifier
) {
    BoxWithConstraints(
        modifier = modifier.clip(RoundedCornerShape(12.dp)).background(Color(0xFF2D2D3F))
    ) {
        if (imageUrl.isBlank()) {
            Canvas(Modifier.fillMaxSize()) {
                drawRect(Color(0xFFB9D8E8))
                for (i in 1..5) {
                    val x = size.width * i / 6f
                    val y = size.height * i / 6f
                    drawLine(Color.White.copy(alpha = 0.45f), androidx.compose.ui.geometry.Offset(x, 0f), androidx.compose.ui.geometry.Offset(x, size.height), 1f)
                    drawLine(Color.White.copy(alpha = 0.45f), androidx.compose.ui.geometry.Offset(0f, y), androidx.compose.ui.geometry.Offset(size.width, y), 1f)
                }
                val land = Path().apply {
                    moveTo(size.width * .20f, size.height * .12f)
                    lineTo(size.width * .47f, size.height * .10f)
                    lineTo(size.width * .54f, size.height * .26f)
                    lineTo(size.width * .72f, size.height * .34f)
                    lineTo(size.width * .69f, size.height * .53f)
                    lineTo(size.width * .61f, size.height * .65f)
                    lineTo(size.width * .57f, size.height * .84f)
                    lineTo(size.width * .46f, size.height * .77f)
                    lineTo(size.width * .41f, size.height * .66f)
                    lineTo(size.width * .31f, size.height * .68f)
                    lineTo(size.width * .25f, size.height * .54f)
                    lineTo(size.width * .18f, size.height * .41f)
                    close()
                }
                drawPath(land, Color(0xFFE5E0C6))
                drawPath(land, Color(0xFF8C9C8B), style = Stroke(width = 3f))
            }
        } else {
            AsyncImage(
                model = imageUrl,
                contentDescription = "Carte de question",
                contentScale = ContentScale.FillBounds,
                modifier = Modifier.fillMaxSize()
            )
        }
        options.forEach { option ->
            val selected = selectedPin?.let {
                kotlin.math.abs(it.first - option.xRatio) < 0.001f && kotlin.math.abs(it.second - option.yRatio) < 0.001f
            } == true
            Box(
                modifier = Modifier
                    .offset(x = maxWidth * option.xRatio - 20.dp, y = maxHeight * option.yRatio - 20.dp)
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(if (selected) Color(0xFFFFD700) else Color(0xFF20202D).copy(alpha = 0.9f))
                    .clickable { onPinSelected(option.xRatio, option.yRatio) },
                contentAlignment = Alignment.Center
            ) {
                Text(option.label, color = if (selected) Color.Black else Color.White, fontSize = 17.sp)
            }
        }
    }
}
