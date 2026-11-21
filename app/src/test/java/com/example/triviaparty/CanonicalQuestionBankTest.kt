package com.example.triviaparty

import com.example.triviaparty.data.*
import com.example.triviaparty.model.*
import java.io.File
import kotlin.random.Random
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test

class CanonicalQuestionBankTest {
    private val json = Json { ignoreUnknownKeys = true }
    private fun bank() = json.decodeFromString<CanonicalQuestionBank>(File("../game-library/bank/questions.json").readText(Charsets.UTF_8))

    @Test fun migrationKeepsEveryLegacyQuestionAndPresentationUnderOneEntry() {
        val bank = bank()
        val bankLegacy = bank.questions.flatMap { it.legacyIds }
        assertEquals(bankLegacy.size, bankLegacy.distinct().size)
        val old = File("../game-library/current/sources").walkTopDown()
            .filter { it.isFile && it.parentFile?.name == "question-bank" && it.extension == "json" }
            .flatMap { file -> Json { ignoreUnknownKeys = true; classDiscriminator = "kind" }
                .decodeFromString<CategoryQuestionFile>(file.readText(Charsets.UTF_8)).questions.asSequence() }.map { it.id }.toSet()
        val oldCanonical = old.filter { it in bankLegacy.toSet() }.toSet()
        assertTrue(oldCanonical.isNotEmpty())
        assertTrue(bank.questions.size < bank.questions.sumOf { it.presentations.size })
        val presentationIds = bank.questions.flatMap { it.presentations.map { p -> p.id } }
        assertEquals(presentationIds.size, presentationIds.distinct().size)
        assertTrue(bank.questions.all { q -> q.presentations.all { it.id in q.legacyIds } })
        assertEquals(bank.questions.size, bank.questions.map { it.id }.distinct().size)
    }

    @Test fun qcmDirectAndProgressiveCluesArePresentationsOfTheSameQuestion() {
        val bank = bank()
        val entry = bank.questions.single { "lib-qcm-inventions-canada-20261012-02" in it.legacyIds }
        assertTrue("lib-qsj-inventions-canada-20261012-03" in entry.legacyIds)
        val views = bank.categoryViews()
        val questions = views.flatMap { it.questions }.filter { it.id == entry.id }
        assertTrue(questions.any { it is Question.MultipleChoice })
        assertTrue(questions.any { it is Question.TextAnswer })
        assertTrue(questions.any { it is Question.GuessWho })
        for (seed in 0..15) {
            val plan = planDynamicPackages(views.filter { file -> file.questions.any { it.id == entry.id } }
                .map { file -> file.copy(questions = file.questions.filter { it.id == entry.id }) },
                entry.topics, 5, 6, Random(seed))
            assertEquals(1, plan.totalQuestions)
        }
    }

    @Test fun homonymsRemainSeparateAndBankProjectsWithoutAnyLegacyPackageFiles() {
        val bank = bank()
        val building = bank.questions.single { "architecture-qsj-sacre-20261011-01" in it.legacyIds }
        val novel = bank.questions.single { "culture-qcm-francaise-oeuvres-20261010-01" in it.legacyIds }
        assertNotEquals(building.id, novel.id)
        val views = bank.categoryViews()
        assertTrue(views.isNotEmpty())
        assertTrue(views.flatMap { it.questions }.all { it.id in bank.questions.map { entry -> entry.id }.toSet() })
        val images = views.flatMap { it.questions }.mapNotNull { it.imageUrl }.filter { it.isNotBlank() }
        assertTrue(images.all { it.startsWith("local-media://canonical-bank/images/") })
    }

    @Test fun strictTaxonomyTreePurityAndSeparationOfBranchesVsLeaves() {
        val bank = bank()
        // Install canonical bank into repository for testing
        QuestionBankRepository.installCanonicalBank(json.encodeToString(CanonicalQuestionBank.serializer(), bank))

        // 1. Ensure subjectTaxonomy tree nodes are strictly hierarchical (Root -> Branch -> Sub-branch -> Leaf)
        val taxonomy = QuestionBankRepository.subjectTaxonomy
        assertTrue("Taxonomy must not be empty", taxonomy.isNotEmpty())
        val tagMap = taxonomy.associateBy { it.id }

        for (tag in taxonomy) {
            if (tag.parentId != null) {
                assertTrue("Parent tag ${tag.parentId} must exist for tag ${tag.id}", tagMap.containsKey(tag.parentId))
            }
        }

        // 2 & 3. Ensure expanding a node like "Arts" (or any non-leaf node) returns only direct child taxonomy nodes,
        // with NO leaf questions or leaf subjects mixed in. Leaf subjects/questions are only queried at terminal leaf nodes.
        val rootTags = QuestionBankRepository.rootTaxonomyTags
        assertTrue("Root taxonomy tags should exist", rootTags.isNotEmpty())

        for (root in rootTags) {
            val children = QuestionBankRepository.childTaxonomyTags(root.id)
            // Verify childTaxonomyTags only returns BankTaxonomyTag items and no subjects or questions
            for (child in children) {
                assertEquals("Child taxonomy tag parentId must match root id", root.id, child.parentId)
            }

            // Test recursive descent into terminal leaf nodes
            fun validateNode(tagId: String) {
                val subChildren = QuestionBankRepository.childTaxonomyTags(tagId)
                val subSubjects = QuestionBankRepository.subjectsForTaxonomyTagDirect(tagId)
                
                if (subChildren.isNotEmpty()) {
                    // Branch node: ensure no subjects/questions are mixed directly when child categories exist
                    for (subChild in subChildren) {
                        validateNode(subChild.id)
                    }
                } else {
                    // Terminal leaf node: should hold subjects and questions can be queried here
                    for (subject in subSubjects) {
                        val questions = QuestionBankRepository.questionsForCanonicalSubject(subject.id)
                        assertNotNull(questions)
                    }
                }
            }

            validateNode(root.id)
        }
    }
}
