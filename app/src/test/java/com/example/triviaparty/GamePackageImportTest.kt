package com.example.triviaparty

import com.example.triviaparty.data.GamePackageImportRepository
import com.example.triviaparty.model.HourglassConfig
import com.example.triviaparty.model.CategoryQuestionFile
import com.example.triviaparty.util.LocalMediaUrls
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream
import kotlin.io.path.createTempDirectory

class GamePackageImportTest {
    @Test
    fun importsCategoryAndLocalImageFromZip() {
        val root = createTempDirectory("game-package-import-").toFile()
        try {
            val entries = linkedMapOf(
                "game.json" to """{"id":"demo","name":"Demo","description":"Test","categoryPackages":["demo"],"answerTimeSeconds":7,"timingConfig":{"secondsPerFlip":10,"decayPercentagePerFlip":0.1,"maxFlips":5,"pointsDecayPerFlip":5}}""",
                "question-bank/demo.json" to """{"category":"Demo","answerMode":"BUZZER","answerTimeSeconds":5,"questionTypes":["Oral"],"questions":[{"kind":"textAnswer","id":"q-demo","category":"Demo","prompt":"","imageUrl":"images/sample.png","basePoints":20,"penaltyPoints":0,"acceptableAnswers":["Answer"],"allowFuzzyMatch":false}]}""",
                "images/sample.png" to "test image bytes"
            )
            val imported = GamePackageImportRepository.importArchive(zip(entries), File(root, "packages"))
            assertEquals("demo", imported.gamePackage.id)
            assertEquals(7, imported.gamePackage.answerTimeSeconds)
            assertEquals(5, imported.gamePackage.timingConfig.pointsDecayPerFlip)
            val category = Json { classDiscriminator = "kind" }
                .decodeFromString<CategoryQuestionFile>(File(imported.directory, "question-bank/demo.json").readText())
            assertEquals(5, category.answerTimeSeconds)
            assertTrue(File(imported.directory, "images/sample.png").isFile)
            assertNotNull(GamePackageImportRepository.mediaFile(File(root, "packages"), "demo", "images/sample.png"))
            assertNull(GamePackageImportRepository.mediaFile(File(root, "packages"), "demo", "images/../game.json"))
        } finally {
            root.deleteRecursively()
        }
    }

    @Test
    fun localMediaUrlUsesHostLanAddress() {
        assertEquals(
            "http://192.168.1.2:8080/media/demo/images/sample.png",
            LocalMediaUrls.resolve("local-media://demo/images/sample.png", "192.168.1.2")
        )
        assertEquals("https://example.test/image.png", LocalMediaUrls.resolve("https://example.test/image.png", "192.168.1.2"))
        assertNull(LocalMediaUrls.resolve("local-media://demo/../private.png", "192.168.1.2"))
    }

    @Test
    fun fixedPointPackageSettingRoundTripsAndScoresAsConfigured() {
        val config = HourglassConfig(secondsPerFlip = 10, pointsDecayPerFlip = 5)
        assertEquals(listOf(20, 15, 10, 5, 0), (0..4).map { config.calculateScore(20, it) })
    }

    @Test
    fun updatesCanBeConfirmedOrRolledBackAndInvalidUpdatesPreserveOriginal() {
        val root = createTempDirectory("package-update-").toFile()
        fun entries(name: String, id: String = "demo") = linkedMapOf(
            "game.json" to """{"id":"$id","name":"$name","description":"","categoryPackages":["demo"],"timingConfig":{}}""",
            "question-bank/demo.json" to """{"category":"Demo","questionTypes":["Oral"],"questions":[{"kind":"textAnswer","id":"q","category":"Demo","prompt":"Question","imageUrl":"images/test.png","acceptableAnswers":["Réponse"]}]}""",
            "images/test.png" to name
        )
        try {
            GamePackageImportRepository.importArchive(zip(entries("Original")), root)
            val image = File(root, "demo/images/test.png")
            assertTrue(runCatching { GamePackageImportRepository.importArchive(zip(entries("Duplicate")), root) }.isFailure)
            assertTrue(runCatching { GamePackageImportRepository.importArchive(zip(entries("Wrong", "other")), root, "demo") }.isFailure)
            assertTrue(runCatching { GamePackageImportRepository.importArchive(zip(entries("Broken").apply { remove("images/test.png") }), root, "demo") }.isFailure)
            assertEquals("Original", image.readText())
            val replacement = GamePackageImportRepository.importArchive(zip(entries("Replacement")), root, "demo")
            assertEquals("Replacement", image.readText())
            assertTrue(replacement.backupDirectory!!.isDirectory)
            assertEquals(1, GamePackageImportRepository.importedDirectories(root).size)
            GamePackageImportRepository.rollbackImport(replacement)
            assertEquals("Original", image.readText())
            val confirmed = GamePackageImportRepository.importArchive(zip(entries("Corrected")), root, "demo")
            GamePackageImportRepository.confirmImport(confirmed)
            assertEquals("Corrected", image.readText())
            assertTrue(!confirmed.backupDirectory!!.exists())
            GamePackageImportRepository.importArchive(zip(entries("Other", "other")), root)
            assertTrue(runCatching { GamePackageImportRepository.removePackage(root, "../other") }.isFailure)
            GamePackageImportRepository.removePackage(root, "demo")
            assertEquals(listOf("other"), GamePackageImportRepository.importedDirectories(root).map { it.name })
        } finally { root.deleteRecursively() }
    }

    private fun zip(entries: Map<String, String>): ByteArrayInputStream {
        val bytes = ByteArrayOutputStream()
        ZipOutputStream(bytes).use { output ->
            entries.forEach { (name, value) ->
                output.putNextEntry(ZipEntry(name))
                output.write(value.toByteArray(Charsets.UTF_8))
                output.closeEntry()
            }
        }
        return ByteArrayInputStream(bytes.toByteArray())
    }
}
