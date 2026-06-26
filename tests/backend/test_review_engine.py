import pytest
from fastapi.testclient import TestClient
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument
from backend.app.models.review import (
    FinancialReview,
    LegalReview,
    OperationsReview,
    TechnicalReview,
)
from backend.app.services.review_engine import PROMPT_REGISTRY, review_engine_service
from backend.app.schemas.review import DepartmentReviewOutput

def test_prompt_registry_keys():
    assert "v1.0" in PROMPT_REGISTRY
    v1 = PROMPT_REGISTRY["v1.0"]
    assert "financial_instruction" in v1
    assert "legal_instruction" in v1
    assert "operations_instruction" in v1
    assert "technical_instruction" in v1


def test_sps_business_rules_financial():
    # Rule 1: NET30 and Insurance <= 5M -> GO
    out1 = review_engine_service.run_financial_review("Mock content", "NET30", 1000000.0)
    assert out1.decision == "GO"
    assert out1.escalation_required is False

    # Rule 2: > NET30 -> CONDITIONALLY_GO & Escalated
    out2 = review_engine_service.run_financial_review("Mock content", "NET45", 1000000.0)
    assert out2.decision == "CONDITIONALLY_GO"
    assert out2.escalation_required is True

    # Rule 3: Insurance > 5M -> NO_GO
    out3 = review_engine_service.run_financial_review("Mock content", "NET30", 6000000.0)
    assert out3.decision == "NO_GO"


def test_review_endpoints_workflow(client: TestClient, test_db):
    # 1. Setup mock Opportunity and RFPDocument
    opp = Opportunity(title="SPS Review Feasibility Opportunity")
    test_db.add(opp)
    test_db.commit()

    doc = RFPDocument(opportunity_id=opp.id, file_name="sps_review_rfp.pdf", file_path="/fake/path")
    test_db.add(doc)
    test_db.commit()

    doc_id = str(doc.id)

    # 2. Run Financial Review API (triggers Net45 and >5M rules -> NO_GO)
    fin_res = client.post(f"/api/v1/rfp/{doc_id}/reviews/financial?payment_terms=NET45&insurance_limit=6000000")
    assert fin_res.status_code == 200
    assert fin_res.json()["decision"] == "NO_GO"

    # 3. Run Legal Review API
    leg_res = client.post(f"/api/v1/rfp/{doc_id}/reviews/legal")
    assert leg_res.status_code == 200
    assert leg_res.json()["decision"] == "GO"

    # 4. Fetch overall status
    status_res = client.get(f"/api/v1/rfp/{doc_id}/reviews")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["financial"]["status"] == "ESCALATED"  # Net45 triggers escalation
    assert status_data["legal"]["status"] == "REVIEWED"
    assert status_data["operations"]["status"] == "PENDING"

    # 5. Aggregate Risks
    risks_res = client.get(f"/api/v1/rfp/{doc_id}/risks")
    assert risks_res.status_code == 200
    assert len(risks_res.json()) > 0

    # 6. Override Financial Review (NO_GO -> GO)
    override_res = client.post(
        f"/api/v1/rfp/{doc_id}/reviews/financial/override",
        json={"new_decision": "GO", "override_reason": "Sufficient working capital reserves.", "overridden_by": "Manager"}
    )
    assert override_res.status_code == 200
    
    # 7. Re-verify status shows OVERRIDDEN
    status_res_2 = client.get(f"/api/v1/rfp/{doc_id}/reviews")
    assert status_res_2.status_code == 200
    assert status_res_2.json()["financial"]["status"] == "OVERRIDDEN"
    assert status_res_2.json()["financial"]["override_decision"] == "GO"
