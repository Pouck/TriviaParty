package com.example.triviaparty.data

import android.content.ContentResolver
import android.net.Uri
import com.example.triviaparty.model.CategoryQuestionFile
import com.example.triviaparty.model.GamePackage
import com.example.triviaparty.model.Question
import kotlinx.serialization.json.Json
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.util.zip.ZipInputStream

/** Imports self-contained game ZIPs into app-private storage. */
object GamePackageImportRepository {
    private const val MAX_ARCHIVE_BYTES = 150L * 1024 * 1024
    private const val MAX_ENTRIES = 600
    private const val MAX_IMAGE_BYTES = 20L * 1024 * 1024
    private val idPattern = Regex("[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}")
    private val relativePathPattern = Regex("[a-zA-Z0-9_-][a-zA-Z0-9_.-]*(?:/[a-zA-Z0-9_-][a-zA-Z0-9_.-]*)*")
    private val json = Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }

    data class ImportedPackage(val gamePackage: GamePackage, val directory: File, val backupDirectory: File? = null)

    fun importZip(contentResolver: ContentResolver, uri: Uri, packagesDirectory: File, expectedPackageId: String? = null): ImportedPackage {
        val input = contentResolver.openInputStream(uri) ?: error("Could not open the selected ZIP")
        return importArchive(input, packagesDirectory, expectedPackageId, enforceQuestionCount = true)
    }

    fun importArchive(input: InputStream, packagesDirectory: File, expectedPackageId: String? = null,
        enforceQuestionCount: Boolean = false): ImportedPackage {
        val staging = File(packagesDirectory, ".import-${System.nanoTime()}")
        require(staging.mkdirs()) { "Unable to create an import folder" }
        try {
            var entryCount = 0
            var totalBytes = 0L
            input.use { archive ->
                ZipInputStream(archive).use { zip ->
                    while (true) {
                        val entry = zip.nextEntry ?: break
                        entryCount++
                        require(entryCount <= MAX_ENTRIES) { "The ZIP contains too many files" }
                        if (entry.isDirectory) continue
                        val path = validateEntryPath(entry.name)
                        val destination = File(staging, path).canonicalFile
                        require(isInside(staging.canonicalFile, destination)) { "Unsafe path in ZIP" }
                        require(path == "game.json" ||
                            path.matches(Regex("question-bank/[a-zA-Z0-9_-]+\\.json")) ||
                            path.startsWith("images/")) { "Unexpected file in ZIP: $path" }
                        destination.parentFile?.mkdirs()
                        val perFileLimit = if (path.startsWith("images/")) MAX_IMAGE_BYTES else 2L * 1024 * 1024
                        var fileBytes = 0L
                        FileOutputStream(destination).use { output ->
                            val buffer = ByteArray(16 * 1024)
                            while (true) {
                                val count = zip.read(buffer)
                                if (count < 0) break
                                fileBytes += count
                                totalBytes += count
                                require(fileBytes <= perFileLimit && totalBytes <= MAX_ARCHIVE_BYTES) {
                                    "The ZIP is larger than the supported import limit"
                                }
                                output.write(buffer, 0, count)
                            }
                        }
                        zip.closeEntry()
                    }
                }
            }

            val manifestFile = File(staging, "game.json")
            require(manifestFile.isFile) { "ZIP is missing game.json" }
            val gamePackage = json.decodeFromString<GamePackage>(manifestFile.readText(Charsets.UTF_8))
            require(idPattern.matches(gamePackage.id)) { "Game package id must use letters, numbers, _ or -" }
            require(expectedPackageId == null || gamePackage.id == expectedPackageId) {
                "Ce ZIP ne correspond pas au forfait à mettre à jour."
            }
            require(gamePackage.categoryPackages.isNotEmpty()) { "Game package must include at least one category" }
            require(gamePackage.categoryPackages.distinct().size == gamePackage.categoryPackages.size) {
                "Game package contains a duplicate category id"
            }
            require(gamePackage.timingConfig.secondsPerFlip > 0 && gamePackage.timingConfig.maxFlips >= 0 && gamePackage.answerTimeSeconds > 0) {
                "Game timer settings are invalid"
            }

            val allQuestionIds = mutableSetOf<String>()
            gamePackage.categoryPackages.forEach { categoryId ->
                require(idPattern.matches(categoryId)) { "Invalid category id: $categoryId" }
                val categoryFile = File(staging, "question-bank/$categoryId.json")
                require(categoryFile.isFile) { "ZIP is missing question-bank/$categoryId.json" }
                val category = json.decodeFromString<CategoryQuestionFile>(categoryFile.readText(Charsets.UTF_8))
                require(category.questions.all { it.category == category.category }) {
                    "Every question in ${categoryFile.name} must use category '${category.category}'"
                }
                category.questions.forEach { question ->
                    if (question is Question.GuessWho) {
                        require(question.clues.size.toLong() == gamePackage.timingConfig.maxFlips.toLong() + 1) {
                            "Qui suis-je ? : prévoir un indice par palier de points (${gamePackage.timingConfig.maxFlips + 1})."
                        }
                    }
                    if (question is Question.MultipleChoice) {
                        require(question.randomVariants.all {
                            it.prompt.isNotBlank() && it.correctOptionIndex in question.options.indices
                        }) { "Une variante de question contient une réponse ou un texte invalide." }
                    }
                    require(allQuestionIds.add(question.id)) { "Question id '${question.id}' is duplicated" }
                    question.imageUrls().forEach { imagePath ->
                        require(relativePathPattern.matches(imagePath) && imagePath.startsWith("images/")) {
                            "Images must use a relative images/... path"
                        }
                        val imageFile = File(staging, imagePath).canonicalFile
                        require(isInside(staging.canonicalFile, imageFile) && imageFile.isFile) {
                            "Image file '$imagePath' is missing from the ZIP"
                        }
                        require(imageFile.extension.lowercase() in setOf("png", "jpg", "jpeg", "webp")) {
                            "Use PNG, JPEG or WebP images"
                        }
                    }
                }
            }

            if(enforceQuestionCount) require(allQuestionIds.size in 5..7) {
                "Un forfait doit contenir entre 5 et 7 questions (${allQuestionIds.size} dans ce ZIP)."
            }
            packagesDirectory.mkdirs()
            val destination = File(packagesDirectory, gamePackage.id)
            require(!destination.exists() || expectedPackageId != null) {
                "Ce forfait est déjà importé. Utilisez METTRE À JOUR."
            }
            val backup = if (destination.exists()) File(packagesDirectory, ".backup-${System.nanoTime()}") else null
            if (backup != null) check(destination.renameTo(backup)) { "Impossible de sauvegarder l’ancien forfait." }
            if (!staging.renameTo(destination)) {
                if (backup != null) check(backup.renameTo(destination)) { "Impossible de restaurer l’ancien forfait." }
                error("Could not save the imported package")
            }
            return ImportedPackage(gamePackage, destination, backup)
        } catch (error: Exception) {
            staging.deleteRecursively()
            throw error
        }
    }

    fun confirmImport(imported: ImportedPackage) {
        imported.backupDirectory?.deleteRecursively()
    }

    fun rollbackImport(imported: ImportedPackage) {
        check(imported.directory.deleteRecursively()) { "Impossible d’annuler l’importation." }
        imported.backupDirectory?.let { backup ->
            check(backup.renameTo(imported.directory)) { "Impossible de restaurer l’ancien forfait." }
        }
    }

    fun removePackage(packagesDirectory: File, packageId: String) {
        require(idPattern.matches(packageId)) { "Invalid package id" }
        val root = packagesDirectory.canonicalFile
        val directory = File(root, packageId).canonicalFile
        require(isInside(root, directory) && directory.isDirectory) { "Forfait importé introuvable." }
        check(directory.deleteRecursively()) { "Impossible de supprimer le forfait." }
    }

    fun importedDirectories(packagesDirectory: File): List<File> = packagesDirectory
        .listFiles { file -> file.isDirectory && !file.name.startsWith(".") }
        .orEmpty()
        .sortedBy { it.name }

    fun mediaFile(packagesDirectory: File, packageId: String, relativePath: String): File? {
        if (!idPattern.matches(packageId) || !relativePathPattern.matches(relativePath) || !relativePath.startsWith("images/")) return null
        val root = File(packagesDirectory, packageId).canonicalFile
        val image = File(root, relativePath).canonicalFile
        return image.takeIf { isInside(root, it) && it.isFile }
    }

    private fun validateEntryPath(name: String): String {
        val normalized = name.replace('\\', '/')
        require(!normalized.startsWith('/') && !normalized.contains(':') &&
            normalized.split('/').none { it.isBlank() || it == "." || it == ".." }) {
            "Unsafe path in ZIP"
        }
        require(relativePathPattern.matches(normalized)) { "Unsupported filename in ZIP: $name" }
        return normalized
    }

    private fun isInside(root: File, candidate: File): Boolean =
        candidate.path.startsWith(root.path + File.separator)

    private fun Question.imageUrls(): List<String> = when (this) {
        is Question.MultipleChoice -> listOfNotNull(imageUrl)
        is Question.Ordering -> listOfNotNull(imageUrl)
        is Question.TextAnswer -> listOfNotNull(imageUrl)
        is Question.GuessWho -> listOfNotNull(imageUrl)
        is Question.MapPin -> listOf(imageUrl).filter(String::isNotBlank)
        is Question.Wager -> listOfNotNull(imageUrl) + subQuestion.imageUrls()
        is Question.SpeedRace -> listOfNotNull(imageUrl) + subQuestion.imageUrls()
    }
}
