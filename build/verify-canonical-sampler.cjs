const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const root = path.resolve('build/question-review-sampler');
const server = http.createServer((req,res) => {
    const file = path.join(root, decodeURIComponent(req.url.split('?')[0] === '/' ? '/sampler.html' : req.url.split('?')[0]));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) { res.writeHead(404).end(); return; }
    if (file.endsWith('.html')) res.setHeader('Content-Type','text/html; charset=utf-8');
    res.end(fs.readFileSync(file));
});
server.listen(0,'127.0.0.1', async () => {
    let chrome, ws;
    try {
        chrome = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless','--disable-gpu','--no-first-run',
            '--remote-debugging-port=0','--user-data-dir='+path.join(root,'verification-profile-'+Date.now()),'about:blank'],
            {windowsHide:true,stdio:['ignore','ignore','pipe']});
        const endpoint = await new Promise((resolve,reject) => {
            const timeout=setTimeout(() => reject(new Error('Chrome did not expose its test endpoint within 30 seconds')),30000);
            let log=''; chrome.stderr.on('data', data => { log+=data; const match=log.match(/DevTools listening on (ws:\/\/\S+)/); if(match) { clearTimeout(timeout); resolve(match[1]); } });
            chrome.once('error',reject); chrome.once('exit',code => reject(new Error('Chrome exited '+code)));
        });
        ws = new WebSocket(endpoint); await new Promise((resolve,reject) => { ws.onopen=resolve; ws.onerror=reject; });
        let sequence=0; const requests=new Map();
        ws.onmessage = message => { const result=JSON.parse(message.data); if(result.id) { const pending=requests.get(result.id); requests.delete(result.id); result.error ? pending.reject(new Error(JSON.stringify(result.error))) : pending.resolve(result.result); } };
        const send=(method,params={},sessionId) => new Promise((resolve,reject) => { const id=++sequence; requests.set(id,{resolve,reject}); ws.send(JSON.stringify({id,method,params,sessionId})); });
        const {targetId}=await send('Target.createTarget',{url:'about:blank'});
        const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
        await send('Page.enable',{},sessionId);
        const evaluate=async expression => {
            const response=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);
            if(response.exceptionDetails) throw new Error(JSON.stringify(response.exceptionDetails));
            return response.result.value;
        };
        const navigate=async () => {
            await send('Page.navigate',{url:'http://127.0.0.1:'+server.address().port+'/'},sessionId);
            for(let i=0;i<40;i++) { await new Promise(resolve=>setTimeout(resolve,100)); if(await evaluate('!!document.querySelector("#presentation")')) return; }
            throw new Error('Sampler did not render');
        };
        await navigate();
        await evaluate('localStorage.removeItem(key)'); await navigate();
        await evaluate(`reviews['lib-qsj-marvel-20261012-05']={...initial.consumed['lib-qsj-marvel-20261012-05'][0]};persist()`);
        await navigate();
        assert.equal(await evaluate("reviews['lib-qsj-marvel-20261012-05'].modification"),'');
        await evaluate(`reviews['lib-qsj-marvel-20261012-05']={rating:'3',modification:'New note after export'};persist()`);
        await navigate();
        assert.equal(await evaluate("reviews['lib-qsj-marvel-20261012-05'].modification"),'New note after export');
        await evaluate('localStorage.removeItem(key)');await navigate();
        const counts=await evaluate('({unique:questions.length, aliases:questions.flatMap(q=>q.legacyIds).length, cards:document.querySelectorAll("article.card").length})');
        assert.ok(counts.unique < counts.aliases); assert.equal(counts.cards,1);
        assert.equal(await evaluate('questions.filter(q=>new Set(q.presentations.map(p=>p.kind+"|"+p.answerMode)).size!==q.presentations.length).length'),0);
        const fifteenth=await evaluate('questions[14].presentations.map(p=>p.label)');
        assert.equal(fifteenth.filter(label=>label==='Réponses écrites').length,1);
        await evaluate(`document.querySelector('#search').value='lib-qcm-inventions-canada-20261012-02'; document.querySelector('#search').dispatchEvent(new Event('input'))`);
        assert.equal(await evaluate('visible.length'),1);
        const entry=await evaluate('({id:visible[index].id, formats:visible[index].presentations.map(p=>p.kind)})');
        assert.ok(entry.formats.includes('multipleChoice')); assert.ok(entry.formats.includes('guessWho')); assert.ok(entry.formats.includes('textAnswer'));
        await evaluate(`document.querySelector('#modification').value='Sampler integration test'; document.querySelector('#modification').dispatchEvent(new Event('input')); document.querySelector('input[name="rating"][value="4"]').checked=true; document.querySelector('input[name="rating"][value="4"]').dispatchEvent(new Event('change'))`);
        await evaluate(`document.querySelector('#presentation').value=String(visible[index].presentations.findIndex(p=>p.kind==='guessWho')); document.querySelector('#presentation').dispatchEvent(new Event('change'))`);
        assert.equal(await evaluate('document.querySelector("#modification").value'),'Sampler integration test');
        assert.equal(await evaluate('visible[index].id'),entry.id);
        assert.equal(await evaluate('document.querySelector("input[name=rating]:checked").value'),'4');
        assert.ok(await evaluate('document.querySelector("#main").textContent.includes("Progressive clues")'));
        await navigate();
        assert.equal(await evaluate(`reviews[${JSON.stringify(entry.id)}].modification`),'Sampler integration test');
        await evaluate(`document.querySelector('#search').value=''; index=questions.findIndex(q=>q.id===${JSON.stringify(entry.id)}); render()`);
        await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true},sessionId);
        assert.deepEqual(await evaluate('({width:innerWidth,overflow:document.documentElement.scrollWidth>390})'),{width:390,overflow:false});
        await evaluate('document.querySelector("article.card").scrollIntoView()');
        const screenshot=await send('Page.captureScreenshot',{format:'png'},sessionId);
        fs.writeFileSync(path.join(root,'canonical-sampler-mobile.png'),Buffer.from(screenshot.data,'base64'));
        const imported = {sampler:'question-review-sampler-v1',generalComments:['Keep this pending'],reviews:[
            {questionId:'lib-qcm-inventions-canada-20261012-02',rating:2,modification:'choice note'},
            {questionId:'lib-qsj-inventions-canada-20261012-03',rating:4,modification:'clue note'}]};
        await evaluate(`document.querySelector('#file').onchange({target:{files:[{text:async()=>${JSON.stringify(JSON.stringify(imported))}}]}})`);
        assert.deepEqual(await evaluate(`({rating:reviews[${JSON.stringify(entry.id)}].rating, comments:reviews[${JSON.stringify(entry.id)}].modification})`),
            {rating:'',comments:'choice note\nclue note'});
        assert.equal(await evaluate(`history[${JSON.stringify(entry.id)}]['lib-qcm-inventions-canada-20261012-02'].rating`),2);
        assert.equal(await evaluate(`history[${JSON.stringify(entry.id)}]['lib-qsj-inventions-canada-20261012-03'].rating`),4);
        await evaluate(`window.reviewBlob=null; URL.createObjectURL=blob=>{window.reviewBlob=blob;return 'blob:test'}; HTMLAnchorElement.prototype.click=function(){}; document.querySelector('#export').click()`);
        const exported=await evaluate('reviewBlob.text().then(JSON.parse)');
        const row=exported.reviews.find(r=>r.questionId===entry.id);
        assert.ok(row.presentationReviews.some(r=>r.questionId==='lib-qcm-inventions-canada-20261012-02'&&r.rating===2));
        assert.ok(row.presentationReviews.some(r=>r.questionId==='lib-qsj-inventions-canada-20261012-03'&&r.rating===4));
        assert.deepEqual(exported.generalComments,['Keep this pending']);
        await evaluate(`document.querySelector('#search').value='test-06-map-choice-q1'; document.querySelector('#search').dispatchEvent(new Event('input'))`);
        assert.equal(await evaluate('document.querySelectorAll(".review-map .map-marker").length'),4);
        assert.equal(await evaluate('document.querySelector(".review-map .map-marker.correct").textContent'),'B');
        assert.ok(await evaluate('!!document.querySelector(".review-map svg")'));
        await evaluate('document.querySelector(".review-map").scrollIntoView({block:"center"})');
        const mapScreenshot=await send('Page.captureScreenshot',{format:'png'},sessionId);
        fs.writeFileSync(path.join(root,'canonical-sampler-map.png'),Buffer.from(mapScreenshot.data,'base64'));
        // Leave a clean verification profile; this is separate from the user's browser.
        await evaluate('localStorage.removeItem(key)');
        console.log(`PASS: ${counts.unique} unique cards / ${counts.aliases} preserved IDs; QCM/direct/clue switching, shared review, persistence and mobile layout.`);
        await send('Browser.close');
    } catch(error) { console.error(error); process.exitCode=1; }
    finally { ws?.close(); chrome?.kill(); server.close(); }
});
