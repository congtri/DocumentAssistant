from pathlib import Path
from dataclasses import dataclass, field

from docx import Document as DocxDocument

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


class DocxLoader:
    def load(self, file_path: str | Path) -> Document:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX not found: {file_path}")

        logger.info(f"Loading DOCX: {file_path.name}")
        docx = DocxDocument(str(file_path))

        paragraphs = []
        current_text = []
        page_num = 1

        for para in docx.paragraphs:
            text = para.text.strip()
            if text:
                current_text.append(text)

        # DOCX doesn't have page breaks easily accessible,
        # treat entire document as one logical page
        full_text = "\n".join(current_text)
        if full_text:
            paragraphs.append(DocumentPage(
                text=full_text,
                page_number=1,
                metadata={"style_count": len(docx.styles)},
            ))

        document = Document(
            name=file_path.name,
            path=str(file_path),
            pages=paragraphs,
            metadata={
                "format": "docx",
                "paragraph_count": len(docx.paragraphs),
            },
        )
        logger.info(f"Loaded DOCX: {file_path.name}")
        return document


docx_loader = DocxLoader()
