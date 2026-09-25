from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.remix import router as remix_router
from app.core import router as core_router
from app.db import conn
from app.integrations import router as integrations_router
from app.dispatch import execute_command
from app.outputs import router as outputs_router
from pydantic import BaseModel, Field
from typing import Literal
import os, time, uuid, json

app = FastAPI(title="DJONE Control API", version="0.3.0")
app.include_router(remix_router)
app.include_router(core_router)
app.include_router(integrations_router)
app.include_router(outputs_router)
MODE = os.getenv("DJONE_MODE", "assistant")
ENV = os.getenv("DJONE_ENV", "development")
API_TOKEN = os.getenv("DJONE_API_TOKEN", "")
STARTED = time.time()
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")
ALLOWED = {"load_track","play","pause","stop","set_gain","set_tempo","set_key","set_loop","set_hotcue","sync","record_start","record_stop"}
COMMANDS: dict[str, dict] = {}

class Command(BaseModel):
    action: str
    deck: int | None = Field(default=None, ge=1, le=4)
    value: str | float | int | bool | None = None

def authorize(authorization: str | None):
    if not API_TOKEN:
        if ENV == "staging":
            raise HTTPException(503, "DJONE_API_TOKEN is required in staging")
        return
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(401, "unauthorized")

app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")

@app.get("/")
def dashboard():
    return FileResponse(os.path.join(UI_DIR, "index.html"))

@app.get("/health")
def health():
    return {"status":"ok","service":"djone-api","version":"0.2.0","environment":ENV,"mode":MODE,"uptime_s":int(time.time()-STARTED)}

@app.get("/ready")
def ready(response: Response):
    configured = ENV != "staging" or bool(API_TOKEN)
    if not configured:
        response.status_code = 503
    return {"ready":configured,"environment":ENV,"auth_configured":bool(API_TOKEN),"mixxx_execution_enabled":False}

@app.get("/v1/capabilities")
def capabilities():
    return {"mode":MODE,"decks":[1,2,3,4],"actions":sorted(ALLOWED),"mixxx_execution_enabled":False}

def _row_command(r):
    return {"id":str(r[0]),"idempotency_key":r[1],"actor":r[2],"mode":r[3],"action":r[4],"deck":r[5],"value":r[6],"status":r[7],"accepted_at":r[8],"executed_at":r[9],"result":r[10],"readback":r[11]}

@app.post("/v1/commands", status_code=202)
def command(c: Command, authorization: str | None = Header(default=None), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    authorize(authorization)
    if c.action not in ALLOWED: raise HTTPException(422, f"unsupported action: {c.action}")
    key=idempotency_key or str(uuid.uuid4())
    with conn() as db:
        existing=db.execute("SELECT id,idempotency_key,actor,mode,action,deck,value_json,status,accepted_at,executed_at,result_json,readback_json FROM dj_commands WHERE idempotency_key=%s",(key,)).fetchone()
        if existing: return _row_command(existing)|{"duplicate":True}
        safety=db.execute("SELECT execution_enabled,emergency_stop,certified FROM safety_state WHERE singleton=true").fetchone()
        status="POLICY_APPROVED" if safety[0] and not safety[1] and safety[2] else "VALIDATED_GATE_CLOSED"
        r=db.execute("INSERT INTO dj_commands(idempotency_key,actor,mode,action,deck,value_json,status) VALUES(%s,'api',%s,%s,%s,%s::jsonb,%s) RETURNING id,idempotency_key,actor,mode,action,deck,value_json,status,accepted_at,executed_at,result_json,readback_json",(key,MODE,c.action,c.deck,json.dumps(c.value),status)).fetchone()
        db.execute("INSERT INTO dj_events(kind,payload) VALUES('COMMAND_RECEIVED',jsonb_build_object('command_id',%s::text,'idempotency_key',%s,'status',%s))",(str(r[0]),key,status))
    if status!="POLICY_APPROVED": return _row_command(r)|{"duplicate":False,"executed":False}\n    out,result=execute_command(r[0],c.action,c.deck,c.value)\n    return _row_command(out)|{"duplicate":False,"executed":result.get("executed",False),"readback_verified":result.get("readback_verified",False)}

@app.get("/v1/commands/{idempotency_key}")
def command_status(idempotency_key: str, authorization: str | None = Header(default=None)):
    authorize(authorization)
    with conn() as db:
        r=db.execute("SELECT id,idempotency_key,actor,mode,action,deck,value_json,status,accepted_at,executed_at,result_json,readback_json FROM dj_commands WHERE idempotency_key=%s",(idempotency_key,)).fetchone()
    if not r: raise HTTPException(404,"command not found")
    return _row_command(r)
