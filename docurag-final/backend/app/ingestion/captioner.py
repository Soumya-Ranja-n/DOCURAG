"""Vision captioning with provider abstraction and hash cache."""
import hashlib, json
from pathlib import Path
from app.config import get_settings
from app.generation.llm_provider import get_provider
class FigureCaptioner:
    def __init__(self):
        self.cache=Path(get_settings().index_data_dir)/"caption_cache.json"; self.data=json.loads(self.cache.read_text()) if self.cache.exists() else {}
    def caption(self,path: str) -> str:
        raw=Path(path).read_bytes(); h=hashlib.sha256(raw).hexdigest()
        if h in self.data: return self.data[h]
        try: value=get_provider().vision_caption(path)
        except Exception: value="Figure/image extracted from the document."
        self.data[h]=value; self.cache.write_text(json.dumps(self.data,indent=2)); return value
