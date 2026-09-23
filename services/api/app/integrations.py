from fastapi import APIRouter, HTTPException
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
