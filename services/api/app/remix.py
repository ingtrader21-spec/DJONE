from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import uuid, time

router=APIRouter(prefix="/v1/remix",tags=["remix"])
JOBS={}
class RemixRequest(BaseModel):
    source_path:str
    operation:Literal["stems","cover","repaint","arrange"]
    target_bpm:float|None=Field(default=None,ge=40,le=240)
    target_key:str|None=None
    style_prompt:str|None=None

@router.post("/jobs",status_code=202)
def create_job(r:RemixRequest):
    job={"id":str(uuid.uuid4()),"status":"queued","request":r.model_dump(),"created_at":int(time.time()),"runtime":"pending"}
    JOBS[job["id"]]=job
    return job

@router.get("/jobs/{job_id}")
def get_job(job_id:str):
    if job_id not in JOBS: raise HTTPException(404,"remix job not found")
    return JOBS[job_id]

@router.get("/capabilities")
def remix_capabilities():
    return {"operations":["stems","cover","repaint","arrange"],"demucs_runtime":False,"ace_step_runtime":False,"note":"API contract active; compute runtimes gated until installed/certified."}
