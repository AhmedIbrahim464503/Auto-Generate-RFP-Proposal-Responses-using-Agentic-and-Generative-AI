import pytest
from backend.app.services.ai_engine import PROMPT_REGISTRY, SectionStructure, ExtractionMetadataOutput

def test_prompt_registry_keys():
    assert "v1.0" in PROMPT_REGISTRY
    v1 = PROMPT_REGISTRY["v1.0"]
    assert "system_instruction" in v1
    assert "segmentation_prompt" in v1
    assert "metadata_prompt" in v1

def test_section_structure_pydantic_validation():
    data = {
        "title": "Scope of work",
        "content": "Provide backend system models...",
        "classification": "Scope",
        "confidence": 0.9,
        "page_start": 2,
        "page_end": 5,
        "subsections": []
    }
    sec = SectionStructure(**data)
    assert sec.title == "Scope of work"
    assert sec.classification == "Scope"
    assert sec.confidence == 0.9

def test_metadata_extraction_pydantic_validation():
    data = {
        "document_title": "Project Capture Proposal RFP",
        "client_name": "SPS Solutions",
        "project_name": "Enterprise AI Orchestrator",
        "rfp_number": "RFP-2026-X11",
        "issue_date": "2026-06-25",
        "submission_deadline": "2026-07-20",
        "contacts": [
            {
                "organization": "SPS",
                "primary_contact": "John Doe",
                "email": "jdoe@sps.com"
            }
        ]
    }
    meta = ExtractionMetadataOutput(**data)
    assert meta.document_title == "Project Capture Proposal RFP"
    assert meta.contacts[0].primary_contact == "John Doe"
