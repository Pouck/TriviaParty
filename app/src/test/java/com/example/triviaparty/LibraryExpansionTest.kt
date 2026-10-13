package com.example.triviaparty

import com.example.triviaparty.cast.TvQuestion
import com.example.triviaparty.data.*
import com.example.triviaparty.model.*
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class LibraryExpansionTest {
    @Test fun everyExpandedPackageImportsWithBalancedChoicesOfflineImagesAndPrivateAnswers() {
        val archives=File("../package-examples/library-2026-10-12").listFiles { f->f.extension=="zip" }.orEmpty()
        assertEquals(136,archives.size)
        val json=Json { classDiscriminator="kind" }
        val directory=Files.createTempDirectory("library-expansion-").toFile()
        val ids=mutableSetOf<String>();val modes=mutableMapOf<String,Int>()
        try {
            archives.forEach { archive ->
                val imported=GamePackageImportRepository.importArchive(archive.inputStream(),directory)
                val game=imported.gamePackage
                val bank=json.decodeFromString<CategoryQuestionFile>(File(imported.directory,"question-bank/${game.categoryPackages.single()}.json").readText())
                assertEquals(5,bank.questions.size)
                assertEquals(game.name,bank.subject,game.browseGroup())
                assertEquals(10,game.answerTimeSeconds)
                val mode=when(bank.questions.first()) { is Question.GuessWho->"qsj";is Question.Ordering->"chronologie";is Question.TextAnswer->"buzzer";else->"qcm" }
                modes[mode]=modes.getOrDefault(mode,0)+1
                val segment=if(mode=="qsj")20 else if(mode=="chronologie")15 else if(bank.subject=="Logique et énigmes")10 else 5
                assertEquals(segment,game.timingConfig.secondsPerFlip)
                assertEquals(if(mode=="qsj")3 else 2,game.timingConfig.maxFlips)
                assertEquals(if(mode=="qsj")CategoryAnswerMode.BUZZER else if(mode=="buzzer")CategoryAnswerMode.BUZZER else CategoryAnswerMode.SIMULTANEOUS,bank.answerMode)
                bank.questions.forEach { q ->
                    assertTrue(ids.add(q.id));assertEquals(bank.category,q.category)
                    assertEquals(if(mode=="qsj")20 else 15,q.basePoints)
                    assertEquals(if(mode=="qsj")5 else 0,q.penaltyPoints)
                    q.imageUrl?.let { assertTrue(File(imported.directory,it).isFile);assertTrue(File(imported.directory,it).length()>1000) }
                    assertNull(TvQuestion.from(q,false).answer)
                    assertNotNull(TvQuestion.from(q,true).answer)
                    if(q is Question.GuessWho)assertEquals(4,q.clues.distinct().size)
                    if(q is Question.Ordering){
                        assertEquals(3,q.items.distinctBy { it.text }.size)
                        assertEquals(q.items.map { it.id }.toSet(),q.correctOrderIds.toSet())
                        assertNotEquals(q.items.map { it.id },q.correctOrderIds)
                        assertTrue(TvQuestion.from(q,false).options.isEmpty())
                        assertEquals(TvQuestion.from(q,false).prompt,TvQuestion.from(q,true).prompt)
                    }
                }
                if(mode=="qcm"||mode=="buzzer")assertEquals(2,bank.questions.count { it.imageUrl!=null })
                val choices=bank.questions.filterIsInstance<Question.MultipleChoice>()
                if(choices.isNotEmpty())assertEquals(listOf(1,1,1,2),(0..3).map { p->choices.count { it.correctOptionIndex==p } }.sorted())
            }
            assertEquals(680,ids.size)
            assertEquals(mapOf("qcm" to 42,"buzzer" to 42,"qsj" to 42,"chronologie" to 10),modes)
        }finally { directory.deleteRecursively() }
    }
}
