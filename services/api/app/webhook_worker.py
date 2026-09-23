import os,time,json,hmac,hashlib,urllib.request,urllib.error
from app.db import conn
MAX_ATTEMPTS=int(os.getenv("WEBHOOK_MAX_ATTEMPTS","6"))
POLL=float(os.getenv("WEBHOOK_POLL_SECONDS","2"))
def sign(secret,body): return hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
def tick():
 with conn() as c:
  events=c.execute("SELECT id,event_type,subject_type,subject_id,correlation_id,payload,attempts FROM webhook_outbox WHERE status='pending' AND next_attempt_at<=now() ORDER BY created_at LIMIT 25 FOR UPDATE SKIP LOCKED").fetchall()
  for e in events:
   domain=e[1].split('.',1)[0]
   subs=c.execute("SELECT endpoint,secret_ref FROM webhook_subscriptions WHERE enabled=true AND domain=%s",(domain,)).fetchall()
   if not subs:
    c.execute("UPDATE webhook_outbox SET status='delivered',delivered_at=now() WHERE id=%s",(e[0],)); continue
   body=json.dumps({"event_id":str(e[0]),"event_type":e[1],"source":"djone","subject_type":e[2],"subject_id":e[3],"correlation_id":e[4],"payload":e[5],"schema_version":"1"} ,default=str,separators=(',',':')).encode()
   failures=[]
   for endpoint,secret_ref in subs:
    secret=os.getenv(secret_ref,"")
    if not secret: failures.append((endpoint,"secret_ref_unresolved")); continue
    req=urllib.request.Request(endpoint,data=body,method="POST",headers={"Content-Type":"application/json","X-DJONE-Event-ID":str(e[0]),"X-DJONE-Signature":"sha256="+sign(secret,body)})
    try:
     with urllib.request.urlopen(req,timeout=5) as r:
      if not 200<=r.status<300: failures.append((endpoint,f"http_{r.status}"))
    except Exception as ex: failures.append((endpoint,type(ex).__name__))
   if not failures:
    c.execute("UPDATE webhook_outbox SET status='delivered',delivered_at=now() WHERE id=%s",(e[0],))
   else:
    attempts=e[6]+1
    if attempts>=MAX_ATTEMPTS:
     for endpoint,err in failures: c.execute("INSERT INTO webhook_dead_letters(outbox_id,event_type,endpoint,attempts,last_error,payload) VALUES(%s,%s,%s,%s,%s,%s::jsonb)",(e[0],e[1],endpoint,attempts,err,json.dumps(e[5])))
     c.execute("UPDATE webhook_outbox SET status='dead_letter',attempts=%s WHERE id=%s",(attempts,e[0]))
    else:
     delay=min(300,2**attempts)
     c.execute("UPDATE webhook_outbox SET attempts=%s,next_attempt_at=now()+(%s || ' seconds')::interval WHERE id=%s",(attempts,delay,e[0]))
if __name__=="__main__":
 while True:
  try: tick()
  except Exception as e: print("worker_error",type(e).__name__,flush=True)
  time.sleep(POLL)
