package com.example.triviaparty.model

import java.io.File
import kotlinx.serialization.json.*

/** Optional private audition files. The distributable app keeps its licensed fallback bank. */
class PrivateReactionBank private constructor(private val directory: File, val clips: List<ReactionClip>, val version: String) {
    fun audio(assetPath: String): ByteArray? {
        val name=assetPath.removePrefix("sounds/")
        if(assetPath!="sounds/$name" || clips.none {it.file==name}) return null
        return File(directory,name).takeIf {it.isFile}?.readBytes()
    }
    fun credits(): String? = File(directory,"credits.html").takeIf {it.isFile}?.readText()
    companion object {
        fun load(directory: File): PrivateReactionBank? = runCatching {
            val manifest=File(directory,"reactions.json").readBytes()
            val records=Json.parseToJsonElement(manifest.toString(Charsets.UTF_8)).jsonArray
            require(records.size in 2..2000)
            val clips=records.map { element ->
                val row=element.jsonObject
                fun text(key: String)=row.getValue(key).jsonPrimitive.content
                val file=text("file");val outcome=text("outcome")
                require(outcome in setOf("good","bad") && file.matches(Regex("$outcome-[0-9]{2,4}[.]wav")))
                require(File(directory,file).let {it.isFile && it.length() in 1000..5_000_000})
                ReactionClip(file,outcome,text("voice"),text("text"),row["film"]?.jsonPrimitive?.contentOrNull.orEmpty(),row["audience"]?.jsonPrimitive?.contentOrNull ?: "unreviewed")
            }
            require(clips.map {it.file}.distinct().size==clips.size)
            require(clips.map {it.outcome}.toSet()==setOf("good","bad"))
            val version=java.security.MessageDigest.getInstance("SHA-256").digest(manifest).take(8)
                .joinToString("") { "%02x".format(it) }
            PrivateReactionBank(directory,clips,"private-$version")
        }.getOrNull()
    }
}
