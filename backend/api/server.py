from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from backend.llm.llama_client import llama_client
from backend.rag.pipeline import rag_pipeline
from backend.utils.logger import logger
from backend.utils.settings import settings

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="DocumentAssistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    history: list[dict] | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict] = []


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None


class IngestResponse(BaseModel):
    chunks_indexed: int
    message: str


class UploadResponse(BaseModel):
    filenames: list[str]
    chunks_indexed: int
    message: str


@app.get("/")
async def index():
    """Serve the built-in doc-aware chat UI (calls /api/query with citations)."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    llm_healthy = await llama_client.health_check()
    return {
        "status": "ok",
        "llm_connected": llm_healthy,
        "indexed": rag_pipeline.is_indexed,
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        result = await rag_pipeline.query(request.question)
        return QueryResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        answer = await rag_pipeline.chat(request.message, request.history)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_documents(directory: str | None = None):
    try:
        chunks = await rag_pipeline.ingest_documents(directory)
        return IngestResponse(
            chunks_indexed=chunks,
            message=f"Successfully indexed {chunks} chunks",
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload", response_model=UploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)):
    """Save uploaded documents into documents/source and auto-ingest (index) them."""
    source_dir = settings.get_path(settings.documents.get("source_dir", "documents/source"))
    source_dir.mkdir(parents=True, exist_ok=True)

    allowed_formats = settings.documents.get("supported_formats", ["pdf", "docx", "md"])
    saved_filenames = []

    try:
        for upload in files:
            extension = Path(upload.filename).suffix.lstrip(".").lower()
            if extension not in allowed_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: .{extension}. Allowed: {allowed_formats}",
                )

            dest_path = source_dir / Path(upload.filename).name
            contents = await upload.read()
            with open(dest_path, "wb") as f:
                f.write(contents)
            saved_filenames.append(dest_path.name)
            logger.info(f"Saved uploaded file: {dest_path}")

        # Auto-ingest (index) after every upload
        chunks = await rag_pipeline.ingest_documents(str(source_dir))

        return UploadResponse(
            filenames=saved_filenames,
            chunks_indexed=chunks,
            message=f"Uploaded {len(saved_filenames)} file(s) and indexed {chunks} chunks",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def status():
    return {
        "indexed": rag_pipeline.is_indexed,
        "model": settings.model.get("name", "Unknown"),
        "llama_cpp_url": f"http://{settings.llama_cpp.get('host')}:{settings.llama_cpp.get('port')}",
    }


def start_server():
    config = settings.app
    uvicorn.run(
        "backend.api.server:app",
        host=config.get("host", "127.0.0.1"),
        port=config.get("port", 8080),
        reload=config.get("debug", False),
    )


if __name__ == "__main__":
    start_server()
