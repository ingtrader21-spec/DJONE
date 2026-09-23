from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os, time

app=FastAPI(title="DJONE Mixxx Bridge",version="0.1.0")
TOKEN=os.getenv("BRIDGE_TOKEN","")
EXECUTE=os.getenv("MIXXX_EXECUTION_ENABLED","false").lower()=="true"
EMERGENCY=os.getenv("EMERGENCY_STOP","false").lower()=="true"
state={"connected":False,"last_command":None,"last_readback":None}

class BridgeCommand(BaseModel):
    command_id:str
    action:str
    deck:int|None=None
    value:str|float|int|bool|None=None

def auth(x_bridge_token:str|None):
    if not TOKEN or x_bridge_token!=TOKEN: raise HTTPException(401,"bridge unauthorized")

@app.get("/health")
def health(): return {"status":"ok","service":"mixxx-bridge","execution_enabled":EXECUTE,"emergency_stop":EMERGENCY}

@app.get("/v1/state")
def get_state(x_bridge_token:str|None=Header(default=None)):
    auth(x_bridge_token); return state|{"execution_enabled":EXECUTE,"emergency_stop":EMERGENCY}

@app.post("/v1/execute")
def execute(c:BridgeCommand,x_bridge_token:str|None=Header(default=None)):
    auth(x_bridge_token)
    if EMERGENCY: raise HTTPException(423,"emergency stop active")
    if not EXECUTE: return {"accepted":False,"executed":False,"reason":"execution gate closed","command_id":c.command_id}
    # Adapter boundary exists, but real Mixxx transport is not certified yet.
    return {"accepted":False,"executed":False,"reason":"mixxx transport/readback not certified","command_id":c.command_id}
