"""LLM/VLM provider abstraction for Anthropic Claude and Ollama."""
from abc import ABC, abstractmethod
import base64, mimetypes, time
from app.config import get_settings
class Provider(ABC):
    @abstractmethod
    def generate(self, system: str, prompt: str, images: list[str]|None=None) -> str: ...
    def vision_caption(self,path: str)->str: return self.generate("Describe document figures with visible numbers and trends.","Caption this figure accurately.",[path])

class NvidiaProvider(Provider):
    def __init__(self):
        import openai; s=get_settings(); self.client=openai.OpenAI(api_key=s.nvidia_api_key, base_url="https://integrate.api.nvidia.com/v1", timeout=s.llm_timeout_seconds)
    def generate(self,system,prompt,images=None):
        s=get_settings()
        model = s.nvidia_vision_model if images else s.nvidia_model
        content=[{"type":"text","text":prompt}]
        for p in images or []:
            data=base64.b64encode(open(p,"rb").read()).decode(); media=mimetypes.guess_type(p)[0] or "image/png"
            content.insert(0,{"type":"image_url","image_url":{"url":f"data:{media};base64,{data}"}})
        for attempt in range(s.llm_max_retries+1):
            try:
                r=self.client.chat.completions.create(model=model,max_tokens=1200,messages=[{"role":"system","content":system},{"role":"user","content":content}]); return r.choices[0].message.content
            except Exception:
                if attempt>=s.llm_max_retries: raise
                time.sleep(2**attempt)
def get_provider()->Provider:
    return NvidiaProvider()
