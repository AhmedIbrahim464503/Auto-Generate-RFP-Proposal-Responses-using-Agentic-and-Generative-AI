import os
import time
import json
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
from groq import Groq
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument
from backend.app.models.review import FinancialReview, LegalReview, OperationsReview, TechnicalReview
from backend.app.models.requirement_intelligence import RFPRisk, ComplianceObligation
from backend.app.models.qualification import QualificationDecision, QualificationScoringBreakdown
from backend.app.services.qualification_rules import QualificationRulesService
from backend.app.schemas.qualification import QualificationExplanationOutput

logger = logging.getLogger("app")

PROMPT_REGISTRY = {
    "v1.0": {
        "qualification_instruction": (
            "You are a Principal Enterprise Capture Consultant and Executive Decision Analyst. "
            "Review the Opportunity details, department reviews, risks, evaluation criteria, "
            "and calculated Opportunity Score. Generate a structured Win Probability (0-100) and "
            "detailed executive decision justification. Be realistic, balance positive and negative factors, "
            "identify blockers, and outline recommended actions."
        )
    }
}

class QualificationEngineService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = "llama-3.3-70b-versatile"
        self.prompt_version = "v1.0"

        if self.api_key and self.api_key != "your-api-key-here":
            self.client = Groq(api_key=self.api_key)
            logger.info(f"QualificationEngineService initialized with Groq Model: {self.model_name}")
        else:
            self.client = None
            logger.warning("QualificationEngineService: GROQ_API_KEY not found. Fallback mockup engine active.")

    def _clean_json(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        first_brace = text.find('{')
        if first_brace != -1:
            last_brace = text.rfind('}')
            if last_brace != -1:
                text = text[first_brace:last_brace+1]
        return text

    def run_inference_with_retry(self, prompt: str, system_instruction: str, schema: Any, retries: int = 3) -> Optional[str]:
        if not self.client:
            return None

        schema_hint = 'You MUST return ONLY valid JSON object with keys: "executive_summary", "key_strengths", "critical_risks", "mitigation_strategies", "next_steps".'
        full_sys = f"{system_instruction}\n\n{schema_hint}"
        models_to_try = [self.model_name, "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

        for model in models_to_try:
            for attempt in range(retries):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": full_sys},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=4096,
                        response_format={"type": "json_object"}
                    )
                    return self._clean_json(response.choices[0].message.content)
                except Exception as e:
                    err_str = str(e)
                    logger.warning(f"Groq API attempt {attempt+1} with model {model} failed: {err_str}")
                    if "429" in err_str or "rate_limit" in err_str.lower():
                        logger.warning(f"Rate limit hit on {model}, falling back to next available Groq model.")
                        break
                    if attempt == retries - 1 and model == models_to_try[-1]:
                        return None
                    time.sleep(1)

    def calculate_opportunity_score_and_run(self, db: Session, opportunity_id: str, scope_key: str = "global") -> QualificationDecision:
        # 1. Fetch Active Ruleset Config
        ruleset = QualificationRulesService.get_active_ruleset(db, scope_key=scope_key)
        rules = json.loads(ruleset.rules_payload)
        weights = rules.get("weights", {})
        veto_rules = rules.get("veto_rules", {})
        blockers_list = rules.get("blockers", [])

        # 2. Fetch Department Reviews
        fin_rev = db.query(FinancialReview).filter(FinancialReview.opportunity_id == opportunity_id).first()
        leg_rev = db.query(LegalReview).filter(LegalReview.opportunity_id == opportunity_id).first()
        ops_rev = db.query(OperationsReview).filter(OperationsReview.opportunity_id == opportunity_id).first()
        tech_rev = db.query(TechnicalReview).filter(TechnicalReview.opportunity_id == opportunity_id).first()

        # 3. Calculate dimension sub-scores (0-100 scale)
        # Strategic Fit
        strategic_fit = 85.0  # default baseline
        
        # Capability Alignment
        ops_score = 100.0 if ops_rev and ops_rev.decision == "GO" else (60.0 if ops_rev and ops_rev.decision == "CONDITIONALLY_GO" else 20.0)
        tech_score = 100.0 if tech_rev and tech_rev.decision == "GO" else (60.0 if tech_rev and tech_rev.decision == "CONDITIONALLY_GO" else 20.0)
        capability = (ops_score + tech_score) / 2.0

        # Financial Viability
        financial = 100.0 if fin_rev and fin_rev.decision == "GO" else (60.0 if fin_rev and fin_rev.decision == "CONDITIONALLY_GO" else 20.0)

        # Technical Readiness
        technical_readiness = 100.0 if tech_rev and tech_rev.decision == "GO" else (70.0 if tech_rev and tech_rev.decision == "CONDITIONALLY_GO" else 30.0)

        # Compliance Readiness
        compliance_readiness = 90.0 if leg_rev and leg_rev.decision == "GO" else (60.0 if leg_rev and leg_rev.decision == "CONDITIONALLY_GO" else 30.0)

        # Fetch all document IDs associated with this opportunity to query document-linked child records
        doc_ids = [d.id for d in db.query(RFPDocument).filter(RFPDocument.opportunity_id == opportunity_id, RFPDocument.is_deleted == False).all()]

        # Risk Score
        risks = db.query(RFPRisk).filter(RFPRisk.rfp_document_id.in_(doc_ids)).all() if doc_ids else []
        risk_score = 100.0
        if risks:
            high_risks = sum(1 for r in risks if r.severity == "HIGH")
            medium_risks = sum(1 for r in risks if r.severity == "MEDIUM")
            risk_score = max(20.0, 100.0 - (high_risks * 15.0) - (medium_risks * 5.0))

        # Relationship
        relationship_score = 75.0

        # Complexity
        # More obligations/requirements implies higher complexity, which lowers the raw opportunity score
        obligations_count = db.query(ComplianceObligation).filter(ComplianceObligation.rfp_document_id.in_(doc_ids)).count() if doc_ids else 0
        complexity = max(40.0, 100.0 - (obligations_count * 2.0))

        sub_scores = {
            "strategic_fit": strategic_fit,
            "capability": capability,
            "financial": financial,
            "technical_readiness": technical_readiness,
            "compliance_readiness": compliance_readiness,
            "risk": risk_score,
            "relationship": relationship_score,
            "complexity": complexity
        }

        # Calculate Overall Opportunity Score
        opportunity_score = 0.0
        for dim, weight in weights.items():
            if dim in sub_scores:
                opportunity_score += sub_scores[dim] * weight

        # 4. Check Blockers and Veto Rules
        has_veto = False
        blockers_triggered = []

        if veto_rules.get("legal_no_go_veto") and leg_rev and leg_rev.decision == "NO_GO":
            has_veto = True
            blockers_triggered.append("Legal veto: Legal review returned NO_GO")
        if veto_rules.get("financial_no_go_veto") and fin_rev and fin_rev.decision == "NO_GO":
            has_veto = True
            blockers_triggered.append("Financial veto: Financial review returned NO_GO")

        # Specific blockers
        # Net Net insurance blocker checking
        if fin_rev and fin_rev.findings and "greater than $5M limit" in fin_rev.findings:
            if "insurance_limit_gt_10M" in blockers_list or "insurance_limit_gt_5M" in blockers_list or True:
                has_veto = True
                blockers_triggered.append("Insurance requirement exceeds allowable thresholds.")

        # Determine Recommendation Outcomes
        escalation_cutoff = rules.get("risk_thresholds", {}).get("escalation_score_cutoff", 65.0)
        
        if has_veto or opportunity_score < 50.0:
            rec = "NO_GO"
        elif fin_rev.escalation_required if fin_rev else False or opportunity_score < escalation_cutoff:
            rec = "ESCALATE"
        elif opportunity_score >= 80.0:
            rec = "GO"
        else:
            rec = "GO_WITH_CONDITIONS"

        # 5. Invoke LLM for Win Probability estimation and structured explanation
        prompt = (
            f"Opportunity ID: {opportunity_id}\n"
            f"Opportunity Score: {opportunity_score:.2f}/100\n"
            f"Calculated Recommendation: {rec}\n"
            f"Department Reviews Decisions:\n"
            f"- Financial: {fin_rev.decision if fin_rev else 'PENDING'}\n"
            f"- Legal: {leg_rev.decision if leg_rev else 'PENDING'}\n"
            f"- Operations: {ops_rev.decision if ops_rev else 'PENDING'}\n"
            f"- Technical: {tech_rev.decision if tech_rev else 'PENDING'}\n"
            f"Blockers Triggered: {', '.join(blockers_triggered) if blockers_triggered else 'None'}\n"
            f"Sub-scores Breakdown: {json.dumps(sub_scores)}\n"
        )

        response = self.run_inference_with_retry(
            prompt,
            PROMPT_REGISTRY[self.prompt_version]["qualification_instruction"],
            QualificationExplanationOutput
        )

        if response:
            try:
                data = json.loads(response)
                explanation = QualificationExplanationOutput(**data)
            except Exception as e:
                logger.error(f"Failed to parse Gemini Qualification response: {str(e)}")
                explanation = self._mock_explanation(rec, opportunity_score, blockers_triggered)
        else:
            explanation = self._mock_explanation(rec, opportunity_score, blockers_triggered)

        # 6. Save results to DB
        # Check if decision already exists
        decision = db.query(QualificationDecision).filter(
            QualificationDecision.opportunity_id == opportunity_id
        ).first()

        if not decision:
            decision = QualificationDecision(
                opportunity_id=opportunity_id,
                recommendation=rec,
                created_at=datetime.utcnow()
            )
            db.add(decision)
            db.flush()

        decision.status = "DRAFT"
        decision.recommendation = rec
        decision.executive_summary = explanation.executive_summary
        decision.confidence = explanation.confidence
        decision.reasoning = explanation.reasoning
        decision.evidence_json = json.dumps(explanation.evidence)
        decision.positive_factors = json.dumps(explanation.positive_factors)
        decision.negative_factors = json.dumps(explanation.negative_factors)
        decision.blocking_issues = json.dumps(explanation.blocking_issues + blockers_triggered)
        decision.mitigating_factors = json.dumps(explanation.mitigating_factors)
        decision.recommended_actions = json.dumps(explanation.recommended_actions)
        decision.escalation_requirements = json.dumps(explanation.escalation_requirements)
        decision.outstanding_clarifications = json.dumps(explanation.outstanding_clarifications)
        decision.next_steps = json.dumps(explanation.next_steps)
        decision.business_impact = explanation.business_impact
        
        decision.opportunity_score = opportunity_score
        decision.estimated_win_probability = explanation.estimated_win_probability
        decision.win_probability_explanation = explanation.win_probability_explanation
        
        decision.prompt_version = self.prompt_version
        decision.model_version = self.model_name
        decision.rule_version = ruleset.version
        decision.updated_at = datetime.utcnow()

        # Update Scoring Breakdown table
        db.query(QualificationScoringBreakdown).filter(
            QualificationScoringBreakdown.qualification_id == decision.id
        ).delete()

        for dim, weight in weights.items():
            if dim in sub_scores:
                breakdown = QualificationScoringBreakdown(
                    qualification_id=decision.id,
                    dimension=dim,
                    raw_score=sub_scores[dim],
                    weight=weight,
                    weighted_score=sub_scores[dim] * weight,
                    details_json=json.dumps({"sub_score": sub_scores[dim]})
                )
                db.add(breakdown)

        db.commit()
        db.refresh(decision)
        return decision

    def _mock_explanation(self, recommendation: str, opportunity_score: float, blockers: List[str]) -> QualificationExplanationOutput:
        win_prob = 80.0 if recommendation == "GO" else (60.0 if recommendation == "GO_WITH_CONDITIONS" else (40.0 if recommendation == "ESCALATE" else 15.0))
        
        return QualificationExplanationOutput(
            executive_summary="Opportunity assessment complete. Win probability estimated based on departmental inputs.",
            confidence=0.95,
            reasoning=f"Overall evaluation score is {opportunity_score:.1f}. Core capabilities align with requirements.",
            evidence=["RFP document outlines standard business conditions."],
            positive_factors=["SPS Technical capabilities match standard configuration requirements.", "Operations delivery schedules are realistic."],
            negative_factors=["Legal review and liability conditions require close auditing."],
            blocking_issues=blockers,
            mitigating_factors=["Partner dependencies will be backed by service-level agreements."],
            recommended_actions=["Schedule formal meeting to review Legal indemnities."],
            escalation_requirements=["Finance sign-off required if Net30 terms not met."],
            outstanding_clarifications=["Are there any regional sub-contracting restrictions?"],
            next_steps=["Send clarification list to purchasing contact.", "Prepare pricing outline."],
            business_impact="Standard margin potential with standard resource allocation.",
            estimated_win_probability=win_prob,
            win_probability_explanation=f"Estimated at {win_prob}% due to capabilites alignment vs. identified legal risks."
        )

qualification_engine_service = QualificationEngineService()
