package com.example.triviaparty
import com.example.triviaparty.model.*
import com.example.triviaparty.cast.TvState
import com.example.triviaparty.network.*
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test
import java.net.ServerSocket
class WrittenAndReadyTest {
    @Suppress("UNCHECKED_CAST") private fun state(s:GameServer)=GameServer::class.java.getDeclaredField("_gameSession").apply {isAccessible=true}.get(s) as MutableStateFlow<GameSession>
    private fun call(s:GameServer,name:String,event:GameEvent)=GameServer::class.java.getDeclaredMethod(name,event.javaClass).apply {isAccessible=true}.invoke(s,event)
    private fun start(s:GameServer,q:Question)=GameServer::class.java.getDeclaredMethod("startQuestion",Question::class.java,String::class.java).apply {isAccessible=true}.invoke(s,q,q.category)
    private fun tick(s:GameServer)=GameServer::class.java.getDeclaredMethod("advanceQuestionTimer",HourglassConfig::class.java).apply {isAccessible=true}.invoke(s,s.gameSession.value.timingConfig)
    private fun begin(s:GameServer)=GameServer::class.java.getDeclaredMethod("handleHostStartQuestionTimer").apply {isAccessible=true}.invoke(s)
    private fun seed(s:GameServer,n:Int=2,mode:CategoryAnswerMode=CategoryAnswerMode.WRITTEN) {state(s).value=s.gameSession.value.copy(currentCategoryAnswerMode=mode,teams=(0 until n).map {Team(('a'+it).toString(),"Team $it",sessionToken="token$it")},timingConfig=HourglassConfig(secondsPerFlip=5,maxFlips=2,pointsDecayPerFlip=5))}
    private fun lock(s:GameServer,id:String,text:String)=call(s,"handleLockAnswer",GameEvent.LockAnswer(id,s.gameSession.value.currentQuestion!!.id,AnswerValue.TextSelection(text)))
    private fun judge(s:GameServer,id:String,correct:Boolean) {
        call(s,"handleWrittenJudgement",GameEvent.HostJudgeWrittenAnswer(id,s.gameSession.value.currentQuestion!!.id,correct))
        call(s,"handleContinueWrittenReview",GameEvent.HostContinueWrittenReview(s.gameSession.value.currentQuestion!!.id))
    }
    private suspend fun WebSocketSession.readState():JsonObject {while(true){val f=incoming.receive();if(f is Frame.Text){val d=Json.parseToJsonElement(f.readText()).jsonObject;d["session"]?.let {return it.jsonObject}}}}
    @Test fun writtenAnswersStayPrivateAndAreScoredOnce() {
        val s=GameServer();try {seed(s);val q=Question.TextAnswer("written","Test","Question",basePoints=15,acceptableAnswers=listOf("Expected"));start(s,q)
            lock(s,"a","Private A");lock(s,"b","Private B");assertEquals(GameState.ANSWER_REVIEW,s.gameSession.value.state)
            val tv=TvState.from(s.gameSession.value).encode();assertTrue(tv.contains("Private A"));assertFalse(tv.contains("Private B"));assertFalse(tv.contains("Expected"))
            assertEquals("Private A",TvState.from(s.gameSession.value).submittedAnswer);
            judge(s,"a",false);assertEquals("Private B",TvState.from(s.gameSession.value).submittedAnswer);assertEquals(1,s.gameSession.value.pendingWrittenAnswers().size);judge(s,"a",true);assertEquals(0,s.gameSession.value.teams[0].score)
            judge(s,"b",true);assertEquals(GameState.REVEAL_ANSWER,s.gameSession.value.state);assertNull(TvState.from(s.gameSession.value).submittedAnswer);assertEquals(15,s.gameSession.value.teams[1].score);judge(s,"b",true);assertEquals(15,s.gameSession.value.teams[1].score)
        }finally{s.stop()}
    }
    @Test fun cluesStartAutomaticallyAndWrongWrittenAnswerOpensNextTimedClue() {
        val s=GameServer();try {seed(s);val q=Question.GuessWho("clues","Test",basePoints=20,clues=listOf("One","Two","Three","Four"),acceptableAnswers=listOf("Expected"));start(s,q)
            for(id in listOf("a","b"))call(s,"handlePlayerReady",GameEvent.PlayerReady(id,q.id,0));assertFalse(s.gameSession.value.questionReading);assertFalse(TvState.from(s.gameSession.value).playersReadyReading)
            begin(s);lock(s,"a","Wrong");lock(s,"b","Also wrong");judge(s,"a",false);judge(s,"b",false)
            assertEquals(listOf(-5,-5),s.gameSession.value.teams.map {it.score});assertEquals(GameState.QUESTION_ACTIVE,s.gameSession.value.state);assertFalse(s.gameSession.value.questionReading);assertEquals(1,s.gameSession.value.currentFlipNumber)
            repeat(8){tick(s)};assertEquals(8,s.gameSession.value.elapsedSecondsInFlip)
        }finally{s.stop()}
    }
    @Test fun choicesLoseOnePointPerSecondAndHaveFeedbackWithoutAnswers() {
        val s=GameServer();try {seed(s,2,CategoryAnswerMode.SIMULTANEOUS);val q=Question.MultipleChoice("mc","Test","Question",basePoints=15,options=listOf("A","B"),correctOptionIndex=0);start(s,q);repeat(3){tick(s)}
            assertEquals(12,TvState.from(s.gameSession.value).points);assertEquals(0,s.gameSession.value.currentFlipNumber);assertTrue(TvState.from(s.gameSession.value).pointsCountdown)
            call(s,"handleLockAnswer",GameEvent.LockAnswer("a",q.id,AnswerValue.MultipleChoiceSelection(0)));repeat(12){tick(s)};assertEquals(12,s.gameSession.value.teams[0].score)
            start(s,q.copy(id="empty"));repeat(15){tick(s)};assertEquals(GameState.REVEAL_ANSWER,s.gameSession.value.state);assertEquals("bad",s.gameSession.value.answerSound);assertNotNull(s.gameSession.value.answerSoundClip)
        }finally{s.stop()}
    }
    @Test fun chronologyReadyIsPrivateAndStartsOnlyAfterEveryConnectedPlayer()=runBlocking {
        val s=GameServer(ServerSocket(0).use {it.localPort});val c=HttpClient(CIO){install(WebSockets)}
        try{s.start();withTimeout(10000){
            val a=c.webSocketSession(host="127.0.0.1",port=s.port,path="/play/ws");val b=c.webSocketSession(host="127.0.0.1",port=s.port,path="/play/ws");a.readState();b.readState()
            seed(s,2,CategoryAnswerMode.SIMULTANEOUS)
            // Associate browser sockets through the normal join protocol.
            suspend fun WebSocketSession.join(name:String,token:String):String {send(Frame.Text(Json.encodeToString<GameEvent>(GameEvent.JoinRoom(s.gameSession.value.roomId,name,token))));while(true){val f=incoming.receive();if(f is Frame.Text){val d=Json.parseToJsonElement(f.readText()).jsonObject;d["teamId"]?.let{return it.jsonPrimitive.content}}}}
            val aid=a.join("Team 0","token0");val bid=b.join("Team 1","token1")
            val q=Question.MultipleChoice("ready","Test","Order?",basePoints=15,options=listOf("One → Two → Three","Two → Three → One","Three → One → Two","Three → Two → One"),correctOptionIndex=0);start(s,q)
            a.send(Frame.Text(Json.encodeToString<GameEvent>(GameEvent.PlayerReady(aid,q.id,0))))
            while(a.readState()["readyTeamIds"]?.jsonArray?.size!=1) {}
            assertTrue(s.gameSession.value.questionReading);assertTrue(TvState.from(s.gameSession.value).playersReadyReading)
            b.send(Frame.Text(Json.encodeToString<GameEvent>(GameEvent.PlayerReady(aid,q.id,0))))
            b.send(Frame.Text(Json.encodeToString<GameEvent>(GameEvent.PlayerReady(bid,q.id,0))))
            while(true){val v=b.readState();if(v["readyTeamIds"]?.jsonArray?.size==2 && v["questionReading"]==JsonPrimitive(false))break}
            assertEquals(setOf(aid,bid),s.gameSession.value.readyTeamIds.toSet());a.close();b.close()
        }}finally{c.close();s.stop()}
    }
    @Test fun finalValidationSnapshotsNeverArriveAfterTheNextPhase()=runBlocking {
        val s=GameServer(ServerSocket(0).use {it.localPort});val c=HttpClient(CIO){install(WebSockets)}
        try{s.start();withTimeout(15000){val h=c.webSocketSession(host="127.0.0.1",port=s.port,path="/ws");h.readState();seed(s,1)
            repeat(20){n->val q=Question.TextAnswer("ordered-$n","Test","Question",basePoints=15,acceptableAnswers=listOf("Yes"));start(s,q);lock(s,"a","Yes");judge(s,"a",true)}
            val snapshots=mutableListOf<JsonObject>();while(true){val v=h.readState();snapshots.add(v);if((v["currentQuestion"] as? JsonObject)?.get("id")==JsonPrimitive("ordered-19") && v["state"]==JsonPrimitive("REVEAL_ANSWER"))break}
            val order=snapshots.mapNotNull {(it["currentQuestion"] as? JsonObject)?.get("id")?.jsonPrimitive?.content?.removePrefix("ordered-")?.toIntOrNull()};assertEquals(order.sorted(),order)
            for(n in 0..19){val phases=snapshots.filter {(it["currentQuestion"] as? JsonObject)?.get("id")==JsonPrimitive("ordered-$n")}.map {it["state"]!!.jsonPrimitive.content};assertEquals("REVEAL_ANSWER",phases.last());assertEquals(1,phases.count {it=="REVEAL_ANSWER"})}
            h.close()
        }}finally{c.close();s.stop()}
    }
    @Test fun validatedSubmissionStaysOnTvUntilHostContinuesAndCannotBeScoredTwice() {
        val s=GameServer();try {seed(s,1)
            val q=Question.TextAnswer("hold","Test","Question",basePoints=15,acceptableAnswers=listOf("Expected"));start(s,q);lock(s,"a","Player answer")
            call(s,"handleWrittenJudgement",GameEvent.HostJudgeWrittenAnswer("a",q.id,true))
            assertEquals(GameState.ANSWER_REVIEW,s.gameSession.value.state);assertTrue(s.gameSession.value.pendingWrittenAnswers().isEmpty())
            val tv=TvState.from(s.gameSession.value);assertEquals("Team 0",tv.answeringTeam);assertEquals("Player answer",tv.submittedAnswer);assertEquals(true,tv.submittedAnswerResult)
            assertNull(tv.question!!.answer);assertEquals(15,s.gameSession.value.teams[0].score)
            repeat(10){tick(s)};assertEquals("Player answer",TvState.from(s.gameSession.value).submittedAnswer)
            call(s,"handleWrittenJudgement",GameEvent.HostJudgeWrittenAnswer("a",q.id,true));assertEquals(15,s.gameSession.value.teams[0].score)
            call(s,"handleContinueWrittenReview",GameEvent.HostContinueWrittenReview("wrong-question"));assertEquals(GameState.ANSWER_REVIEW,s.gameSession.value.state)
            call(s,"handleContinueWrittenReview",GameEvent.HostContinueWrittenReview(q.id));assertEquals(GameState.REVEAL_ANSWER,s.gameSession.value.state);assertNull(TvState.from(s.gameSession.value).submittedAnswer)
        }finally{s.stop()}
    }

    @Test fun tvWebsocketReceivesCurrentPlayerSubmissionAndRetainsValidatedResult()=runBlocking {
        val s=GameServer(ServerSocket(0).use {it.localPort});val c=HttpClient(CIO){install(WebSockets)}
        try{s.start();withTimeout(10000){
            val tv=c.webSocketSession(host="127.0.0.1",port=s.port,path="/tv/ws")
            suspend fun snapshot(check:(JsonObject)->Boolean):JsonObject {while(true){val f=tv.incoming.receive();if(f is Frame.Text){val d=Json.parseToJsonElement(f.readText()).jsonObject;if(check(d))return d}}}
            snapshot {true};seed(s)
            val q=Question.TextAnswer("tv-review","Test","Question",basePoints=15,acceptableAnswers=listOf("Secret expected answer"));start(s,q);lock(s,"a","Answer One");lock(s,"b","Answer Two")
            val first=snapshot {it["phase"]==JsonPrimitive("ANSWER_REVIEW") && it["submittedAnswer"]==JsonPrimitive("Answer One")}
            assertEquals(JsonPrimitive("Team 0"),first["answeringTeam"]);assertFalse(first.toString().contains("Answer Two"));assertFalse(first.toString().contains("Secret expected answer"))
            call(s,"handleWrittenJudgement",GameEvent.HostJudgeWrittenAnswer("a",q.id,false))
            val result=snapshot {it["submittedAnswerResult"]==JsonPrimitive(false)}
            assertEquals(JsonPrimitive("Team 0"),result["answeringTeam"]);assertEquals(JsonPrimitive("Answer One"),result["submittedAnswer"])
            call(s,"handleContinueWrittenReview",GameEvent.HostContinueWrittenReview(q.id))
            val next=snapshot {it["submittedAnswer"]==JsonPrimitive("Answer Two")};assertEquals(JsonPrimitive("Team 1"),next["answeringTeam"])
            tv.close()
        }}finally{c.close();s.stop()}
    }

}
