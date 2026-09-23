from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os,socket,json
app=FastAPI(title="DJONE Mixxx Bridge",version="1.0.0-rc")
TOKEN=os.getenv("BRIDGE_TOKEN",""); NATIVE_TOKEN=os.getenv("DJONE_MIXXX_TOKEN","")
HOST=os.getenv("DJONE_MIXXX_HOST","172.21.0.1"); PORT=int(os.getenv("DJONE_MIXXX_PORT","18092"))
EXECUTE=os.getenv("MIXXX_EXECUTION_ENABLED","false").lower()=="true"; EMERGENCY=os.getenv("EMERGENCY_STOP","false").lower()=="true"
ALLOWED={"play"}
class Command(BaseModel):
 command_id:str; action:str; deck:int; value:float|int|bool|None=None
def auth(t):
 if not TOKEN or t!=TOKEN: raise HTTPException(401,"bridge unauthorized")
def native(payload):
 payload["token"]=NATIVE_TOKEN
 try:
  with socket.create_connection((HOST,PORT),timeout=1.5) as s:
   s.sendall((json.dumps(payload,separators=(',',':'))+"\n").encode()); return json.loads(s.makefile().readline())
 except Exception as e:return {"ok":False,"error":"native_unreachable","detail":type(e).__name__}
@app.get("/health")
def health():
 r=native({"op":"get","deck":1,"control":"play"})
 return {"status":"ok","service":"mixxx-bridge","native_reachable":r.get("ok",False),"transport_ready":r.get("ok",False),"execution_enabled":EXECUTE,"emergency_stop":EMERGENCY}
@app.get("/v1/decks/{deck}/play")
def read(deck:int,x_bridge_token:str|None=Header(default=None)):
 auth(x_bridge_token)
 if deck not in range(1,5): raise HTTPException(422,"invalid deck")
 return native({"op":"get","deck":deck,"control":"play"})
@app.post("/v1/execute")
def execute(c:Command,x_bridge_token:str|None=Header(default=None)):
 auth(x_bridge_token)
 if c.action not in ALLOWED: raise HTTPException(422,"unsupported action")
 if EMERGENCY: raise HTTPException(423,"emergency stop active")
 if not EXECUTE:return {"accepted":False,"executed":False,"reason":"execution gate closed"}
 before=native({"op":"get","deck":c.deck,"control":c.action})
 if not before.get("ok"):return {"accepted":False,"executed":False,"reason":"native transport unavailable","native":before}
 result=native({"op":"set","deck":c.deck,"control":c.action,"value":float(c.value)})
 after=native({"op":"get","deck":c.deck,"control":c.action})
 verified=result.get("ok") and after.get("ok") and float(after.get("observed",-999))==float(c.value)
 return {"accepted":True,"executed":bool(result.get("ok")),"readback_verified":verified,"before":before,"result":result,"after":after}
