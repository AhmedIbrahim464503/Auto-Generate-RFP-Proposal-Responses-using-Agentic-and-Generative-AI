import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument
from backend.app.models.proposal import ProposalPlan, ProposalSection
from backend.app.models.proposal_generation import GeneratedSection
from backend.app.services.proposal_generator import proposal_generator_service

def test_writer_config_resolutions():
    c1 = proposal_generator_service.get_writer_config("Executive Summary")
    c2 = proposal_generator_service.get_writer_config("Technical Solution Design")
    c3 = proposal_generator_service.get_writer_config("Unknown Custom Section Name")

    assert c1["version"] == "1.0.0"
    assert "Executive" in c1["system"]
    assert "Technical" in c2["system"]
    assert c3["version"] == "1.0.0"

def test_style_tone_instructions():
    s_engine = proposal_generator_service.style_engine
    inst1 = s_engine.get_style_instructions("Professional")
    inst2 = s_engine.get_style_instructions("Technical")
    
    assert "corporate" in inst1.lower()
    assert "terminology" in inst2.lower()

def test_quality_checks_validator():
    text = "Paragraph 1 content\n\nParagraph 2 content\n\nParagraph 1 content" # duplicated
    checks = proposal_generator_service.run_quality_checks(text, requirements_count=2, citations_count=1, tone="Professional")
    
    assert checks["duplicate_paragraphs"] is True
    assert checks["quality_score"] < 1.0

def test_proposal_generation_workflow(client: TestClient, test_db: Session):
    # 1. Create prerequisite Opportunity, Document, and Plan Outline
    opp = Opportunity(title="Proposal Capture Opp")
    test_db.add(opp)
    test_db.commit()

    doc = RFPDocument(opportunity_id=opp.id, file_name="rfp.pdf", file_path="/tmp/rfp.pdf")
    test_db.add(doc)
    test_db.commit()

    plan = ProposalPlan(opportunity_id=opp.id, title="Enterprise Capture Plan", client="Enterprise Client", status="DRAFT")
    test_db.add(plan)
    test_db.commit()

    section = ProposalSection(proposal_plan_id=plan.id, title="Executive Summary", content="Basic outline content", status="DRAFT", estimated_hours=10)
    test_db.add(section)
    test_db.commit()

    # 2. Run API generation for all sections
    res_gen = client.post(f"/api/v1/proposals/{plan.id}/generate", json={"tone_style": "Professional", "actor": "Proposal Writer"})
    assert res_gen.status_code == 200
    gen_list = res_gen.json()
    assert len(gen_list) >= 1
    assert gen_list[0]["tone_style"] == "Professional"
    assert "[CONTENT_GAP" in gen_list[0]["content"]  # No knowledge base data indexed yet, so GAP is returned.

    # 3. Fetch generated sections list
    res_get = client.get(f"/api/v1/proposals/{plan.id}/generated")
    assert res_get.status_code == 200
    assert len(res_get.json()) >= 1

    # 4. Single section regeneration with custom context
    sec_id = section.id
    res_single = client.post(
        f"/api/v1/proposals/{plan.id}/generate/section/{sec_id}",
        json={"tone_style": "Technical", "actor": "Lead Architect", "additional_context": "Add cloud architecture context"}
    )
    assert res_single.status_code == 200
    assert res_single.json()["tone_style"] == "Technical"

    # 5. Fetch generation history
    res_hist = client.get(f"/api/v1/proposals/{plan.id}/generation-history")
    assert res_hist.status_code == 200
    assert len(res_hist.json()) >= 2

    # 6. Fetch citations
    res_cit = client.get(f"/api/v1/proposals/{plan.id}/citations")
    assert res_cit.status_code == 200
