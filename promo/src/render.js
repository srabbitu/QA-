const { chromium } = require('playwright');const fs=require('fs');
const [a,b,step,out]=[+(process.argv[2]||0),+(process.argv[3]||1770),+(process.argv[4]||1),process.argv[5]||'frames'];
(async()=>{const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
 p.setDefaultTimeout(0); p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+__dirname+'/comp.html');await p.evaluate(()=>window.ready);await p.waitForTimeout(500);
 fs.mkdirSync(__dirname+'/'+out,{recursive:true});
 for(let f=a;f<b;f+=step){await p.evaluate(f=>window.render(f),f);await p.screenshot({path:`${__dirname}/${out}/${String(f).padStart(4,'0')}.jpg`,quality:92});}
 await br.close();})();
