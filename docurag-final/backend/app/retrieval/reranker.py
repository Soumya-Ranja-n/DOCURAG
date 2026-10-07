"""Optional BGE cross-encoder reranking."""
from functools import lru_cache
from app.config import get_settings
@lru_cache(maxsize=1)
def get_reranker():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(get_settings().reranker_model,device=get_settings().device if get_settings().device!="auto" else None)
def rerank(query,items,limit=5):
    if not items:return []
    if not get_settings().enable_reranker:return [(x,1.0/(i+1)) for i,x in enumerate(items[:limit])]
    scores=get_reranker().predict([(query,x["text"]) for x in items]); order=sorted(range(len(items)),key=lambda i:float(scores[i]),reverse=True)[:limit]; return [(items[i],float(scores[i])) for i in order]
