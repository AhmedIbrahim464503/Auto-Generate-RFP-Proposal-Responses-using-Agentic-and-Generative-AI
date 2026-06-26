import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.proposal_review import (
    ProposalReviewSession, ProposalReviewFinding, ProposalReviewScore,
    ProposalReviewWorkflow, ProposalReviewAudit
)
from backend.app.models.proposal_generation import GeneratedSection, GenerationHistory
from backend.app.core.agents.review_agents import (
    ComplianceReviewAgent, TechnicalReviewAgent, LegalReviewAgent,
    FinancialReviewAgent, OperationsReviewAgent, ExecutiveReviewAgent,
    EditorialReviewAgent, GrammarReadabilityAgent, CitationValidationAgent,
    RequirementCoverageAgent, ConsistencyReviewAgent, SecurityReviewAgent,
    RiskReviewAgent, EvaluationAlignmentAgent
)
from backend.app.core.agents.implementations import WriterAgent

class ReviewCoordinatorService:
    def __init__(self):
        self.agents_map = {
            "compliance_review": ComplianceReviewAgent(),
            "technical_review": TechnicalReviewAgent(),
            "legal_review": LegalReviewAgent(),
            "financial_review": FinancialReviewAgent(),
            "operations_review": OperationsReviewAgent(),
            "executive_review": ExecutiveReviewAgent(),
            "editorial_review": EditorialReviewAgent(),
            "grammar_readability_review": GrammarReadabilityAgent(),
            "citation_validation_review": CitationValidationAgent(),
            "requirement_coverage_review": RequirementCoverageAgent(),
            "consistency_review": ConsistencyReviewAgent(),
            "security_review": SecurityReviewAgent(),
            "risk_review": RiskReviewAgent(),
            "evaluation_alignment_review": EvaluationAlignmentAgent()
        }

    def run_review_workflow(self, db: Session, proposal_plan_id: str, workflow_id: Optional[str] = None) -> ProposalReviewSession:
        # Determine stages from workflow if provided, otherwise default to all 14 review stages
        stages = [
            "compliance_review", "technical_review", "legal_review", "financial_review",
            "operations_review", "executive_review", "editorial_review", "grammar_readability_review",
            "citation_validation_review", "requirement_coverage_review", "consistency_review",
            "security_review", "risk_review", "evaluation_alignment_review"
        ]
        
        if workflow_id:
            workflow = db.query(ProposalReviewWorkflow).filter(ProposalReviewWorkflow.id == workflow_id).first()
            if workflow and workflow.stages:
                stages = workflow.stages.get("stages", stages)

        # Create session
        session = ProposalReviewSession(
            proposal_plan_id=proposal_plan_id,
            status="AWAIT_HUMAN_REVIEW",
            overall_score=0.0,
            meta_payload={"stages_evaluated": stages}
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Query all generated sections
        sections = db.query(GeneratedSection).filter(GeneratedSection.proposal_plan_id == proposal_plan_id).all()
        
        total_score_sum = 0.0
        score_count = 0

        for section in sections:
            section_data = {
                "proposal_plan_id": proposal_plan_id,
                "section_id": section.proposal_section_id,
                "content": section.content,
                "tone_style": section.tone_style
            }

            for stage in stages:
                agent = self.agents_map.get(stage)
                if not agent:
                    continue

                output = agent.run(db, section_data)
                
                # Extract findings
                findings = output.metadata.get("findings", [])
                for f in findings:
                    finding = ProposalReviewFinding(
                        session_id=session.id,
                        generated_section_id=section.id,
                        agent_id=stage,
                        category=f.get("category", stage),
                        severity=f.get("severity", "warning"),
                        message=f.get("message", "Validation failed"),
                        evidence=f.get("evidence")
                    )
                    db.add(finding)

                # Extract score
                score_val = output.metadata.get("score", 1.0)
                score = ProposalReviewScore(
                    session_id=session.id,
                    generated_section_id=section.id,
                    metric_name=stage,
                    score=score_val,
                    weight=1.0
                )
                db.add(score)
                
                total_score_sum += score_val
                score_count += 1

        if score_count > 0:
            session.overall_score = total_score_sum / score_count

        # Decide overall status
        critical_findings = db.query(ProposalReviewFinding).filter(
            ProposalReviewFinding.session_id == session.id,
            ProposalReviewFinding.severity == "critical"
        ).count()

        if critical_findings > 0:
            session.status = "BLOCKED"
        elif session.overall_score < 0.7:
            session.status = "PASS_WITH_REVISIONS"
        else:
            session.status = "PASS"

        db.commit()
        db.refresh(session)
        return session

    def refine_proposal_sections(self, db: Session, session_id: str) -> ProposalReviewSession:
        session = db.query(ProposalReviewSession).filter(ProposalReviewSession.id == session_id).first()
        if not session:
            raise ValueError(f"Review Session {session_id} not found.")

        # Get findings that are warnings or critical
        critical_findings = db.query(ProposalReviewFinding).filter(
            ProposalReviewFinding.session_id == session_id,
            ProposalReviewFinding.severity.in_(["warning", "critical"])
        ).all()

        refined_section_ids = set()
        writer = WriterAgent()

        for finding in critical_findings:
            section_id = finding.generated_section_id
            if section_id in refined_section_ids:
                continue

            section = db.query(GeneratedSection).filter(GeneratedSection.id == section_id).first()
            if not section:
                continue

            # Check retry counts (simulated check in meta_payload to avoid infinite loops)
            refinements_payload = session.meta_payload or {}
            retries = refinements_payload.get("retries", {})
            current_retry = retries.get(section.id, 0)
            if current_retry >= 3:
                # Max retry limit hit
                continue

            # RunWriterAgent regeneration
            section_data = {
                "proposal_plan_id": session.proposal_plan_id,
                "section_id": section.proposal_section_id,
                "tone_style": section.tone_style,
                "actor": "Refinement Engine",
                "additional_context": f"Refinement feedback: {finding.message} (Category: {finding.category})"
            }
            
            # Write a snapshot to history
            history = GenerationHistory(
                proposal_plan_id=session.proposal_plan_id,
                proposal_section_id=section.proposal_section_id,
                action="REGENERATE",
                actor="Refinement Engine",
                comments=f"Refining section due to {finding.category} finding: {finding.message}",
                content_snapshot=section.content
            )
            db.add(history)

            # Re-generate content
            writer.run(db, section_data)
            
            # Increment retry count
            current_retry += 1
            retries[section.id] = current_retry
            refinements_payload["retries"] = retries
            session.meta_payload = refinements_payload
            
            refined_section_ids.add(section_id)

        # Log audit action
        audit = ProposalReviewAudit(
            session_id=session.id,
            action="refine",
            actor="Refinement Engine",
            payload={"sections_refined": list(refined_section_ids)}
        )
        db.add(audit)

        # Re-run workflow review to fetch new scores/findings
        db.commit()
        return self.run_review_workflow(db, session.proposal_plan_id)

    def record_human_decision(self, db: Session, session_id: str, action: str, actor: str, message: Optional[str] = None, override_payload: Optional[Dict[str, Any]] = None) -> ProposalReviewSession:
        session = db.query(ProposalReviewSession).filter(ProposalReviewSession.id == session_id).first()
        if not session:
            raise ValueError(f"Review Session {session_id} not found.")

        if action == "approve":
            session.status = "PASS"
        elif action == "reject":
            session.status = "BLOCKED"
        elif action == "override":
            session.status = override_payload.get("new_status", "PASS")
            if "overall_score" in override_payload:
                session.overall_score = override_payload["overall_score"]

        # Log audit record
        audit = ProposalReviewAudit(
            session_id=session_id,
            action=action,
            actor=actor,
            payload={"message": message, "override_payload": override_payload}
        )
        db.add(audit)
        db.commit()
        db.refresh(session)
        return session

review_coordinator_service = ReviewCoordinatorService()
