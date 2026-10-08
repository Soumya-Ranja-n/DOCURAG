"""Lazy-loaded NIM text embedding model."""
from app.config import get_settings

class TextEmbedder:
    def ensure_loaded(self):
        pass # No local model to load for NIM
    
    import logfire
    @logfire.instrument("TextEmbedder.embed")
    def embed(self,texts:list[str]):
        import openai
        s = get_settings()
        client = openai.OpenAI(api_key=s.nvidia_api_key, base_url="https://integrate.api.nvidia.com/v1")
        response = client.embeddings.create(
            input=texts,
            model=s.text_embedding_model,
            encoding_format="float"
        )
        return [data.embedding for data in response.data]
