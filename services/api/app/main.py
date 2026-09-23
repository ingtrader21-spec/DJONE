from fastapi import FastAPI
from pydantic import BaseModel
import os, time, uuid

app=FastAPI(title="DJONE Control API",version="0.1.0")
MODE=os.getenv("DJONE_MODE","assistant")
class Command(BaseModel):
    action:str
    deck:int|None=None
    value:str|float|int|bool|None=None

@app.get("/health")
def health():
    return {"status":"ok","service":"djone-api","mode":MODE}

@app.post("/v1/commands")
def command(c:Command):
    # Phase 0: ledger/validation boundary only. Mixxx execution is intentionally not enabled yet.
    return {"id":str(uuid.uuid4()),"accepted":True,"executed":False,"mode":MODE,"command":c.model_dump(),"ts":int(time.time())}
