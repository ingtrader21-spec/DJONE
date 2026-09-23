from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from app.db import conn
router=APIRouter(prefix="/v1/integrations",tags=["integrations"])
DOMAINS=["core","library","decks","commands","safety","sessions","agent","remix"]
@router.get("")
def integrations():
    return {"domains":[{"id":d,"connector":f"djone-{d}","webhooks":True,"status":"foundation"} for d in DOMAINS]}
@router.get("/{domain}")
def integration(domain:str):
    if domain not in DOMAINS: raise HTTPException(404,"integration domain not found")
    return {"id":domain,"connector":f"djone-{domain}","v3_prefix":f"/platform/v1/djone/{domain}","webhook_source":"djone","status":"foundation"}
@router.get("/webhooks/outbox/status")
def outbox_status():
    with conn() as c:
        rows=c.execute("SELECT status,count(*) FROM webhook_outbox GROUP BY status ORDER BY status").fetchall()
    return {"counts":{r[0]:r[1] for r in rows}}

class SubscriptionIn(BaseModel):
    domain:str
    endpoint:str
    secret_ref:str

@router.get("/webhooks/subscriptions")
def subscriptions():
    with conn() as c:
        rows=c.execute("SELECT id,domain,endpoint,secret_ref,enabled,created_at FROM webhook_subscriptions ORDER BY created_at").fetchall()
    return {"items":[{"id":str(r[0]),"domain":r[1],"endpoint":r[2],"secret_ref":r[3],"enabled":r[4],"created_at":r[5]} for r in rows]}

@router.post("/webhooks/subscriptions",status_code=201)
def create_subscription(s:SubscriptionIn):
    if s.domain not in DOMAINS: raise HTTPException(422,"unknown domain")
    if not s.endpoint.startswith(("https://","http://127.0.0.1","http://localhost")): raise HTTPException(422,"webhook endpoint must use HTTPS or loopback")
    with conn() as c:
        r=c.execute("INSERT INTO webhook_subscriptions(domain,endpoint,secret_ref) VALUES(%s,%s,%s) ON CONFLICT(domain,endpoint) DO UPDATE SET secret_ref=excluded.secret_ref,enabled=true RETURNING id,created_at",(s.domain,s.endpoint,s.secret_ref)).fetchone()
    return {"id":str(r[0]),"domain":s.domain,"endpoint":s.endpoint,"secret_ref":s.secret_ref,"enabled":True,"created_at":r[1]}
