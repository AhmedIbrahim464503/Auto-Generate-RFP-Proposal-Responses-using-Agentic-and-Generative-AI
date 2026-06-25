import pytest
from pydantic import ValidationError
from backend.app.schemas.agent import AgentOutput
from backend.app.schemas.state import GraphState, GraphStateAuditMetadata
from backend.app.schemas.api_contracts import DepartmentReviewRequest, GateApprovalRequest

def test_agent_output_validation():
    # Valid output
    valid_data = {
        "decision": "GO",
        "confidence": 0.85,
        "reasoning": "Strong qualifications match RFP requirements.",
        "evidence": ["Historic win SPS-2025"],
        "risks": ["Slight resource constraints in Q3"],
        "recommendations": ["Assign senior lead"],
        "processing_time_ms": 120.5,
        "metadata": {"model": "gemini-2.5-flash"}
    }
    output = AgentOutput(**valid_data)
    assert output.decision == "GO"
    assert output.confidence == 0.85

    # Invalid confidence score (> 1.0)
    invalid_data = valid_data.copy()
    invalid_data["confidence"] = 1.5
    with pytest.raises(ValidationError):
        AgentOutput(**invalid_data)

    # Invalid confidence score (< 0.0)
    invalid_data["confidence"] = -0.1
    with pytest.raises(ValidationError):
        AgentOutput(**invalid_data)

def test_graph_state_pydantic_structure():
    state_data = {
        "opportunity_id": "opp-123",
        "opportunity_title": "Enterprise Cloud Migration",
        "requirements": [],
        "reviews": [],
        "qualification_decision": "GO",
        "planning_sections": [],
        "compliance_items": [],
        "approvals": [],
        "audit": {
            "correlation_id": "corr-456",
            "user_actor": "Ahmed",
            "created_at": "2026-06-25T23:59:00Z"
        },
        "current_step": "qualification"
    }
    state = GraphState(**state_data)
    assert state.opportunity_id == "opp-123"
    assert state.audit.user_actor == "Ahmed"

def test_department_review_validation():
    review = DepartmentReviewRequest(
        decision="GO",
        confidence=0.9,
        reasoning="Financially viable project."
    )
    assert review.decision == "GO"

def test_gate_approval_validation():
    approval = GateApprovalRequest(
        decision="APPROVED",
        comments="Everything looks compliant."
    )
    assert approval.decision == "APPROVED"
