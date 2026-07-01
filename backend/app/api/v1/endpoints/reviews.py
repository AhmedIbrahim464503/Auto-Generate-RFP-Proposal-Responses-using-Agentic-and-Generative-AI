import json
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.document import RFPDocument
from backend.app.models.review import (
    FinancialReview,
    LegalReview,
    OperationsReview,
    TechnicalReview,
    ReviewComment,
    ReviewOverrideHistory,
)
from backend.app.models.requirement_intelligence import RFPRisk
from backend.app.services.review_engine import review_engine_service
from backend.app.schemas.review import (
    DepartmentReviewOutput,
    AggregatedRiskResponse,
    ReviewCommentRequest,
    ReviewOverrideRequest,
    ReviewApproveRequest,
    AllReviewsStatusResponse,
    DepartmentStatusResponse,
)

router = APIRouter()

def get_opportunity_id(doc_id: str, db: Session) -> str:
    doc = db.query(RFPDocument).filter(RFPDocument.id == doc_id, RFPDocument.is_deleted == False).first()
    if not doc:
        raise HTTPException(status_code=404, detail="RFP Document not found")
    return doc.opportunity_id

def _ensure_str(val) -> str:
    if val is None:
        return ""
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return str(val)

@router.post("/{id}/reviews/financial", response_model=DepartmentReviewOutput)
def run_financial_review(id: str, payment_terms: str = "NET30", insurance_limit: float = 1000000.0, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    
    # Run analysis
    review_output = review_engine_service.run_financial_review("RFP Content", payment_terms, insurance_limit)

    # Delete existing
    db.query(FinancialReview).filter(FinancialReview.opportunity_id == opp_id).delete()

    # Save to db
    db_review = FinancialReview(
        opportunity_id=opp_id,
        reviewer="AI Financial Analyst",
        decision=review_output.decision,
        confidence=review_output.confidence,
        reasoning=_ensure_str(review_output.reasoning),
        evidence=_ensure_str(review_output.evidence),
        risks=json.dumps(review_output.risks),
        recommendations=json.dumps(review_output.recommendations),
        escalation_required=review_output.escalation_required,
        findings=json.dumps(review_output.findings),
        assumptions=json.dumps(review_output.assumptions),
        missing_information=json.dumps(review_output.missing_information),
        clarification_questions=json.dumps(review_output.clarification_questions),
        reviewer_metadata=json.dumps({"model": "gemini-2.5-flash", "api": "generativeai"}),
        processing_metadata=json.dumps({"latency_ms": 120.0})
    )
    db.add(db_review)
    db.commit()
    return review_output

@router.post("/{id}/reviews/legal", response_model=DepartmentReviewOutput)
def run_legal_review(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    review_output = review_engine_service.run_legal_review("RFP Content")

    db.query(LegalReview).filter(LegalReview.opportunity_id == opp_id).delete()

    db_review = LegalReview(
        opportunity_id=opp_id,
        reviewer="AI Legal Counsel",
        decision=review_output.decision,
        confidence=review_output.confidence,
        reasoning=_ensure_str(review_output.reasoning),
        evidence=_ensure_str(review_output.evidence),
        risks=json.dumps(review_output.risks),
        recommendations=json.dumps(review_output.recommendations),
        escalation_required=review_output.escalation_required,
        findings=json.dumps(review_output.findings),
        assumptions=json.dumps(review_output.assumptions),
        missing_information=json.dumps(review_output.missing_information),
        clarification_questions=json.dumps(review_output.clarification_questions),
        reviewer_metadata=json.dumps({"model": "gemini-2.5-flash"}),
        processing_metadata=json.dumps({"latency_ms": 110.0})
    )
    db.add(db_review)
    db.commit()
    return review_output

@router.post("/{id}/reviews/operations", response_model=DepartmentReviewOutput)
def run_operations_review(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    review_output = review_engine_service.run_operations_review("RFP Content")

    db.query(OperationsReview).filter(OperationsReview.opportunity_id == opp_id).delete()

    db_review = OperationsReview(
        opportunity_id=opp_id,
        reviewer="AI Operations Specialist",
        decision=review_output.decision,
        confidence=review_output.confidence,
        reasoning=_ensure_str(review_output.reasoning),
        evidence=_ensure_str(review_output.evidence),
        risks=json.dumps(review_output.risks),
        recommendations=json.dumps(review_output.recommendations),
        escalation_required=review_output.escalation_required,
        findings=json.dumps(review_output.findings),
        assumptions=json.dumps(review_output.assumptions),
        missing_information=json.dumps(review_output.missing_information),
        clarification_questions=json.dumps(review_output.clarification_questions),
        reviewer_metadata=json.dumps({"model": "gemini-2.5-flash"}),
        processing_metadata=json.dumps({"latency_ms": 95.0})
    )
    db.add(db_review)
    db.commit()
    return review_output

@router.post("/{id}/reviews/technical", response_model=DepartmentReviewOutput)
def run_technical_review(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    review_output = review_engine_service.run_technical_review("RFP Content")

    db.query(TechnicalReview).filter(TechnicalReview.opportunity_id == opp_id).delete()

    db_review = TechnicalReview(
        opportunity_id=opp_id,
        reviewer="AI Technical Lead",
        decision=review_output.decision,
        confidence=review_output.confidence,
        reasoning=_ensure_str(review_output.reasoning),
        evidence=_ensure_str(review_output.evidence),
        risks=json.dumps(review_output.risks),
        recommendations=json.dumps(review_output.recommendations),
        escalation_required=review_output.escalation_required,
        findings=json.dumps(review_output.findings),
        assumptions=json.dumps(review_output.assumptions),
        missing_information=json.dumps(review_output.missing_information),
        clarification_questions=json.dumps(review_output.clarification_questions),
        reviewer_metadata=json.dumps({"model": "gemini-2.5-flash"}),
        processing_metadata=json.dumps({"latency_ms": 115.0})
    )
    db.add(db_review)
    db.commit()
    return review_output

@router.get("/{id}/reviews", response_model=AllReviewsStatusResponse)
def get_reviews_status(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)

    # Fetch reviews
    fin = db.query(FinancialReview).filter(FinancialReview.opportunity_id == opp_id).first()
    leg = db.query(LegalReview).filter(LegalReview.opportunity_id == opp_id).first()
    ops = db.query(OperationsReview).filter(OperationsReview.opportunity_id == opp_id).first()
    tec = db.query(TechnicalReview).filter(TechnicalReview.opportunity_id == opp_id).first()

    def build_status(r, name):
        if not r:
            return DepartmentStatusResponse(status="PENDING")
        
        status_val = "REVIEWED"
        if r.is_overridden:
            status_val = "OVERRIDDEN"
        elif r.escalation_required:
            status_val = "ESCALATED"

        try:
            findings = json.loads(r.findings) if r.findings else []
            risks = json.loads(r.risks) if r.risks else []
            recs = json.loads(r.recommendations) if r.recommendations else []
        except:
            findings, risks, recs = [], [], []

        return DepartmentStatusResponse(
            status=status_val,
            decision=r.decision,
            confidence=r.confidence,
            reviewer=r.reviewer,
            escalation_required=r.escalation_required,
            is_overridden=r.is_overridden,
            override_decision=r.override_decision,
            override_reason=r.override_reason,
            findings=findings,
            risks=risks,
            evidence=r.evidence,
            recommendations=recs
        )

    return AllReviewsStatusResponse(
        opportunity_id=opp_id,
        financial=build_status(fin, "financial"),
        legal=build_status(leg, "legal"),
        operations=build_status(ops, "operations"),
        technical=build_status(tec, "technical")
    )

@router.get("/{id}/risks", response_model=List[AggregatedRiskResponse])
def get_aggregated_risks(id: str, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    out = []

    # 1. Load Requirement/RFP Risks (from Phase 5 extraction)
    req_risks = db.query(RFPRisk).filter(RFPRisk.rfp_document_id == id, RFPRisk.is_deleted == False).all()
    for rr in req_risks:
        out.append(
            AggregatedRiskResponse(
                id=str(rr.id),
                severity=rr.severity or "Medium",
                likelihood=rr.likelihood or "Medium",
                business_impact=rr.business_impact or "General Impact",
                mitigation=rr.mitigation_suggestion or "Formulate standard mitigation",
                mitigation_suggestion=rr.mitigation_suggestion,
                owning_department="Requirement",
                description=rr.description,
                confidence=rr.confidence
            )
        )

    # 2. Financial risks
    fin = db.query(FinancialReview).filter(FinancialReview.opportunity_id == opp_id).first()
    if fin and fin.risks:
        for r in json.loads(fin.risks):
            out.append(AggregatedRiskResponse(severity="High", likelihood="Medium", business_impact="Cost Exposure Risk", mitigation="Detailed cost tracking plan", owning_department="Financial", description=r))

    # 3. Legal risks
    leg = db.query(LegalReview).filter(LegalReview.opportunity_id == opp_id).first()
    if leg and leg.risks:
        for r in json.loads(leg.risks):
            out.append(AggregatedRiskResponse(severity="High", likelihood="Low", business_impact="Contract Compliance Risk", mitigation="Add legal caveats to terms", owning_department="Legal", description=r))

    # 4. Operations risks
    ops = db.query(OperationsReview).filter(OperationsReview.opportunity_id == opp_id).first()
    if ops and ops.risks:
        for r in json.loads(ops.risks):
            out.append(AggregatedRiskResponse(severity="Medium", likelihood="Medium", business_impact="Deadline Conflict Risk", mitigation="Establish progress milestone dates", owning_department="Operations", description=r))

    # 5. Technical risks
    tec = db.query(TechnicalReview).filter(TechnicalReview.opportunity_id == opp_id).first()
    if tec and tec.risks:
        for r in json.loads(tec.risks):
            out.append(AggregatedRiskResponse(severity="Medium", likelihood="High", business_impact="Architecture Complexity Risk", mitigation="Develop deployment sandbox", owning_department="Technical", description=r))

    return out

@router.post("/{id}/reviews/{department}/approve")
def approve_review(id: str, department: str, req: ReviewApproveRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)
    
    # Find matching review model
    if department == "financial":
        rev = db.query(FinancialReview).filter(FinancialReview.opportunity_id == opp_id).first()
    elif department == "legal":
        rev = db.query(LegalReview).filter(LegalReview.opportunity_id == opp_id).first()
    elif department == "operations":
        rev = db.query(OperationsReview).filter(OperationsReview.opportunity_id == opp_id).first()
    elif department == "technical":
        rev = db.query(TechnicalReview).filter(TechnicalReview.opportunity_id == opp_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid department name")

    if not rev:
        raise HTTPException(status_code=404, detail="Department review not found")

    # Update approval state
    rev.is_overridden = False
    rev.reviewer = req.reviewer
    db.commit()
    return {"message": f"{department} review approved successfully"}

@router.post("/{id}/reviews/{department}/override")
def override_review(id: str, department: str, req: ReviewOverrideRequest, db: Session = Depends(get_db)):
    opp_id = get_opportunity_id(id, db)

    if department == "financial":
        rev = db.query(FinancialReview).filter(FinancialReview.opportunity_id == opp_id).first()
    elif department == "legal":
        rev = db.query(LegalReview).filter(LegalReview.opportunity_id == opp_id).first()
    elif department == "operations":
        rev = db.query(OperationsReview).filter(OperationsReview.opportunity_id == opp_id).first()
    elif department == "technical":
        rev = db.query(TechnicalReview).filter(TechnicalReview.opportunity_id == opp_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid department name")

    if not rev:
        raise HTTPException(status_code=404, detail="Department review not found")

    # Record history
    hist = ReviewOverrideHistory(
        opportunity_id=opp_id,
        department=department,
        previous_decision=rev.decision,
        new_decision=req.new_decision,
        override_reason=req.override_reason,
        overridden_by=req.overridden_by,
        timestamp=datetime.utcnow()
    )
    db.add(hist)

    # Perform override updates
    rev.is_overridden = True
    rev.override_decision = req.new_decision
    rev.override_reason = req.override_reason
    rev.overridden_by = req.overridden_by
    rev.override_timestamp = datetime.utcnow()
    db.commit()

    return {"message": f"{department} review override logged successfully"}
