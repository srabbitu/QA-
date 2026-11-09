const {open,rec,cam,clean}=require('./lib');const fs=require('fs');
const STATE={'terryIsland.v1':fs.readFileSync(__dirname+'/state.json','utf8')};
const shot=process.argv[2], DSF=+(process.argv[3]||2.5), OUT=__dirname+'/cap/'+shot;
fs.rmSync(OUT,{recursive:true,force:true});fs.mkdirSync(OUT,{recursive:true});
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2, L=(a,b,t)=>a+(b-a)*t;
(async()=>{
 const fresh=['open','welcome'].includes(shot);
 const {b,p,T,step,settle}=await open({dsf:DSF,state:fresh?null:STATE});
 const still=async(n,ms=200)=>{await step(ms);await step(16);await p.screenshot({timeout:0,path:`${OUT}/${n}.jpg`,quality:93})};
 const quiet=async()=>{await T('try{sndSet(false)}catch(e){};try{dlgEnd()}catch(e){};0');await p.evaluate(()=>{const t=document.getElementById('toast');if(t)t.style.display='none'})};
 const camPath=async(n,f)=>{for(let i=0;i<n;i++){await cam(T,f(i/(n-1)));await step(33);await p.screenshot({timeout:0,path:`${OUT}/${String(i).padStart(4,'0')}.jpg`,quality:93})}};
 await p.clock.runFor(1200); await step(16);
 if(shot==='open'){ // crane down from sky onto island, no UI
   await T('dlgEnd()'); await T('close()'); await clean(p); await p.addStyleTag({content:'.lab{opacity:0!important}'});
   await camPath(120,t=>{const e=ease(t);return {x:0,y:0,z:L(4,2,e),r:L(120,48,e),th:L(1.2,0.25,e),ph:L(.32,.98,e)}});
 }
 if(shot==='welcome'){ // dialogue typing at chief; hide top HUD only
   await p.addStyleTag({content:'#top,#toast,#tk,#p{visibility:hidden!important}'});
   await T('dlgEnd()'); await p.clock.runFor(200);
   const c=JSON.parse(await T('(function(){var w=new THREE.Vector3();chief.getWorldPosition(w);return JSON.stringify([w.x,w.y,w.z,chief.rotation?0:0])})()'));
   await T(`dlgShow("島主泰瑞",[{t:"嗨！歡迎來到泰瑞島 🏝️"}],null)`);
   await T('(function(){var v=villagers.find(function(v){return v.g===chief||v.hd&&chief.parent===v.g});if(v)v.talk=performance.now()+1e9;return 0})()');
   for(let i=0;i<120;i++){const t=i/119;if(i>0)await T('chief.position.copy(__cp);chief.rotation.copy(__cr);0');const q=JSON.parse(await T('(function(){var w=new THREE.Vector3(),d=new THREE.Vector3();chief.getWorldPosition(w);chief.getWorldDirection(d);return JSON.stringify([w.x,w.z,Math.atan2(d.x,d.z)])})()'));
     if(i==0){globalThis.TH0=q[2];await T('window.__cp=chief.position.clone();window.__cr=chief.rotation.clone();0')}else await T('chief.position.copy(__cp);chief.rotation.copy(__cr);0');await cam(T,{x:q[0],y:.9,z:q[1],r:L(7.5,5.6,ease(t)),th:(i?globalThis.TH0:q[2])+.35-.15*t,ph:1.15});await step(33);await p.screenshot({timeout:0,path:`${OUT}/${String(i).padStart(4,'0')}.jpg`,quality:93});}
 }
 if(shot==='isles'){ await quiet(); await T('close()'); await clean(p);
   const D=JSON.parse(await T('JSON.stringify(D.map(d=>[d.id,d.x,d.z,d.ang||0]))'));
   for(const [id,x,z,a] of D){ await cam(T,{x,y:0,z,r:id=='t'?24:19,th:-a+0.35,ph:.9}); await still('isle_'+id,150);} 
   await cam(T,{x:0,y:0,z:2,r:62,th:.25,ph:.9}); await still('wide',150);
 }
 if(shot==='pets'){ await quiet(); await T('close()'); await clean(p);
   const home=JSON.parse(await T('JSON.stringify(pets.map(v=>[v.g.position.x,v.g.position.y,v.g.position.z]))'));
   for(let i=0;i<4;i++){
     const q=JSON.parse(await T(`(function(){var A=by.a,c=new THREE.Vector3(),w=new THREE.Vector3();A.g.getWorldPosition(c);pets.forEach(function(v,j){v.g.visible=(j==${i});v.fixed=1});var v=pets[${i}],h=${JSON.stringify(home)}[${i}];v.g.position.set(h[0],h[1],h[2]);v.g.getWorldPosition(w);var th=Math.atan2(w.x-c.x,w.z-c.z);v.talk=performance.now()+1e9;return JSON.stringify([w.x,w.y,w.z,th])})()`));
     {for(const o of [-1.1,-0.5,0.6,1.3]){await cam(T,{x:q[0],y:q[1]+.55,z:q[2],r:3.4,th:q[3]+o,ph:1.18}); await still('v'+i+'_'+o,60);}} await cam(T,{x:q[0],y:q[1]+.55,z:q[2],r:3.4,th:q[3]+[.6,0,0,0][i],ph:1.18}); await still('pet'+i,60);}
   await T('pets.forEach(function(v){v.g.visible=true});0');
   await cam(T,{x:0,y:.5,z:-13.5,r:12,th:.2,ph:1.0}); await still('disc_isle',150);
 }
 if(shot==='seasons'){ await quiet(); await T('close()'); await clean(p);
   const v={x:0,y:0,z:1,r:34,th:.5,ph:.88};
   for(const s of ['spring','summer','autumn','winter']){await T(`seaSet("${s}")`);await cam(T,v);await still('sea_'+s,200)}
   await T('seaSet("winter")');
   for(const f of ['xmas','moon','newyear','lantern']){await T(`festSet("${f}");try{document.getElementById('toast').style.display='none'}catch(e){};0`);await cam(T,v);await still('fest_'+f,250)}
 }
 if(shot==='sort'){ await quiet(); await p.addStyleTag({content:'#toast,#dlg{display:none!important}'});
   await T('sortGame()'); let i=0; let simT=0;await settle();const fr=async()=>{await T(`if(SO&&SO.on)SO.end=performance.now()+${30000-simT};0`);simT+=33;await step(33);await p.screenshot({timeout:0,path:`${OUT}/${String(i++).padStart(4,'0')}.jpg`,quality:93})};
   for(let k=0;k<30;k++) await fr();
   await p.clock.runFor(2600);await step(16);await T('SO.on=true;0');
   for(let r=0;r<4;r++){ for(let k=0;k<22;k++) await fr();
     await T('(function(){var q=SO.q[SO.i],k="DISC".indexOf(q[1]);var b=[...document.querySelectorAll("#p [data-act=so]")].find(e=>+e.dataset.v==k);b&&b.click()})()');
     for(let k=0;k<18;k++) await fr(); }
 }
 if(shot==='dojo'){ await quiet(); await p.addStyleTag({content:'#toast,#dlg{display:none!important}'});
   await T('dojo(0)'); await p.clock.runFor(900); await settle();
   for(let i=0;i<90;i++){ await p.evaluate(y=>{document.getElementById('p').scrollTop=y},Math.round(ease(Math.min(1,i/70))*260)); await step(33); await p.screenshot({timeout:0,path:`${OUT}/${String(i).padStart(4,'0')}.jpg`,quality:93}); }
 }
 if(shot==='ward'){ await quiet(); await p.addStyleTag({content:'#toast,#dlg{display:none!important}'});
   await T('avOpen()'); await p.clock.runFor(900); await settle(); const picks=['小貓','兔子','小熊','狐狸'];
   for(let i=0;i<150;i++){ if(i%30==10){const t=picks[(i/30|0)%4];await p.evaluate(t=>{const b=[...document.querySelectorAll('#p button,#p [data-act]')].find(e=>e.textContent.trim().endsWith(t));b&&b.click()},t);} await step(33); await p.screenshot({timeout:0,path:`${OUT}/${String(i).padStart(4,'0')}.jpg`,quality:93}); }
 }
 if(shot==='drink'){ await quiet(); await p.addStyleTag({content:'#toast,#dlg{display:none!important}'}); await T('rewards()'); await p.clock.runFor(900); await settle(); await still('drink',100); }
 await b.close(); console.log('done',shot);
})().catch(e=>{console.error(shot,e);process.exit(1)});
