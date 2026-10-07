"""Lazy-loaded BGE text embedding model."""
from functools import lru_cache
from app.config import get_settings
@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer
    s=get_settings(); return SentenceTransformer(s.text_embedding_model,cache_folder=s.model_cache_dir,device=s.device if s.device!="auto" else None)
class TextEmbedder:
    def ensure_loaded(self): get_model()
    def embed(self,texts:list[str]): return get_model().encode(texts,normalize_embeddings=True).tolist()
