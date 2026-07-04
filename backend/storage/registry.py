"""Document registry for version management and duplicate detection."""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from backend.core.config import config
from backend.core.logger import logger
from backend.metadata.manager import metadata_manager


@dataclass
class DocumentRecord:
    """Registry entry for a tracked document."""

    document_id: str
    filename: str
    hash: str
    version: int
    upload_time: str


class DocumentRegistry:
    """Tracks uploaded documents, detects duplicates, manages versions."""

    def __init__(self):
        self._registry_path = config.get_path(config.data.get("chunks_dir", "data/chunks")) / "registry.json"
        self._records: dict[str, DocumentRecord] = {}
        self._load()

    def _load(self) -> None:
        if self._registry_path.exists():
            data = json.loads(self._registry_path.read_text())
            for entry in data:
                record = DocumentRecord(**entry)
                self._records[record.hash] = record

    def _save(self) -> None:
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(r) for r in self._records.values()]
        self._registry_path.write_text(json.dumps(data, indent=2))

    def check_duplicate(self, content_hash: str) -> DocumentRecord | None:
        """Check if a document with this hash already exists."""
        return self._records.get(content_hash)

    def register(self, filename: str, content_hash: str) -> DocumentRecord:
        """Register a new document or update version if duplicate strategy allows."""
        strategy = config.get("documents", "duplicate_strategy", "skip")
        existing = self._records.get(content_hash)

        if existing:
            if strategy == "skip":
                logger.info(f"Skipping duplicate: {filename}")
                return existing
            elif strategy == "version":
                existing.version += 1
                existing.upload_time = datetime.now().isoformat()
                self._save()
                return existing
            elif strategy == "replace":
                pass  # Fall through to overwrite

        record = DocumentRecord(
            document_id=f"doc:{content_hash[:12]}",
            filename=filename,
            hash=content_hash,
            version=1 if not existing else existing.version + 1,
            upload_time=datetime.now().isoformat(),
        )
        self._records[content_hash] = record
        self._save()
        logger.info(f"Registered document: {filename} (v{record.version})")
        return record

    def is_duplicate(self, content_hash: str) -> bool:
        return content_hash in self._records

    @property
    def all_records(self) -> list[DocumentRecord]:
        return list(self._records.values())


document_registry = DocumentRegistry()
