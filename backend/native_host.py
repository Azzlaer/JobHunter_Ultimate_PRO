"""Azzlaer JobHunter Community Native Messaging host (Python 3.10+, standard library)."""
import json, os, pathlib, re, sqlite3, struct, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qsl, urlencode
ROOT = pathlib.Path(os.environ.get("AZZLAER_JOBHUNTER_HOME", str(pathlib.Path.home()/"AzzlaerJobHunter")))
DATABASE = ROOT/"jobhunter.sqlite3"
CONFIG = ROOT/"config.json"
def stamp(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def linkedin(link, search=False):
    p=urlparse(str(link))
    if p.scheme!="https" or p.hostname not in ("linkedin.com","www.linkedin.com"): raise ValueError("Solo enlaces HTTPS de LinkedIn")
    if search:
        if not p.path.startswith("/jobs/search"): raise ValueError("No es una búsqueda LinkedIn Jobs")
        q={k:v for k,v in parse_qsl(p.query) if k in ("keywords","location","f_TPR","f_WT","f_E","f_JT")}
        return "https://www.linkedin.com/jobs/search/?"+urlencode(q)
    m=re.fullmatch(r"/jobs/view/(\d+)/?",p.path)
    if not m: raise ValueError("No es una oferta LinkedIn Jobs")
    return "https://www.linkedin.com/jobs/view/"+m.group(1)+"/"
def open_db():
    ROOT.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DATABASE,timeout=10)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA busy_timeout=10000")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS searches(id INTEGER PRIMARY KEY AUTOINCREMENT,url TEXT UNIQUE NOT NULL, term TEXT, location TEXT, opened_at TEXT, times_opened INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS search_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,search_id INTEGER NOT NULL, opened_at TEXT NOT NULL, query_position INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS offers(id TEXT PRIMARY KEY,url TEXT UNIQUE NOT NULL,title TEXT NOT NULL,company TEXT NOT NULL,location TEXT,status TEXT,score INTEGER,search_run_id INTEGER,result_position INTEGER,saved_at TEXT,updated_at TEXT);
    CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY AUTOINCREMENT,action TEXT,at TEXT,detail TEXT);
    CREATE TABLE IF NOT EXISTS dispatches(id INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,item_key TEXT,state TEXT,created_at TEXT,error TEXT,UNIQUE(kind,item_key));
    """)
    return db
def readcfg():
    try:
        data=json.loads(CONFIG.read_text(encoding="utf-8"))
        if isinstance(data,dict): return data
    except (OSError,ValueError): pass
    return {"webhook":"","send_searches":False,"send_offers":False}
def configure(m):
    c=readcfg()
    if m.get("remove_webhook"): c["webhook"]=""
    if m.get("webhook"):
        p=urlparse(str(m["webhook"]))
        if p.scheme!="https" or p.hostname not in ("discord.com","discordapp.com") or not re.fullmatch(r"/api(?:/v\d+)?/webhooks/\d+/[A-Za-z0-9_-]+/?",p.path) or p.query or p.fragment:
            raise ValueError("URL de webhook Discord inválida")
        c["webhook"]=str(m["webhook"])
    if "send_searches" in m: c["send_searches"]=bool(m["send_searches"])
    if "send_offers" in m: c["send_offers"]=bool(m["send_offers"])
    if not c["webhook"]: c["send_searches"]=c["send_offers"]=False
    ROOT.mkdir(parents=True,exist_ok=True)
    CONFIG.write_text(json.dumps(c,indent=2),encoding="utf-8")
    if os.name!="nt": os.chmod(CONFIG,0o600)
    return {"configured":bool(c["webhook"]),"send_searches":c["send_searches"],"send_offers":c["send_offers"]}
def publish(db,kind,key,title,url,details):
    c=readcfg()
    if not c.get("webhook") or not c.get("send_searches" if kind=="search" else "send_offers"): return
    if db.execute("SELECT 1 FROM dispatches WHERE kind=? AND item_key=? AND state='sent'",(kind,key)).fetchone():return
    safe=linkedin(url,kind=="search")
    payload=json.dumps({"username":"JobHunter Comunidad","allowed_mentions":{"parse":[]},"embeds":[{"title":str(title)[:200],"url":safe,"description":str(details)[:800],"color":3447003,"footer":{"text":"Búsqueda compartida por usuario · Verifica en LinkedIn"}}]}).encode()
    request=urllib.request.Request(c["webhook"]+"?wait=true",data=payload,headers={"Content-Type":"application/json","User-Agent":"JobHunterCommunity/6.0"},method="POST")
    state,error="failed",""
    try:
        with urllib.request.urlopen(request,timeout=12) as response:
            if 200<=response.status<300: state="sent"
            else: error="Discord HTTP "+str(response.status)
    except Exception as exc: error=type(exc).__name__
    db.execute("INSERT INTO dispatches(kind,item_key,state,created_at,error) VALUES(?,?,?,?,?) ON CONFLICT(kind,item_key) DO UPDATE SET state=excluded.state,created_at=excluded.created_at,error=excluded.error",(kind,key,state,stamp(),error))
    db.commit()
def record_search(db,m):
    url=linkedin(m.get("url"),True);t=stamp()
    term=str(m.get("term") or "Búsqueda de empleo")[:180]
    location=str(m.get("location") or "")[:120]
    db.execute("INSERT INTO searches(url,term,location,opened_at,times_opened) VALUES(?,?,?,?,1) ON CONFLICT(url) DO UPDATE SET times_opened=times_opened+1,opened_at=excluded.opened_at",(url,term,location,t))
    sid=db.execute("SELECT id FROM searches WHERE url=?",(url,)).fetchone()["id"]
    position=db.execute("SELECT COUNT(*) FROM search_runs").fetchone()[0]+1
    rid=db.execute("INSERT INTO search_runs(search_id,opened_at,query_position) VALUES(?,?,?)",(sid,t,position)).lastrowid
    db.execute("INSERT INTO activity(action,at,detail) VALUES(?,?,?)",("search",t,term));db.commit()
    publish(db,"search",str(rid),"🔎 Búsqueda: "+term,url,"Enlace a resultados de búsqueda; no es una vacante confirmada. Ubicación: "+location)
    return {"run_id":rid,"position":position}
def save_offer(db,m,publish_new=True):
    o=m.get("offer") or m
    url=linkedin(o.get("url"));oid=str(o.get("id") or "")[:120]
    title=str(o.get("title") or "").strip()[:180];company=str(o.get("company") or "").strip()[:140]
    if not oid or not title or not company: raise ValueError("Faltan id, cargo o empresa")
    status=str(o.get("status") or "guardada")[:30]
    score=max(0,min(100,int(m.get("score",o.get("score",0)) or 0)))
    row=db.execute("SELECT id,search_run_id,result_position,saved_at FROM offers WHERE url=?",(url,)).fetchone()
    t=stamp();rid=row["search_run_id"] if row else None
    if not row:
        last=db.execute("SELECT id FROM search_runs ORDER BY id DESC LIMIT 1").fetchone()
        rid=last["id"] if last else None
    position=row["result_position"] if row else db.execute("SELECT COALESCE(MAX(result_position),0)+1 FROM offers WHERE search_run_id IS ?",(rid,)).fetchone()[0]
    actual_id=row["id"] if row else oid
    db.execute("""INSERT INTO offers(id,url,title,company,location,status,score,search_run_id,result_position,saved_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,company=excluded.company,location=excluded.location,status=excluded.status,score=excluded.score,updated_at=excluded.updated_at""",
      (actual_id,url,title,company,str(o.get("location") or "")[:100],status,score,rid,position,row["saved_at"] if row else t,t))
    db.commit()
    if not row and publish_new: publish(db,"offer",actual_id,"💼 "+title,url,"Empresa: "+company+" · "+str(o.get("location") or "")[:100])
    return {"id":actual_id,"position":position}
def stats(db):
    counts={"search_runs":"SELECT COUNT(*) FROM search_runs","unique_searches":"SELECT COUNT(*) FROM searches","offers":"SELECT COUNT(*) FROM offers","matches":"SELECT COUNT(*) FROM offers WHERE score>=70","applied":"SELECT COUNT(*) FROM offers WHERE status='postulada'","interviews":"SELECT COUNT(*) FROM offers WHERE status='entrevista'","published":"SELECT COUNT(*) FROM dispatches WHERE state='sent'","failed":"SELECT COUNT(*) FROM dispatches WHERE state='failed'"}
    out={k:db.execute(q).fetchone()[0] for k,q in counts.items()}
    out["searches"]=[dict(r) for r in db.execute("SELECT r.query_position,r.opened_at,s.term,s.location,s.url,(SELECT COUNT(*) FROM offers o WHERE o.search_run_id=r.id) offers_saved FROM search_runs r JOIN searches s ON s.id=r.search_id ORDER BY r.id DESC LIMIT 60")]
    out["recent_offers"]=[dict(r) for r in db.execute("SELECT title,company,url,status,score,search_run_id,result_position FROM offers ORDER BY updated_at DESC LIMIT 30")]
    return out
def handle(m):
    if not isinstance(m,dict):raise ValueError("Mensaje inválido")
    action=m.get("action")
    if action=="configure":return configure(m)
    if action=="config":
        c=readcfg();return {"configured":bool(c.get("webhook")),"send_searches":bool(c.get("send_searches")),"send_offers":bool(c.get("send_offers"))}
    with open_db() as db:
        if action=="ping":return {"db":str(DATABASE),"version":"6.0.0"}
        if action=="record_search":return record_search(db,m)
        if action=="upsert_offer":return save_offer(db,m)
        if action=="sync_offers":
            rows=m.get("offers") or []
            if not isinstance(rows,list) or len(rows)>5000:raise ValueError("Lista de ofertas inválida")
            count=0
            for offer in rows:
                try:save_offer(db,offer,False);count+=1
                except (ValueError,TypeError,KeyError):continue
            return {"synced":count}
        if action=="delete_offer":
            db.execute("DELETE FROM offers WHERE id=?",(str(m.get("id") or "")[:120],));db.commit();return {"ok":True}
        if action=="stats":return stats(db)
        if action=="export_rows":return {"search_runs":[dict(x) for x in db.execute("SELECT r.*,s.url,s.term,s.location FROM search_runs r JOIN searches s ON s.id=r.search_id ORDER BY r.id")],"offers":[dict(x) for x in db.execute("SELECT * FROM offers ORDER BY search_run_id,result_position")]}
    raise ValueError("Acción no permitida")
def main():
    stream=sys.stdin.buffer
    header=stream.read(4)
    if len(header)!=4:return
    size=struct.unpack("=I",header)[0]
    if size>2_000_000:raise ValueError("Mensaje demasiado grande")
    raw=stream.read(size)
    if len(raw)!=size:raise ValueError("Mensaje truncado")
    try: response={"ok":True,"data":handle(json.loads(raw))}
    except Exception as exc:response={"ok":False,"error":str(exc)[:250]}
    payload=json.dumps(response,ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("=I",len(payload))+payload)
    sys.stdout.buffer.flush()
if __name__=="__main__":main()
