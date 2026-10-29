package com.example.triviaparty

import com.example.triviaparty.model.*
import com.example.triviaparty.data.*
import com.example.triviaparty.network.*
import com.example.triviaparty.cast.TvState
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.net.ServerSocket
import java.nio.file.Files

class SubjectVotingTest {
    @Test fun cutoffTieRetainsWinnersAndOnlyRevotesTiedSubjects() {
        val vote=SubjectVoting(VoteSettings(2,1),listOf("A","B","C","D"),ballots=mapOf("1" to listOf("A","B"),"2" to listOf("A","C")))
        val second=vote.closeRound()
        assertEquals(listOf("A"),second.selected)
        assertEquals(setOf("B","C"),second.candidates.toSet())
        assertEquals(1,second.remainingSlots); assertEquals(2,second.round); assertFalse(second.hostTieBreak)
        val final=second.copy(ballots=mapOf("1" to listOf("B"),"2" to listOf("C"))).closeRound()
        assertTrue(final.hostTieBreak); assertFalse(final.completed)
        val resolved=second.copy(ballots=mapOf("1" to listOf("B"),"2" to listOf("B"))).closeRound()
        assertTrue(resolved.completed); assertEquals(listOf("A","B"),resolved.selected)
    }
    @Test fun noCutoffTieNeedsNoRevoteAndAbstentionsRemainTies() {
        assertTrue(SubjectVoting(VoteSettings(2),listOf("A","B"),ballots=emptyMap()).closeRound().completed)
        val empty=SubjectVoting(VoteSettings(1),listOf("A","B")).closeRound()
        assertEquals(2,empty.round)
        assertTrue(empty.closeRound().hostTieBreak)
        val ids=listOf("a1","a2","b1","b2","c1")
        val result=selectBalancedPackages(ids,4,emptyMap(),{ CategoryProfile(CategoryFormat.QCM,it.take(1)) },subjectLimit=2)
        assertTrue(result.groupingBy { it.take(1) }.eachCount().values.all { it<=2 })
    }
    @Test fun browserVotingPreservesJoinedPlayersAndSelectsRequestedSetsAfterHostTieBreak()=runBlocking {
        val directory=Files.createTempDirectory("vote-packages").toFile()
        val snapshots=listOf(QuestionBankRepository to listOf("fileQuestions","categoryMetadata","generatedMetadata","generatedQuestions"),GamePackageRepository to listOf("loadedPackages","categoryNames"))
            .flatMap { (repo,names) -> names.map { name -> val field=repo.javaClass.getDeclaredField(name).apply { isAccessible=true }; Triple(repo,field,field.get(repo)) } }
        val port=ServerSocket(0).use { it.localPort }
        val server=GameServer(port,importedPackagesDirectory=directory)
        val client=HttpClient(CIO) { install(WebSockets) }
        try {
            val imported=listOf("qcm","buzzer").flatMap { mode -> listOf("oiseaux","instruments","bd-franco-belge").map { topic ->
                val file=File("../package-examples/library-2026-10-12/lib-$mode-$topic-20261012.zip")
                GamePackageImportRepository.importArchive(file.inputStream(),directory).directory
            } }
            QuestionBankRepository.reloadImportedPackages(imported); GamePackageRepository.reloadImportedPackages(imported)
            server.start()
            withTimeout(20000) {
                val host=client.webSocketSession(host="127.0.0.1",port=port,path="/ws")
                host.eventOf("RoomStateBroadcast")
                host.sendEvent(GameEvent.HostStartGame(QuestionBankRepository.sampleCategories,voteSettings=VoteSettings(2,2)))
                val room=host.stateWhere { it["subjectVoting"] is JsonObject }["roomId"]!!.jsonPrimitive.content
                val a=client.webSocketSession(host="127.0.0.1",port=port,path="/play/ws")
                val b=client.webSocketSession(host="127.0.0.1",port=port,path="/play/ws")
                a.eventOf("RoomStateBroadcast"); b.eventOf("RoomStateBroadcast")
                coroutineScope { awaitAll(async { a.sendEvent(GameEvent.JoinRoom(room,"A","token-a")) },async { b.sendEvent(GameEvent.JoinRoom(room,"B","token-b")) }) }
                val aId=a.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                val bId=b.eventOf("JoinResponse")["teamId"]!!.jsonPrimitive.content
                host.stateWhere { it["teams"]!!.jsonArray.size==2 }
                host.sendEvent(GameEvent.HostOpenSubjectVote)
                a.stateWhere { it["state"]!!.jsonPrimitive.content=="SUBJECT_VOTING" }
                a.sendEvent(GameEvent.HostCloseSubjectVote) // Browser cannot control the vote.
                a.sendEvent(GameEvent.SubmitSubjectVote(bId,1,listOf("Musique"))) // Cannot impersonate another team.
                a.sendEvent(GameEvent.SubmitSubjectVote(aId,1,listOf("Musique","Nature")))
                b.sendEvent(GameEvent.SubmitSubjectVote(bId,1,listOf("Musique","BD et manga")))
                host.stateWhere { (it["subjectVoting"] as? JsonObject)?.get("ballots")?.jsonObject?.size==2 }
                val private=a.stateWhere { (it["subjectVoting"] as? JsonObject)?.get("ballots")?.jsonObject?.containsKey(aId)==true }
                assertEquals(setOf(aId),private["subjectVoting"]!!.jsonObject["ballots"]!!.jsonObject.keys)
                assertEquals(1,server.gameSession.value.subjectVoting!!.round)
                val tv=TvState.from(server.gameSession.value).encode()
                assertFalse(tv.contains("token-a")); assertFalse(tv.contains(aId)); assertFalse(tv.contains("correctOptionIndex"))
                host.sendEvent(GameEvent.HostCloseSubjectVote)
                a.stateWhere { it["subjectVoting"]!!.jsonObject["round"]!!.jsonPrimitive.int==2 }
                a.sendEvent(GameEvent.SubmitSubjectVote(aId,1,listOf("Nature"))) // stale round ignored
                a.sendEvent(GameEvent.SubmitSubjectVote(aId,2,listOf("Nature")))
                b.sendEvent(GameEvent.SubmitSubjectVote(bId,2,listOf("BD et manga")))
                host.stateWhere { it["subjectVoting"]!!.jsonObject["round"]!!.jsonPrimitive.int==2 && it["subjectVoting"]!!.jsonObject["ballots"]!!.jsonObject.size==2 }
                host.sendEvent(GameEvent.HostCloseSubjectVote)
                host.stateWhere { it["subjectVoting"]!!.jsonObject["hostTieBreak"]!!.jsonPrimitive.boolean }
                host.sendEvent(GameEvent.HostBreakSubjectTie(listOf("Nature")))
                val complete=host.stateWhere { it["subjectVoting"]!!.jsonObject["completed"]!!.jsonPrimitive.boolean }
                assertEquals(room,complete["roomId"]!!.jsonPrimitive.content)
                assertEquals(2,complete["teams"]!!.jsonArray.size)
                assertEquals(4,server.gameSession.value.masterCategories.size)
                assertEquals(20,server.gameSession.value.totalRounds)
                assertEquals(setOf("Musique","Nature"),server.gameSession.value.masterCategories.map { categoryProfileFor(it).subject }.toSet())
                host.sendEvent(GameEvent.HostBeginCategorySelect)
                host.stateWhere { it["state"]!!.jsonPrimitive.content=="CATEGORY_INTRO" }
                a.close(); b.close(); host.close()
            }
        } finally {
            client.close(); server.stop()
            snapshots.forEach { (repo,field,value) -> field.set(repo,value) }
            directory.deleteRecursively()
        }
    }
    private val json=Json { encodeDefaults=true }
    private suspend fun WebSocketSession.sendEvent(event: GameEvent)=send(Frame.Text(json.encodeToString(event)))
    private suspend fun WebSocketSession.eventOf(name: String): JsonObject {
        while(true) { val frame=incoming.receive(); if(frame is Frame.Text) { val event=Json.parseToJsonElement(frame.readText()).jsonObject; if(event["type"]!!.jsonPrimitive.content.endsWith(".$name")) return event } }
    }
    private suspend fun WebSocketSession.stateWhere(predicate: (JsonObject)->Boolean): JsonObject {
        while(true) { val state=eventOf("RoomStateBroadcast")["session"]!!.jsonObject; if(predicate(state)) return state }
    }
}
