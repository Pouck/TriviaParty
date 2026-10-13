package com.example.triviaparty

import com.example.triviaparty.data.*
import org.junit.Assert.*
import org.junit.Test
import java.nio.file.Files
import kotlin.random.Random

class HostReviewTest {
    @Test fun zeroMeansNeedsRevisionAndSurvivesStatsReset() {
        val directory=Files.createTempDirectory("flagged-review").toFile()
        try {
            val file=java.io.File(directory,"review.json")
            val store=HostReviewStore(file)
            store.saveReview(QuestionReview("q0","Architecture","Qui suis-je ?","Indice trop explicite",0))
            store.resetUsage()
            assertEquals(0,HostReviewStore(file).read().reviews.getValue("q0").difficulty)
            store.saveReview(QuestionReview("q5","Architecture","Qui ?",difficulty=5))
            assertEquals(5,store.read().reviews.getValue("q5").difficulty)
        } finally { directory.deleteRecursively() }
    }
    @Test fun largeDrawComputesEachProfileOnlyOnce() {
        val ids=(0..249).map { "p$it" }
        val calls=mutableMapOf<String,Int>()
        val result=selectBalancedPackages(ids,250,emptyMap(),{ id ->
            calls[id]=(calls[id] ?: 0)+1
            val n=id.drop(1).toInt()
            CategoryProfile(CategoryFormat.entries[n%4],"subject${n%16}")
        },random=Random(42))
        assertEquals(250,result.distinct().size)
        assertEquals(250,calls.size)
        assertTrue(calls.values.all { it==1 })
    }
    @Test fun testAndDemoPackagesAreExcludedWithoutMatchingOrdinaryWords() {
        fun pack(id: String, name: String) = com.example.triviaparty.model.GamePackage(id,name,"",emptyList(),com.example.triviaparty.model.HourglassConfig())
        assertTrue(pack("test-01-qcm","Choix multiples").isTestPackage())
        assertTrue(pack("qui-suis-je-demo","Démo — Qui suis-je ?").isTestPackage())
        assertTrue(pack("custom","TEST Buzzer").isTestPackage())
        assertFalse(pack("lib-qcm-geographie","Géographie").isTestPackage())
        assertFalse(pack("contest","Démocratie et contestations").isTestPackage())
    }
    @Test fun reviewsSurvivePackageUseAndStatsReset() {
        val directory=Files.createTempDirectory("host-review").toFile()
        try {
            val file=java.io.File(directory,"review.json")
            val store=HostReviewStore(file)
            store.saveReview(QuestionReview("q1","BD","Cheval ?","Image à corriger",3))
            store.recordPackages(listOf("p1","p1")); store.recordPackages(listOf("p1","p2"))
            assertEquals(2,HostReviewStore(file).read().usage.getValue("p1").plays)
            store.resetUsage()
            assertTrue(store.read().usage.isEmpty())
            assertEquals(3,store.read().reviews.getValue("q1").difficulty)
            assertEquals("Image à corriger",store.read().reviews.getValue("q1").comment)
            store.recordPackages(listOf("p1"),"game1")
            HostReviewStore(file).recordPackages(listOf("p1"),"game1")
            assertEquals(1,store.read().usage.getValue("p1").plays)
            store.recordPackages(listOf("p1"),"game2")
            assertEquals(2,store.read().usage.getValue("p1").plays)
        } finally { directory.deleteRecursively() }
    }
    @Test fun randomSelectionBalancesAndAvoidsPlayedPackages() {
        val profiles=(0..15).associate { "p$it" to CategoryProfile(CategoryFormat.entries[it%4],"s${it/4}") }
        val selected=selectBalancedPackages(profiles.keys.toList(),4,emptyMap(),profiles::getValue,random=Random(42))
        assertEquals(4,selected.map { profiles.getValue(it).format }.distinct().size)
        assertEquals(4,selected.map { profiles.getValue(it).subject }.distinct().size)
        val usage=selected.associateWith { PackageUsage(1,100) }
        val next=selectBalancedPackages(profiles.keys.toList(),4,usage,profiles::getValue,random=Random(42))
        assertTrue(next.none { it in selected })
        val subjects=selectBalancedPackages(profiles.keys.toList(),16,emptyMap(),profiles::getValue,true,Random(7))
        assertEquals(4,subjects.size)
        assertEquals(4,subjects.map { profiles.getValue(it).subject }.distinct().size)
    }
}
