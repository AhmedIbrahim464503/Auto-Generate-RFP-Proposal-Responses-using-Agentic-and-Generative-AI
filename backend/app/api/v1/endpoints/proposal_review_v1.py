from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.proposal_review import (
    ProposalReviewSession, ProposalReviewFinding, ProposalReviewScore,
    ProposalReviewWorkflow, ProposalReviewAudit
)
from backend.app.schemas.proposal_review import (
    ProposalReviewSessionResponse, ProposalReviewFindingResponse, ProposalReviewScoreResponse,
    ProposalReviewWorkflowResponse, ProposalReviewWorkflowCreate, StartReviewRequest, RefineReviewRequest, HumanDecisionRequest
)
from backend.app.services.review_coordinator import review_coordinator_service

router = APIRouter()

@router.post("/start", response_model=ProposalReviewSessionResponse)
def start_review(payload: StartReviewRequest, db: Session = Depends(get_db)):
    try:
        return review_coordinator_service.run_review_workflow(
            db=db,
            proposal_plan_id=payload.proposal_plan_id,
            workflow_id=payload.workflow_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refine", response_model=ProposalReviewSessionResponse)
def refine_review(payload: RefineReviewRequest, db: Session = Depends(get_db)):
    try:
        return review_coordinator_service.refine_proposal_sections(db=db, session_id=payload.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve", response_model=ProposalReviewSessionResponse)
def approve_review(payload: HumanDecisionRequest, db: Session = Depends(get_db)):
    try:
        return review_coordinator_service.record_human_decision(
            db=db,
            session_id=payload.session_id,
            action="approve",
            actor=payload.actor,
            message=payload.message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reject", response_model=ProposalReviewSessionResponse)
def reject_review(payload: HumanDecisionRequest, db: Session = Depends(get_db)):
    try:
        return review_coordinator_service.record_human_decision(
            db=db,
            session_id=payload.session_id,
            action="reject",
            actor=payload.actor,
            message=payload.message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/override", response_model=ProposalReviewSessionResponse)
def override_review(payload: HumanDecisionRequest, db: Session = Depends(get_db)):
    try:
        return review_coordinator_service.record_human_decision(
            db=db,
            session_id=payload.session_id,
            action="override",
            actor=payload.actor,
            message=payload.message,
            override_payload=payload.override_payload
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows", response_model=List[ProposalReviewWorkflowResponse])
def list_workflows(db: Session = Depends(get_db)):
    if not db.query(ProposalReviewWorkflow).first():
        # Seed standard workflow
        db.add(ProposalReviewWorkflow(
            name="Default Standard Compliance and Legal workflow",
            stages={"stages": ["compliance_review", "technical_review", "legal_review", "executive_review"]}
        ))
        db.commit()
    return db.query(ProposalReviewWorkflow).all()

@router.get("/history", response_model=List[ProposalReviewSessionResponse])
def get_review_history(db: Session = Depends(get_db)):
    return db.query(ProposalReviewSession).all()

@router.get("/findings", response_model=List[ProposalReviewFindingResponse])
def get_all_findings(db: Session = Depends(get_db)):
    return db.query(ProposalReviewFinding).all()

@router.get("/quality", response_model=List[ProposalReviewScoreResponse])
def get_all_quality_scores(db: Session = Depends(get_db)):
    return db.query(ProposalReviewScore).all()

@router.get("/coverage")
def get_requirement_coverage_report(db: Session = Depends(get_db)):
    # Aggregated report detailing requirement coverage
    findings = db.query(ProposalReviewFinding).filter(ProposalReviewFinding.agent_id == "requirement_coverage_review").all()
    warnings = [f.message for f in findings if f.severity == "warning"]
    criticals = [f.message for f in findings if f.severity == "critical"]
    
    total_req_count = 10  # Mock count
    satisfied_count = total_req_count - len(criticals)
    
    return {
        "coverage_percentage": (satisfied_count / total_req_count) * 100,
        "total_requirements": total_req_count,
        "satisfied": satisfied_count,
        "missing_obligations": criticals,
        "weak_points": warnings
    }

@router.get("/citations")
def get_citation_validation_report(db: Session = Depends(get_db)):
    findings = db.query(ProposalReviewFinding).filter(ProposalReviewFinding.agent_id == "citation_validation_review").all()
    broken = [f.message for f in findings if f.severity == "critical"]
    warnings = [f.message for f in findings if f.severity == "warning"]
    
    return {
        "citation_accuracy": 100.0 - (len(broken) * 10),
        "broken_references": broken,
        "warnings": warnings
    }

@router.get("/{proposalId}", response_model=ProposalReviewSessionResponse)
def get_latest_review(proposalId: str, db: Session = Depends(get_db)):
    session = db.query(ProposalReviewSession).filter(ProposalReviewSession.proposal_plan_id == proposalId).order_by(ProposalReviewSession.created_at.desc()).first()
    if not session:
        raise HTTPException(status_code=404, detail="No review session found for this proposal plan.")
    return session
