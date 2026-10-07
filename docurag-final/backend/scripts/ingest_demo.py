"""Prepare local directories for the DocuRAG demo."""
from pathlib import Path
ROOT = Path("/app")
for directory in (ROOT/"data"/"raw", ROOT/"data"/"images", ROOT/"data"/"index"):
    directory.mkdir(parents=True, exist_ok=True); print(f"Ready: {directory}")
print("DocuRAG demo storage is ready. Full ingestion begins in Phase 2.")
