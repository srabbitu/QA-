const { chromium } = require('playwright');const fs=require('fs');
const [a,b,step,out]=[+(process.argv[2]||0),+(process.argv[3]||99999),+(process.argv[4]||1),process.argv[5]||'frames'];
(async()=>{const br=await chromium.launch({args:['--allow-file-access-from-files']});const p=await br.newPage({viewport:{width:1080,height:1920}});
 p.setDefaultTimeout(0);p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CERR',m.text())});
 await p.addInitScript(t=>{window.TLDATA=t},JSON.parse(fs.readFileSync(__dirname+'/timeline.json','utf8')));await p.goto('file://'+__dirname+'/px.html');const total=await p.evaluate(()=>window.ready);console.log('total',total);
 fs.mkdirSync(__dirname+'/'+out,{recursive:true});
 for(let f=a;f<Math.min(b,total);f+=step){await p.evaluate(f=>window.render(f),f);await p.screenshot({path:`${__dirname}/${out}/${String(f).padStart(4,'0')}.png`});}
 await br.close();})();
