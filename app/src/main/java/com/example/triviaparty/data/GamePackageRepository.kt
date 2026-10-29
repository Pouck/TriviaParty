package com.example.triviaparty.data

import com.example.triviaparty.model.GamePackage
import com.example.triviaparty.model.CategoryQuestionFile
import kotlinx.serialization.json.Json

object GamePackageRepository {
    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true; classDiscriminator = "kind" }
    @Volatile private var loadedPackages: List<GamePackage>? = null
    @Volatile private var categoryNames: Map<String, String> = emptyMap()
    @Volatile private var canonicalBank: CanonicalQuestionBank? = null

    val packages: List<GamePackage>
        get() = loadedPackages ?: emptyList()

    fun categoryNamesFor(gamePackage: GamePackage): List<String> = gamePackage.categoryPackages.mapNotNull(categoryNames::get)

    fun reloadImportedPackages(packageDirectories: List<java.io.File>) {
        val importedPackages = packageDirectories.mapNotNull { directory ->
            val manifest = java.io.File(directory, "game.json")
            if (manifest.isFile) json.decodeFromString<GamePackage>(manifest.readText(Charsets.UTF_8)) else null
        }
        val allPackages = importedPackages
        require(allPackages.map { it.id }.distinct().size == allPackages.size) { "Game package IDs must be unique" }

        val importedCategoryNames = packageDirectories.flatMap { directory ->
            val categoryDirectory = java.io.File(directory, "question-bank")
            categoryDirectory.listFiles { file -> file.isFile && file.extension.equals("json", true) }
                .orEmpty().map { file ->
                    val category = json.decodeFromString<CategoryQuestionFile>(file.readText(Charsets.UTF_8))
                    file.nameWithoutExtension to category.category
                }
        }.toMap()
        val combinedCategoryNames = importedCategoryNames
        require(allPackages.all { pack -> pack.categoryPackages.isNotEmpty() && pack.categoryPackages.all { it in combinedCategoryNames } }) {
            "Every game package must reference existing category packages"
        }
        categoryNames = combinedCategoryNames
        loadedPackages = allPackages
        canonicalBank?.let(::installBankViews)
    }

    /** Compatibility catalog, built in memory from entries; never author question data here. */
    fun installBankViews(bank: CanonicalQuestionBank) {
        canonicalBank = bank
        val groups = bank.questions.flatMap { entry -> entry.presentations.map { entry to it } }
            .groupBy { it.second.legacyPackageId }
        val names = categoryNames.toMutableMap()
        val views = groups.map { (id, records) ->
            val categories = records.map { it.second.legacyCategory }.distinct()
            val keys = categories.mapIndexed { index, category ->
                val key = "bank:$id:$index"
                names[key] = category
                key
            }
            val first = records.first().second
            GamePackage(id, categories.first(), "", keys,
                com.example.triviaparty.model.HourglassConfig())
        }
        categoryNames = names
        loadedPackages = views + packages.filter { it.id !in groups }
    }
}
