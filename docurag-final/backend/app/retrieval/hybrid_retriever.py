"""Hybrid dense + BM25 + CLIP retrieval with reciprocal rank fusion."""
from app.config import get_settings
from app.indexing.vector_store import VectorStore
from app.indexing.bm25_index import BM25Index
from app.retrieval.query_rewriter import QueryRewriter
class HybridRetriever:
    def retrieve(self,q:str,top_k:int=20,doc_ids=None):
        vs=VectorStore(); bm=BM25Index(); fused={}; meta={}
        for query in QueryRewriter().rewrite(q):
            dense=vs.search_text(query,top_k,doc_ids)
            for rank,p in enumerate(dense,1): fused[p.id]=fused.get(p.id,0)+1/(get_settings().rrf_k+rank); meta[p.id]=p.payload
            for rank,(d,_) in enumerate(bm.search(query,top_k,doc_ids),1): fused[d["chunk_id"]]=fused.get(d["chunk_id"],0)+1/(get_settings().rrf_k+rank); meta[d["chunk_id"]]=d
            try:
                for rank,p in enumerate(vs.search_image(query,top_k),1): fused[p.id]=fused.get(p.id,0)+1/(get_settings().rrf_k+rank); meta[p.id]=p.payload
            except Exception: pass
        ids=sorted(fused,key=fused.get,reverse=True)[:top_k]; return [{**meta[i],"rrf_score":fused[i]} for i in ids]
