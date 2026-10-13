package com.example.triviaparty

import com.example.triviaparty.cast.TvQuestion
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.util.zip.ZipFile

class ChronologyCardsTest {
    @Test fun everyExistingChronologyArchiveBecomesCardsWithTheSameAnswerAndStableTvLayout() {
        val json=Json { ignoreUnknownKeys=true; classDiscriminator="kind" }
        var checked=0
        File("../package-examples").walkTopDown().filter { it.extension=="zip" }.forEach { archive ->
            ZipFile(archive).use { zip ->
                zip.entries().asSequence().filter { it.name.startsWith("question-bank/") && it.name.endsWith(".json") }.forEach { entry ->
                    val bank=json.decodeFromString<CategoryQuestionFile>(zip.getInputStream(entry).reader().readText())
                    bank.questions.filter { it.isChronologyQuestion() }.forEach { original ->
                        val cards=original.withChronologyCards()
                        assertTrue("${archive.name}: ${original.id}",cards is Question.Ordering)
                        cards as Question.Ordering
                        assertEquals(original.id,cards.id)
                        assertEquals(original.basePoints,cards.basePoints)
                        assertEquals(original.penaltyPoints,cards.penaltyPoints)
                        val before=TvQuestion.from(original,true).answer!!.replace(Regex("^[A-D]\\s*[—.)\\-:]\\s*"),"")
                        assertEquals(before,TvQuestion.from(cards,true).answer)
                        val active=TvQuestion.from(cards,false)
                        assertNull(active.answer)
                        assertTrue(active.options.isEmpty())
                        assertEquals(active.prompt,TvQuestion.from(cards,true).prompt)
                        assertTrue(cards.items.all { "• ${it.text}" in active.prompt })
                        assertEquals(cards.items.map { it.id }.toSet(),cards.correctOrderIds.toSet())
                        checked++
                    }
                }
            }
        }
        assertTrue("Expected coverage of all existing chronology collections",checked>=40)
    }
    @Test fun oralTvAnswersUseOnlyTheMainNameWhileHostKeepsAliases() {
        val q=Question.TextAnswer("q","Art","Qui ?",acceptableAnswers=listOf("Johannes Vermeer","Vermeer","J. Vermeer"))
        assertEquals("Johannes Vermeer",TvQuestion.from(q,true).answer)
        assertEquals(3,q.acceptableAnswers.size)
        assertNull(TvQuestion.from(q,false).answer)
        val guess=Question.GuessWho("g","Art",clues=listOf("Indice"),acceptableAnswers=q.acceptableAnswers)
        assertEquals("Johannes Vermeer",TvQuestion.from(guess,true).answer)
    }
}
