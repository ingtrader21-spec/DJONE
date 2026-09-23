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
