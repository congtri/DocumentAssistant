from pathlib import Path
import subprocess
import signal
import platform
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from backend.llm.llama_client import llama_client
from backend.rag.pipeline import rag_pipeline
from backend.core.logger import logger
from backend.core.config import config, ROOT_DIR


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


# Processing state for document uploads
processing_state = {"active": False, "status": "", "progress": 0}


class LlamaServerManager:
    """Manages the llama-server subprocess lifecycle."""

    def __init__(self):
        self.process = None
        self._find_binary()

    def _find_binary(self):
        llama_dir = ROOT_DIR / "third_party" / "llama_cpp"
        self.binary = None
        if llama_dir.exists():
            for p in llama_dir.rglob("llama-server*"):
                if p.is_file() and not p.suffix:
                    self.binary = p
                    break

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def start(self, model_path: str) -> bool:
        if not self.binary or not self.binary.exists():
            logger.warning("llama-server binary not found")
            return False

        full_model = ROOT_DIR / model_path
        if not full_model.exists():
            logger.error(f"Model not found: {full_model}")
            return False

        llama_cfg = config.llama_cpp
        host = llama_cfg.get("host", "127.0.0.1")
        port = str(llama_cfg.get("port", 8081))
        ctx_size = str(llama_cfg.get("context_length", 8192))

        cmd = [
            str(self.binary),
            "--model", str(full_model),
            "--host", host,
            "--port", port,
            "--ctx-size", ctx_size,
            "--n-gpu-layers", "99",
        ]

        logger.info(f"Starting llama-server: {' '.join(cmd)}")
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=None if platform.system() == "Windows" else lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
        )
        return True

    def stop(self):
        if self.process and self.process.poll() is None:
            logger.info(f"Stopping llama-server (PID: {self.process.pid})")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def restart(self, model_path: str) -> bool:
        self.stop()
        return self.start(model_path)


llama_manager = LlamaServerManager()


@asynccontextmanager
async def lifespan(app):
    # Startup: start llama-server if not already running
    if not await llama_client.health_check():
        model_path = config.model.get("path", "")
        if model_path and llama_manager.binary:
            logger.info("llama-server not detected, starting it...")
            llama_manager.start(model_path)
    yield
    # Shutdown: stop llama-server if we started it
    llama_manager.stop()


STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="DocumentAssistant", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    global processing_state

    if processing_state["active"]:
        raise HTTPException(status_code=409, detail="A document is already being processed")

    source_dir = config.get_path(config.documents.get("source_dir", "documents/source"))
    source_dir.mkdir(parents=True, exist_ok=True)

    allowed_formats = config.documents.get("supported_formats", ["pdf", "docx", "md"])
    saved_filenames = []

    try:
        processing_state = {"active": True, "status": "Uploading files...", "progress": 10}

        for upload in files:
            extension = Path(upload.filename).suffix.lstrip(".").lower()
            if extension not in allowed_formats:
                processing_state = {"active": False, "status": "", "progress": 0}
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

        processing_state = {"active": True, "status": "Indexing documents...", "progress": 50}

        # Auto-ingest (index) after every upload
        chunks = await rag_pipeline.ingest_documents(str(source_dir))

        processing_state = {"active": False, "status": "Done", "progress": 100}

        return UploadResponse(
            filenames=saved_filenames,
            chunks_indexed=chunks,
            message=f"Uploaded {len(saved_filenames)} file(s) and indexed {chunks} chunks",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        processing_state = {"active": False, "status": f"Error: {e}", "progress": 0}
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def status():
    return {
        "indexed": rag_pipeline.is_indexed,
        "model": config.model.get("name", "Unknown"),
        "llama_cpp_url": f"http://{config.llama_cpp.get('host')}:{config.llama_cpp.get('port')}",
    }


@app.get("/api/processing")
async def get_processing_status():
    return processing_state


@app.get("/api/models")
async def list_models():
    """List available GGUF models in models/gguf/ directory."""
    gguf_dir = ROOT_DIR / "models" / "gguf"
    models = []
    if gguf_dir.exists():
        for f in sorted(gguf_dir.iterdir()):
            if f.suffix.lower() == ".gguf" and f.is_file():
                models.append({
                    "name": f.stem,
                    "filename": f.name,
                    "path": str(f.relative_to(ROOT_DIR)),
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1),
                })
    current = config.model.get("path", "")
    return {"models": models, "current": current}


@app.post("/api/models/switch")
async def switch_model(request: dict):
    """Switch to a different GGUF model by restarting llama-server."""
    model_path = request.get("path")
    if not model_path:
        raise HTTPException(status_code=400, detail="path is required")

    full_path = ROOT_DIR / model_path
    if not full_path.exists() or full_path.suffix.lower() != ".gguf":
        raise HTTPException(status_code=404, detail="Model file not found")

    # Update model.yaml
    import yaml
    config_path = ROOT_DIR / "config" / "model.yaml"
    yaml_data = {}
    if config_path.exists():
        with open(config_path) as f:
            yaml_data = yaml.safe_load(f) or {}

    yaml_data.setdefault("model", {})
    yaml_data["model"]["name"] = full_path.stem
    yaml_data["model"]["path"] = model_path

    with open(config_path, "w") as f:
        yaml.dump(yaml_data, f, default_flow_style=False)

    # Reload config
    config.reload()

    # Restart llama-server with new model
    if llama_manager.binary:
        success = llama_manager.restart(model_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to restart llama-server")

        # Wait for llama-server to become healthy
        import httpx
        llama_url = f"http://{config.llama_cpp.get('host', '127.0.0.1')}:{config.llama_cpp.get('port', 8081)}"
        for _ in range(30):
            time.sleep(1)
            try:
                with httpx.Client(timeout=2.0) as client:
                    resp = client.get(f"{llama_url}/health")
                    if resp.status_code == 200:
                        break
            except Exception:
                continue
        else:
            return {
                "message": f"Model switched to {full_path.stem} but llama-server may still be loading.",
                "model": full_path.stem,
                "path": model_path,
            }

    return {
        "message": f"Model switched to {full_path.stem}. llama-server restarted.",
        "model": full_path.stem,
        "path": model_path,
    }


def start_server():
    app_config = config.app
    uvicorn.run(
        "backend.api.server:app",
        host=app_config.get("host", "127.0.0.1"),
        port=app_config.get("port", 8080),
        reload=app_config.get("debug", False),
    )


if __name__ == "__main__":
    start_server()
