package com.example.triviaparty.model

import java.io.File
import kotlinx.serialization.json.*

/** Optional private audition files. The distributable app keeps its licensed fallback bank. */
class PrivateReactionBank private constructor(private val directory: File, val clips: List<ReactionClip>) {
    fun audio(assetPath: String): ByteArray? {
        val name=assetPath.removePrefix("sounds/")
        if(assetPath!="sounds/$name" || clips.none {it.file==name}) return null
        return File(directory,name).takeIf {it.isFile}?.readBytes()
    }
    fun credits(): String? = File(directory,"credits.html").takeIf {it.isFile}?.readText()
    companion object {
        fun load(directory: File): PrivateReactionBank? = runCatching {
            val records=Json.parseToJsonElement(File(directory,"reactions.json").readText()).jsonArray
            require(records.size in 2..100)
            val clips=records.map { element ->
                val row=element.jsonObject
                fun text(key: String)=row.getValue(key).jsonPrimitive.content
                val file=text("file");val outcome=text("outcome")
                require(outcome in setOf("good","bad") && file.matches(Regex("$outcome-[0-9]{2}[.]wav")))
                require(File(directory,file).let {it.isFile && it.length() in 1000..5_000_000})
                ReactionClip(file,outcome,text("voice"),text("text"))
            }
            require(clips.map {it.file}.distinct().size==clips.size)
            require(clips.map {it.outcome}.toSet()==setOf("good","bad"))
            PrivateReactionBank(directory,clips)
        }.getOrNull()
    }
}
