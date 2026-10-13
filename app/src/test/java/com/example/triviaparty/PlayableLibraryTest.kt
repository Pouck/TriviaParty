package com.example.triviaparty

import com.example.triviaparty.data.*
import com.example.triviaparty.model.*
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test
import java.io.*
import java.nio.file.Files
import java.util.zip.*

class PlayableLibraryTest {
    private val json=Json { classDiscriminator="kind"; ignoreUnknownKeys=true }
    @Test fun everyCurrentPackageImportsWithFiveToSevenAndEveryHistoricalQuestionSurvives() {
        val library=File("../game-library/current")
        val archives=library.listFiles { f->f.extension=="zip" }.orEmpty()
        val catalog=Json.parseToJsonElement(File(library,"CATALOGUE.json").readText()).jsonArray
        assertEquals(catalog.size,archives.size)
        val directory=Files.createTempDirectory("playable-library").toFile()
        val snapshots=listOf(QuestionBankRepository to listOf("fileQuestions","categoryMetadata"),GamePackageRepository to listOf("loadedPackages","categoryNames"))
            .flatMap { (repo,names) -> names.map { name -> val field=repo.javaClass.getDeclaredField(name).apply { isAccessible=true }; Triple(repo,field,field.get(repo)) } }
        val imported=mutableListOf<File>();val questionIds=mutableSetOf<String>();val packageIds=mutableSetOf<String>();var tests=0
        try {
            archives.forEach { archive ->
                val result=GamePackageImportRepository.importArchive(archive.inputStream(),directory,enforceQuestionCount=true)
                val game=result.gamePackage
                assertTrue(packageIds.add(game.id));imported.add(result.directory)
                val banks=game.categoryPackages.map { id -> json.decodeFromString<CategoryQuestionFile>(File(result.directory,"question-bank/$id.json").readText()) }
                assertTrue(banks.sumOf { it.questions.size } in 5..7)
                if(game.isTestPackage()) { tests++;assertEquals(5,banks.sumOf { it.questions.size }) }
                banks.flatMap { it.questions }.forEach { question ->
                    assertTrue(questionIds.add(question.id))
                    assertEquals(game.name,question.category)
                    if(question is Question.GuessWho) {
                        assertEquals(question.clues.size-1,game.timingConfig.maxFlips)
                        assertEquals(question.clues.size*5,question.basePoints)
                    }
                    if(question is Question.Ordering) assertEquals(question.items.map { it.id }.toSet(),question.correctOrderIds.toSet())
                }
            }
            assertEquals(6,tests)
            QuestionBankRepository.reloadImportedPackages(imported);GamePackageRepository.reloadImportedPackages(imported)
            GamePackageRepository.packages.forEach { game ->
                val banks=GamePackageRepository.categoryNamesFor(game).map { QuestionBankRepository.getCategoryPackage(it)!! }
                assertEquals(banks.map { it.subject }.distinct().single(),game.browseGroup())
            }
            val original=File("../package-examples").walkTopDown().filter { it.isFile && it.extension=="zip" }.flatMap { archive ->
                ZipFile(archive).use { z -> z.entries().asSequence().filter { it.name.startsWith("question-bank/") && it.name.endsWith(".json") }
                    .flatMap { entry -> Json.parseToJsonElement(z.getInputStream(entry).bufferedReader().readText()).jsonObject["questions"]!!.jsonArray.asSequence() }.map { it.jsonObject["id"]!!.jsonPrimitive.content }.toList() }.asSequence()
            }.toSet()
            assertTrue("Historical question IDs missing: ${original-questionIds}",questionIds.containsAll(original))
            val additions=questionIds-original
            // The root charade archive may be omitted by the Windows test fixture traversal.
            assertTrue("Unexpected added IDs: $additions",additions.all { it=="charades-nun-ace" || it.startsWith("resize-20261012-") || it.startsWith("test-20261012-") })
            assertEquals(40,additions.count { it.startsWith("resize-20261012-") || it.startsWith("test-20261012-") })
            val migration=Json.parseToJsonElement(File(library,"MIGRATION.json").readText()).jsonObject
            assertTrue(migration["retiredPackageIds"]!!.jsonArray.none { it.jsonPrimitive.content in packageIds })
            assertEquals(questionIds,migration["questionMap"]!!.jsonObject.keys)
        } finally {
            snapshots.forEach { (repo,field,value)->field.set(repo,value) }
            directory.deleteRecursively()
        }
    }
    @Test fun publicImportRejectsShortAndOversizedPackagesWithoutInstallingThem() {
        val archive=File("../game-library/current/architecture-buzzer-europe-20261011.zip")
        for(count in listOf(1,8)) {
            val directory=Files.createTempDirectory("package-size-rejection").toFile()
            try {
                val bytes=ByteArrayOutputStream()
                ZipFile(archive).use { source -> ZipOutputStream(bytes).use { target ->
                    source.entries().asSequence().forEach { entry ->
                        var content=source.getInputStream(entry).readBytes()
                        if(entry.name.startsWith("question-bank/")) {
                            val bank=Json.parseToJsonElement(content.decodeToString()).jsonObject
                            val first=bank["questions"]!!.jsonArray.first().jsonObject
                            val qs=JsonArray((0 until count).map { n -> JsonObject(first + ("id" to JsonPrimitive("test-size-$n"))) })
                            content=JsonObject(bank+("questions" to qs)).toString().toByteArray()
                        }
                        target.putNextEntry(ZipEntry(entry.name));target.write(content);target.closeEntry()
                    }
                } }
                val error=runCatching { GamePackageImportRepository.importArchive(ByteArrayInputStream(bytes.toByteArray()),directory,enforceQuestionCount=true) }.exceptionOrNull()
                assertNotNull(error);assertTrue(error!!.message.orEmpty().contains("entre 5 et 7"))
                assertTrue(directory.listFiles().orEmpty().isEmpty())
            } finally { directory.deleteRecursively() }
        }
    }
}
