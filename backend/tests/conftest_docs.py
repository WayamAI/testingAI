"""Helper for building real, minimal PDF/DOCX fixtures in tests — hand-built
with pypdf's low-level object API (no extra PDF-writer dependency needed)
so document parsing is exercised against genuine binary files, not mocks.
"""
import io

import pypdf
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, StreamObject


def build_pdf_bytes(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=400, height=300)

    content = f"BT /F1 12 Tf 20 250 Td ({text}) Tj ET".encode()
    stream = StreamObject()
    stream.set_data(content)
    stream_ref = writer._add_object(stream)

    font = DictionaryObject()
    font[NameObject("/Type")] = NameObject("/Font")
    font[NameObject("/Subtype")] = NameObject("/Type1")
    font[NameObject("/BaseFont")] = NameObject("/Helvetica")
    font_ref = writer._add_object(font)

    resources = DictionaryObject()
    resources[NameObject("/Font")] = DictionaryObject({NameObject("/F1"): font_ref})
    page[NameObject("/Resources")] = resources
    page[NameObject("/Contents")] = stream_ref

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def build_docx_bytes(paragraphs: list[str]) -> bytes:
    from docx import Document

    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
