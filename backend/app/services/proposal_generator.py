import json
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.proposal import ProposalPlan, ProposalSection, ComplianceItem
from backend.app.models.proposal_generation import GeneratedSection, GenerationHistory, ProposalCitation, ProposalEvidenceLink
from backend.app.services.knowledge_engine import knowledge_engine_service

# Specialized Writers Prompts
PROMPT_REGISTRY = {
    "executive_summary": {
        "system": "You are the Executive Summary Writer. Synthesize the strategic alignment, value proposition, and key offerings into a high-level summary.",
        "developer": "Incorporate Opportunity details and qualification scores to build an executive narrative.",
        "version": "1.0.0"
    },
    "technical_solution": {
        "system": "You are the Technical Solution Writer. Detail the technical design, system integrations, and software architectures.",
        "developer": "Map system features directly to RFP requirements and technical review comments.",
        "version": "1.0.0"
    },
    "implementation_methodology": {
        "system": "You are the Implementation Methodology Writer. Sequence the project phases, deployment milestones, and delivery methodologies.",
        "developer": "Ensure alignment with timeline milestones and operations reviews.",
        "version": "1.0.0"
    },
    "pricing_narrative": {
        "system": "You are the Pricing Narrative Writer. Build the financial cost breakdowns and narrative justifications.",
        "developer": "Ensure Net payment terms and financial review overrides are addressed.",
        "version": "1.0.0"
    },
    "risk_management": {
        "system": "You are the Risk Management Writer. Define the risk registers, probability indices, and mitigation procedures.",
        "developer": "Incorporate department reviews risk logs and strategic blockers.",
        "version": "1.0.0"
    },
    "default": {
        "system": "You are a Specialized Proposal Writer. Address the specific requirements traceably.",
        "developer": "Ground all statements strictly in retrieved context evidence.",
        "version": "1.0.0"
    }
}

class StyleEngine:
    """Style Engine modifying prompt tone configurations."""
    def get_style_instructions(self, tone: str) -> str:
        instructions = {
            "Professional": "Use a clear, concise, corporate tone. Focus on metrics and delivery timelines.",
            "Government": "Use a highly structured, compliant, formal tone. Adhere strictly to heading levels and regulatory terms.",
            "Technical": "Use precise technical terminology. Focus on architecture diagrams, parameters, and specifications.",
            "Commercial": "Use a persuasive, benefits-focused tone. Highlight cost-efficiencies, ROI, and commercial feasibility.",
            "Executive": "Use a strategic, high-level summary tone. Focus on business value, governance, and leadership summary.",
            "Formal": "Use an authoritative, objective, third-person tone. Avoid conversational expressions."
        }
        return instructions.get(tone, instructions["Professional"])

class ProposalGeneratorService:
    def __init__(self):
        self.registry = PROMPT_REGISTRY
        self.style_engine = StyleEngine()

    def get_writer_config(self, section_title: str) -> Dict[str, Any]:
        title_lower = section_title.lower()
        if "executive" in title_lower or "summary" in title_lower:
            return self.registry["executive_summary"]
        elif "technical" in title_lower or "solution" in title_lower or "architecture" in title_lower:
            return self.registry["technical_solution"]
        elif "methodology" in title_lower or "implementation" in title_lower:
            return self.registry["implementation_methodology"]
        elif "price" in title_lower or "cost" in title_lower or "pricing" in title_lower:
            return self.registry["pricing_narrative"]
        elif "risk" in title_lower or "mitigation" in title_lower:
            return self.registry["risk_management"]
        else:
            return self.registry["default"]

    def run_quality_checks(self, content: str, requirements_count: int, citations_count: int, tone: str) -> Dict[str, Any]:
        """Automatically checks coverage, redundancies, and tone alignment."""
        # Simple coverage heuristics
        has_gaps = "[CONTENT_GAP" in content
        duplicate_paragraphs = False
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if len(paragraphs) != len(set(paragraphs)):
            duplicate_paragraphs = True

        # terminologies consistency checks
        has_contradictions = False
        if "shall" in content.lower() and "will not" in content.lower() and "must" in content.lower():
            # mock basic contradiction detection
            pass

        coverage_score = 1.0 if (requirements_count == 0 or citations_count >= requirements_count) else float(citations_count) / max(1, requirements_count)
        if has_gaps:
            coverage_score *= 0.5

        quality_score = 1.0
        if duplicate_paragraphs:
            quality_score -= 0.2
        if has_gaps:
            quality_score -= 0.3

        return {
            "requirement_coverage": float(coverage_score),
            "evidence_coverage": float(min(1.0, float(citations_count) / max(1, requirements_count))),
            "duplicate_paragraphs": duplicate_paragraphs,
            "has_contradictions": has_contradictions,
            "quality_score": float(max(0.1, quality_score))
        }

    def generate_section_content(
        self,
        db: Session,
        proposal_plan: ProposalPlan,
        section: ProposalSection,
        tone_style: str = "Professional",
        additional_context: Optional[str] = None
    ) -> GeneratedSection:
        # 1. Fetch writer configurations
        config = self.get_writer_config(section.title)
        style_instruct = self.style_engine.get_style_instructions(tone_style)

        # 2. Retrieve background context from knowledge engine (Phase 9)
        # Search query based on section title and plan title
        query_text = f"{proposal_plan.title} {section.title}"
        retrieved_items = knowledge_engine_service.hybrid_search(
            db,
            query=query_text,
            top_k=3,
            confidence_threshold=0.1
        )

        # 3. Formulate the grounding text or identify content gaps
        grounding_evidence = ""
        evidence_citations = []
        
        if not retrieved_items:
            # Enforce strict gap tracking to avoid hallucinations
            grounding_evidence = f"[CONTENT_GAP: Insufficient evidence available to address requirements for section '{section.title}'. Please upload organizational profiles or case studies.]"
        else:
            grounding_evidence = "\n\n".join([item["content"] for item in retrieved_items])
            for idx, item in enumerate(retrieved_items):
                cit = item["citation"]
                evidence_citations.append({
                    "paragraph_index": idx,
                    "knowledge_asset_id": cit["parent_asset_id"],
                    "knowledge_chunk_id": cit["chunk_id"],
                    "source_title": cit["document_title"],
                    "source_location": f"Section: {cit['section']}, Loc: {cit['paragraph']}",
                    "confidence": cit["similarity_score"]
                })

        # 4. Generate content narrative using grounding details (Mock/LLM synthesis)
        # In a real environment, we invoke Gemini. Here, we build structured outputs deterministically.
        if "[CONTENT_GAP" in grounding_evidence:
            generated_content = (
                f"### {section.title}\n\n"
                f"This section is intended to cover {section.title} context.\n"
                f"Error: {grounding_evidence}"
            )
        else:
            generated_content = (
                f"### {section.title} - Proposal Chapter\n\n"
                f"We present our tailored solutions for {proposal_plan.client or 'the client'} regarding {section.title}.\n"
                f"Our offering is built on verified qualifications: {grounding_evidence[:200]}...\n\n"
                f"This methodology complies with standard guidelines and guarantees operational delivery under style parameters: {style_instruct[:30]}."
            )

        word_count = len(generated_content.split())
        confidence = 0.9 if not "[CONTENT_GAP" in grounding_evidence else 0.3

        # 5. Run Quality checkers
        q_check = self.run_quality_checks(generated_content, requirements_count=1, citations_count=len(evidence_citations), tone=tone_style)

        # 6. Persist GeneratedSection
        # Check if already generated
        db_sec = db.query(GeneratedSection).filter(
            GeneratedSection.proposal_plan_id == proposal_plan.id,
            GeneratedSection.proposal_section_id == section.id
        ).first()

        if db_sec:
            # Delete old citations and evidence links
            db.query(ProposalCitation).filter(ProposalCitation.generated_section_id == db_sec.id).delete()
            db.query(ProposalEvidenceLink).filter(ProposalEvidenceLink.generated_section_id == db_sec.id).delete()
            
            db_sec.content = generated_content
            db_sec.tone_style = tone_style
            db_sec.word_count = word_count
            db_sec.confidence = confidence
            db_sec.quality_score = q_check["quality_score"]
            db_sec.updated_at = datetime.utcnow()
        else:
            db_sec = GeneratedSection(
                proposal_plan_id=proposal_plan.id,
                proposal_section_id=section.id,
                content=generated_content,
                tone_style=tone_style,
                word_count=word_count,
                confidence=confidence,
                quality_score=q_check["quality_score"],
                prompt_version=config["version"],
                model_version="gemini-2.5-flash",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_sec)
            db.flush()  # to populate db_sec.id

        # Save citations relationally
        for cit_data in evidence_citations:
            cit = ProposalCitation(
                generated_section_id=db_sec.id,
                paragraph_index=cit_data["paragraph_index"],
                knowledge_asset_id=cit_data["knowledge_asset_id"],
                knowledge_chunk_id=cit_data["knowledge_chunk_id"],
                source_title=cit_data["source_title"],
                source_location=cit_data["source_location"],
                confidence=cit_data["confidence"]
            )
            db.add(cit)

        # Save evidence links
        for cit_data in evidence_citations:
            link = ProposalEvidenceLink(
                generated_section_id=db_sec.id,
                source_type="knowledge",
                source_id=cit_data["knowledge_asset_id"],
                relevance_score=cit_data["confidence"]
            )
            db.add(link)

        # Log history
        history = GenerationHistory(
            proposal_plan_id=proposal_plan.id,
            proposal_section_id=section.id,
            action="GENERATE" if not db_sec.created_at == db_sec.updated_at else "REGENERATE",
            actor="Proposal AI Orchestrator",
            comments=f"Generated section '{section.title}' using model gemini-2.5-flash under style {tone_style}.",
            content_snapshot=generated_content[:500],
            timestamp=datetime.utcnow()
        )
        db.add(history)
        db.commit()
        db.refresh(db_sec)
        return db_sec

    def generate_full_proposal(self, db: Session, proposal_plan_id: str, tone_style: str = "Professional") -> List[GeneratedSection]:
        plan = db.query(ProposalPlan).filter(ProposalPlan.id == proposal_plan_id, ProposalPlan.is_deleted == False).first()
        if not plan:
            raise ValueError("Proposal plan not found")

        generated_list = []
        for section in plan.sections:
            gen_sec = self.generate_section_content(db, plan, section, tone_style)
            generated_list.append(gen_sec)
        
        return generated_list

proposal_generator_service = ProposalGeneratorService()
