from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from app.db import conn
from app.security import authorize
import uuid
router=APIRouter(prefix="/v1/sessions",tags=["sessions"],dependencies=[Depends(authorize)])
class SessionIn(BaseModel):
 name:str="DJONE Session"
@router.post("",status_code=201)
def create(s:SessionIn):
 with conn() as c:
  r=c.execute("INSERT INTO dj_sessions(name,status) VALUES(%s,'active') RETURNING id,name,status,created_at",(s.name,)).fetchone()
 return {"id":str(r[0]),"name":r[1],"status":r[2],"created_at":r[3]}
@router.get("")
def list_sessions():
 with conn() as c: rows=c.execute("SELECT id,name,status,created_at,ended_at FROM dj_sessions ORDER BY created_at DESC LIMIT 100").fetchall()
 return {"items":[{"id":str(r[0]),"name":r[1],"status":r[2],"created_at":r[3],"ended_at":r[4]} for r in rows]}
@router.post("/{sid}/stop")
def stop(sid:str):
 with conn() as c:
  r=c.execute("UPDATE dj_sessions SET status='stopped',ended_at=now() WHERE id=%s RETURNING id,name,status,ended_at",(sid,)).fetchone()
 if not r: raise HTTPException(404,"session not found")
 return {"id":str(r[0]),"name":r[1],"status":r[2],"ended_at":r[3]}
