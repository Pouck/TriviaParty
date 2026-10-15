package com.example.triviaparty.model

import kotlin.random.Random

data class ReactionClip(val file: String,val outcome: String,val voice: String,val text: String,val source: String = "")

/** A per-game shuffle bag: exhaust an outcome before repeating a clip. */
class AnswerReactionPicker(private val catalogue: List<ReactionClip> = ReactionCatalogue.clips) {
    private val remaining=mutableMapOf<String,MutableList<ReactionClip>>()
    private val recentPhrases=ArrayDeque<String>()
    private var lastVoice: String?=null
    private var lastSource: String?=null
    @Synchronized fun choose(outcome:String,previous:String?,random:Random=Random.Default):String {
        val pool=remaining.getOrPut(outcome){mutableListOf()}
        if(pool.isEmpty()) pool.addAll(catalogue.filter {it.outcome==outcome}.shuffled(random))
        require(pool.isNotEmpty())
        fun phrase(clip:ReactionClip)=clip.text.lowercase().trim().trimEnd('!','?','.')
        val noRepeat=pool.filter {it.file!=previous}.ifEmpty {pool.toList()}
        val varied=noRepeat.filter {it.voice!=lastVoice && phrase(it) !in recentPhrases && (it.source.isBlank() || it.source!=lastSource)}
            .ifEmpty {noRepeat.filter {it.source.isNotBlank() && it.source!=lastSource && it.voice!=lastVoice}}
            .ifEmpty {noRepeat.filter {it.voice!=lastVoice && phrase(it) !in recentPhrases}}
            .ifEmpty {noRepeat.filter {it.voice!=lastVoice}}
            .ifEmpty {noRepeat.filter {phrase(it) !in recentPhrases}}
            .ifEmpty {noRepeat}
        val chosen=varied[random.nextInt(varied.size)]
        pool.remove(chosen);lastVoice=chosen.voice;lastSource=chosen.source.takeIf {it.isNotBlank()};recentPhrases.addLast(phrase(chosen))
        while(recentPhrases.size>6)recentPhrases.removeFirst()
        return chosen.file
    }
}

/** Recorded clips, shared by the local TV page and Cast receiver. */
object AnswerReactions {
    private val picker=AnswerReactionPicker()
    fun clips(outcome:String):List<String> = ReactionCatalogue.clips.filter {it.outcome==outcome}.map {it.file}
    fun isAllowed(file:String?):Boolean = file in clips("good")+clips("bad")+listOf("good.wav","bad.wav","buzzer.wav","enabled.wav","good-ping.wav","bad-ping.wav","game-end.wav","good-02.mp3","good-26.mp3","bad-04.mp3","bad-14.mp3")
    fun choose(outcome:String,previous:String?,random:Random=Random.Default):String=picker.choose(outcome,previous,random)
}
