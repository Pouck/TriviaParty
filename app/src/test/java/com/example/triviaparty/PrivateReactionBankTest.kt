package com.example.triviaparty

import com.example.triviaparty.model.PrivateReactionBank
import com.example.triviaparty.network.GameServer
import java.io.File
import java.net.HttpURLConnection
import java.net.ServerSocket
import java.net.URL
import java.nio.file.Files
import org.junit.Assert.*
import org.junit.Test

class PrivateReactionBankTest {
    @Test fun reviewedBankSupportsHundredsOfClipsAndChangesItsCacheVersionWithTheManifest() {
        val dir=Files.createTempDirectory("reviewed-reactions").toFile()
        val bytes=File("src/main/assets/tv/sounds/good-01.wav").readBytes()
        try {
            val rows=(1..130).flatMap { n -> listOf("good","bad").map { outcome ->
                val file="$outcome-%03d.wav".format(n)
                File(dir,file).writeBytes(bytes)
                """{"file":"$file","outcome":"$outcome","voice":"user-$n","text":"Clip $n","audience":"all"}"""
            } }
            val manifest=File(dir,"reactions.json")
            manifest.writeText(rows.joinToString(",", "[", "]"))
            val bank=PrivateReactionBank.load(dir)!!
            assertEquals(260,bank.clips.size)
            assertArrayEquals(bytes,bank.audio("sounds/bad-130.wav"))
            assertNull(bank.audio("sounds/bad-999.wav"))
            manifest.writeText(manifest.readText().replace("\"audience\":\"all\"", "\"audience\":\"mature\""))
            assertNotEquals(bank.version,PrivateReactionBank.load(dir)!!.version)
        } finally {dir.deleteRecursively()}
    }
    private fun manifest(good: String="good-62.wav")="""[
      {"file":"$good","outcome":"good","voice":"Actor A","text":"Bravo"},
      {"file":"bad-65.wav","outcome":"bad","voice":"Actor B","text":"Non"}
    ]"""
    @Test fun privateClipsLoadAndAreServedWhileUnlistedFilesStayPrivate() {
        val dir=Files.createTempDirectory("reaction-preview").toFile()
        val bytes=File("src/main/assets/tv/sounds/good-01.wav").readBytes()
        val port=ServerSocket(0).use {it.localPort}
        try {
            File(dir,"good-62.wav").writeBytes(bytes);File(dir,"bad-65.wav").writeBytes(bytes)
            File(dir,"reactions.json").writeText(manifest())
            File(dir,"credits.html").writeText("Private audition")
            val bank=PrivateReactionBank.load(dir)!!
            assertEquals(2,bank.clips.size);assertTrue(bank.clips.all {it.audience=="unreviewed"});assertNull(bank.audio("sounds/../reactions.json"));assertNull(bank.audio("good-62.wav"))
            val server=GameServer(port,privateReactions=bank)
            try {
                server.start()
                assertEquals(bank.version,com.example.triviaparty.cast.TvState.from(server.gameSession.value).audioBankVersion)
                val response=URL("http://127.0.0.1:$port/tv/sounds/good-62.wav").openConnection() as HttpURLConnection
                try {assertEquals(200,response.responseCode);assertArrayEquals(bytes,response.inputStream.use {it.readBytes()})} finally {response.disconnect()}
                assertEquals("Private audition",URL("http://127.0.0.1:$port/tv/audio-credits").readText())
            } finally {server.stop()}
            File(dir,"good-62.wav").delete();assertNull(PrivateReactionBank.load(dir))
        } finally {dir.deleteRecursively()}
    }
    @Test fun invalidOrIncompletePrivateBankFallsBackWithoutLoadingPaths() {
        val dir=Files.createTempDirectory("bad-preview").toFile()
        try {
            assertNull(PrivateReactionBank.load(dir))
            File(dir,"reactions.json").writeText(manifest("../good-62.wav"));assertNull(PrivateReactionBank.load(dir))
            File(dir,"reactions.json").writeText("not json");assertNull(PrivateReactionBank.load(dir))
            File(dir,"reactions.json").writeText("[]");assertNull(PrivateReactionBank.load(dir))
        } finally {dir.deleteRecursively()}
    }
}
