"""Real document text extraction — PDF (pypdf), DOCX (python-docx), and
plain text/markdown. Never invents content; unreadable documents raise a
specific reason rather than silently returning nothing.
"""
import io

import pypdf
from docx import Document as DocxDocument

_SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".txt", ".md")


class DocumentParseError(Exception):
    pass


def extract_text(filename: str, content: bytes) -> str:
    lowered = filename.lower()

    if lowered.endswith(".pdf"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
        except Exception as exc:
            raise DocumentParseError(f"Could not parse PDF: {exc}") from exc
        if not text:
            raise DocumentParseError("Unable to extract sufficient content — the PDF may be scanned/image-only.")
        return text

    if lowered.endswith(".docx"):
        try:
            doc = DocxDocument(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs).strip()
        except Exception as exc:
            raise DocumentParseError(f"Could not parse DOCX: {exc}") from exc
        if not text:
            raise DocumentParseError("Unable to extract sufficient content from this DOCX file.")
        return text

    if lowered.endswith((".txt", ".md")):
        try:
            text = content.decode("utf-8", errors="replace").strip()
        except Exception as exc:
            raise DocumentParseError(f"Could not decode text file: {exc}") from exc
        if not text:
            raise DocumentParseError("The uploaded file is empty.")
        return text

    raise DocumentParseError(
        f"Unsupported file type — expected one of {_SUPPORTED_EXTENSIONS}."
    )
