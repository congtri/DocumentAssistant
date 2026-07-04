from pathlib import Path

from backend.document.pdf_loader import pdf_loader
from backend.document.docx_loader import docx_loader
from backend.document.markdown_loader import markdown_loader
from backend.core.logger import logger
from backend.domain.models import Document


LOADERS = {
    ".pdf": pdf_loader,
    ".docx": docx_loader,
    ".md": markdown_loader,
}


def load_document(file_path: str | Path) -> Document:
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    loader = LOADERS.get(ext)
    if not loader:
        raise ValueError(f"Unsupported format: {ext}")
    return loader.load(file_path)


def load_all_documents(directory: str | Path) -> list[Document]:
    directory = Path(directory)
    if not directory.exists():
        logger.warning(f"Document directory not found: {directory}")
        return []

    documents = []
    for ext, loader in LOADERS.items():
        for file_path in directory.rglob(f"*{ext}"):
            try:
                doc = loader.load(file_path)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

    logger.info(f"Loaded {len(documents)} documents from {directory}")
    return documents
