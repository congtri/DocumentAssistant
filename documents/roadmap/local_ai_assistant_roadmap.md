# Local AI Assistant Roadmap

## Project Goal

Build a cross-platform (Windows + macOS Intel + Apple Silicon) local AI document assistant using:

- llama.cpp (with its built-in Web UI — no separate front-end needed)
- GGUF models (initially Qwen3 4B)
- Local document storage
- Future RAG support

---

# Phase 0 - Define Requirements

## Objectives

Define the scope of V1.

## Deliverables

- Supported operating systems
  - Windows x64
  - macOS Intel
  - macOS Apple Silicon

- Supported document formats
  - PDF
  - DOCX
  - Markdown

- Initial model selection
  - Qwen3 4B GGUF

- Success criteria

```text
User starts application
    ↓
Browser opens
    ↓
User asks question
    ↓
Local model answers
```

---

# Phase 1 - Local LLM Prototype

## Objectives

Create a working local chatbot.

## Components

- llama.cpp (built-in Web UI, served directly by `llama-server`)
- Qwen3 4B GGUF

## Tasks

- Install and validate llama.cpp
- Download and test GGUF model
- Configure llama.cpp server
- Verify llama.cpp's built-in Web UI loads in browser
- Verify chat functionality
- Verify streaming responses

## Deliverables

```text
llama.cpp built-in Web UI
     |
llama.cpp
     |
Qwen3 4B
```

---

# Phase 2 - Deployment and Packaging

## Objectives

Create a simple startup experience.

## Tasks

- Design folder layout
- Create startup scripts
- Test Windows startup
- Test macOS startup
- Verify model loading

## Deliverables

```text
Double-click
     ↓
Application starts
     ↓
Browser opens
```

---

# Phase 3 - Document Ingestion

## Objectives

Load and extract document contents.

## Tasks

- PDF loader
- DOCX loader
- Markdown loader
- Metadata extraction
- Page tracking
- Upload endpoint saves files to `documents/source/`
- Auto-ingest (index) documents immediately after upload

## Candidate Libraries

- PyMuPDF
- pdfplumber
- python-docx
- Docling (optional evaluation)

## Deliverables

```text
Document
     ↓
Extracted Text
```

---

# Phase 4 - Chunking Strategy

## Objectives

Convert documents into searchable chunks.

## Tasks

- Evaluate chunking methods
- Heading-based chunking
- Section-based chunking
- Metadata preservation

## Deliverables

```text
Document
     ↓
Chunks
```

---

# Phase 5 - Retrieval Engine

## Objectives

Retrieve relevant content without using the LLM.

## Tasks

### BM25

- Build keyword search
- Tune ranking

### Vector Search

- Select embedding model
- Generate embeddings
- Build FAISS index

### Hybrid Search

- Combine BM25 and vector search

## Deliverables

```text
Question
     ↓
Top Relevant Chunks
```

---

# Phase 6 - RAG Pipeline

## Objectives

Connect retrieval with the LLM.

## Tasks

- Context retrieval
- Prompt generation
- Query processing
- Answer generation

## Deliverables

```text
Question
     ↓
Retrieval
     ↓
Prompt
     ↓
Qwen3
     ↓
Answer
```

---

# Phase 7 - Source Citations

## Objectives

Increase trustworthiness.

## Tasks

- Page references
- Document references
- Source formatting

## Deliverables

Example:

```text
Sources:

ISO21434.pdf page 42
ISO21434.pdf page 43
```

---

# Phase 8 - Evaluation Framework

## Objectives

Measure system quality.

## Tasks

- Create benchmark questions
- Define expected sources
- Measure retrieval accuracy
- Measure answer accuracy

## Deliverables

Dataset:

```text
Question
Expected Source
Expected Answer
```

---

# Phase 9 - Performance Optimization

## Objectives

Reduce resource consumption.

## Areas

### Model Optimization

- Quantization evaluation
- Smaller model testing

### Retrieval Optimization

- Chunk tuning
- Top-K tuning

### Memory Optimization

- Cache tuning
- Embedding optimization

## Deliverables

- Faster response time
- Lower RAM usage

---

# Phase 10 - Production Release

## Objectives

Create a user-friendly release package.

## Tasks

- Build release structure
- Package dependencies
- Documentation
- Installation guide
- Upgrade process

## Deliverables

```text
AI Assistant/
│
├── llama.cpp (built-in Web UI)
├── models
├── documents
├── indexes
└── launch scripts
```

---

# Recommended Execution Order

1. Phase 0 - Define Requirements
2. Phase 1 - Local LLM Prototype
3. Phase 2 - Deployment and Packaging
4. Phase 3 - Document Ingestion
5. Phase 4 - Chunking Strategy
6. Phase 5 - Retrieval Engine
7. Phase 6 - RAG Pipeline
8. Phase 7 - Source Citations
9. Phase 8 - Evaluation Framework
10. Phase 9 - Performance Optimization
11. Phase 10 - Production Release

---

# Current Status

All core phases implemented. System is functional with:
- llama.cpp + Qwen3.5-4B running locally
- React ChatUI with markdown rendering
- Full RAG pipeline (hybrid search + reranker + citations)
- Document upload + auto-indexing
- Cross-platform scripts (macOS + Windows)

Architecture:

```text
Browser (ChatUI :3000)
        │
        ▼
DocumentAssistant API (FastAPI :8080)
        │
   ┌────┴────┐
   │         │
RAG Pipeline  Upload + Auto-Ingest
   │
Hybrid Search (BM25 + FAISS) → Reranker
   │
   ▼
llama.cpp Server (:8081)
   │
Qwen3.5-4B GGUF
```
