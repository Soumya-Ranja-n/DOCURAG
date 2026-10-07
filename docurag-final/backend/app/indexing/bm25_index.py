"""Persistent BM25 keyword index."""
import json,re
from pathlib import Path
from app.config import get_settings
class BM25Index:
    def __init__(self): self.path=Path(get_settings().index_data_dir)/"bm25.json"; self.docs=json.loads(self.path.read_text()) if self.path.exists() else []
    def add(self,chunks,doc):
        self.docs=[d for d in self.docs if d["doc_id"]!=doc.id]
        self.docs += [{"chunk_id":c.id,"doc_id":doc.id,"doc_name":doc.name,"page":c.page,"type":c.type,"text":c.text,"image_path":c.image_path} for c in chunks]
    def save(self): self.path.write_text(json.dumps(self.docs))
    def search(self,q,limit=20,doc_ids=None):
        ds=[d for d in self.docs if not doc_ids or d["doc_id"] in doc_ids]
        if not ds:return []
        from rank_bm25 import BM25Okapi
        bm=BM25Okapi([re.findall(r"\w+",d["text"].lower()) for d in ds]); scores=bm.get_scores(re.findall(r"\w+",q.lower())); idx=sorted(range(len(ds)),key=lambda i:scores[i],reverse=True)[:limit]; return [(ds[i],float(scores[i])) for i in idx]
    def remove(self,doc_id): self.docs=[d for d in self.docs if d["doc_id"]!=doc_id]; self.save()
