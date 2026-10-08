# DocuRAG: Multimodal Retrieval-Augmented Generation

DocuRAG is an advanced Multimodal Retrieval-Augmented Generation (RAG) application that allows you to upload, index, and intelligently query your PDF documents and images. 

By leveraging **NVIDIA NIM** (NVIDIA Inference Microservices) APIs, **Qdrant** for vector storage, and **Pydantic Logfire** for comprehensive observability, DocuRAG provides highly accurate, grounded answers to complex questions over your data.

---

## 🌟 Key Features

* **Multimodal Ingestion**: Upload PDFs and images. The ingestion pipeline extracts text, crops figures/tables, and uses vision models to caption complex visual data.
* **Hybrid Retrieval Strategy**: Combines dense vector search (Qdrant) with sparse keyword search (BM25), merged using Reciprocal Rank Fusion (RRF) for unparalleled retrieval accuracy.
* **Advanced Reranking**: Uses NVIDIA NIM cross-encoder reranking to prioritize the most relevant document chunks before generation.
* **Fully Grounded Generation**: Instructs the LLM to strictly base answers on retrieved context.
* **Complete Observability**: Integrated with Pydantic Logfire, allowing real-time tracing of LLM latency, chunk ingestion, and retrieval pipeline performance.

---

## 🏗️ System Architecture

1. **Frontend (React/Vite/Tailwind)**: A responsive chat UI where users can upload documents, ask queries, and view the precise source snippets (text or cropped images) cited by the model.
2. **Backend (FastAPI)**: Orchestrates the RAG pipeline asynchronously.
3. **Database (SQLite)**: Stores document metadata, chunk text, and ingestion status.
4. **Vector Database (Qdrant)**: Runs locally via Docker to persist highly-dimensional text and image embeddings.
5. **NVIDIA NIM Models**:
   - *Text Embedding*: `nvidia/nemotron-3-embed-1b`
   - *Image Embedding*: `nvidia/llama-nemotron-embed-vl-1b-v2`
   - *Reranker*: `nvidia/llama-nemotron-rerank-1b-v2`
   - *Generator LLM*: `nvidia/nemotron-3-ultra-550b-a55b`
   - *Vision LLM*: `meta/llama-3.2-90b-vision-instruct`

---

## 🚀 Setup Guide

### 1. Prerequisites
- Python 3.10+
- Node.js (for the frontend)
- Docker Desktop (for running the local Qdrant database)
- An **NVIDIA API Key** (to access NIM models)
- A **Pydantic Logfire Token** (for observability)

### 2. Environment Variables
Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```
Populate `.env` with your actual tokens and paths:
```env
# NVIDIA NIM (Required)
NVIDIA_API_KEY=nvapi-...

# Pydantic Logfire (Required for observability)
LOGFIRE_TOKEN=pylf_...

# Qdrant Database
QDRANT_URL=http://localhost:6333

# Models Configuration
TEXT_EMBEDDING_MODEL=nvidia/nemotron-3-embed-1b
IMAGE_EMBEDDING_MODEL=nvidia/llama-nemotron-embed-vl-1b-v2
RERANKER_MODEL=nvidia/llama-nemotron-rerank-1b-v2
NVIDIA_MODEL=nvidia/nemotron-3-ultra-550b-a55b
NVIDIA_VISION_MODEL=meta/llama-3.2-90b-vision-instruct
```

### 3. Start Qdrant Vector Database
Use Docker Compose to spin up the local Qdrant database:
```bash
docker-compose up -d
```
*Note: This will expose Qdrant on port 6333 and create a local persistent volume for your vectors.*

### 4. Setup Backend (FastAPI)
Navigate to the root directory and create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
```
Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```
Start the FastAPI server:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*The backend will automatically create the SQLite database (`docurag.db`) and synchronize the necessary collections in Qdrant.*

### 5. Setup Frontend (React)
Open a new terminal window, navigate to the frontend directory, and install dependencies:
```bash
cd frontend
npm install
```
Start the development server:
```bash
npm run dev
```
The application UI will now be accessible at `http://localhost:5173`.

---

## 🧠 How the RAG Pipeline Works

1. **Ingestion (`app/ingestion/`)**: When a PDF is dropped into the UI, PyMuPDF parses the document. It slices text into boundary-aware chunks and crops detected figures. The `meta/llama-3.2-90b-vision-instruct` model captions the figures.
2. **Embedding (`app/indexing/`)**: Text chunks and figure captions are embedded via `nemotron-3-embed-1b`. Standalone images are embedded multimodally via `llama-nemotron-embed-vl-1b-v2`. Vectors are stored in Qdrant.
3. **Retrieval (`app/retrieval/`)**: Upon querying, the user's prompt is rewritten to optimize vector search. `HybridRetriever` runs a dense vector search in Qdrant and a sparse keyword search using BM25. The results are merged.
4. **Reranking**: The merged chunks are submitted to the `llama-nemotron-rerank-1b-v2` cross-encoder API, which precisely scores and sorts the chunks by relevance.
5. **Generation (`app/generation/`)**: The top chunks are structured into an augmented prompt and fed to `nemotron-3-ultra-550b-a55b` to generate a final answer, guaranteeing citations map strictly to the context. 
6. **Observability**: Every single function block above is wrapped in `@logfire.instrument`, allowing developers to view exact latency, exceptions, and token usage in the Pydantic Logfire dashboard.
