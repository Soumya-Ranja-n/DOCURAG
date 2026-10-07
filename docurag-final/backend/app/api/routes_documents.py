"""Document upload, status, listing, deletion, and image serving."""
import os, uuid, mimetypes
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.config import get_settings
from app.models.db import Document, Chunk, SessionLocal
from app.models.schemas import DocumentOut
from app.ingestion.pipeline import IngestionPipeline
from app.indexing.vector_store import VectorStore
from app.indexing.bm25_index import BM25Index
router=APIRouter(prefix="/api/documents",tags=["documents"])
@router.post("/upload",response_model=DocumentOut)
async def upload(background_tasks:BackgroundTasks,file:UploadFile=File(...)):
    s=get_settings(); ext=Path(file.filename or "").suffix.lower().lstrip(".")
    if ext not in s.allowed_upload_extensions: raise HTTPException(400,"Unsupported file type")
    data=await file.read()
    if len(data)>s.max_upload_bytes: raise HTTPException(413,f"Maximum upload size is {s.max_upload_mb} MB")
    did=str(uuid.uuid4()); path=Path(s.raw_data_dir)/f"{did}.{ext}"; path.write_bytes(data)
    db=SessionLocal(); d=Document(id=did,name=file.filename or path.name,path=str(path),content_type=mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream",size_bytes=len(data)); db.add(d); db.commit(); db.refresh(d); db.close(); background_tasks.add_task(IngestionPipeline().run,did); return d
@router.get("",response_model=list[DocumentOut])
def list_documents():
    db=SessionLocal(); out=db.query(Document).order_by(Document.created_at.desc()).all(); db.close(); return out
@router.get("/{doc_id}",response_model=DocumentOut)
def get_document(doc_id:str):
    db=SessionLocal(); d=db.get(Document,doc_id); db.close();
    if not d: raise HTTPException(404,"Document not found")
    return d
@router.delete("/{doc_id}")
def delete_document(doc_id:str):
    db=SessionLocal(); d=db.get(Document,doc_id)
    if not d: db.close(); raise HTTPException(404,"Document not found")
    path=d.path; db.delete(d); db.commit(); db.close()
    try: VectorStore().delete_doc(doc_id)
    except Exception: pass
    try: BM25Index().remove(doc_id)
    except Exception: pass
    if os.path.exists(path): os.remove(path)
    return {"deleted":doc_id}
@router.get("/{doc_id}/images/{name}")
def document_image(doc_id:str,name:str):
    p=Path(get_settings().image_data_dir)/name
    if not p.exists(): raise HTTPException(404,"Image not found")
    return FileResponse(p)
