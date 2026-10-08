from fastapi import APIRouter
from app.config import get_settings
from app.models.db import init_db
import httpx
router=APIRouter(prefix="/api",tags=["system"])
@router.get("/health")
def health():
    s=get_settings(); services={"database":"ok"};
    try:
        if s.qdrant_url.startswith("http"):
            httpx.get(s.qdrant_url+"/healthz",timeout=2).raise_for_status(); services["qdrant"]="ok"
        else:
            services["qdrant"]="ok" # local qdrant
    except Exception as e: services["qdrant"]=f"unavailable: {e.__class__.__name__}"
    status="healthy" if services["qdrant"]=="ok" else "degraded"; return {"status":status,"service":s.app_name,"services":services,"dependencies":services}
@router.get("/metrics")
def metrics(): return {"service":"docurag","status":"ok"}
