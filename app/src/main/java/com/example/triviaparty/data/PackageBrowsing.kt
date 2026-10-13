package com.example.triviaparty.data

import com.example.triviaparty.model.GamePackage
import java.text.Normalizer

fun searchablePackageText(text: String): String = Normalizer.normalize(text,Normalizer.Form.NFD)
    .replace(Regex("\\p{M}+"),"").lowercase()

fun subjectGroup(name: String): String {
    val text = searchablePackageText(name)
    return when {
        "musique" in text || "chanson" in text || "jazz" in text -> "Musique"
        "super-heros" in text || "marvel" in text || Regex("\\bdc\\b").containsMatchIn(text) -> "Super-héros"
        Regex("\\bbd\\b|manga").containsMatchIn(text) -> "BD et manga"
        "logique" in text || "enigme" in text || "devinette" in text -> "Logique et énigmes"
        "conte" in text || "legende" in text || "table ronde" in text -> "Contes et légendes"
        "cuisine" in text -> "Cuisine"
        "nature" in text || "oiseaux" in text || "insectes" in text || "animaux" in text -> "Nature"
        "mytholog" in text -> "Mythologie"
        "architecture" in text -> "Architecture"
        Regex("\\barts\\b|peinture|sculpture").containsMatchIn(text) -> "Arts"
        "cinema" in text || "film" in text || "movie" in text || "disney" in text || "ghibli" in text -> "Cinéma"
        "litterature" in text || "literature" in text -> "Littérature"
        "geograph" in text -> "Géographie"
        "invention" in text || "science" in text -> "Sciences"
        "jeu" in text || "video" in text || "gaming" in text -> "Jeux vidéo"
        "histoire" in text || "history" in text || "antiqu" in text || "moyen age" in text ||
            "renaissance" in text || "revolution" in text || "canada" in text -> "Histoire"
        "pop culture" in text || "culture populaire" in text -> "Culture populaire"
        else -> "Autres"
    }
}

fun GamePackage.browseGroup(): String = GamePackageRepository.categoryNamesFor(this)
    .mapNotNull { QuestionBankRepository.getCategoryPackage(it)?.subject?.takeIf(String::isNotBlank) }
    .distinct().singleOrNull() ?: subjectGroup(name)

fun GamePackage.isTestPackage(): Boolean = listOf(id, name).any {
    Regex("(^|[^a-z0-9])(tests?|demo|demonstration)([^a-z0-9]|$)")
        .containsMatchIn(searchablePackageText(it))
}
