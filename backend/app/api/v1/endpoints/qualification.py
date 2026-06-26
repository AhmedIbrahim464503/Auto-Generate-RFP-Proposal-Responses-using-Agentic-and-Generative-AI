import json
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.document import RFPDocument
from backend.app.models.qualification import (
    QualificationDecision,
    QualificationScoringBreakdown,
    QualificationDecisionHistory,
    QualificationExecutiveComment,
    QualificationRule
)
from backend.app.services.qualification_engine import qualification_engine_service
from backend.app.services.qualification_rules import QualificationRulesService
from backend.app.schemas.qualification import (
    QualificationDecisionResponse,
    QualificationApproveRequest,
    QualificationOverrideRequest,
    QualificationRecalculateRequest,
    QualificationRuleResponse,
    QualificationRuleUpdateRequest,
    ExecutiveCommentCreateRequest,
    ExecutiveCommentResponse,
    DecisionHistoryResponse
)

router = APIRouter()

def get_opportunity_id(doc_id: str, db: Session) -> str:
    doc = db.query(RFPDocument).filter(RFPDocument.id == doc_id, RFPDocument.is_deleted == False).first()
    if not doc:
        raise HTTPException(status_code=404, detail="RFP Document not found")
    return doc.opportunity_id

def serialize_decision(dec: QualificationDecision) -> QualificationDecisionResponse:
    # Safe JSON list loader helper
    def safe_load(field_val) -> List[str]:
        if not field_val:
            return []
        try:
            return json.loads(field_val)
        except Exception:
            return [field_val]

    breakdowns = []
    for b in dec.scoring_breakdowns:
        breakdowns.append({
            "dimension": b.dimension,
            "raw_score": b.raw_score,
            "weight": b.weight,
            "weighted_score": b.weighted_score,
            "details": json.loads(b.details_json) if b.details_json else None
        })

    comments = []
    for c in dec.comments:
        comments.append({
            "id": str(c.id),
            "author": c.author,
            "comment_text": c.comment_text,
            "timestamp": c.timestamp
        })

    return QualificationDecisionResponse(
        id=str(dec.id),
        opportunity_id=dec.opportunity_id,
        status=dec.status,
        recommendation=dec.recommendation,
        final_decision=dec.final_decision,
        decision_by=dec.decision_by,
        decision_timestamp=dec.decision_timestamp,
        executive_summary=dec.executive_summary,
        confidence=dec.confidence,
        reasoning=dec.reasoning,
        evidence=safe_load(dec.evidence_json),
        positive_factors=safe_load(dec.positive_factors),
        negative_factors=safe_load(dec.negative_factors),
        blocking_issues=safe_load(dec.blocking_issues),
        mitigating_factors=safe_load(dec.mitigating_factors),
        recommended_actions=safe_load(dec.recommended_actions),
        escalation_requirements=safe_load(dec.escalation_requirements),
        outstanding_clarifications=safe_load(dec.outstanding_clarifications),
        next_steps=safe_load(dec.next_steps),
        business_impact=dec.business_impact,
        opportunity_score=dec.opportunity_score,
        estimated_win_probability=dec.estimated_win_probability,
        win_probability_explanation=dec.win_probability_explanation,
        prompt_version=dec.prompt_version,
        model_version=dec.model_version,
        rule_version=dec.rule_version,
        created_at=dec.created_at,
        updated_at=dec.updated_at,
        scoring_breakdowns=breakdowns,
        comments=comments
    )


# Rules endpoints - nested outside document scope
@router.get("/rules/qualification", response_model=QualificationRuleResponse)
def get_active_rules(db: Session = Depends(get_db)):
    ruleset = QualificationRulesService.get_active_ruleset(db)
    return QualificationRuleResponse(
        id=str(ruleset.id),
        version=ruleset.version,
        name=ruleset.name,
        scope_key=ruleset.scope_key,
        rules_payload=json.loads(ruleset.rules_payload),
        is_active=ruleset.is_active,
        created_at=ruleset.created_at
    )

@router.post("/rules/qualification", response_model=QualificationRuleResponse)
def update_rules(req: QualificationRuleUpdateRequest, db: Session = Depends(get_db)):
    ruleset = QualificationRulesService.update_active_ruleset_payload(db, req.rules_payload)
    return QualificationRuleResponse(
        id=str(ruleset.id),
        version=ruleset.version,
        name=ruleset.name,
        scope_key=ruleset.scope_key,
        rules_payload=json.loads(ruleset.rules_payload),
        is_active=ruleset.is_active,
        created_at=ruleset.created_at
    )

@router.post("/{id}/qualification", response_model=QualificationDecisionResponse)
def run_qualification(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    
    # Run qualification engine
    dec = qualification_engine_service.calculate_opportunity_score_and_run(db, opp_id)
    
    # Record history
    history = QualificationDecisionHistory(
        opportunity_id=opp_id,
        action="GENERATE",
        actor="AI Qualification Analyst",
        previous_status=None,
        new_status=dec.status,
        comments="Qualification decision calculated by AI Engine",
        payload_json=json.dumps({"opportunity_score": dec.opportunity_score, "recommendation": dec.recommendation}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()

    return serialize_decision(dec)

@router.get("/{id}/qualification", response_model=QualificationDecisionResponse)
def get_qualification(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    dec = db.query(QualificationDecision).filter(
        QualificationDecision.opportunity_id == opp_id,
        QualificationDecision.is_deleted == False
    ).first()

    if not dec:
        # Run automatically if it hasn't run yet
        dec = qualification_engine_service.calculate_opportunity_score_and_run(db, opp_id)

    return serialize_decision(dec)

@router.get("/{id}/decision-history", response_model=List[DecisionHistoryResponse])
def get_decision_history(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    history = db.query(QualificationDecisionHistory).filter(
        QualificationDecisionHistory.opportunity_id == opp_id
    ).order_by(QualificationDecisionHistory.timestamp.desc()).all()

    out = []
    for h in history:
        out.append(DecisionHistoryResponse(
            id=str(h.id),
            opportunity_id=h.opportunity_id,
            action=h.action,
            actor=h.actor,
            previous_status=h.previous_status,
            new_status=h.new_status,
            comments=h.comments,
            payload=json.loads(h.payload_json) if h.payload_json else None,
            timestamp=h.timestamp
        ))
    return out

@router.post("/{id}/approve-decision", response_model=QualificationDecisionResponse)
def approve_decision(id: str, req: QualificationApproveRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    dec = db.query(QualificationDecision).filter(
        QualificationDecision.opportunity_id == opp_id,
        QualificationDecision.is_deleted == False
    ).first()

    if not dec:
        raise HTTPException(status_code=404, detail="Qualification decision not found")

    old_status = dec.status
    dec.status = "APPROVED"
    dec.final_decision = dec.recommendation
    dec.decision_by = req.reviewer
    dec.decision_timestamp = datetime.utcnow()
    dec.updated_at = datetime.utcnow()

    # Log to history
    history = QualificationDecisionHistory(
        opportunity_id=opp_id,
        action="APPROVE",
        actor=req.reviewer,
        previous_status=old_status,
        new_status="APPROVED",
        comments=req.comments or "Recommendation approved.",
        payload_json=json.dumps({"final_decision": dec.final_decision}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(dec)

    return serialize_decision(dec)

@router.post("/{id}/override-decision", response_model=QualificationDecisionResponse)
def override_decision(id: str, req: QualificationOverrideRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    dec = db.query(QualificationDecision).filter(
        QualificationDecision.opportunity_id == opp_id,
        QualificationDecision.is_deleted == False
    ).first()

    if not dec:
        raise HTTPException(status_code=404, detail="Qualification decision not found")

    old_status = dec.status
    dec.status = "OVERRIDDEN"
    dec.final_decision = req.new_decision
    dec.decision_by = req.overridden_by
    dec.decision_timestamp = datetime.utcnow()
    dec.updated_at = datetime.utcnow()

    # Log to history
    history = QualificationDecisionHistory(
        opportunity_id=opp_id,
        action="OVERRIDE",
        actor=req.overridden_by,
        previous_status=old_status,
        new_status="OVERRIDDEN",
        comments=req.override_reason,
        payload_json=json.dumps({"override_decision": req.new_decision, "reason": req.override_reason}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(dec)

    return serialize_decision(dec)

@router.post("/{id}/recalculate", response_model=QualificationDecisionResponse)
def recalculate_decision(id: str, req: QualificationRecalculateRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    
    # 1. Update weights in active ruleset payload configuration
    ruleset = QualificationRulesService.get_active_ruleset(db)
    payload = json.loads(ruleset.rules_payload)
    
    # Verify and update weights
    for dim, weight in req.weights.items():
        if dim in payload.get("weights", {}):
            payload["weights"][dim] = weight

    # Normalize weights if necessary or validate sum
    QualificationRulesService.update_active_ruleset_payload(db, {"weights": payload["weights"]})

    # 2. Run qualification engine calculation
    dec = qualification_engine_service.calculate_opportunity_score_and_run(db, opp_id)

    # Log to history
    history = QualificationDecisionHistory(
        opportunity_id=opp_id,
        action="WEIGHT_ADJUSTED",
        actor="System",
        previous_status=dec.status,
        new_status=dec.status,
        comments="Recalculated qualification score with new weights",
        payload_json=json.dumps({"weights": req.weights, "opportunity_score": dec.opportunity_score}),
        timestamp=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(dec)

    return serialize_decision(dec)


@router.post("/{id}/comments", response_model=ExecutiveCommentResponse)
def add_executive_comment(id: str, req: ExecutiveCommentCreateRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    dec = db.query(QualificationDecision).filter(
        QualificationDecision.opportunity_id == opp_id,
        QualificationDecision.is_deleted == False
    ).first()

    if not dec:
        raise HTTPException(status_code=404, detail="Qualification decision not found")

    comment = QualificationExecutiveComment(
        qualification_id=dec.id,
        author=req.author,
        comment_text=req.comment_text,
        timestamp=datetime.utcnow()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return ExecutiveCommentResponse(
        id=str(comment.id),
        author=comment.author,
        comment_text=comment.comment_text,
        timestamp=comment.timestamp
    )
