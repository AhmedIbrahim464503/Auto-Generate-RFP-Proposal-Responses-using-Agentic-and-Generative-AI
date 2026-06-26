from typing import List, Optional
from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.proposal import ProposalPlan, ProposalSection
from backend.app.models.proposal_generation import GeneratedSection, GenerationHistory, ProposalCitation, ProposalEvidenceLink
from backend.app.services.proposal_generator import proposal_generator_service
from backend.app.schemas.proposal_generation import (
    GeneratedSectionResponse,
    GenerationHistoryResponse,
    ProposalCitationResponse,
    ProposalEvidenceLinkResponse,
    ProposalGenerateRequest,
    ProposalSectionGenerateRequest
)

router = APIRouter()

def serialize_generated_section(gs: GeneratedSection) -> GeneratedSectionResponse:
    citations = []
    for c in gs.citations:
        citations.append(ProposalCitationResponse(
            id=str(c.id),
            generated_section_id=str(c.generated_section_id),
            paragraph_index=c.paragraph_index,
            knowledge_asset_id=str(c.knowledge_asset_id) if c.knowledge_asset_id else None,
            knowledge_chunk_id=str(c.knowledge_chunk_id) if c.knowledge_chunk_id else None,
            requirement_id=str(c.requirement_id) if c.requirement_id else None,
            compliance_item_id=str(c.compliance_item_id) if c.compliance_item_id else None,
            source_title=c.source_title,
            source_location=c.source_location,
            confidence=c.confidence
        ))

    evidence_links = []
    for el in gs.evidence_links:
        evidence_links.append(ProposalEvidenceLinkResponse(
            id=str(el.id),
            generated_section_id=str(el.generated_section_id),
            source_type=el.source_type,
            source_id=str(el.source_id),
            relevance_score=el.relevance_score
        ))

    return GeneratedSectionResponse(
        id=str(gs.id),
        proposal_plan_id=str(gs.proposal_plan_id),
        proposal_section_id=str(gs.proposal_section_id),
        content=gs.content,
        tone_style=gs.tone_style,
        word_count=gs.word_count,
        confidence=gs.confidence,
        quality_score=gs.quality_score,
        prompt_version=gs.prompt_version,
        model_version=gs.model_version,
        created_at=gs.created_at,
        updated_at=gs.updated_at,
        citations=citations,
        evidence_links=evidence_links
    )

@router.post("/{id}/generate", response_model=List[GeneratedSectionResponse])
def generate_proposal(id: str, payload: ProposalGenerateRequest, db: Session = Depends(get_db)):
    plan = db.query(ProposalPlan).filter(ProposalPlan.id == id, ProposalPlan.is_deleted == False).first()
    if not plan:
        # Fallback to check by opportunity ID or return 404
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    try:
        sections = proposal_generator_service.generate_full_proposal(db, plan.id, tone_style=payload.tone_style)
        return [serialize_generated_section(s) for s in sections]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/generate/section/{section_id}", response_model=GeneratedSectionResponse)
def generate_section(
    id: str,
    section_id: str,
    payload: ProposalSectionGenerateRequest,
    db: Session = Depends(get_db)
):
    plan = db.query(ProposalPlan).filter(ProposalPlan.id == id, ProposalPlan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Proposal plan not found")

    section = db.query(ProposalSection).filter(
        ProposalSection.id == section_id,
        ProposalSection.proposal_plan_id == plan.id
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Proposal section not found")

    try:
        gs = proposal_generator_service.generate_section_content(
            db,
            proposal_plan=plan,
            section=section,
            tone_style=payload.tone_style,
            additional_context=payload.additional_context
        )
        return serialize_generated_section(gs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}/generated", response_model=List[GeneratedSectionResponse])
def get_generated_sections(id: str, db: Session = Depends(get_db)):
    sections = db.query(GeneratedSection).filter(GeneratedSection.proposal_plan_id == id).all()
    return [serialize_generated_section(s) for s in sections]

@router.get("/{id}/generation-history", response_model=List[GenerationHistoryResponse])
def get_generation_history(id: str, db: Session = Depends(get_db)):
    history = db.query(GenerationHistory).filter(GenerationHistory.proposal_plan_id == id).order_by(GenerationHistory.timestamp.desc()).all()
    out = []
    for h in history:
        out.append(GenerationHistoryResponse(
            id=str(h.id),
            proposal_plan_id=str(h.proposal_plan_id),
            proposal_section_id=str(h.proposal_section_id),
            action=h.action,
            actor=h.actor,
            comments=h.comments,
            content_snapshot=h.content_snapshot,
            timestamp=h.timestamp
        ))
    return out

@router.get("/{id}/citations", response_model=List[ProposalCitationResponse])
def get_proposal_citations(id: str, db: Session = Depends(get_db)):
    citations = db.query(ProposalCitation).join(GeneratedSection).filter(GeneratedSection.proposal_plan_id == id).all()
    out = []
    for c in citations:
        out.append(ProposalCitationResponse(
            id=str(c.id),
            generated_section_id=str(c.generated_section_id),
            paragraph_index=c.paragraph_index,
            knowledge_asset_id=str(c.knowledge_asset_id) if c.knowledge_asset_id else None,
            knowledge_chunk_id=str(c.knowledge_chunk_id) if c.knowledge_chunk_id else None,
            requirement_id=str(c.requirement_id) if c.requirement_id else None,
            compliance_item_id=str(c.compliance_item_id) if c.compliance_item_id else None,
            source_title=c.source_title,
            source_location=c.source_location,
            confidence=c.confidence
        ))
    return out
