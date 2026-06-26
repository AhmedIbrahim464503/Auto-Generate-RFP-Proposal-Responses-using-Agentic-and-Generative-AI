from typing import Any, Dict, List
import time
import uuid
from sqlalchemy.orm import Session
from backend.app.core.agents.base import BaseAgent
from backend.app.schemas.agent import AgentOutput
from backend.app.core.agents.implementations import StandardAgentExecutor

class ProposalReviewAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)

    def run(self, db: Session, section_data: Dict[str, Any], config: Dict[str, Any] = None) -> AgentOutput:
        # Standardized review logic block
        def logic(db_session: Session, sdata: Dict[str, Any], cfg: Dict[str, Any]):
            content = sdata.get("content", "")
            findings = []
            score = 0.95
            
            # Simple content checking for demo/testing purposes
            if len(content) < 100:
                findings.append({
                    "category": self.agent_id,
                    "severity": "warning",
                    "message": "Content is unusually brief, possibly lacking depth.",
                    "evidence": content
                })
                score = 0.70
                
            if "[CONTENT_GAP" in content:
                findings.append({
                    "category": self.agent_id,
                    "severity": "critical",
                    "message": "Unresolved content gap placeholder found.",
                    "evidence": content
                })
                score = 0.40

            return AgentOutput(
                decision="PASS" if score >= 0.8 else "PASS_WITH_REVISIONS" if score >= 0.5 else "BLOCKED",
                confidence=0.9,
                reasoning=f"Review agent {self.agent_id} completed evaluation of the section content.",
                evidence=[f["message"] for f in findings],
                risks=[],
                recommendations=[],
                processing_time_ms=0.0,
                metadata={"findings": findings, "score": score}
            )

        return StandardAgentExecutor.execute(db, self.agent_id, section_data, logic, config)


class ComplianceReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("compliance_review")


class TechnicalReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("technical_review")


class LegalReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("legal_review")


class FinancialReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("financial_review")


class OperationsReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("operations_review")


class ExecutiveReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("executive_review")


class EditorialReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("editorial_review")


class GrammarReadabilityAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("grammar_readability_review")


class CitationValidationAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("citation_validation_review")


class RequirementCoverageAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("requirement_coverage_review")


class ConsistencyReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("consistency_review")


class SecurityReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("security_review")


class RiskReviewAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("risk_review")


class EvaluationAlignmentAgent(ProposalReviewAgent):
    def __init__(self):
        super().__init__("evaluation_alignment_review")
