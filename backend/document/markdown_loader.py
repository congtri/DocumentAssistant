from pathlib import Path

from backend.core.interfaces.document_loader import DocumentLoader
from backend.core.logger import logger
from backend.domain.models import Document, DocumentPage


class MarkdownLoader(DocumentLoader):
    def supported_extensions(self) -> list[str]:
        return [".md"]

    def load(self, file_path: str | Path) -> Document:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown not found: {file_path}")

        logger.info(f"Loading Markdown: {file_path.name}")
        content = file_path.read_text(encoding="utf-8")

        pages = [DocumentPage(
            text=content.strip(),
            page_number=1,
            metadata={"char_count": len(content)},
        )] if content.strip() else []

        document = Document(
            name=file_path.name,
            path=str(file_path),
            pages=pages,
            metadata={
                "format": "markdown",
                "line_count": content.count("\n") + 1,
            },
        )
        logger.info(f"Loaded Markdown: {file_path.name}")
        return document


markdown_loader = MarkdownLoader()
