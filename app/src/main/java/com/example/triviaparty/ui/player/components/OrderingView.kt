package com.example.triviaparty.ui.player.components

import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGesturesAfterLongPress
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.boundsInParent
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import com.example.triviaparty.model.Question

@Composable
fun OrderingView(
    items: List<Question.OrderItem>,
    onReorder: (List<Question.OrderItem>) -> Unit,
    modifier: Modifier = Modifier
) {
    var draggingId by remember { mutableStateOf<String?>(null) }
    var dragOffset by remember { mutableFloatStateOf(0f) }
    val centers=remember { mutableMapOf<String,Float>() }
    var dragCenters by remember { mutableStateOf<Map<String,Float>>(emptyMap()) }
    val colors=listOf(Color(0xFF294B67),Color(0xFF624B35),Color(0xFF345844),Color(0xFF553F68))
    val colorIds=remember(items.map { it.id }.toSet()) { items.map { it.id } }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Text("Maintenez une réponse et faites-la glisser pour la déplacer.", color = Color.LightGray, fontSize = 12.sp)
        items.forEachIndexed { index, item ->
            val isDragging = draggingId == item.id
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .onGloballyPositioned { centers[item.id]=it.boundsInParent().center.y }
                    .zIndex(if (isDragging) 1f else 0f)
                    .graphicsLayer { translationY = if (isDragging) dragOffset else 0f }
                    .background(
                        colors[colorIds.indexOf(item.id).coerceAtLeast(0)%colors.size],
                        shape = RoundedCornerShape(12.dp)
                    )
                    .pointerInput(items, item.id) {
                        detectDragGesturesAfterLongPress(
                            onDragStart = {
                                draggingId = item.id
                                dragOffset = 0f
                                dragCenters=centers.toMap()
                            },
                            onDrag = { change, amount ->
                                change.consume()
                                dragOffset += amount.y
                            },
                            onDragEnd = {
                                val from = items.indexOfFirst { it.id == item.id }
                                val center=(dragCenters[item.id] ?: 0f)+dragOffset
                                val target=dragCenters.minByOrNull { kotlin.math.abs(it.value-center) }?.key
                                val to=items.indexOfFirst { it.id==target }.takeIf { it>=0 } ?: from
                                if (from >= 0 && to != from) {
                                    val reordered = items.toMutableList()
                                    reordered.add(to, reordered.removeAt(from))
                                    onReorder(reordered)
                                }
                                draggingId = null
                                dragOffset = 0f
                            },
                            onDragCancel = {
                                draggingId = null
                                dragOffset = 0f
                            }
                        )
                    }
                    .padding(horizontal = 14.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("${index + 1}.", fontWeight = FontWeight.Bold, color = Color(0xFFFFD700), fontSize = 18.sp, modifier = Modifier.padding(end = 12.dp))
                Text(item.text, color = Color.White, fontSize = 21.sp,lineHeight=27.sp)
            }
        }
    }
}
