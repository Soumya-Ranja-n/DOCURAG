"""Background ingestion orchestration."""
from pathlib import Path
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.db import Document, Chunk, SessionLocal
from app.ingestion.pdf_parser import parse_pdf, parse_image
from app.ingestion.chunker import chunk_text
from app.ingestion.captioner import FigureCaptioner
from app.indexing.text_embedder import TextEmbedder
from app.indexing.image_embedder import ImageEmbedder
from app.indexing.vector_store import VectorStore
from app.indexing.bm25_index import BM25Index
from app.config import get_settings
class IngestionPipeline:
    def __init__(self): self.settings=get_settings()
    def run(self,doc_id: str):
        db:Session=SessionLocal(); doc=db.get(Document,doc_id)
        if not doc: db.close(); return
        try:
            doc.status="processing"; doc.progress=5; db.commit(); p=Path(doc.path)
            records,pages=(parse_pdf(str(p),self.settings.image_data_dir) if p.suffix.lower()==".pdf" else parse_image(str(p),self.settings.image_data_dir)); doc.page_count=pages; doc.progress=25; db.commit()
            chunks=[]; captioner=FigureCaptioner()
            for i,r in enumerate(records):
                text=r["text"]
                if r["type"]=="figure": text=captioner.caption(r["image_path"]); kind="figure_caption"
                else: kind=r["type"]
                if not text.strip(): continue
                chunks.extend(chunk_text(text,f"{doc_id}-{i}",r["page"],kind,r.get("image_path")))
            for c in chunks: db.add(Chunk(id=c.id,doc_id=doc_id,page=c.page,type=c.type,text=c.text,image_path=c.image_path))
            db.commit(); doc.progress=50; db.commit()
            TextEmbedder().ensure_loaded(); ImageEmbedder().ensure_loaded(); vs=VectorStore(); bm=BM25Index()
            vs.upsert_text(chunks,doc); vs.upsert_images(chunks,doc); bm.add(chunks,doc); bm.save(); doc.progress=95; db.commit(); doc.status="done"; doc.progress=100; db.commit()
        except Exception as exc:
            db.rollback(); doc=db.get(Document,doc_id); doc.status="failed"; doc.error=str(exc)[:2000]; db.commit()
        finally: db.close()
