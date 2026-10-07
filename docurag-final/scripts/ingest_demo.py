"""Prepare local directories for the DocuRAG demo."""
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
for directory in (PROJECT_ROOT/"data"/"raw", PROJECT_ROOT/"data"/"images", PROJECT_ROOT/"data"/"index"):
    directory.mkdir(parents=True, exist_ok=True); print(f"Ready: {directory}")
print("DocuRAG demo storage is ready. Full document ingestion starts in Phase 2.")
