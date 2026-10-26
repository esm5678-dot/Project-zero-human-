const { test, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const server = http.createServer(async (_req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(await fs.readFile(path.resolve(__dirname,'../prototype/demo.html')));});
const url = new Promise(resolve=>server.listen(0,'127.0.0.1',()=>resolve('http://127.0.0.1:'+server.address().port+'/')));
const browser = chromium.launch({headless:true,args:['--no-sandbox']});
after(async()=>{(await browser).close();server.close();});
test('guided demo completion and reset',async()=>{
 const ctx=await (await browser).newContext();try{
 const p=await ctx.newPage();await p.goto(await url);
 assert.equal(await p.locator('#progress').innerText(),'진행 0/3');
 assert.equal(await p.locator('#two').isDisabled(),true);
 await p.locator('#one').click();assert.equal(await p.locator('#progress').innerText(),'진행 1/3');
 await p.locator('#two').click();assert.equal(await p.locator('#progress').innerText(),'진행 2/3');
 await p.locator('#status').selectOption('완료');assert.equal(await p.locator('#progress').innerText(),'진행 3/3');
 await p.locator('#reset').click();assert.equal(await p.locator('#progress').innerText(),'진행 0/3');
 }finally{await ctx.close();}
});
test('no outbound network calls',async()=>{
 const ctx=await (await browser).newContext();try{
 const p=await ctx.newPage();const outgoing=[];p.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:'))outgoing.push(r.url());});
 await p.goto(await url);await p.locator('#one').click();await p.locator('#two').click();await p.locator('#status').selectOption('완료');assert.deepEqual(outgoing,[]);
 }finally{await ctx.close();}
});
