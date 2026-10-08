"""DocuRAG FastAPI application."""
from dotenv import load_dotenv
load_dotenv("../.env")
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from typing import AsyncIterator
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from app.api.routes_documents import router as documents_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_health import router as health_router
from app.api.routes_query import router as query_router
from app.config import get_settings
from app.models.db import init_db
from app.utils.logging import configure_logging
logger=logging.getLogger("docurag")
def prep():
 s=get_settings()
 for d in (s.data_dir,s.raw_data_dir,s.image_data_dir,s.index_data_dir,s.model_cache_dir): Path(d).mkdir(parents=True,exist_ok=True)
@asynccontextmanager
async def lifespan(app:FastAPI)->AsyncIterator[None]:
 s=get_settings(); configure_logging(s); prep(); init_db(); logger.info("DocuRAG started"); yield; logger.info("DocuRAG stopped")
s=get_settings(); app=FastAPI(title=s.app_name,version=__version__,docs_url="/docs",redoc_url="/redoc",openapi_url="/openapi.json",lifespan=lifespan)
import logfire
logfire.configure(metrics=False)

app.add_middleware(CORSMiddleware,allow_origins=s.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.middleware("http")
async def timing(request:Request,call_next):
 t=perf_counter(); response=await call_next(request); response.headers["X-Response-Time-Ms"]=str(round((perf_counter()-t)*1000,2)); return response
@app.get("/")
def root(): return {"service":s.app_name,"version":s.app_version,"docs":"/docs","health":"/api/health"}
app.include_router(health_router); app.include_router(documents_router); app.include_router(query_router); app.include_router(feedback_router)
