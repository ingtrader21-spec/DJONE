from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db import conn
from app.security import authorize
import hashlib, os, json

router=APIRouter(prefix="/v1",tags=["core"],dependencies=[Depends(authorize)])
class TrackIn(BaseModel):
    path:str
    source:str="local"
    provenance:str|None=None

@router.get("/decks")
def decks():
    with conn() as c:
        rows=c.execute("SELECT deck,connected,track_id,play,bpm,musical_key,observed_at FROM deck_state ORDER BY deck").fetchall()
    return {"decks":[{"deck":r[0],"connected":r[1],"track_id":str(r[2]) if r[2] else None,"play":r[3],"bpm":r[4],"key":r[5],"observed_at":r[6]} for r in rows],"authority":"observed_mixxx_state"}

@router.get("/decks/{deck}")
def deck(deck:int):
    if deck not in range(1,5): raise HTTPException(404,"deck not found")
    with conn() as c:
        r=c.execute("SELECT deck,connected,track_id,play,bpm,musical_key,observed_at FROM deck_state WHERE deck=%s",(deck,)).fetchone()
    return {"deck":r[0],"connected":r[1],"track_id":str(r[2]) if r[2] else None,"play":r[3],"bpm":r[4],"key":r[5],"observed_at":r[6]}

@router.get("/library/tracks")
def tracks():
    with conn() as c:
        rows=c.execute("SELECT id,sha256,path,source,provenance,status,created_at FROM music_tracks ORDER BY created_at DESC LIMIT 500").fetchall()
    items=[{"id":str(r[0]),"sha256":r[1],"path":r[2],"source":r[3],"provenance":r[4],"status":r[5],"created_at":r[6]} for r in rows]
    return {"items":items,"count":len(items)}

@router.post("/library/tracks",status_code=202)
def ingest(t:TrackIn):
    if not os.path.isfile(t.path): raise HTTPException(422,"source file not found")
    h=hashlib.sha256()
    with open(t.path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    digest=h.hexdigest()
    with conn() as c:
        r=c.execute("SELECT id,sha256,path,source,provenance,status,created_at FROM music_tracks WHERE sha256=%s",(digest,)).fetchone()
        if r: return {"id":str(r[0]),"sha256":r[1],"path":r[2],"source":r[3],"provenance":r[4],"status":r[5],"created_at":r[6],"duplicate":True}
        r=c.execute("INSERT INTO music_tracks(sha256,path,source,provenance) VALUES(%s,%s,%s,%s) RETURNING id,created_at",(digest,t.path,t.source,t.provenance)).fetchone()
    return {"id":str(r[0]),"sha256":digest,"path":t.path,"source":t.source,"provenance":t.provenance,"status":"registered","created_at":r[1],"duplicate":False}

@router.get("/safety/status")
def safety():
    with conn() as c:
        r=c.execute("SELECT execution_enabled,emergency_stop,manual_override,certified,updated_at FROM safety_state WHERE singleton=true").fetchone()
    return {"execution_enabled":r[0],"emergency_stop":r[1],"manual_override":r[2],"certified":r[3],"updated_at":r[4],"fail_closed":not r[0]}

@router.post("/safety/emergency-stop")
def emergency():
    with conn() as c:
        c.execute("UPDATE safety_state SET emergency_stop=true,execution_enabled=false,updated_at=now() WHERE singleton=true")
        c.execute("INSERT INTO dj_events(kind,payload) VALUES('EMERGENCY_STOP','{}'::jsonb)")
    return safety()

@router.post("/safety/resume")
def resume():
    with conn() as c:
        certified=c.execute("SELECT certified FROM safety_state WHERE singleton=true").fetchone()[0]
        if not certified: raise HTTPException(409,"Mixxx control/readback certification required")
        c.execute("UPDATE safety_state SET emergency_stop=false,updated_at=now() WHERE singleton=true")
        c.execute("INSERT INTO dj_events(kind,payload) VALUES('SAFETY_REARM','{}'::jsonb)")
    return safety()|{"note":"stop cleared; execution remains independently gated"}

class ArmIn(BaseModel):
    enabled: bool

@router.post("/safety/execution")
def execution_gate(a:ArmIn):
    with conn() as c:
        s=c.execute("SELECT emergency_stop,certified,manual_override FROM safety_state WHERE singleton=true").fetchone()
        if a.enabled and s[0]: raise HTTPException(409,"clear emergency stop before enabling execution")
        if a.enabled and not s[1]: raise HTTPException(409,"Mixxx certification required")
        if a.enabled and not s[2]: raise HTTPException(409,"manual override capability required")
        c.execute("UPDATE safety_state SET execution_enabled=%s,updated_at=now() WHERE singleton=true",(a.enabled,))
        c.execute("INSERT INTO dj_events(kind,payload) VALUES('EXECUTION_GATE',jsonb_build_object('enabled',%s))",(a.enabled,))
    return safety()

@router.get("/events")
def events(limit:int=100):
    limit=max(1,min(limit,500))
    with conn() as c:
        rows=c.execute("SELECT id,kind,payload,created_at FROM dj_events ORDER BY id DESC LIMIT %s",(limit,)).fetchall()
    return {"items":[{"id":r[0],"kind":r[1],"payload":r[2],"created_at":r[3]} for r in rows]}

@router.get("/production/status")
def production_status():
    with conn() as c:
        s=c.execute("SELECT execution_enabled,emergency_stop,manual_override,certified,updated_at FROM safety_state WHERE singleton=true").fetchone()
        counts=c.execute("SELECT count(*) FILTER(WHERE status='COMPLETED'),count(*) FILTER(WHERE status='EXECUTION_FAILED'),count(*) FROM dj_commands").fetchone()
    blockers=[]
    if not s[3]: blockers.append("mixxx_not_certified")
    if s[1]: blockers.append("emergency_stop_active")
    if not s[2]: blockers.append("manual_override_unavailable")
    return {"production_candidate":len([x for x in blockers if x!="emergency_stop_active"])==0,"production_enabled":bool(s[0] and not s[1] and s[3]),"safety":{"execution_enabled":s[0],"emergency_stop":s[1],"manual_override":s[2],"certified":s[3],"updated_at":s[4]},"commands":{"completed":counts[0],"failed":counts[1],"total":counts[2]},"blockers":blockers}

@router.get("/certification/evidence")
def certification_evidence():
    with conn() as c:
        safety_row=c.execute("SELECT execution_enabled,emergency_stop,manual_override,certified,updated_at FROM safety_state WHERE singleton=true").fetchone()
        mutation=c.execute("SELECT payload,created_at FROM dj_events WHERE kind='MIXXX_CERT_MUTATION' ORDER BY id DESC LIMIT 1").fetchone()
        recent=c.execute("SELECT idempotency_key,status,result_json,readback_json,executed_at FROM dj_commands ORDER BY accepted_at DESC LIMIT 20").fetchall()
    return {"safety":{"execution_enabled":safety_row[0],"emergency_stop":safety_row[1],"manual_override":safety_row[2],"certified":safety_row[3],"updated_at":safety_row[4]},"native_mutation":None if not mutation else {"payload":mutation[0],"created_at":mutation[1]},"recent_commands":[{"idempotency_key":r[0],"status":r[1],"result":r[2],"readback":r[3],"executed_at":r[4]} for r in recent]}
