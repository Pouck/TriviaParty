// Local audition server: exposes only the sampler and its ten original sounds.
const fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const root=path.resolve(__dirname,'../app/src/main/assets/tv');
const server=http.createServer((req,res)=>{
 const pathname=new URL(req.url,'http://localhost').pathname;
 if(pathname==='/' || pathname==='/tv/buzzer-sampler') {res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(root,'buzzer-sampler.html')));return;}
 const match=pathname.match(/^\/tv\/sounds\/(buzzer-(0[1-9]|10)\.wav)$/);
 if(match){res.setHeader('Content-Type','audio/wav');res.end(fs.readFileSync(path.join(root,'sounds',match[1])));return;}
 res.writeHead(404);res.end('Not found');
});
server.listen(18082,'127.0.0.1',()=>console.log('Buzzer sampler: http://127.0.0.1:18082/'));
