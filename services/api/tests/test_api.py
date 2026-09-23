import os
os.environ["DJONE_ENV"]="development"
from fastapi.testclient import TestClient
from app.main import app

c=TestClient(app)
def test_health(): assert c.get("/health").status_code==200
def test_ready(): assert c.get("/ready").json()["ready"] is True
def test_capabilities(): assert "play" in c.get("/v1/capabilities").json()["actions"]
def test_command_idempotency():
    h={"Idempotency-Key":"same"}
    a=c.post("/v1/commands",json={"action":"play","deck":1},headers=h)
    b=c.post("/v1/commands",json={"action":"play","deck":1},headers=h)
    assert a.status_code==202 and a.json()["id"]==b.json()["id"]
def test_reject_unknown(): assert c.post("/v1/commands",json={"action":"shell"}).status_code==422

def test_dashboard():
    r=c.get("/")
    assert r.status_code==200 and "DJONE" in r.text and "DECK A" in r.text

def test_remix_contract():
    r=c.post("/v1/remix/jobs",json={"source_path":"/music/test.wav","operation":"stems"})
    assert r.status_code==202
    jid=r.json()["id"]
    assert c.get(f"/v1/remix/jobs/{jid}").status_code==200
    caps=c.get("/v1/remix/capabilities").json()
    assert caps["demucs_runtime"] is False

def test_integration_registry():
    r=c.get("/v1/integrations")
    assert r.status_code==200
    ids={x["id"] for x in r.json()["domains"]}
    assert ids=={"core","library","decks","commands","safety","sessions","agent","remix"}

def test_integration_unknown():
    assert c.get("/v1/integrations/nope").status_code==404
