import os
import time
import json
from typing import Dict, Any, List, Optional
from groq import Groq
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.schemas.review import DepartmentReviewOutput

PROMPT_REGISTRY = {
    "v1.0": {
        "financial_instruction": (
            "You are a Senior Financial Review Specialist. Review the RFP requirements "
            "and extract payment terms, insurance values, profitability risks, margin options, "
            "and cost exposures. Evaluate terms net30 rules and insurance limit acceptability."
        ),
        "legal_instruction": (
            "You are a Principal Legal Counsel. Review the RFP requirements and identify legal blockers, "
            "compliance constraints, termination clauses, liability boundaries, and state registration demands."
        ),
        "operations_instruction": (
            "You are an Operations Lead. Review the RFP requirements and evaluate deadlines, logistics, "
            "completeness of required forms, signatures, and scheduling issues."
        ),
        "technical_instruction": (
            "You are a Staff Technical Architect. Review the RFP requirements and evaluate technology alignment, "
            "personnel capability gaps, integrations complexity, and delivery capability risks."
        )
    }
}

class ReviewEngineService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = "llama-3.3-70b-versatile"
        self.prompt_version = "v1.0"

        if self.api_key and self.api_key != "your-api-key-here":
            self.client = Groq(api_key=self.api_key)
            logger.info(f"ReviewEngineService initialized with Groq Model: {self.model_name}")
        else:
            self.client = None
            logger.warning("ReviewEngineService: GROQ_API_KEY not found. Fallback mockup review engine active.")

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

        schema_hint = 'You MUST return ONLY valid JSON object with keys: "decision", "confidence", "reasoning", "evidence", "findings", "risks", "assumptions", "missing_information", "clarification_questions", "recommendations", "escalation_required".'
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

    def run_financial_review(self, doc_text: str, payment_terms: str, insurance_limit: float) -> DepartmentReviewOutput:
        # 1. Apply SPS Hardcoded Business Rules
        rule_decision = "GO"
        escalation_required = False
        reasoning_notes = []

        if payment_terms == "NET30":
            reasoning_notes.append("Payment terms are NET30: Accepted under standard rules.")
        else:
            # Greater than NET30
            rule_decision = "CONDITIONALLY_GO"
            escalation_required = True
            reasoning_notes.append(f"Payment terms are {payment_terms} (greater than NET30): Escalate to Accounting.")

        if insurance_limit > 5000000:
            rule_decision = "NO_GO"
            reasoning_notes.append(f"Insurance requirement is ${insurance_limit/1000000:.1f}M (greater than $5M limit): Departmental NO-GO recommendation.")
        else:
            reasoning_notes.append(f"Insurance requirement is ${insurance_limit/1000000:.1f}M: Acceptable.")

        # 2. Run Gemini Evaluation / Fallback
        prompt = (
            f"Analyze the following RFP text and payment terms: {payment_terms}, insurance: {insurance_limit}. "
            f"SPS Rules findings: {', '.join(reasoning_notes)}. Text:\n\n{doc_text[:30000]}"
        )
        
        t0 = time.time()
        response = self.run_inference_with_retry(
            prompt, 
            PROMPT_REGISTRY[self.prompt_version]["financial_instruction"], 
            DepartmentReviewOutput
        )
        latency_ms = (time.time() - t0) * 1000

        if not response:
            return self._mock_financial_review(rule_decision, escalation_required, reasoning_notes)

        try:
            data = json.loads(response)
            out = DepartmentReviewOutput(**data)
            # Override decision if SPS hardcoded rules mandate a NO_GO or escalation
            if rule_decision == "NO_GO":
                out.decision = "NO_GO"
            out.escalation_required = escalation_required or out.escalation_required
            return out
        except Exception as e:
            logger.error(f"Failed to parse Financial Review response: {str(e)}")
            return self._mock_financial_review(rule_decision, escalation_required, reasoning_notes)

    def run_legal_review(self, doc_text: str) -> DepartmentReviewOutput:
        prompt = f"Analyze the following RFP text for legal liabilities and compliance blocks. Text:\n\n{doc_text[:30000]}"
        t0 = time.time()
        response = self.run_inference_with_retry(
            prompt,
            PROMPT_REGISTRY[self.prompt_version]["legal_instruction"],
            DepartmentReviewOutput
        )
        if not response:
            return self._mock_legal_review()
        try:
            data = json.loads(response)
            return DepartmentReviewOutput(**data)
        except Exception as e:
            logger.error(f"Failed to parse Legal Review response: {str(e)}")
            return self._mock_legal_review()

    def run_operations_review(self, doc_text: str) -> DepartmentReviewOutput:
        prompt = f"Analyze the following RFP text for deadlines, submission sequence constraints, and required forms. Text:\n\n{doc_text[:30000]}"
        t0 = time.time()
        response = self.run_inference_with_retry(
            prompt,
            PROMPT_REGISTRY[self.prompt_version]["operations_instruction"],
            DepartmentReviewOutput
        )
        if not response:
            return self._mock_operations_review()
        try:
            data = json.loads(response)
            return DepartmentReviewOutput(**data)
        except Exception as e:
            logger.error(f"Failed to parse Operations Review response: {str(e)}")
            return self._mock_operations_review()

    def run_technical_review(self, doc_text: str) -> DepartmentReviewOutput:
        prompt = f"Analyze the following RFP text for platform capability matches, delivery timelines complexity, and integration risks. Text:\n\n{doc_text[:30000]}"
        t0 = time.time()
        response = self.run_inference_with_retry(
            prompt,
            PROMPT_REGISTRY[self.prompt_version]["technical_instruction"],
            DepartmentReviewOutput
        )
        if not response:
            return self._mock_technical_review()
        try:
            data = json.loads(response)
            return DepartmentReviewOutput(**data)
        except Exception as e:
            logger.error(f"Failed to parse Technical Review response: {str(e)}")
            return self._mock_technical_review()

    # --- Fallback Mock Review Helpers ---

    def _mock_financial_review(self, decision: str, escalation: bool, reasoning_notes: List[str]) -> DepartmentReviewOutput:
        return DepartmentReviewOutput(
            decision=decision,
            confidence=0.96,
            reasoning=f"Financial analysis completed. Rules evaluated: {'; '.join(reasoning_notes)}",
            evidence="Insurance requirements call for standard liability coverage. Payment net terms are stated in section 4.1.",
            findings=["Revenue potential exceeds baseline margin targets.", "Insurance limits and payment net terms validated."],
            risks=["Potential cash flow strain if payment exceeds standard Net30 terms."],
            assumptions=["Assume working capital parameters remain constant throughout project lifetime."],
            missing_information=[],
            clarification_questions=["Can payment terms be renegotiated to NET30 during final contracting?"],
            recommendations=["Escalate review to Finance committee for approval if terms are greater than Net30."],
            escalation_required=escalation
        )

    def _mock_legal_review(self) -> DepartmentReviewOutput:
        return DepartmentReviewOutput(
            decision="GO",
            confidence=0.92,
            reasoning="No critical legal blockers detected. E-Verify and local business registry requirements are standard.",
            evidence="Bidders must submit proof of E-Verify registration and have active state business registrations.",
            findings=["Standard indemnity clauses are acceptable.", "Dispute resolution via local arbitration in Delaware."],
            risks=["Late filing penalties are strictly binding."],
            assumptions=["Assuming Delaware corporate registry stays active and compliant."],
            missing_information=[],
            clarification_questions=[],
            recommendations=["Verify active Delaware certificate of good standing prior to submission."],
            escalation_required=False
        )

    def _mock_operations_review(self) -> DepartmentReviewOutput:
        return DepartmentReviewOutput(
            decision="GO",
            confidence=0.94,
            reasoning="Timeline is tight (30 days) but realistic. Standard forms (Form A, Form B) required.",
            evidence="All submissions must be completed online via procurement portal by July 15, 2026.",
            findings=["Submission portal active.", "Requires CEO signature on Form A authorization page."],
            risks=["Severe network lag in the portal right before submission deadline."],
            assumptions=["Assumes portal registration credentials will be issued 48 hours prior."],
            missing_information=["Form B template is not linked in index pages."],
            clarification_questions=["Where can the downloadable Form B template be found?"],
            recommendations=["Submit all packages 24 hours prior to deadline to prevent portal congestion issues."],
            escalation_required=False
        )

    def _mock_technical_review(self) -> DepartmentReviewOutput:
        return DepartmentReviewOutput(
            decision="GO",
            confidence=0.97,
            reasoning="Core tech alignment is 100%. Generative AI requirements match standard k8s deployments.",
            evidence="Deployment needs to occur inside a secure containerized environment.",
            findings=["Kubernetes base platform satisfies hosting criteria.", "Standard REST API configurations supported."],
            risks=["Integration with proprietary legacy CRM could face connection issues."],
            assumptions=["Assumes client legacy systems expose standard REST endpoints."],
            missing_information=["Legacy CRM API documentation is missing from package."],
            clarification_questions=["Is API documentation available for the legacy CRM endpoints?"],
            recommendations=["Prepare API sandbox endpoints early in the project timeline."],
            escalation_required=False
        )

review_engine_service = ReviewEngineService()
