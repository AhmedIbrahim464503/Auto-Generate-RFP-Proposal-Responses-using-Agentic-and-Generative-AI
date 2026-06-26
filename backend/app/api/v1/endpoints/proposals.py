import json
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.document import RFPDocument
from backend.app.models.proposal import (
    ProposalPlan,
    ProposalSection,
    ComplianceMatrix,
    ComplianceItem,
    ProposalTask,
    ProposalMilestone,
    RequiredDocument,
    ClarificationRequest,
    PlanningHistory
)
from backend.app.services.planning_engine import planning_engine_service
from backend.app.schemas.proposal import (
    ProposalPlanResponse,
    ProposalSectionResponse,
    ComplianceMatrixItemResponse,
    ProposalTaskResponse,
    ProposalMilestoneResponse,
    RequiredDocumentResponse,
    ClarificationRequestResponse,
    PlanningHistoryResponse,
    ProposalApproveRequest,
    ProposalUpdateRequest
)

router = APIRouter()

def get_opportunity_id(doc_id: str, db: Session) -> str:
    doc = db.query(RFPDocument).filter(RFPDocument.id == doc_id, RFPDocument.is_deleted == False).first()
    if not doc:
        raise HTTPException(status_code=404, detail="RFP Document not found")
    return doc.opportunity_id

def serialize_plan(plan: ProposalPlan, db: Session) -> ProposalPlanResponse:
    # Safe JSON list loader helper
    def safe_load(field_val) -> List[str]:
        if not field_val:
            return []
        try:
            return json.loads(field_val)
        except Exception:
            return [field_val]

    sections = []
    for s in plan.sections:
        sections.append(ProposalSectionResponse(
            id=str(s.id),
            proposal_plan_id=str(s.proposal_plan_id),
            title=s.title,
            content=s.content,
            status=s.status,
            owner=s.owner,
            reviewer=s.reviewer,
            approver=s.approver,
            estimated_hours=s.estimated_hours or 0,
            dependencies=safe_load(s.dependencies),
            priority=s.priority or "Medium",
            risk_level=s.risk_level or "Low",
            is_human_editable=s.is_human_editable
        ))

    tasks = []
    for t in plan.tasks:
        tasks.append(ProposalTaskResponse(
            id=str(t.id),
            proposal_plan_id=str(t.proposal_plan_id),
            parent_task_id=str(t.parent_task_id) if t.parent_task_id else None,
            title=t.title,
            owner=t.owner,
            priority=t.priority or "Medium",
            estimated_hours=t.estimated_hours or 0.0,
            status=t.status,
            dependencies=safe_load(t.dependencies),
            due_date=t.due_date,
            is_critical_path=t.is_critical_path
        ))

    milestones = []
    for m in plan.milestones:
        milestones.append(ProposalMilestoneResponse(
            id=str(m.id),
            proposal_plan_id=str(m.proposal_plan_id),
            name=m.name,
            start_date=m.start_date,
            end_date=m.end_date,
            status=m.status
        ))

    req_docs = []
    for rd in plan.required_documents:
        req_docs.append(RequiredDocumentResponse(
            id=str(rd.id),
            proposal_plan_id=str(rd.proposal_plan_id),
            document_name=rd.document_name,
            document_type=rd.document_type,
            status=rd.status,
            required_by_date=rd.required_by_date,
            notes=rd.notes
        ))

    clarifications = []
    for cr in plan.clarification_requests:
        clarifications.append(ClarificationRequestResponse(
            id=str(cr.id),
            proposal_plan_id=str(cr.proposal_plan_id),
            question=cr.question,
            reason=cr.reason,
            related_requirement_id=str(cr.related_requirement_id) if cr.related_requirement_id else None,
            priority=cr.priority or "Medium",
            owner=cr.owner,
            status=cr.status,
            client_response=cr.client_response,
            impact=cr.impact,
            resolution=cr.resolution
        ))

    history = []
    for h in plan.history_records:
        history.append(PlanningHistoryResponse(
            id=str(h.id),
            proposal_plan_id=str(h.proposal_plan_id),
            action=h.action,
            actor=h.actor,
            comments=h.comments,
            payload=json.loads(h.payload_json) if h.payload_json else None,
            timestamp=h.timestamp
        ))

    return ProposalPlanResponse(
        id=str(plan.id),
        opportunity_id=plan.opportunity_id,
        title=plan.title,
        client=plan.client,
        rfp_name=plan.rfp_name,
        proposal_type=plan.proposal_type,
        submission_deadline=plan.submission_deadline,
        estimated_duration_days=plan.estimated_duration_days or 0,
        estimated_effort_hours=plan.estimated_effort_hours or 0,
        complexity=plan.complexity or "Medium",
        priority=plan.priority or "Medium",
        required_departments=safe_load(plan.required_departments),
        executive_sponsor=plan.executive_sponsor,
        proposal_owner=plan.proposal_owner,
        status=plan.status,
        version=plan.version,
        planning_notes=plan.planning_notes,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        sections=sections,
        tasks=tasks,
        milestones=milestones,
        required_documents=req_docs,
        clarification_requests=clarifications,
        history=history
    )

@router.post("/{id}/planning", response_model=ProposalPlanResponse)
def generate_planning(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    
    # Check if plan already exists and is locked
    existing = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id).first()
    if existing and existing.status == "LOCKED":
        raise HTTPException(status_code=400, detail="Cannot regenerate planning package because the plan is LOCKED")

    plan = planning_engine_service.generate_proposal_plan(db, opp_id)

    # Log to history
    history = PlanningHistory(
        proposal_plan_id=plan.id,
        action="GENERATE",
        actor="AI Planning Assistant",
        comments="Proposal Plan generated automatically by AI Planning Engine",
        payload_json=json.dumps({"version": plan.version, "sections_count": len(plan.sections)}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(plan)

    return serialize_plan(plan, db)

@router.get("/{id}/planning", response_model=ProposalPlanResponse)
def get_planning(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(
        ProposalPlan.opportunity_id == opp_id,
        ProposalPlan.is_deleted == False
    ).first()

    if not plan:
        # Auto generate if it does not exist
        plan = planning_engine_service.generate_proposal_plan(db, opp_id)

    return serialize_plan(plan, db)

@router.get("/{id}/outline", response_model=List[ProposalSectionResponse])
def get_outline(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    return serialize_plan(plan, db).sections

@router.get("/{id}/compliance-matrix", response_model=List[ComplianceMatrixItemResponse])
def get_compliance_matrix(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    matrix = db.query(ComplianceMatrix).filter(ComplianceMatrix.opportunity_id == opp_id, ComplianceMatrix.is_deleted == False).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="Compliance Matrix not found")

    out = []
    for item in matrix.items:
        out.append(ComplianceMatrixItemResponse(
            id=str(item.id),
            compliance_matrix_id=str(item.compliance_matrix_id),
            requirement_id=str(item.requirement_id),
            proposal_section_id=str(item.proposal_section_id) if item.proposal_section_id else None,
            status=item.status,
            explanation=item.explanation,
            responsible_department=item.responsible_department,
            responsible_owner=item.responsible_owner,
            priority=item.priority or "Medium",
            mandatory=item.mandatory,
            evidence_required=item.evidence_required,
            source_page=item.source_page,
            source_paragraph=item.source_paragraph,
            risk_if_missing=item.risk_if_missing,
            dependencies=json.loads(item.dependencies) if item.dependencies else [],
            reviewer=item.reviewer,
            approval_status=item.approval_status,
            traceability_links=json.loads(item.traceability_links) if item.traceability_links else [],
            confidence=item.confidence,
            comments=item.comments
        ))
    return out

@router.get("/{id}/timeline", response_model=List[ProposalMilestoneResponse])
def get_timeline(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")
    
    return serialize_plan(plan, db).milestones

@router.get("/{id}/tasks", response_model=List[ProposalTaskResponse])
def get_tasks(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    return serialize_plan(plan, db).tasks

@router.post("/{id}/approve-plan", response_model=ProposalPlanResponse)
def approve_plan(id: str, req: ProposalApproveRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    if plan.status == "LOCKED" and req.action == "REJECT":
        # Unlock if rejected
        plan.status = "DRAFT"
    elif req.action == "APPROVE":
        plan.status = "APPROVED"
    else:
        plan.status = "DRAFT"

    plan.updated_at = datetime.utcnow()

    # Log history
    history = PlanningHistory(
        proposal_plan_id=plan.id,
        action=req.action,
        actor=req.reviewer,
        comments=req.comments or f"Proposal Plan status updated to: {plan.status}",
        payload_json=json.dumps({"status": plan.status}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(plan)

    return serialize_plan(plan, db)

@router.post("/{id}/update-plan", response_model=ProposalPlanResponse)
def update_plan(id: str, req: ProposalUpdateRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    if plan.status == "LOCKED":
        raise HTTPException(status_code=400, detail="Cannot edit proposal plan because it is LOCKED")

    # Update metadata fields
    if req.title:
        plan.title = req.title
    if req.client:
        plan.client = req.client
    if req.proposal_owner:
        plan.proposal_owner = req.proposal_owner
    if req.planning_notes:
        plan.planning_notes = req.planning_notes

    # Update sections if provided
    if req.sections:
        for sec_data in req.sections:
            sec_id = sec_data.get("id")
            if sec_id:
                section = db.query(ProposalSection).filter(ProposalSection.id == sec_id).first()
                if section:
                    if "title" in sec_data:
                        section.title = sec_data["title"]
                    if "owner" in sec_data:
                        section.owner = sec_data["owner"]
                    if "reviewer" in sec_data:
                        section.reviewer = sec_data["reviewer"]
                    if "approver" in sec_data:
                        section.approver = sec_data["approver"]
                    if "estimated_hours" in sec_data:
                        section.estimated_hours = sec_data["estimated_hours"]
                    if "priority" in sec_data:
                        section.priority = sec_data["priority"]
                    if "risk_level" in sec_data:
                        section.risk_level = sec_data["risk_level"]

    plan.updated_at = datetime.utcnow()

    # Log history
    history = PlanningHistory(
        proposal_plan_id=plan.id,
        action="EDIT",
        actor=req.proposal_owner or "Capture Manager",
        comments="Proposal Plan sections and metadata manually updated",
        payload_json=json.dumps({"updated_fields": list(req.model_dump(exclude_unset=True).keys())}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(plan)

    return serialize_plan(plan, db)

@router.post("/{id}/lock-plan", response_model=ProposalPlanResponse)
def lock_plan(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    plan.status = "LOCKED"
    plan.updated_at = datetime.utcnow()

    # Log history
    history = PlanningHistory(
        proposal_plan_id=plan.id,
        action="LOCK",
        actor="Capture Manager",
        comments="Proposal Plan locked. Editing restricted.",
        payload_json=json.dumps({"status": "LOCKED"}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(plan)

    return serialize_plan(plan, db)

@router.post("/{id}/unlock-plan", response_model=ProposalPlanResponse)
def unlock_plan(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opp_id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    plan.status = "DRAFT"
    plan.updated_at = datetime.utcnow()

    # Log history
    history = PlanningHistory(
        proposal_plan_id=plan.id,
        action="UNLOCK",
        actor="Capture Manager",
        comments="Proposal Plan unlocked. Editing permitted.",
        payload_json=json.dumps({"status": "DRAFT"}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(plan)

    return serialize_plan(plan, db)
