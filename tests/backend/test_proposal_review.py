import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.proposal import ProposalPlan, ProposalSection
from backend.app.models.proposal_generation import GeneratedSection
from backend.app.services.ai_platform import ai_platform_service
from backend.app.services.review_coordinator import review_coordinator_service

def test_proposal_review_workflow(client: TestClient, test_db: Session):
    ai_platform_service.seed_ai_platform_defaults(test_db)

    # 1. Setup mock proposal plan and sections
    plan = ProposalPlan(
        id="test_plan_review_id",
        opportunity_id="test_opp_review",
        title="Test Proposal Plan for Reviews",
        status="DRAFT"
    )
    test_db.add(plan)
    
    sec1 = ProposalSection(
        id="test_sec_review_1",
        proposal_plan_id="test_plan_review_id",
        title="Executive Summary",
        estimated_hours=5,
        priority="High"
    )
    sec2 = ProposalSection(
        id="test_sec_review_2",
        proposal_plan_id="test_plan_review_id",
        title="Technical Approach",
        estimated_hours=10,
        priority="Medium"
    )
    test_db.add(sec1)
    test_db.add(sec2)

    # 2. Add generated content (one brief, one with a gap placeholder)
    g1 = GeneratedSection(
        id="gen_sec_1",
        proposal_plan_id="test_plan_review_id",
        proposal_section_id="test_sec_review_1",
        content="Brief content.",  # Brief (will trigger brief content finding)
        tone_style="Professional"
    )
    g2 = GeneratedSection(
        id="gen_sec_2",
        proposal_plan_id="test_plan_review_id",
        proposal_section_id="test_sec_review_2",
        content="This section has a placeholder [CONTENT_GAP: pricing details].",  # Gap (will trigger critical gap finding)
        tone_style="Technical"
    )
    test_db.add(g1)
    test_db.add(g2)
    test_db.commit()

    # 3. Start review coordinator execution via service
    session = review_coordinator_service.run_review_workflow(test_db, "test_plan_review_id")
    
    assert session is not None
    assert session.proposal_plan_id == "test_plan_review_id"
    assert session.overall_score < 0.95
    assert session.status == "BLOCKED"  # Due to critical findings

    # Check findings registered
    from backend.app.models.proposal_review import ProposalReviewFinding, ProposalReviewScore
    findings = test_db.query(ProposalReviewFinding).filter(ProposalReviewFinding.session_id == session.id).all()
    assert len(findings) > 0
    categories = [f.category for f in findings]
    assert "compliance_review" in categories or "technical_review" in categories

    scores = test_db.query(ProposalReviewScore).filter(ProposalReviewScore.session_id == session.id).all()
    assert len(scores) > 0

    # 4. Run auto-refinement
    refined_session = review_coordinator_service.refine_proposal_sections(test_db, session.id)
    assert refined_session is not None

    # Check a history record is created
    from backend.app.models.proposal_generation import GenerationHistory
    hist = test_db.query(GenerationHistory).filter(GenerationHistory.proposal_plan_id == "test_plan_review_id").first()
    assert hist is not None
    assert hist.action == "REGENERATE"

    # 5. Record human approval decision
    final_session = review_coordinator_service.record_human_decision(
        db=test_db,
        session_id=session.id,
        action="approve",
        actor="Bid Director",
        message="Manual sign-off"
    )
    assert final_session.status == "PASS"

    # Check audit record created
    from backend.app.models.proposal_review import ProposalReviewAudit
    audit = test_db.query(ProposalReviewAudit).filter(
        ProposalReviewAudit.session_id == session.id,
        ProposalReviewAudit.action == "approve"
    ).first()
    assert audit is not None
    assert audit.action == "approve"
    assert audit.actor == "Bid Director"

    # 6. Verify API Endpoints
    # Start review endpoint
    res_start = client.post("/api/v1/review/start", json={"proposal_plan_id": "test_plan_review_id"})
    assert res_start.status_code == 200
    
    # Get latest session endpoint
    res_get = client.get("/api/v1/review/test_plan_review_id")
    assert res_get.status_code == 200
    assert res_get.json()["proposal_plan_id"] == "test_plan_review_id"

    # History, findings, quality endpoints
    assert client.get("/api/v1/review/history").status_code == 200
    assert client.get("/api/v1/review/findings").status_code == 200
    assert client.get("/api/v1/review/quality").status_code == 200
    assert client.get("/api/v1/review/coverage").status_code == 200
    assert client.get("/api/v1/review/citations").status_code == 200
