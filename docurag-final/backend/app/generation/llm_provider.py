"""LLM/VLM provider abstraction for Anthropic Claude and Ollama."""
from abc import ABC, abstractmethod
import base64, mimetypes, time
from app.config import get_settings
class Provider(ABC):
    @abstractmethod
    def generate(self, system: str, prompt: str, images: list[str]|None=None) -> str: ...
    def vision_caption(self,path: str)->str: return self.generate("Describe document figures with visible numbers and trends.","Caption this figure accurately.",[path])
class AnthropicProvider(Provider):
    def __init__(self):
        import anthropic; s=get_settings(); self.client=anthropic.Anthropic(api_key=s.anthropic_api_key, timeout=s.llm_timeout_seconds); self.model=s.anthropic_model
    def generate(self,system,prompt,images=None):
        content=[{"type":"text","text":prompt}]
        for p in images or []:
            data=base64.b64encode(open(p,"rb").read()).decode(); media=mimetypes.guess_type(p)[0] or "image/png"
            content.insert(0,{"type":"image","source":{"type":"base64","media_type":media,"data":data}})
        for attempt in range(get_settings().llm_max_retries+1):
            try:
                r=self.client.messages.create(model=self.model,max_tokens=1200,system=system,messages=[{"role":"user","content":content}]); return "".join(getattr(x,"text","") for x in r.content)
            except Exception:
                if attempt>=get_settings().llm_max_retries: raise
                time.sleep(2**attempt)
class OllamaProvider(Provider):
    def __init__(self):
        from ollama import Client; s=get_settings(); self.client=Client(host=s.ollama_url,timeout=s.llm_timeout_seconds); self.model=s.ollama_model
    def generate(self,system,prompt,images=None):
        msg={"role":"user","content":prompt};
        if images: msg["images"]=[base64.b64encode(open(p,"rb").read()).decode() for p in images]
        r=self.client.chat(model=self.model,messages=[{"role":"system","content":system},msg]); return r["message"]["content"]
def get_provider()->Provider:
    s=get_settings(); return AnthropicProvider() if s.llm_provider=="anthropic" and s.anthropic_api_key else OllamaProvider()
