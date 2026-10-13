package com.example.triviaparty.util

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.google.zxing.BarcodeFormat
import com.google.zxing.qrcode.QRCodeWriter
import com.google.zxing.common.BitMatrix
import kotlin.math.floor

@Composable
fun SimpleQrCodeComposable(data: String, size: Dp = 180.dp, modifier: Modifier = Modifier) {
    val matrix = remember(data) { joinQrMatrix(data) }
    Canvas(modifier.size(size).background(Color.White).semantics { contentDescription = "QR : $data" }) {
        val cell = floor(this.size.minDimension / matrix.width)
        val origin = (this.size.minDimension - cell * matrix.width) / 2f
        for (y in 0 until matrix.height) for (x in 0 until matrix.width) {
            if (matrix[x, y]) drawRect(Color.Black, Offset(origin + x * cell, origin + y * cell), Size(cell, cell))
        }
    }
}

internal fun joinQrMatrix(data: String): BitMatrix = QRCodeWriter().encode(data, BarcodeFormat.QR_CODE, 0, 0)
