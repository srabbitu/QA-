const { chromium } = require('playwright');
const fs=require('fs');
const HTML=fs.readFileSync(__dirname+'/site.html','utf8').replace('(function(){\nvar SRC_REG','(function(){\nwindow.__T=function(s){return eval(s)};\nvar SRC_REG');
if(!HTML.includes('window.__T'))throw new Error('inject failed');
async function open({state,hour=10,min=30,w=432,h=768,dsf=2.5}={}){
  const b = await chromium.launch({args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required']});
  const ctx = await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:dsf,timezoneId:'Asia/Taipei',locale:'zh-TW'});
  const p = await ctx.newPage(); p.setDefaultTimeout(0);
  p.on('pageerror',e=>console.log('PAGEERR',String(e).slice(0,200)));
  await p.route('https://terry-island.pages.dev/',r=>r.fulfill({body:HTML,contentType:'text/html; charset=utf-8'}));
  await p.route(/script\.google\.com|open-meteo/,r=>r.abort());
  if(state) await p.addInitScript(s=>{for(const k in s)localStorage.setItem(k,s[k])},state);
  await p.clock.install({time:new Date(`2026-11-09T${String(hour).padStart(2,'0')}:${String(min).padStart(2,'0')}:00+08:00`)});
  await p.goto('https://terry-island.pages.dev/',{waitUntil:'load',timeout:90000});
  await p.evaluate(()=>{window.__rafs=[];window.requestAnimationFrame=cb=>{window.__rafs.push(cb);return window.__rafs.length}});
  const T=(s)=>p.evaluate(s=>window.__T(s),s);
  const step=async(ms=66)=>{await p.clock.runFor(ms);await p.evaluate(()=>{const l=window.__rafs;window.__rafs=[];const t=performance.now();l.forEach(cb=>{try{cb(t)}catch(e){}})})};
  const settle=async(n=2)=>{await T('tgt.copy(dt);rad=drad;if(thT!=null){th=thT;thT=null}if(phT!=null){ph=phT;phT=null}offC=null;0');for(let i=0;i<n;i++)await step(16)};
  return {b,p,T,step,settle};
}
async function rec(p,dir,n,start=0,{fps=30,clip}={}){
  fs.mkdirSync(dir,{recursive:true});
  for(let i=0;i<n;i++){await p.clock.runFor(Math.round(1000/fps)); await p.screenshot({path:`${dir}/${String(start+i).padStart(4,'0')}.jpg`,quality:92,clip});}
  return start+n;
}
module.exports={open,rec};
// camera: set current+target directly
module.exports.cam=(T,{x=0,y=0,z=2.5,r=60,th=0,ph=.95})=>T(`dt.set(${x},${y},${z});tgt.set(${x},${y},${z});drad=rad=${r};th=${th};ph=${ph};thT=null;phT=null;0`);
module.exports.clean=(p,on=true)=>p.evaluate(on=>{let s=document.getElementById('__cl');if(!s){s=document.createElement('style');s.id='__cl';document.head.appendChild(s)}s.textContent=on?'#top,#p,#dlg,#tk,#toast,#hint,#onl,#fdbar,#arr,#bub{visibility:hidden!important}':''},on);
