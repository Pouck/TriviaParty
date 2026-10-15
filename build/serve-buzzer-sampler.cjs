// Local audition server: exposes only the sampler and its forty original sound candidates.
const fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const root=path.resolve(__dirname,'../app/src/main/assets/tv');
const server=http.createServer((req,res)=>{
 const pathname=new URL(req.url,'http://localhost').pathname;
 if(pathname==='/' || /^\/(tv\/)?buzzer-sampler(\.html)?$/.test(pathname)) {res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(root,'buzzer-sampler.html')));return;}
 if(/^\/(tv\/)?success-sampler(\.html)?$/.test(pathname)){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(root,'success-sampler.html')));return;}
 const match=pathname.match(/^\/tv\/sounds\/((buzzer|success)-(0[1-9]|1[0-9]|20)\.wav)$/);
 if(match){res.setHeader('Content-Type','audio/wav');res.end(fs.readFileSync(path.join(root,'sounds',match[1])));return;}
 res.writeHead(404);res.end('Not found');
});
server.listen(18082,'127.0.0.1',()=>console.log('Buzzer sampler: http://127.0.0.1:18082/'));
