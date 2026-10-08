"""Application configuration for DocuRAG."""
from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Strongly typed application settings loaded from environment variables."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    app_name: str = "DocuRAG"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 3000
    vite_api_base_url: str = "http://localhost:8000"
    api_key: str | None = None
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])
    max_upload_mb: int = Field(default=50, ge=1, le=1024)
    allowed_upload_extensions: list[str] = Field(default_factory=lambda: ["pdf", "png", "jpg", "jpeg"])
    data_dir: str = "./data"
    raw_data_dir: str = "./data/raw"
    image_data_dir: str = "./data/images"
    index_data_dir: str = "./data/index"
    database_url: str = "sqlite:///./data/index/docurag.db"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_text_collection: str = "docurag_text"
    qdrant_image_collection: str = "docurag_images"
    text_embedding_model: str = "nemotron-3-embed-1b"
    image_embedding_model: str = "nvidia/nv-clip-v1"
    reranker_model: str = "nvidia/llama-nemotron-rerank-1b-v2"
    model_cache_dir: str = "./models"
    device: Literal["cpu", "cuda", "auto"] = "cpu"
    ocr_engine: Literal["paddleocr", "pytesseract"] = "paddleocr"
    enable_reranker: bool = True
    enable_query_rewrite: bool = False
    retrieval_top_k: int = Field(default=20, ge=1, le=100)
    rerank_top_k: int = Field(default=5, ge=1, le=50)
    rrf_k: int = Field(default=60, ge=1)
    llm_provider: Literal["nvidia", "ollama"] = "nvidia"
    nvidia_api_key: str | None = None
    nvidia_model: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    nvidia_vision_model: str = "meta/llama-3.2-90b-vision-instruct"
    llm_timeout_seconds: int = Field(default=60, ge=1)
    llm_max_retries: int = Field(default=3, ge=0, le=10)
    query_rate_limit_per_minute: int = Field(default=30, ge=1)
    log_level: str = "INFO"
    log_json: bool = True
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str): return [x.strip() for x in value.split(",") if x.strip()]
        if isinstance(value, list): return [str(x).strip() for x in value if str(x).strip()]
        raise ValueError("cors_origins must be a comma-separated string or list")
    @field_validator("allowed_upload_extensions", mode="before")
    @classmethod
    def parse_extensions(cls, value: object) -> list[str]:
        if isinstance(value, str): return [x.strip().lower().lstrip(".") for x in value.split(",") if x.strip()]
        if isinstance(value, list): return [str(x).strip().lower().lstrip(".") for x in value if str(x).strip()]
        raise ValueError("allowed_upload_extensions must be a comma-separated string or list")
    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton application settings instance."""
    return Settings()
