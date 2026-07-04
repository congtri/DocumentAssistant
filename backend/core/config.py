"""Centralized configuration manager.

Loads all YAML configs and provides typed access to settings.
"""

from pathlib import Path
from typing import Any

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def _load_yaml(filename: str) -> dict:
    config_path = ROOT_DIR / "config" / filename
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


class ConfigManager:
    """Central access point for all application configuration."""

    def __init__(self):
        self._app = _load_yaml("app.yaml")
        self._model = _load_yaml("model.yaml")
        self._rag = _load_yaml("rag.yaml")

    @property
    def app(self) -> dict:
        return self._app.get("app", {})

    @property
    def documents(self) -> dict:
        return self._app.get("documents", {})

    @property
    def data(self) -> dict:
        return self._app.get("data", {})

    @property
    def logging(self) -> dict:
        return self._app.get("logging", {})

    @property
    def model(self) -> dict:
        return self._model.get("model", {})

    @property
    def llama_cpp(self) -> dict:
        return self._model.get("llama_cpp", {})

    @property
    def chunking(self) -> dict:
        return self._rag.get("chunking", {})

    @property
    def embedding(self) -> dict:
        return self._rag.get("embedding", {})

    @property
    def retrieval(self) -> dict:
        return self._rag.get("retrieval", {})

    @property
    def rag(self) -> dict:
        return self._rag.get("rag", {})

    def get_path(self, relative: str) -> Path:
        """Resolve a relative path from project root."""
        return ROOT_DIR / relative

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a config value by section and key."""
        data = getattr(self, section, {})
        if isinstance(data, dict):
            return data.get(key, default)
        return default

    def reload(self) -> None:
        """Reload all configuration from disk."""
        self._app = _load_yaml("app.yaml")
        self._model = _load_yaml("model.yaml")
        self._rag = _load_yaml("rag.yaml")


config = ConfigManager()
