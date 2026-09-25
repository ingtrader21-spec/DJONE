import os
from fastapi import Header, HTTPException

def authorize(authorization: str | None = Header(default=None)):
    env=os.getenv("DJONE_ENV","development")
    token=os.getenv("DJONE_API_TOKEN","")
    if not token:
        if env=="staging": raise HTTPException(503,"DJONE_API_TOKEN is required in staging")
        return
    if authorization != f"Bearer {token}": raise HTTPException(401,"unauthorized")
