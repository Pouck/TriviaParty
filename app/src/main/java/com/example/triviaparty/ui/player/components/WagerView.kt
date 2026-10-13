package com.example.triviaparty.ui.player.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.triviaparty.model.Question

@Composable
fun WagerView(
    wagerQuestion: Question.Wager,
    maxWagerPoints: Int,
    onSelectionChanged: (wagerAmount: Int, selectedOptionIndex: Int) -> Unit,
    modifier: Modifier = Modifier
) {
    var wagerAmount by remember(wagerQuestion.id, maxWagerPoints) { mutableFloatStateOf(0f) }
    var selectedOptionIndex by remember(wagerQuestion.id) { mutableIntStateOf(-1) }

    val maxPointsClamped = maxWagerPoints.coerceAtLeast(0)

    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Wager Slider Card
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFF2D2D3F), shape = RoundedCornerShape(12.dp))
                .padding(16.dp)
        ) {
            Text(
                text = "Mise : ${wagerAmount.toInt().coerceIn(0, maxPointsClamped)} points",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFFD700)
            )

            Spacer(modifier = Modifier.height(8.dp))

            Slider(
                value = wagerAmount,
                enabled = maxPointsClamped > 0,
                onValueChange = {
                    wagerAmount = it
                    if (selectedOptionIndex != -1) {
                        onSelectionChanged(wagerAmount.toInt().coerceIn(0, maxPointsClamped), selectedOptionIndex)
                    }
                },
                valueRange = 0f..maxPointsClamped.coerceAtLeast(1).toFloat(),
                colors = SliderDefaults.colors(
                    thumbColor = Color(0xFFFFD700),
                    activeTrackColor = Color(0xFFFFD700)
                )
            )

            Text(
                text = "Mise maximale : $maxPointsClamped pts",
                fontSize = 12.sp,
                color = Color.Gray
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Multiple Choice Options
        wagerQuestion.subQuestion.options.forEachIndexed { index, optionText ->
            val isSelected = selectedOptionIndex == index
            Button(
                onClick = {
                    selectedOptionIndex = index
                    onSelectionChanged(wagerAmount.toInt().coerceIn(0, maxPointsClamped), selectedOptionIndex)
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isSelected) Color(0xFFFFD700) else Color(0xFF2D2D3F),
                    contentColor = if (isSelected) Color.Black else Color.White
                )
            ) {
                Text(
                    text = optionText,
                    fontSize = 16.sp,
                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
        }
    }
}
