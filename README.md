# DocumentAssistant

A fully local AI document assistant. Upload your PDFs, DOCX, or Markdown files and ask questions — answers are grounded in your documents with source citations. Everything runs on your machine, no cloud API needed.

## Features

- **100% Local** — No data leaves your machine. Uses llama.cpp + GGUF models.
- **RAG Pipeline** — Hybrid search (BM25 + FAISS vector) with reranking for accurate retrieval.
- **Source Citations** — Every answer references the document and page it came from.
- **Upload & Auto-Index** — Drop files in the UI or via API; they're indexed immediately.
- **React Chat UI** — Clean, responsive interface with markdown rendering.
- **Cross-Platform** — macOS (Intel + Apple Silicon) and Windows.

## Quick Start

### 1. Setup (one-time)

```bash
chmod +x scripts/setup.sh scripts/start.sh
./scripts/setup.sh
```

This will:
- Download llama.cpp binary for your platform
- Create Python virtual environment and install dependencies
- Install ChatUI (npm packages)
- Create required directories
- Download the default model (~2.5GB) if not present

### 2. Start

```bash
./scripts/start.sh
```

This launches three services and opens your browser automatically:

| Service | URL | Purpose |
|---------|-----|---------|
| **ChatUI** | http://127.0.0.1:3000 | React chat interface (recommended) |
| **API Backend** | http://127.0.0.1:8080 | FastAPI server (RAG + upload + ingest) |
| **llama.cpp** | http://127.0.0.1:8081 | LLM inference server |

Press `Ctrl+C` to stop all services.

### 3. Use

1. Open http://127.0.0.1:3000 (opens automatically)
2. Click the 📎 button to upload your documents (PDF, DOCX, MD)
3. Ask questions — the assistant answers using your documents
4. Toggle between **RAG** mode (document-grounded) and **Chat** mode (direct LLM)

## How It Works

### Chat Flow (RAG Query)

```
User asks question in ChatUI
        │
        ▼
ChatUI → POST /api/query → FastAPI Backend
        │
        ▼
   Hybrid Search
   ├── BM25 (keyword matching, weight: 0.4)
   └── FAISS (semantic similarity, weight: 0.6)
        │
        ▼
   Reranker (top 5 → top 3 most relevant chunks)
        │
        ▼
   Prompt Builder (question + context chunks → structured prompt)
        │
        ▼
   llama.cpp Server → Qwen3.5-4B generates answer
        │
        ▼
   Citation Extractor (attaches source doc + page references)
        │
        ▼
   Response returned to ChatUI with answer + sources
```

### Document Upload Flow

```
User uploads file(s) via ChatUI (📎 button)
        │
        ▼
ChatUI → POST /api/upload (multipart form) → FastAPI Backend
        │
        ▼
   Save file(s) to documents/source/
        │
        ▼
   Document Loader (PDF/DOCX/MD → raw text with metadata)
        │
        ▼
   Chunker (heading-based splitting, 512 tokens, 50 overlap)
        │
        ▼
   Embedding Service (all-MiniLM-L6-v2 → 384-dim vectors)
        │
        ▼
   Index Builder
   ├── FAISS index (vector similarity search)
   └── BM25 index (keyword search)
        │
        ▼
   Indexes saved to data/indexes/ (persist across restarts)
        │
        ▼
   Response: "Indexed N chunks from filename.pdf"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (LLM connection + index status) |
| POST | `/api/query` | RAG query — answers grounded in documents with citations |
| POST | `/api/chat` | Direct chat with LLM (no document context) |
| POST | `/api/upload` | Upload file(s), save to `documents/source/`, auto-index |
| POST | `/api/ingest` | Re-index all documents in `documents/source/` |
| GET | `/api/status` | System status (model info, index state) |

### Examples

```bash
# Query your documents
curl -X POST http://127.0.0.1:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the document say about revenue?"}'

# Upload a document
curl -X POST http://127.0.0.1:8080/api/upload \
  -F "files=@report.pdf"

# Re-index all documents
curl -X POST http://127.0.0.1:8080/api/ingest

# Health check
curl http://127.0.0.1:8080/health
```

## Project Structure

```
DocumentAssistant/
├── ChatUI/                 # React frontend (Vite + React)
│   ├── src/
│   │   ├── api/            # API client (health, query, chat, upload)
│   │   ├── components/     # Header, ChatArea, Message, InputBar
│   │   └── styles/         # Global CSS (light/dark theme)
│   ├── package.json
│   └── vite.config.js      # Dev proxy to backend :8080
│
├── backend/                # Python backend
│   ├── api/                # FastAPI server + routes
│   ├── chunking/           # Text splitting (heading-based, recursive)
│   ├── document/           # Loaders (PDF, DOCX, Markdown)
│   ├── embedding/          # Sentence-transformers (all-MiniLM-L6-v2)
│   ├── llm/                # llama.cpp client + prompt templates
│   ├── rag/                # RAG pipeline + citation extraction
│   ├── retrieval/          # FAISS, BM25, hybrid search, reranker
│   └── utils/              # Settings loader, logging
│
├── config/                 # YAML configuration
│   ├── app.yaml            # Server host/port, paths, logging
│   ├── model.yaml          # Model path, llama.cpp settings
│   └── rag.yaml            # Chunking, embedding, retrieval, generation settings
│
├── data/                   # Runtime data (gitignored)
│   ├── chunks/             # Serialized chunks
│   ├── embeddings/         # Cached embeddings
│   ├── indexes/            # FAISS + BM25 indexes
│   └── cache/              # General cache
│
├── documents/
│   └── source/             # Your uploaded/ingested documents go here
│
├── models/                 # GGUF model files (gitignored)
│   └── gguf/               # Qwen3.5-4B-Q4_K_M.gguf
│
├── scripts/                # Setup & start scripts
│   ├── setup.sh / .bat     # One-time installation
│   └── start.sh / .bat     # Launch all services
│
├── third_party/            # Pre-built binaries (gitignored)
│   └── llama_cpp/          # llama-server, llama-cli, etc.
│
├── logs/                   # Application logs (gitignored)
├── requirements.txt        # Python dependencies
└── .gitignore
```

## Configuration

All config lives in `config/`:

### app.yaml
```yaml
app:
  host: 127.0.0.1
  port: 8080
documents:
  source_dir: documents/source
```

### model.yaml
```yaml
model:
  name: Qwen3.5-4B
  path: models/gguf/Qwen_Qwen3.5-4B-Q4_K_M.gguf
llama_cpp:
  host: 127.0.0.1
  port: 8081
  context_length: 8192
```

### rag.yaml
```yaml
chunking:
  method: heading          # heading-based splitting
  chunk_size: 512
  chunk_overlap: 50
retrieval:
  top_k: 5                 # candidates from hybrid search
  bm25_weight: 0.4         # keyword relevance
  vector_weight: 0.6       # semantic relevance
  rerank: true
  rerank_top_k: 3          # final chunks sent to LLM
rag:
  temperature: 0.7
  max_tokens: 1024
```

## Requirements

- **Python** 3.10+
- **Node.js** 18+ (for ChatUI)
- **RAM** ~4GB for the model + ~500MB for embedding model (downloaded on first use)
- **Disk** ~3GB (model + llama.cpp + dependencies)

## Supported Document Formats

| Format | Library | Notes |
|--------|---------|-------|
| PDF | PyMuPDF | Extracts text with page numbers |
| DOCX | python-docx | Preserves headings for chunking |
| Markdown | markdown | Splits on headings |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "backend unreachable" in ChatUI | Ensure `start.sh` is running |
| "LLM disconnected" | llama.cpp failed to start — check model path exists |
| Slow first query | Embedding model downloading (~90MB), subsequent queries are fast |
| npm permission errors | Run `sudo chown -R $(id -u):$(id -g) ~/.npm` |
| No documents indexed | Upload via UI or run `curl -X POST http://127.0.0.1:8080/api/ingest` |

## Development

```bash
# Run backend only (for API development)
source venv/bin/activate
python -m backend.api.server

# Run ChatUI only (for frontend development)
cd ChatUI && npm run dev

# ChatUI dev server proxies /api/* and /health to backend :8080 automatically
```

## Windows

```cmd
scripts\setup.bat
scripts\start.bat
```
