"""Filesystem-based storage provider."""

import json
from pathlib import Path
from typing import Any

from backend.core.interfaces.storage_provider import StorageProvider
from backend.core.config import config
from backend.core.logger import logger


class FilesystemStorage(StorageProvider):
    """Stores data as JSON files on the local filesystem."""

    def __init__(self, base_dir: Path | None = None):
        self._base_dir = base_dir or config.get_path(config.data.get("chunks_dir", "data/chunks"))
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: Any) -> None:
        path = self._base_dir / f"{key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(f"Saved: {path}")

    def load(self, key: str) -> Any | None:
        path = self._base_dir / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def exists(self, key: str) -> bool:
        path = self._base_dir / f"{key}.json"
        return path.exists()

    def delete(self, key: str) -> None:
        path = self._base_dir / f"{key}.json"
        if path.exists():
            path.unlink()
            logger.info(f"Deleted: {path}")
