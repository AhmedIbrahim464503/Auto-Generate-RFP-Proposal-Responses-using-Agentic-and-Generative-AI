import pytest
import json
from datetime import datetime
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument, Requirement
from backend.app.models.proposal import ProposalPlan, ComplianceMatrix

def test_planning_generation_and_ownership(test_db):
    opp = Opportunity(title="SPS Planning Opportunity")
    test_db.add(opp)
    test_db.commit()

    doc = RFPDocument(id="test-planning-doc", opportunity_id=opp.id, file_name="sample.pdf", file_path="/tmp/sample.pdf")
    test_db.add(doc)
    test_db.commit()

    # Seed some requirements
    req1 = Requirement(rfp_document_id=doc.id, title="Req 1 Pricing", text_content="Provide total cost of ownership pricing", priority="High")
    req2 = Requirement(rfp_document_id=doc.id, title="Req 2 Technical", text_content="Provide solution architecture technical details", priority="High")
    test_db.add_all([req1, req2])
    test_db.commit()

    from backend.app.services.planning_engine import planning_engine_service
    plan = planning_engine_service.generate_proposal_plan(test_db, opp.id)

    assert plan is not None
    assert plan.client == "Enterprise Customer Corp"
    assert plan.status == "DRAFT"
    assert len(plan.sections) == 6
    assert len(plan.tasks) == 6
    assert len(plan.milestones) == 6
    assert len(plan.required_documents) == 3

    # Check compliance items auto-mapping
    matrix = test_db.query(ComplianceMatrix).filter(ComplianceMatrix.opportunity_id == opp.id).first()
    assert matrix is not None
    assert len(matrix.items) == 2

    # Check heuristic owner assignment
    pricing_item = [item for item in matrix.items if "pricing" in item.requirement.text_content.lower()][0]
    assert pricing_item.responsible_department == "Finance"
    assert pricing_item.responsible_owner == "Finance Lead"

def test_planning_endpoints_workflow(client, test_db):
    opp = Opportunity(title="SPS Planning API Opportunity")
    test_db.add(opp)
    test_db.commit()

    doc = RFPDocument(id="test-doc-planning-api", opportunity_id=opp.id, file_name="sample.pdf", file_path="/tmp/sample.pdf")
    test_db.add(doc)
    test_db.commit()

    # 1. Run Planning generation
    resp = client.post(f"/api/v1/proposals/test-doc-planning-api/planning")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "DRAFT"
    assert len(data["sections"]) == 6
    plan_id = data["id"]

    # 2. Get Plan summary
    resp = client.get(f"/api/v1/proposals/test-doc-planning-api/planning")
    assert resp.status_code == 200
    assert resp.json()["id"] == plan_id

    # 3. Get Outline
    resp = client.get(f"/api/v1/proposals/test-doc-planning-api/outline")
    assert resp.status_code == 200
    assert len(resp.json()) == 6

    # 4. Get Timeline
    resp = client.get(f"/api/v1/proposals/test-doc-planning-api/timeline")
    assert resp.status_code == 200
    assert len(resp.json()) == 6

    # 5. Get Tasks
    resp = client.get(f"/api/v1/proposals/test-doc-planning-api/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) == 6

    # 6. Update Plan API
    update_payload = {
        "title": "New Proposal Plan Title",
        "client": "Custom Client Corp",
        "proposal_owner": "Lead Capture Manager",
        "planning_notes": "Custom planning guidelines",
        "sections": [
            {"id": data["sections"][0]["id"], "title": "Updated Summary", "estimated_hours": 20}
        ]
    }
    resp = client.post(f"/api/v1/proposals/test-doc-planning-api/update-plan", json=update_payload)
    assert resp.status_code == 200
    updated_data = resp.json()
    assert updated_data["title"] == "New Proposal Plan Title"
    assert updated_data["client"] == "Custom Client Corp"
    assert updated_data["sections"][0]["title"] == "Updated Summary"

    # 7. Lock Plan API
    resp = client.post(f"/api/v1/proposals/test-doc-planning-api/lock-plan")
    assert resp.status_code == 200
    assert resp.json()["status"] == "LOCKED"

    # 8. Attempt editing while LOCKED (should fail)
    resp = client.post(f"/api/v1/proposals/test-doc-planning-api/update-plan", json={"title": "Should Fail"})
    assert resp.status_code == 400
    assert "is LOCKED" in resp.json()["detail"]

    # 9. Unlock Plan API
    resp = client.post(f"/api/v1/proposals/test-doc-planning-api/unlock-plan")
    assert resp.status_code == 200
    assert resp.json()["status"] == "DRAFT"

    # 10. Approve/Reject Plan API
    resp = client.post(
        f"/api/v1/proposals/test-doc-planning-api/approve-plan",
        json={"reviewer": "John Owner", "action": "APPROVE", "comments": "Plan is solid."}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "APPROVED"
