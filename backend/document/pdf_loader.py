from pathlib import Path
from dataclasses import dataclass, field

import fitz  # PyMuPDF

from backend.utils.logger import logger


@dataclass
class DocumentPage:
    text: str
    page_number: int
    metadata: dict = field(default_factory=dict)


@dataclass
class Document:
    name: str
    path: str
    pages: list[DocumentPage] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class PDFLoader:
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
