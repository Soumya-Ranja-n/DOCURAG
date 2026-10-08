"""Optional NIM cross-encoder reranking."""
import requests
from app.config import get_settings

import logfire
@logfire.instrument("rerank")
def rerank(query,items,limit=5):
    if not items:return []
    s = get_settings()
    if not s.enable_reranker:return [(x,1.0/(i+1)) for i,x in enumerate(items[:limit])]
    
    url = f"https://ai.api.nvidia.com/v1/retrieval/{s.reranker_model}/reranking"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {s.nvidia_api_key}"
    }
    data = {
        "model": s.reranker_model,
        "query": {"text": query},
        "passages": [{"text": x.get("text", "")} for x in items],
        "truncate": "END"
    }
    
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    rankings = resp.json().get("rankings", [])
    
    # rank.index is the original passage index
    ordered_items = []
    for rank in rankings[:limit]:
        idx = rank["index"]
        score = rank.get("logit", 0.0) # Might be logit or score depending on API
        ordered_items.append((items[idx], float(score)))
        
    return ordered_items
