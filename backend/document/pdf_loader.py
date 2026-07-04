from pathlib import Path

import fitz  # PyMuPDF

from backend.core.interfaces.document_loader import DocumentLoader
from backend.core.logger import logger
from backend.domain.models import Document, DocumentPage


class PDFLoader(DocumentLoader):
    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    def load(self, file_path: str | Path) -> Document:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        logger.info(f"Loading PDF: {file_path.name}")
        doc = fitz.open(str(file_path))
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                pages.append(DocumentPage(
                    text=text.strip(),
                    page_number=page_num + 1,
                    metadata={"width": page.rect.width, "height": page.rect.height},
                ))

        document = Document(
            name=file_path.name,
            path=str(file_path),
            pages=pages,
            metadata={
                "format": "pdf",
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
            },
        )
        doc.close()
        logger.info(f"Loaded {len(pages)} pages from {file_path.name}")
        return document


pdf_loader = PDFLoader()
