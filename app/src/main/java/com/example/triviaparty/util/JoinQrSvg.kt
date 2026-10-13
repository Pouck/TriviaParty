package com.example.triviaparty.util

import com.google.zxing.BarcodeFormat
import com.google.zxing.EncodeHintType
import com.google.zxing.qrcode.QRCodeWriter

/** Local, scannable QR with its quiet zone; no external QR service. */
object JoinQrSvg {
    fun render(url: String): String {
        val matrix = QRCodeWriter().encode(url, BarcodeFormat.QR_CODE, 0, 0,
            mapOf(EncodeHintType.MARGIN to 4))
        return buildString {
            append("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 ${matrix.width} ${matrix.height}\" shape-rendering=\"crispEdges\">")
            append("<rect width=\"100%\" height=\"100%\" fill=\"white\"/>")
            for (y in 0 until matrix.height) for (x in 0 until matrix.width) if (matrix[x, y]) {
                append("<rect x=\"$x\" y=\"$y\" width=\"1\" height=\"1\" fill=\"black\"/>")
            }
            append("</svg>")
        }
    }
}
