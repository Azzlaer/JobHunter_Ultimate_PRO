'use strict';
(()=> {
 const HOST='com.azzlaer.jobhunter', DB_KEY='azh_jobhunter_v3';
 const el=id=>document.getElementById(id);
 let connected=false;
 const getDB=async()=> (await chrome.storage.local.get(DB_KEY))[DB_KEY]||{offers:[],profile:{}};
 const request=(action,data={})=>new Promise((resolve,reject)=>chrome.runtime.sendNativeMessage(HOST,{action,...data},r=>{
   const e=chrome.runtime.lastError;
   if(e)return reject(Error(e.message));
   if(!r?.ok)return reject(Error(r?.error||'Respuesta inválida'));
   resolve(r.data);
 }));
 const status=x=>el('native-status').textContent=x;
 async function refresh(){
   if(!connected)return;
   try{
     const s=await request('stats');
     for(const [id,key] of [['sq-runs','search_runs'],['sq-offers','offers'],['sq-published','published'],['sq-failed','failed'],['dash-search-runs','search_runs'],['dash-shared','published']]){
       if(el(id))el(id).textContent=s[key]??0;
     }
     const list=el('search-history');list.replaceChildren();
     if(!s.searches?.length){const p=document.createElement('p');p.className='muted';p.textContent='Todavía no registraste búsquedas.';list.append(p);}
     for(const r of (s.searches||[])){
       const article=document.createElement('article');article.className='job';
       const strong=document.createElement('strong');strong.textContent='#'+r.query_position+' · '+r.term;
       const p=document.createElement('p');p.className='hint';p.textContent=r.opened_at+' · '+r.location+' · Ofertas guardadas: '+r.offers_saved;
       const btn=document.createElement('button');btn.className='secondary';btn.textContent='Abrir LinkedIn';btn.addEventListener('click',()=>chrome.tabs.create({url:r.url}));
       article.append(strong,p,btn);list.append(article);
     }
   }catch(e){status('Error SQLite: '+e.message);}
 }
 async function connect(){
   try{
     const data=await request('ping');connected=true;status('● Conectado a '+data.db);
     const cfg=await request('config');
     el('discord-searches').checked=Boolean(cfg.send_searches);el('discord-offers').checked=Boolean(cfg.send_offers);
     const db=await getDB();const offers=(db.offers||[]).map(o=>({...o,score:window.JobCore?.score?JobCore.score(o,db.profile).value:0}));
     await request('sync_offers',{offers});await refresh();
   }catch(e){connected=false;status('○ Backend no disponible: '+e.message+'. Ejecuta backend/INSTALAR_WINDOWS.bat.');}
 }
 async function captureSearch(){
   if(!connected)return;
   try{
     const opts={profile:el('search-profile').value,custom:el('search-custom').value,location:el('search-location').value,age:el('search-age').value,remote:el('search-remote').checked,entry:el('search-entry').checked};
     const url=JobCore.searchUrl(opts);
     await request('record_search',{url,term:opts.profile==='custom'?opts.custom:opts.profile,location:opts.location});
     await refresh();
   }catch(e){status('No se pudo registrar búsqueda: '+e.message);}
 }
 async function offersChanged(before,after){
   if(!connected)return;
   try{
     const db=await getDB(),prev=new Map((before?.offers||[]).map(o=>[o.id,o]));
     const afterOffers=after?.offers||[];
     for(const o of afterOffers){
       if(!prev.has(o.id)){
         const score=JobCore.score(o,db.profile).value;
         await request('upsert_offer',{offer:o,score});
       }
     }
     const offers=afterOffers.map(o=>({...o,score:JobCore.score(o,db.profile).value}));
     await request('sync_offers',{offers});
     for(const old of (before?.offers||[]))if(!afterOffers.some(o=>o.id===old.id))await request('delete_offer',{id:old.id});
     await refresh();
   }catch(e){status('Sincronización: '+e.message);}
 }
 async function saveConfig(remove=false){
   if(!connected)return status('Primero conecta el backend.');
   try{
     const req={send_searches:el('discord-searches').checked,send_offers:el('discord-offers').checked};
     if(el('discord-hook').value.trim())req.webhook=el('discord-hook').value.trim();
     if(remove)req.remove_webhook=true;
     const r=await request('configure',req);
     el('discord-hook').value='';
     el('discord-searches').checked=r.send_searches;el('discord-offers').checked=r.send_offers;
     status(r.configured?'Configuración guardada.':'Webhook desconectado.');await refresh();
   }catch(e){status('Discord: '+e.message);}
 }
 el('native-test').addEventListener('click',connect);
 el('sq-refresh').addEventListener('click',refresh);
 el('discord-save').addEventListener('click',()=>saveConfig(false));
 el('discord-remove').addEventListener('click',()=>{if(confirm('¿Quitar el webhook?'))saveConfig(true);});
 el('sq-export').addEventListener('click',async()=>{
   try{
     const data=await request('export_rows');
     const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
     const a=document.createElement('a');a.href=url;a.download='JobHunter_Community_SQLite_'+new Date().toISOString().slice(0,10)+'.json';a.click();
     setTimeout(()=>URL.revokeObjectURL(url),3000);
   }catch(e){status('Exportación: '+e.message);}
 });
 el('search-btn').addEventListener('click',captureSearch);
 chrome.storage.onChanged.addListener((changes,area)=>{if(area==='local'&&changes[DB_KEY])offersChanged(changes[DB_KEY].oldValue,changes[DB_KEY].newValue);});
 connect();
})();
