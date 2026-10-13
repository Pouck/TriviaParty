package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.data.OriginalPackageMigration
import com.example.triviaparty.model.CategoryQuestionFile
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.nio.file.Files

class OriginalPackageMigrationTest {
    @Test fun originalsImportOnceAndStayDeletedOrUpdatedAfterRestart() {
        val root = Files.createTempDirectory("original-packages-").toFile()
        val archives = File("src/main/assets/original-packages").listFiles { f -> f.extension == "zip" }!!.sortedBy { it.name }
        val sources = archives.map { file -> file.nameWithoutExtension to { file.inputStream() as java.io.InputStream } }
        val json = Json { classDiscriminator = "kind" }
        try {
            OriginalPackageMigration.seed(root, sources)
            assertEquals(5, GamePackageImportRepository.importedDirectories(root).size)
            archives.forEach { archive ->
                val id = archive.nameWithoutExtension
                val categoryId = id.removePrefix("original-")
                val imported = json.decodeFromString<CategoryQuestionFile>(File(root, "$id/question-bank/$categoryId.json").readText())
                val original = json.decodeFromString<CategoryQuestionFile>(File("src/main/assets/question-bank/$categoryId.json").readText())
                assertEquals(original, imported)
            }
            val update = archives.last()
            val imported = GamePackageImportRepository.importArchive(update.inputStream(), root, update.nameWithoutExtension)
            GamePackageImportRepository.confirmImport(imported)
            val manifest = File(imported.directory, "game.json")
            manifest.writeText(manifest.readText().replace("Ensemble de questions original", "Ensemble révisé"))
            val updated = manifest.readText()
            GamePackageImportRepository.removePackage(root, archives.first().nameWithoutExtension)
            OriginalPackageMigration.seed(root, sources.map { (id, _) -> id to { error("Seeds must not reopen after migration") } })
            assertEquals(4, GamePackageImportRepository.importedDirectories(root).size)
            assertFalse(File(root, archives.first().nameWithoutExtension).exists())
            assertEquals(updated, manifest.readText())
        } finally { root.deleteRecursively() }
    }
}
