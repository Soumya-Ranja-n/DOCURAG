"""Lazy-loaded NIM image embeddings."""
from app.config import get_settings
import requests, base64, mimetypes

class ImageEmbedder:
    def ensure_loaded(self):
        pass # No local model to load for NIM

    def _call_nim(self, input_data):
        s = get_settings()
        url = "https://integrate.api.nvidia.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {s.nvidia_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": s.image_embedding_model,
            "input": input_data,
            "input_type": "image" if isinstance(input_data, list) and str(input_data[0]).startswith("data:image") else "text",
            "encoding_format": "float"
        }
        # Try sending it as-is (standard OpenAI compatible)
        resp = requests.post(url, headers=headers, json={"model": s.image_embedding_model, "input": input_data, "encoding_format": "float"})
        if resp.status_code != 200:
            # NV-CLIP might need a specific multimodal payload
            resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return [d["embedding"] for d in resp.json()["data"]]

    import logfire
    @logfire.instrument("ImageEmbedder.embed_images")
    def embed_images(self, paths: list[str]):
        if not paths: return []
        inputs = []
        for p in paths:
            data = base64.b64encode(open(p, "rb").read()).decode()
            media = mimetypes.guess_type(p)[0] or "image/jpeg"
            # OpenAI / NIM standard multimodal image input format for embeddings is typically the data URI
            inputs.append(f"data:{media};base64,{data}")
        return self._call_nim(inputs)

    @logfire.instrument("ImageEmbedder.embed_query")
    def embed_query(self, text: str):
        return self._call_nim([text])[0]
