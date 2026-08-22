import pytest

from app.services.document_parsing import DocumentParseError, extract_text
from tests.conftest_docs import build_docx_bytes, build_pdf_bytes


def test_extract_text_from_real_pdf():
    pdf_bytes = build_pdf_bytes("Users should be able to reset their password.")
    text = extract_text("requirements.pdf", pdf_bytes)
    assert "reset their password" in text


def test_extract_text_from_real_docx():
    docx_bytes = build_docx_bytes([
        "The system must allow users to log in with email and password.",
        "Users can view their order history.",
    ])
    text = extract_text("prd.docx", docx_bytes)
    assert "log in with email" in text
    assert "order history" in text


def test_extract_text_from_markdown():
    text = extract_text("spec.md", b"# Spec\n\nUsers should be able to add items to their cart.")
    assert "add items to their cart" in text


def test_extract_text_rejects_unsupported_extension():
    with pytest.raises(DocumentParseError, match="Unsupported file type"):
        extract_text("archive.zip", b"PK\x03\x04")


def test_extract_text_rejects_empty_text_file():
    with pytest.raises(DocumentParseError, match="empty"):
        extract_text("empty.txt", b"")
