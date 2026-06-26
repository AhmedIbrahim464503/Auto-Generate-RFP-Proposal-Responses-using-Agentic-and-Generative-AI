from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProposalCitationResponse(BaseModel):
    id: str
    generated_section_id: str
    paragraph_index: int
    knowledge_asset_id: Optional[str] = None
    knowledge_chunk_id: Optional[str] = None
    requirement_id: Optional[str] = None
    compliance_item_id: Optional[str] = None
    source_title: str
    source_location: Optional[str] = None
    confidence: float

class ProposalEvidenceLinkResponse(BaseModel):
    id: str
    generated_section_id: str
    source_type: str
    source_id: str
    relevance_score: float

class GeneratedSectionResponse(BaseModel):
    id: str
    proposal_plan_id: str
    proposal_section_id: str
    content: str
    tone_style: str
    word_count: int
    confidence: float
    quality_score: float
    prompt_version: str
    model_version: str
    created_at: datetime
    updated_at: datetime
    citations: List[ProposalCitationResponse] = []
    evidence_links: List[ProposalEvidenceLinkResponse] = []

class GenerationHistoryResponse(BaseModel):
    id: str
    proposal_plan_id: str
    proposal_section_id: str
    action: str
    actor: str
    comments: Optional[str] = None
    content_snapshot: str
    timestamp: datetime

class ProposalGenerateRequest(BaseModel):
    tone_style: Optional[str] = "Professional"
    actor: Optional[str] = "Proposal Writer"

class ProposalSectionGenerateRequest(BaseModel):
    tone_style: Optional[str] = "Professional"
    actor: Optional[str] = "Proposal Writer"
    additional_context: Optional[str] = None
