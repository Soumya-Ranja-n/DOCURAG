"""Qdrant collections and hybrid vector search."""
from app.config import get_settings
from app.indexing.text_embedder import TextEmbedder
from app.indexing.image_embedder import ImageEmbedder
class VectorStore:
    def __init__(self):
        from qdrant_client import QdrantClient
        s=get_settings(); self.s=s
        if s.qdrant_url.startswith("http"):
            self.client=QdrantClient(url=s.qdrant_url,api_key=s.qdrant_api_key)
        else:
            import os
            os.makedirs(s.qdrant_url, exist_ok=True)
            self.client=QdrantClient(path=s.qdrant_url)
        self._ensure()
    def _ensure(self):
        from qdrant_client import models
        size=len(TextEmbedder().embed(["dimension probe"])[0])
        for name,dim in [(self.s.qdrant_text_collection,size),(self.s.qdrant_image_collection,512)]:
            try:self.client.get_collection(name)
            except Exception:self.client.create_collection(name, vectors_config=models.VectorParams(size=dim,distance=models.Distance.COSINE))
    import logfire
    @logfire.instrument("VectorStore.upsert_text")
    def upsert_text(self,chunks,doc):
        if not chunks: return
        from qdrant_client import models
        vec=TextEmbedder().embed([c.text for c in chunks]); self.client.upsert(self.s.qdrant_text_collection,[models.PointStruct(id=c.id,vector=v,payload={"chunk_id":c.id,"doc_id":doc.id,"doc_name":doc.name,"page":c.page,"type":c.type,"text":c.text,"image_path":c.image_path}) for c,v in zip(chunks,vec)])
    
    @logfire.instrument("VectorStore.upsert_images")
    def upsert_images(self,chunks,doc):
        from qdrant_client import models
        imgs=[c for c in chunks if c.image_path]
        if not imgs:return
        vec=ImageEmbedder().embed_images([c.image_path for c in imgs]); self.client.upsert(self.s.qdrant_image_collection,[models.PointStruct(id=c.id,vector=v,payload={"chunk_id":c.id,"doc_id":doc.id,"doc_name":doc.name,"page":c.page,"type":c.type,"text":c.text,"image_path":c.image_path}) for c,v in zip(imgs,vec)])
    
    @logfire.instrument("VectorStore.search_text")
    def search_text(self,q,limit=20,doc_ids=None):
        from qdrant_client import models
        filt=models.Filter(must=[models.FieldCondition(key="doc_id",match=models.MatchAny(any=doc_ids))]) if doc_ids else None
        return self.client.query_points(self.s.qdrant_text_collection,query=TextEmbedder().embed([q])[0],limit=limit,query_filter=filt).points
    def search_image(self,q,limit=20): return self.client.query_points(self.s.qdrant_image_collection,query=ImageEmbedder().embed_query(q),limit=limit).points
    def delete_doc(self,doc_id):
        from qdrant_client import models
        for c in [self.s.qdrant_text_collection,self.s.qdrant_image_collection]: self.client.delete(c,models.Filter(must=[models.FieldCondition(key="doc_id",match=models.MatchValue(value=doc_id))]))
