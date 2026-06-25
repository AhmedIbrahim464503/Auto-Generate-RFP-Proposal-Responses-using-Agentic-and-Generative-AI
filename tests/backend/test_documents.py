import io
import os
import pytest
from fastapi.testclient import TestClient
from backend.app.services.document_processor import DocumentProcessorFactory, PDFProcessor, DOCXProcessor

def test_document_processor_factory_resolution():
    # PDF resolution
    pdf_processor = DocumentProcessorFactory.get_processor("test_rfp.pdf")
    assert isinstance(pdf_processor, PDFProcessor)

    # DOCX resolution
    docx_processor = DocumentProcessorFactory.get_processor("test_rfp.docx")
    assert isinstance(docx_processor, DOCXProcessor)

    # Unsupported format
    with pytest.raises(ValueError):
        DocumentProcessorFactory.get_processor("test_rfp.xlsx")

def test_upload_validation_unsupported_format(client: TestClient):
    file_payload = {"file": ("test_rfp.txt", io.BytesIO(b"Unsupported format text content"), "text/plain")}
    response = client.post("/api/v1/documents/upload", files=file_payload)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]

def test_upload_validation_empty_file(client: TestClient):
    file_payload = {"file": ("test_rfp.pdf", io.BytesIO(b""), "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=file_payload)
    assert response.status_code == 400
    assert "content is empty" in response.json()["detail"]
