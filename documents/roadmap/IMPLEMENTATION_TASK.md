# DocumentAssistant Architecture Refactoring Task

## Objective

Refactor the current codebase into a modular, maintainable, production-quality local RAG framework.

This is **NOT** a rewrite.

The application must remain functional after every completed task.

The public API should remain backward compatible unless explicitly stated.

---

# Important Rules

## Do NOT

- Rewrite the project.
- Change the frontend.
- Replace FastAPI.
- Replace llama.cpp.
- Change existing API routes.
- Introduce cloud dependencies.
- Introduce Docker.
- Introduce authentication.
- Break existing functionality.

## Must

- Refactor incrementally.
- Keep commits small.
- Keep the application runnable after every milestone.
- Prefer composition over inheritance.
- Prefer interfaces over concrete implementations.
- Write clean, typed Python.
- Keep code well documented.

---

# Task 1 — Create Core Layer

Create:

backend/core/

Structure:

backend/core/

    config.py

    logger.py

    dependency.py

    interfaces/

Responsibilities

config.py

- load all yaml configs

logger.py

- central logging

dependency.py

- dependency injection helpers

interfaces/

Contains abstract interfaces for:

- DocumentLoader
- ChunkStrategy
- EmbeddingProvider
- Retriever
- Reranker
- PromptBuilder
- LLMClient
- StorageProvider
- IndexManager

Acceptance Criteria

- Existing code still works.
- No business logic inside interfaces.

---

# Task 2 — Introduce Domain Models

Create

backend/domain/

Models

Document

Chunk

Embedding

Query

Citation

Answer

Metadata

Use dataclasses or Pydantic models.

Business logic should exchange domain objects instead of dictionaries whenever possible.

Acceptance Criteria

No magic dictionaries passed between major modules.

---

# Task 3 — Build Pipeline Engine

Create

backend/pipeline/

Structure

pipeline/

    engine.py

    context.py

    stage.py

    stages/

Stages

DocumentLoaded

DocumentParsed

DocumentCleaned

ChunksCreated

MetadataAttached

EmbeddingsGenerated

IndexesBuilt

Completed

Pipeline Engine should execute stages sequentially.

Acceptance Criteria

Current upload flow uses Pipeline Engine.

---

# Task 4 — Refactor Document Module

Current document loading should become:

document/

    loaders/

        pdf_loader.py

        docx_loader.py

        markdown_loader.py

    cleaner.py

    registry.py

Create Loader interface implementation for every format.

Acceptance Criteria

Adding a new loader should require no changes elsewhere.

---

# Task 5 — Refactor Chunking

Create

chunking/

    strategies/

        fixed.py

        heading.py

        semantic.py

Strategy interface

ChunkStrategy

Requirements

Support:

Fixed chunking

Heading chunking

Semantic chunking (placeholder if not implemented)

Rules

Never split:

- tables
- code blocks
- bullet lists

Acceptance Criteria

Chunking strategy selectable from config.

---

# Task 6 — Refactor Embedding

Current embedding implementation should become

embedding/

    providers/

        sentence_transformer.py

        bge.py

        e5.py

Create interface

EmbeddingProvider

Move embedding model selection into config.

Acceptance Criteria

Changing embedding model requires config only.

---

# Task 7 — Refactor Retrieval

Create

retrieval/

    bm25.py

    vector.py

    hybrid.py

    reranker.py

    strategy.py

Interfaces

Retriever

Implementations

BM25Retriever

VectorRetriever

HybridRetriever

Features

Hybrid retrieval

Metadata filtering

Adaptive retrieval (future)

Acceptance Criteria

Retrieval implementation replaceable.

---

# Task 8 — Prompt System

Create

prompt/

    builder.py

    loader.py

Templates

system.md

rag.md

chat.md

citation.md

summary.md

Prompt Builder

Loads Markdown

Performs variable substitution

Returns final prompt

Acceptance Criteria

No prompt string hardcoded in Python.

---

# Task 9 — Metadata Manager

Create

metadata/

    manager.py

Metadata fields

document_id

document_name

document_hash

page

heading

language

chunk_id

created_time

updated_time

tags

Acceptance Criteria

Every chunk contains metadata.

---

# Task 10 — Storage Layer

Create

storage/

    filesystem.py

    registry.py

    persistence.py

Responsibilities

Document registry

Embedding persistence

Chunk persistence

Metadata persistence

Acceptance Criteria

Storage implementation isolated.

---

# Task 11 — Index Manager

Create

index/

    manager.py

Responsibilities

Build index

Delete index

Update index

Rebuild index

Optimize index

Acceptance Criteria

Retrieval module never modifies indexes directly.

---

# Task 12 — Document Version Management

Implement

SHA256 hash

Duplicate detection

Versioning

Registry format

{
    document_id
    filename
    hash
    version
    upload_time
}

Configurable behavior

duplicate_strategy:

- skip
- replace
- version

Acceptance Criteria

Uploading same document twice does not create duplicate indexes.

---

# Task 13 — Evaluation Module

Create

evaluation/

Metrics

Recall@K

Precision@K

MRR

Hit Rate

Create benchmark runner.

Acceptance Criteria

Quality metrics can be generated.

---

# Task 14 — Configuration Cleanup

Split configuration

config/

app.yaml

model.yaml

rag.yaml

retrieval.yaml

prompt.yaml

logging.yaml

No duplicated settings.

Acceptance Criteria

All configs loaded through ConfigManager.

---

# Task 15 — Dependency Injection

Refactor services.

Avoid

service = ConcreteClass()

Prefer

constructor injection

Example

Retriever

EmbeddingProvider

PromptBuilder

LLMClient

Acceptance Criteria

Business logic depends on interfaces only.

---

# Task 16 — Future Plugin Support

Architecture should allow future implementations.

Embedding

- SentenceTransformer
- BGE
- llama.cpp embedding
- Ollama

Retriever

- FAISS
- Chroma
- Qdrant

LLM

- llama.cpp
- Ollama
- vLLM

Storage

- Filesystem
- SQLite
- PostgreSQL

No implementation required now.

Only architecture.

---

# Final Validation

The application must still support:

✓ Upload PDF

✓ Upload DOCX

✓ Upload Markdown

✓ Automatic indexing

✓ Hybrid Retrieval

✓ Reranking

✓ Prompt generation

✓ llama.cpp inference

✓ Source citations

✓ Existing REST APIs

✓ Existing React frontend

---

# Code Quality Requirements

- Python 3.11+
- Type hints everywhere
- Small classes
- Small functions
- SOLID principles
- Dependency Injection
- No circular imports
- No duplicated code
- Clear module boundaries
- Unit-test friendly

---

# Deliverables

After implementation, the project should become a reusable local RAG framework with:

- Clean architecture
- Domain models
- Pipeline engine
- Modular retrieval
- Prompt management
- Metadata management
- Storage abstraction
- Index abstraction
- Plugin-ready design
- Easy future extension

Functionality must remain compatible with the current application.