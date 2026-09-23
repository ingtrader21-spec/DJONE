from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.remix import router as remix_router
from pydantic import BaseModel, Field
from typing import Literal
import os, time, uuid

app = FastAPI(title="DJONE Control API", version="0.3.0")
app.include_router(remix_router)
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

@app.post("/v1/commands", status_code=202)
def command(c: Command, authorization: str | None = Header(default=None), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    authorize(authorization)
    if c.action not in ALLOWED:
        raise HTTPException(422, f"unsupported action: {c.action}")
    key = idempotency_key or str(uuid.uuid4())
    if key in COMMANDS:
        return COMMANDS[key]
    item = {"id":str(uuid.uuid4()),"idempotency_key":key,"accepted":True,"executed":False,"status":"queued_for_bridge","mode":MODE,"command":c.model_dump(),"ts":int(time.time())}
    COMMANDS[key] = item
    return item

@app.get("/v1/commands/{idempotency_key}")
def command_status(idempotency_key: str, authorization: str | None = Header(default=None)):
    authorize(authorization)
    if idempotency_key not in COMMANDS:
        raise HTTPException(404, "command not found")
    return COMMANDS[idempotency_key]
