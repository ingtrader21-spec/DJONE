from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import conn
import hashlib, os, json

router=APIRouter(prefix="/v1",tags=["core"])
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
