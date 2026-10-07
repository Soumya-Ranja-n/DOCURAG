"""Lazy-loaded CLIP image/text embeddings."""
from functools import lru_cache
from app.config import get_settings
@lru_cache(maxsize=1)
def get_clip():
    from transformers import CLIPProcessor, CLIPModel
    s=get_settings(); return CLIPModel.from_pretrained(s.image_embedding_model,cache_dir=s.model_cache_dir), CLIPProcessor.from_pretrained(s.image_embedding_model,cache_dir=s.model_cache_dir)
class ImageEmbedder:
    def ensure_loaded(self): get_clip()
    def embed_images(self,paths:list[str]):
        from PIL import Image
        model,proc=get_clip(); imgs=[Image.open(p).convert("RGB") for p in paths]; inputs=proc(images=imgs,return_tensors="pt",padding=True); vec=model.get_image_features(**inputs); vec=vec/vec.norm(dim=-1,keepdim=True); return vec.detach().cpu().tolist()
    def embed_query(self,text:str):
        model,proc=get_clip(); inputs=proc(text=[text],return_tensors="pt",padding=True); vec=model.get_text_features(**inputs); vec=vec/vec.norm(dim=-1,keepdim=True); return vec[0].detach().cpu().tolist()
