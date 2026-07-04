
# DocumentAssistant — Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User's Browser                        │
│                                                             │
│   ChatUI (React + Vite, :3000)                              │
│   ├── Message rendering (markdown)                          │
│   ├── File upload (drag & drop / button)                    │
│   └── RAG / Chat mode toggle                                │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP (proxied to :8080)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (:8080)                          │
│                                                             │
│   /api/query    → RAG pipeline (search + generate)          │
│   /api/chat     → Direct LLM generation                     │
│   /api/upload   → Save file + auto-ingest                   │
│   /api/ingest   → Re-index documents/source/                │
│   /health       → Status check                              │
└────────┬────────────────────────────┬───────────────────────┘
         │                            │
         ▼                            ▼
┌─────────────────────┐    ┌─────────────────────────────────┐
│   RAG Pipeline      │    │   Document Ingestion            │
│                     │    │                                 │
│   1. Hybrid Search  │    │   1. Loader (PDF/DOCX/MD)       │
│      ├── BM25 (0.4) │    │   2. Chunker (heading-based)    │
│      └── FAISS(0.6) │    │   3. Embedder (MiniLM-L6-v2)   │
│   2. Reranker       │    │   4. Index Builder              │
│   3. Prompt Builder │    │      ├── FAISS (vectors)        │
│   4. LLM Generate   │    │      └── BM25 (keywords)       │
│   5. Citation Extract│    │   5. Save to data/indexes/      │
└────────┬────────────┘    └─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              llama.cpp Server (:8081)                         │
│                                                             │
│   Model: Qwen3.5-4B-Q4_K_M.gguf                            │
│   Context: 8192 tokens                                      │
│   GPU layers: 99 (auto Metal/CUDA)                          │
│   API: OpenAI-compatible /v1/chat/completions               │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### ChatUI (Frontend)

| File | Purpose |
|------|---------|
| `src/api/client.js` | API client — all HTTP calls to backend |
| `src/components/Header.jsx` | Status badge, clear button |
| `src/components/ChatArea.jsx` | Message list, welcome screen, auto-scroll |
| `src/components/Message.jsx` | Markdown rendering, source citations, `<think>` stripping |
| `src/components/InputBar.jsx` | Textarea, file upload, RAG/Chat toggle, send button |
| `src/styles/global.css` | CSS variables, light/dark theme, scrollbar |
| `vite.config.js` | Dev server proxy (`/api/*` → `:8080`) |

### Backend (Python)

| Module | Files | Purpose |
|--------|-------|---------|
| `api/` | `server.py` | FastAPI app, routes, CORS, static serving |
| `document/` | `pdf_loader.py`, `docx_loader.py`, `markdown_loader.py` | Extract text + metadata from files |
| `chunking/` | `heading_splitter.py`, `splitter.py` | Split documents into searchable chunks |
| `embedding/` | `embedding_service.py` | Generate 384-dim vectors (all-MiniLM-L6-v2) |
| `retrieval/` | `faiss_store.py`, `bm25_store.py`, `hybrid_search.py`, `reranker.py` | Search indexes |
| `rag/` | `pipeline.py`, `citation.py` | Orchestrate retrieval → generation → citations |
| `llm/` | `llama_client.py`, `prompt_builder.py` | HTTP client to llama.cpp + prompt templates |
| `utils/` | `settings.py`, `logger.py` | Config loader (YAML) + structured logging |

### Configuration

| File | Controls |
|------|----------|
| `config/app.yaml` | Server host/port, document paths, logging level |
| `config/model.yaml` | Model file path, llama.cpp host/port/context |
| `config/rag.yaml` | Chunk size, embedding model, retrieval weights, generation params |

## Data Flow: User Asks a Question (RAG)

```
1. User types question in ChatUI
2. ChatUI sends POST /api/query { question, history }
3. Backend checks if index exists (loads from disk if needed)
4. Hybrid search runs:
   a. BM25: tokenizes question → keyword match against all chunks → scored list
   b. FAISS: embeds question → cosine similarity against chunk vectors → scored list
   c. Merge: weighted combination (BM25 × 0.4 + FAISS × 0.6)
5. Reranker: cross-encoder re-scores top-5 → selects top-3
6. Prompt builder: formats system prompt + context chunks + question
7. llama_client sends to llama.cpp /v1/chat/completions
8. Model generates answer (temperature 0.7, max 1024 tokens)
9. Citation extractor: maps answer back to source docs + pages
10. Response: { answer, sources: [{source, page, score}] }
11. ChatUI renders markdown answer + source cards
```

## Data Flow: User Uploads a Document

```
1. User clicks 📎 in ChatUI, selects file(s)
2. ChatUI sends POST /api/upload (multipart/form-data)
3. Backend saves file(s) to documents/source/
4. For each file:
   a. Loader detects format (PDF/DOCX/MD) → extracts text + page numbers
   b. Chunker splits text by headings (fallback: recursive at 512 tokens)
   c. Each chunk gets: text, source filename, page number, heading path
5. Embedding service encodes all chunks → 384-dim float vectors
6. FAISS index updated (add vectors)
7. BM25 index updated (add tokenized texts)
8. Indexes persisted to data/indexes/
9. Response: { filenames, chunks_indexed }
10. ChatUI shows "✓ Indexed N chunks"
```

## Folder Structure

```
DocumentAssistant/
│
├── ChatUI/                     # React frontend
│   ├── src/
│   │   ├── api/client.js       # API calls
│   │   ├── components/         # UI components
│   │   └── styles/global.css   # Theme + layout
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                    # Python backend
│   ├── api/server.py           # FastAPI routes
│   ├── document/               # File loaders
│   ├── chunking/               # Text splitters
│   ├── embedding/              # Vector encoding
│   ├── retrieval/              # Search engines
│   ├── rag/                    # Pipeline + citations
│   ├── llm/                    # LLM client + prompts
│   └── utils/                  # Config + logging
│
├── config/                     # YAML configs
│   ├── app.yaml
│   ├── model.yaml
│   └── rag.yaml
│
├── data/                       # Runtime (gitignored)
│   ├── chunks/
│   ├── embeddings/
│   ├── indexes/                # FAISS + BM25 persisted here
│   └── cache/
│
├── documents/
│   ├── source/                 # User documents (uploaded or placed manually)
│   └── roadmap/                # Project documentation
│
├── models/gguf/                # GGUF model (gitignored)
├── third_party/llama_cpp/      # llama.cpp binaries (gitignored)
├── scripts/                    # setup.sh/.bat, start.sh/.bat
├── logs/                       # Runtime logs (gitignored)
└── requirements.txt
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| llama.cpp (not Ollama) | Smaller footprint, direct control, no extra daemon |
| Hybrid BM25+FAISS | Keyword search catches exact terms; vectors catch semantics |
| Heading-based chunking | Preserves document structure better than fixed-size splits |
| all-MiniLM-L6-v2 | Fast, small (90MB), good quality for retrieval |
| Qwen3.5-4B Q4_K_M | Best quality/size trade-off for local hardware |
| Vite + React (ChatUI) | Fast dev experience, component isolation, hot reload |
| No database | File-based indexes are simpler; adequate for single-user local use |

## Adding a New Document Format

1. Create `backend/document/new_loader.py` with a `load(path) → Document` function
2. Register it in `backend/document/__init__.py`
3. Add extension to `config/app.yaml` → `documents.supported_formats`

## Changing the Model

1. Download a GGUF model to `models/gguf/`
2. Update `config/model.yaml` → `model.path`
3. Adjust `llama_cpp.context_length` if needed
4. Restart