import json, os, urllib.request
from app.db import conn

def execute_command(command_id, action, deck, value):
    payload=json.dumps({"command_id":str(command_id),"action":action,"deck":deck,"value":value}).encode()
    req=urllib.request.Request(os.getenv("BRIDGE_URL","http://mixxx-bridge:8091")+"/v1/execute",data=payload,method="POST",headers={"Content-Type":"application/json","X-Bridge-Token":os.getenv("BRIDGE_TOKEN","")})
    try:
        result=json.loads(urllib.request.urlopen(req,timeout=3).read())
    except Exception as exc:
        result={"executed":False,"readback_verified":False,"error":type(exc).__name__}
    final="COMPLETED" if result.get("executed") and result.get("readback_verified") else "EXECUTION_FAILED"
    with conn() as db:
        db.execute("UPDATE dj_commands SET status=%s,executed_at=now(),result_json=%s::jsonb,readback_json=%s::jsonb WHERE id=%s",(final,json.dumps(result),json.dumps(result.get("after")),str(command_id)))
        db.execute("INSERT INTO dj_events(kind,payload) VALUES('COMMAND_RESULT',jsonb_build_object('command_id',%s::text,'status',%s::text))",(str(command_id),final))
        r=db.execute("SELECT id,idempotency_key,actor,mode,action,deck,value_json,status,accepted_at,executed_at,result_json,readback_json FROM dj_commands WHERE id=%s",(str(command_id),)).fetchone()
    return r,result
