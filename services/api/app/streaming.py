from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,HttpUrl
from app.db import conn
from app.security import authorize
router=APIRouter(prefix="/v1/streaming",tags=["streaming"],dependencies=[Depends(authorize)])
PROVIDERS={"spotify","youtube_music"}
class Ref(BaseModel):
 provider:str
 external_id:str
 title:str
 artist:str|None=None
 album:str|None=None
 url:str
 artwork_url:str|None=None
class Playback(BaseModel):
 provider:str
 external_id:str
 action:str="open"
@router.get("/providers")
def providers():
 return {"items":[{"id":"spotify","mode":"reference","download":False},{"id":"youtube_music","mode":"reference","download":False}]}
@router.post("/references",status_code=201)
def add(r:Ref):
 if r.provider not in PROVIDERS: raise HTTPException(422,"unsupported provider")
 with conn() as c:
  row=c.execute("""INSERT INTO streaming_tracks(provider,external_id,title,artist,album,url,artwork_url)
  VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(provider,external_id) DO UPDATE SET title=excluded.title,artist=excluded.artist,album=excluded.album,url=excluded.url,artwork_url=excluded.artwork_url,updated_at=now()
  RETURNING id,created_at,updated_at""",(r.provider,r.external_id,r.title,r.artist,r.album,r.url,r.artwork_url)).fetchone()
 return {"id":str(row[0]),**r.model_dump(),"created_at":row[1],"updated_at":row[2],"local_file":False}
@router.get("/references")
def search(q:str|None=None,provider:str|None=None,limit:int=100):
 limit=max(1,min(limit,500))
 with conn() as c:
  rows=c.execute("""SELECT id,provider,external_id,title,artist,album,url,artwork_url,created_at,updated_at FROM streaming_tracks
  WHERE (%s::text IS NULL OR provider=%s::text) AND (%s::text IS NULL OR title ILIKE '%%'||%s::text||'%%' OR artist ILIKE '%%'||%s::text||'%%' OR album ILIKE '%%'||%s::text||'%%')
  ORDER BY updated_at DESC LIMIT %s""",(provider,provider,q,q,q,q,limit)).fetchall()
 keys=["id","provider","external_id","title","artist","album","url","artwork_url","created_at","updated_at"]
 return {"items":[dict(zip(keys,[str(r[0])]+list(r[1:]))) for r in rows],"count":len(rows)}
@router.post("/playback")
def playback(p:Playback):
 if p.provider not in PROVIDERS: raise HTTPException(422,"unsupported provider")
 if p.action!="open": raise HTTPException(422,"only provider-authorized open playback is enabled")
 with conn() as c:
  r=c.execute("SELECT url FROM streaming_tracks WHERE provider=%s AND external_id=%s",(p.provider,p.external_id)).fetchone()
 if not r: raise HTTPException(404,"streaming reference not found")
 return {"provider":p.provider,"external_id":p.external_id,"action":"open","url":r[0],"download":False}
