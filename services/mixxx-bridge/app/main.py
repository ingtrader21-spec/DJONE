from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os,socket,json
import psycopg
app=FastAPI(title="DJONE Mixxx Bridge",version="1.0.0-rc")
TOKEN=os.getenv("BRIDGE_TOKEN",""); NATIVE_TOKEN=os.getenv("DJONE_MIXXX_TOKEN","")
HOST=os.getenv("DJONE_MIXXX_HOST","172.21.0.1"); PORT=int(os.getenv("DJONE_MIXXX_PORT","18092"))
DSN=os.getenv("DATABASE_URL","postgresql://djone:djone@postgres:5432/djone")
def safety():
 try:
  with psycopg.connect(DSN) as db:
   r=db.execute("SELECT execution_enabled,emergency_stop,certified FROM safety_state WHERE singleton=true").fetchone()
  return {"execution_enabled":r[0],"emergency_stop":r[1],"certified":r[2]}
 except Exception:
  return {"execution_enabled":False,"emergency_stop":True,"certified":False}
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
 st=safety()
 return {"status":"ok","service":"mixxx-bridge","native_reachable":r.get("ok",False),"transport_ready":r.get("ok",False),**st}
@app.get("/v1/decks/{deck}/play")
def read(deck:int,x_bridge_token:str|None=Header(default=None)):
 auth(x_bridge_token)
 if deck not in range(1,5): raise HTTPException(422,"invalid deck")
 return native({"op":"get","deck":deck,"control":"play"})
@app.post("/v1/execute")
def execute(c:Command,x_bridge_token:str|None=Header(default=None)):
 auth(x_bridge_token)
 if c.action not in ALLOWED: raise HTTPException(422,"unsupported action")
 if c.deck not in range(1,5): raise HTTPException(422,"invalid deck")
 if c.value is None: raise HTTPException(422,"value required")
 st=safety()
 if st["emergency_stop"]: raise HTTPException(423,"emergency stop active")
 if not st["certified"]: raise HTTPException(423,"Mixxx certification required")
 if not st["execution_enabled"]: return {"accepted":False,"executed":False,"reason":"execution gate closed"}
 before=native({"op":"get","deck":c.deck,"control":c.action})
 if not before.get("ok"):return {"accepted":False,"executed":False,"reason":"native transport unavailable","native":before}
 result=native({"op":"set","deck":c.deck,"control":c.action,"value":float(c.value)})
 after=native({"op":"get","deck":c.deck,"control":c.action})
 verified=result.get("ok") and after.get("ok") and float(after.get("observed",-999))==float(c.value)
 return {"accepted":True,"executed":bool(result.get("ok")),"readback_verified":verified,"before":before,"result":result,"after":after}
