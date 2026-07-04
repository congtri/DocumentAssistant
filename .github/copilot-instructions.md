# DocumentAssistant Architecture Principles

Version: 1.0

---

# Vision

DocumentAssistant is not just a document chatbot.

It is a reusable, local-first RAG framework designed for desktop and edge devices.

Every architectural decision should support long-term maintainability, modularity, and extensibility.

---

# Core Philosophy

The project should follow these principles.

1. Modular

Every module has one responsibility.

2. Replaceable

Every major component can be replaced without affecting business logic.

3. Local-first

Everything runs locally.

Cloud providers are optional plugins, never requirements.

4. Simple

Avoid unnecessary abstraction.

Only introduce abstraction when multiple implementations are expected.

5. Maintainable

Readable code is more important than clever code.

6. Testable

Every service should be independently testable.

---

# Architecture Style

Use a layered architecture.

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Dependencies always point inward.

Outer layers never contain business rules.

---

# Domain First

Business logic must depend on domain models.

Avoid passing dictionaries across modules.

Prefer strongly typed models.

Example

Document

Chunk

Query

Citation

Answer

Metadata

---

# SOLID

Follow SOLID principles.

Especially

Single Responsibility

Dependency Inversion

Interface Segregation

Avoid large utility classes.

---

# Dependency Injection

Never instantiate concrete implementations inside business logic.

Bad

retriever = HybridRetriever()

Good

class QueryService:

    def __init__(self, retriever: Retriever):
        ...

---

# Interface-Based Design

Every replaceable component should expose an interface.

Examples

EmbeddingProvider

Retriever

ChunkStrategy

PromptBuilder

StorageProvider

IndexManager

LLMClient

Concrete implementations belong to Infrastructure.

---

# Separation of Responsibilities

Document Module

Responsible for reading documents.

Chunking Module

Responsible for splitting text.

Embedding Module

Responsible for generating vectors.

Retrieval Module

Responsible for searching.

Prompt Module

Responsible for prompt generation.

LLM Module

Responsible for inference.

Storage Module

Responsible for persistence.

Index Module

Responsible for index lifecycle.

Evaluation Module

Responsible for measuring quality.

No module should perform another module's responsibility.

---

# Configuration

Everything configurable belongs in YAML.

Avoid hardcoded values.

Examples

chunk size

embedding model

retrieval strategy

prompt template

weights

paths

ports

---

# Prompt Management

Prompt templates are not source code.

Store prompts as Markdown.

Prompt Builder loads templates and injects variables.

---

# Pipeline

Complex workflows should use Pipeline Engine.

Each stage has one responsibility.

Stages should not know about future stages.

Example

Load

↓

Clean

↓

Chunk

↓

Embed

↓

Index

---

# Retrieval Principles

Prefer quality over complexity.

Pipeline

Hybrid Search

↓

Metadata Filter

↓

Rerank

↓

LLM

Avoid unnecessary retrieval tricks.

Measure improvements before adding complexity.

---

# Metadata

Every chunk should carry metadata.

Minimum

document id

page

heading

language

chunk id

hash

created time

Metadata should flow through the entire pipeline.

---

# Document Lifecycle

Documents have versions.

Uploading the same file twice should not create duplicate indexes.

Every document should have

ID

Hash

Version

Timestamp

---

# Storage

Storage should be abstract.

Current implementation

Filesystem

Future

SQLite

PostgreSQL

Object Storage

Business logic must not care.

---

# Error Handling

Fail gracefully.

Never crash because

one document failed

one embedding failed

one chunk failed

Log everything.

Continue whenever possible.

---

# Logging

Every important operation should be logged.

Examples

Upload

Index

Embedding

Retrieval

LLM

Prompt

Errors

Logs should help debugging.

---

# Performance

Optimize only after measuring.

Preferred priorities

Correctness

↓

Maintainability

↓

Performance

↓

Micro-optimizations

---

# Future Expansion

Architecture should support future plugins.

Embedding

SentenceTransformer

BGE

E5

llama.cpp

Retriever

FAISS

Qdrant

Chroma

Storage

Filesystem

SQLite

PostgreSQL

LLM

llama.cpp

Ollama

vLLM

Adding new implementations should require minimal code changes.

---

# Code Quality

Prefer

small files

small classes

small functions

clear naming

type hints

docstrings

Avoid

god classes

magic constants

hidden side effects

deep inheritance

circular imports

---

# Testing

Every major component should support

Unit Testing

Integration Testing

Regression Testing

Business logic should be testable without running the UI.

---

# What This Project Is NOT

This project is NOT

a cloud platform

a distributed system

a Kubernetes service

a microservice architecture

Keep it lightweight.

Everything should run comfortably on a developer laptop or office PC.

---

# Success Criteria

A new developer should be able to

understand the architecture in less than one hour,

replace any major component in less than one day,

and add a new feature without modifying unrelated modules.

Architecture should always be easier to extend than to rewrite.