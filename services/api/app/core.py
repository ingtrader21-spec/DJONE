from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib, os, time, uuid

router=APIRouter(prefix="/v1",tags=["core"])
DECKS={i:{"deck":i,"connected":False,"track":None,"play":None,"bpm":None,"key":None,"observed_at":None} for i in range(1,5)}
TRACKS={}
SAFETY={"execution_enabled":False,"emergency_stop":False,"manual_override":True,"certified":False}

class TrackIn(BaseModel):
    path:str
    source:str="local"
    provenance:str|None=None

@router.get("/decks")
def decks(): return {"decks":list(DECKS.values()),"authority":"observed_mixxx_state"}

@router.get("/decks/{deck}")
def deck(deck:int):
    if deck not in DECKS: raise HTTPException(404,"deck not found")
    return DECKS[deck]

@router.get("/library/tracks")
def tracks(): return {"items":list(TRACKS.values()),"count":len(TRACKS)}

@router.post("/library/tracks",status_code=202)
def ingest(t:TrackIn):
    if not os.path.isfile(t.path): raise HTTPException(422,"source file not found")
    h=hashlib.sha256()
    with open(t.path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    digest=h.hexdigest()
    if digest in TRACKS: return TRACKS[digest]|{"duplicate":True}
    item={"id":str(uuid.uuid4()),"sha256":digest,"path":t.path,"source":t.source,"provenance":t.provenance,"status":"registered","created_at":int(time.time())}
    TRACKS[digest]=item
    return item|{"duplicate":False}

@router.get("/safety/status")
def safety(): return SAFETY|{"fail_closed":not SAFETY["execution_enabled"]}

@router.post("/safety/emergency-stop")
def emergency():
    SAFETY["emergency_stop"]=True; SAFETY["execution_enabled"]=False
    return SAFETY

@router.post("/safety/resume")
def resume():
    if not SAFETY["certified"]: raise HTTPException(409,"Mixxx control/readback certification required")
    SAFETY["emergency_stop"]=False
    return SAFETY|{"note":"resume clears stop; execution still requires explicit arm"}
