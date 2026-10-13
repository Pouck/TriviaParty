package com.example.triviaparty.data

import com.example.triviaparty.model.CategoryGameRules
import com.example.triviaparty.model.GamePackage

data class CombinedGameSetup(
    val categories: List<String>,
    val totalQuestions: Int,
    val categoryRules: Map<String, CategoryGameRules>,
    val conflictingCategories: List<String>
)

/** Shared categories appear once; selection order determines precedence for conflicting rules. */
fun combineGamePackages(
    packages: List<GamePackage>,
    categoryNamesFor: (GamePackage) -> List<String>,
    questionCountFor: (String) -> Int
): CombinedGameSetup {
    val rules = linkedMapOf<String, CategoryGameRules>()
    val conflicts = linkedSetOf<String>()
    packages.forEach { pack ->
        val packageRules = CategoryGameRules(pack.timingConfig, pack.answerTimeSeconds)
        categoryNamesFor(pack).distinct().forEach { category ->
            val existing = rules[category]
            if (existing == null) rules[category] = packageRules
            else if (existing != packageRules) conflicts.add(category)
        }
    }
    return CombinedGameSetup(rules.keys.toList(), rules.keys.sumOf(questionCountFor), rules, conflicts.toList())
}
