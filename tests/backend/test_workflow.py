import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.workflow import (
    WorkflowExecution,
    WorkflowCheckpoint,
    WorkflowEvent,
    WorkflowMetric,
    WorkflowApprovalGate
)
from backend.app.services.workflow_orchestrator import WorkflowOrchestratorService

def test_workflow_orchestrator_lifecycle(test_db):
    orchestrator = WorkflowOrchestratorService()
    proposal_id = "test-prop-id-123"
    
    # 1. Start workflow
    db_exec = orchestrator.start_execution(test_db, "Proposal Lifecycle Workflow", proposal_id)
    assert db_exec.id is not None
    assert db_exec.proposal_id == proposal_id
    assert db_exec.status == "paused"
    assert db_exec.current_node == "qualification_approval_gate"
    
    # Check checkpoints are saved
    checkpoints = test_db.query(WorkflowCheckpoint).filter(WorkflowCheckpoint.execution_id == db_exec.id).all()
    assert len(checkpoints) > 0
    
    # Check events are saved
    events = test_db.query(WorkflowEvent).filter(WorkflowEvent.execution_id == db_exec.id).all()
    assert len(events) > 0
    assert any(e.event_type == "WorkflowStarted" for e in events)
    assert any(e.event_type == "CheckpointSaved" for e in events)

    # 2. Resume workflow (Approve)
    decision = {"action": "approve"}
    db_exec = orchestrator.resume_execution(test_db, db_exec.id, decision)
    assert db_exec.status == "completed"
    assert db_exec.current_node == "proposal_assembly"

    # Check metrics
    metrics = test_db.query(WorkflowMetric).filter(WorkflowMetric.execution_id == db_exec.id).all()
    assert len(metrics) > 0
    assert any(m.node_name == "proposal_generation" for m in metrics)

def test_workflow_rollback_and_retry(test_db):
    orchestrator = WorkflowOrchestratorService()
    proposal_id = "test-prop-id-456"

    # Start
    db_exec = orchestrator.start_execution(test_db, "Proposal Lifecycle Workflow", proposal_id)
    assert db_exec.status == "paused"
    assert db_exec.current_node == "qualification_approval_gate"

    # Rollback to document_processing
    db_exec = orchestrator.rollback_execution(test_db, db_exec.id, "document_processing")
    assert db_exec.status == "paused"
    assert db_exec.current_node == "qualification_approval_gate"

    # Retry node
    db_exec = orchestrator.retry_node(test_db, db_exec.id)
    assert db_exec.status == "paused"
    assert db_exec.current_node == "qualification_approval_gate"

def test_workflow_endpoints_workflow(client: TestClient, test_db):
    # 1. Start execution API
    res = client.post("/api/v1/workflow/start", json={
        "workflow_name": "Proposal Lifecycle Workflow",
        "proposal_id": "api-test-proposal"
    })
    assert res.status_code == 201
    data = res.json()
    exec_id = data["id"]
    assert data["status"] == "paused"
    assert data["current_node"] == "qualification_approval_gate"

    # 2. History API
    res = client.get("/api/v1/workflow/history")
    assert res.status_code == 200
    assert len(res.json()) > 0

    # 3. Checkpoints API
    res = client.get(f"/api/v1/workflow/{exec_id}/checkpoints")
    assert res.status_code == 200
    assert len(res.json()) > 0

    # 4. Resume API
    res = client.post(f"/api/v1/workflow/{exec_id}/resume", json={
        "action": "approve"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    # 5. Events API
    res = client.get(f"/api/v1/workflow/{exec_id}/events")
    assert res.status_code == 200
    assert len(res.json()) > 0

    # 6. Metrics API
    res = client.get(f"/api/v1/workflow/{exec_id}/metrics")
    assert res.status_code == 200
    assert len(res.json()) > 0
