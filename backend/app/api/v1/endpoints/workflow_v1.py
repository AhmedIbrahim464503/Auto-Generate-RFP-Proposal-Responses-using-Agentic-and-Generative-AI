from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.workflow import (
    WorkflowExecution,
    WorkflowCheckpoint,
    WorkflowEvent,
    WorkflowMetric,
    WorkflowApprovalGate
)
from backend.app.services.workflow_orchestrator import WorkflowOrchestratorService
from backend.app.schemas.workflow import (
    WorkflowExecutionResponse,
    WorkflowCheckpointResponse,
    WorkflowEventResponse,
    WorkflowMetricResponse,
    WorkflowApprovalGateResponse,
    StartWorkflowRequest,
    ResumeWorkflowRequest,
    RollbackWorkflowRequest
)

router = APIRouter()
orchestrator = WorkflowOrchestratorService()

@router.post("/start", response_model=WorkflowExecutionResponse, status_code=status.HTTP_201_CREATED)
def start_workflow(request: StartWorkflowRequest, db: Session = Depends(get_db)):
    try:
        return orchestrator.start_execution(db, request.workflow_name, request.proposal_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{execution_id}/resume", response_model=WorkflowExecutionResponse)
def resume_workflow(execution_id: str, request: ResumeWorkflowRequest, db: Session = Depends(get_db)):
    try:
        payload = request.payload or {}
        payload["action"] = request.action
        return orchestrator.resume_execution(db, execution_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{execution_id}/rollback", response_model=WorkflowExecutionResponse)
def rollback_workflow(execution_id: str, request: RollbackWorkflowRequest, db: Session = Depends(get_db)):
    try:
        return orchestrator.rollback_execution(db, execution_id, request.target_node)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{execution_id}/retry", response_model=WorkflowExecutionResponse)
def retry_workflow(execution_id: str, db: Session = Depends(get_db)):
    try:
        return orchestrator.retry_node(db, execution_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{execution_id}/pause", response_model=WorkflowExecutionResponse)
def pause_workflow(execution_id: str, db: Session = Depends(get_db)):
    db_exec = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
    if not db_exec:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    db_exec.status = "paused"
    db.commit()
    
    # Log event
    orchestrator._log_event(db, execution_id, "WorkflowPaused", {"current_node": db_exec.current_node})
    
    return db_exec

@router.get("/history", response_model=List[WorkflowExecutionResponse])
def get_workflow_history(db: Session = Depends(get_db)):
    return db.query(WorkflowExecution).all()

@router.get("/{execution_id}", response_model=WorkflowExecutionResponse)
def get_workflow_details(execution_id: str, db: Session = Depends(get_db)):
    db_exec = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
    if not db_exec:
        raise HTTPException(status_code=404, detail="Execution not found")
    return db_exec

@router.get("/{execution_id}/checkpoints", response_model=List[WorkflowCheckpointResponse])
def get_workflow_checkpoints(execution_id: str, db: Session = Depends(get_db)):
    return db.query(WorkflowCheckpoint).filter(WorkflowCheckpoint.execution_id == execution_id).all()

@router.get("/{execution_id}/events", response_model=List[WorkflowEventResponse])
def get_workflow_events(execution_id: str, db: Session = Depends(get_db)):
    return db.query(WorkflowEvent).filter(WorkflowEvent.execution_id == execution_id).all()

@router.get("/{execution_id}/metrics", response_model=List[WorkflowMetricResponse])
def get_workflow_metrics(execution_id: str, db: Session = Depends(get_db)):
    return db.query(WorkflowMetric).filter(WorkflowMetric.execution_id == execution_id).all()
