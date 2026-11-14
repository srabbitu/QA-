// Capture the 攏好宮 temple, the puppy newbie and Terry from the live site (backend calls are blocked).
const {open,cam,clean}=require('./lib');const fs=require('fs');
const OUT=process.argv[2]||(__dirname+'/cap/temple');
fs.mkdirSync(OUT,{recursive:true});
(async()=>{
 const {b,p,T,step}=await open({w:1280,h:720,dsf:1.5,hour:10,min:30});
 const still=async(n,ms=200)=>{await step(ms);await step(16);await p.screenshot({timeout:0,path:`${OUT}/${n}.png`})};
 await p.clock.runFor(1200);await step(16);
 await T('try{sndSet(false)}catch(e){};try{dlgEnd()}catch(e){};try{close()}catch(e){};0');
 await clean(p);await p.addStyleTag({content:'.lab{opacity:0!important}'});
 const t=JSON.parse(await T('(function(){var d=D.find(function(d){return d.id=="t"});var w=new THREE.Vector3();if(by.t&&by.t.g)by.t.g.getWorldPosition(w);return JSON.stringify([d.x,d.z,d.ang||0,w.x,w.y,w.z])})()'));
 console.log('temple',t);
 const x=t[3]||t[0],z=t[5]||t[1],a=t[2];
 const views=[[22,0.35,.9],[12,0.35,1.05],[8,0.1,1.15],[8,0.9,1.15],[8,-0.7,1.15],[6,0.35,1.25],[5,3.5,1.2]];
 for(let i=0;i<views.length;i++){const [r,o,ph]=views[i];await cam(T,{x,y:.6,z,r,th:-a+o,ph});await still('temple_'+i,150);}
 // chief (Terry)
 try{const c=JSON.parse(await T('(function(){var w=new THREE.Vector3(),d=new THREE.Vector3();chief.getWorldPosition(w);chief.getWorldDirection(d);return JSON.stringify([w.x,w.y,w.z,Math.atan2(d.x,d.z)])})()'));
  await cam(T,{x:c[0],y:c[1]+.8,z:c[2],r:4,th:c[3],ph:1.2});await still('terry',100);}catch(e){console.log('chief err',e.message)}
 await b.close();
})();
