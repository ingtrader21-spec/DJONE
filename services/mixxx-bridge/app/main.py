from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os, socket, json
app=FastAPI(title="DJONE Mixxx Bridge",version="0.2.0")
TOKEN=os.getenv("BRIDGE_TOKEN",""); NATIVE_TOKEN=os.getenv("DJONE_NATIVE_TOKEN","")
NATIVE_HOST=os.getenv("DJONE_NATIVE_HOST","host.docker.internal"); NATIVE_PORT=int(os.getenv("DJONE_NATIVE_PORT","18091"))
EXECUTE=os.getenv("MIXXX_EXECUTION_ENABLED","false").lower()=="true"; EMERGENCY=os.getenv("EMERGENCY_STOP","false").lower()=="true"
class BridgeCommand(BaseModel):
 command_id:str; action:str; deck:int|None=None; value:str|float|int|bool|None=None
def auth(t):
 if not TOKEN or t!=TOKEN: raise HTTPException(401,"bridge unauthorized")
def native(p):
 p["token"]=NATIVE_TOKEN
 try:
  with socket.create_connection((NATIVE_HOST,NATIVE_PORT),timeout=1.5) as s:
   s.sendall((json.dumps(p)+"\n").encode()); return json.loads(s.makefile().readline())
 except Exception as e: return {"ok":False,"error":"native_unreachable","detail":type(e).__name__}
@app.get("/health")
def health():
 n=native({"op":"state"}); return {"status":"ok","service":"mixxx-bridge","native_reachable":n.get("ok",False),"transport_ready":n.get("transport_ready",False),"execution_enabled":EXECUTE,"emergency_stop":EMERGENCY}
@app.get("/v1/state")
def state(x_bridge_token:str|None=Header(default=None)):
 auth(x_bridge_token); return native({"op":"state"})
@app.post("/v1/execute")
def execute(c:BridgeCommand,x_bridge_token:str|None=Header(default=None)):
 auth(x_bridge_token)
 if EMERGENCY: raise HTTPException(423,"emergency stop active")
 s=native({"op":"state"})
 if not s.get("transport_ready"): return {"accepted":False,"executed":False,"reason":"native transport/readback not ready","native":s}
 if not EXECUTE: return {"accepted":False,"executed":False,"reason":"execution gate closed"}
 return native({"op":"command","command_id":c.command_id,"action":c.action,"deck":c.deck,"value":c.value})
