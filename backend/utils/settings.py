from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def load_yaml(filename: str) -> dict:
    config_path = ROOT_DIR / "config" / filename
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


class Settings:
    def __init__(self):
        self._app = load_yaml("app.yaml")
        self._model = load_yaml("model.yaml")
        self._rag = load_yaml("rag.yaml")

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
        return ROOT_DIR / relative


settings = Settings()
