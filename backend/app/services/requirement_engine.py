import os
import time
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.schemas.requirement_intelligence import (
    RequirementIntelligenceOutput,
    RequirementExtractionOutput,
    DeliverableExtractionOutput,
    EvaluationCriteriaOutput,
    SubmissionInstructionOutput,
    ComplianceItemOutput,
    RiskOutput,
    AssumptionOutput,
    ClarificationQuestionOutput,
    KnowledgeGraphEdgeOutput,
)

PROMPT_REGISTRY = {
    "v1.0": {
        "system_instruction": (
            "You are a Principal Requirement Intelligence Engine. Extract structured business "
            "knowledge from the provided RFP text. Extract all requirements, deliverables, "
            "evaluation criteria, submission instructions, compliance items, risks, assumptions, "
            "and clarification questions. Formulate a relationship knowledge graph mapping their edges."
        ),
        "extraction_prompt": (
            "Analyze the following RFP text and extract all structural requirements, deliverables, "
            "evaluation criteria, submission instructions, compliance items, risks, assumptions, "
            "and clarification questions. Build relational knowledge graph edges connecting these nodes "
            "(e.g., connecting a deliverable DEL-X to a requirement REQ-Y). You must return exactly "
            "the schema structure defined. Text:\n\n{text}"
        )
    }
}

class RequirementEngineService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash"
        self.prompt_version = "v1.0"
        
        if self.api_key and self.api_key != "your-api-key-here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"RequirementEngineService initialized with Gemini Model: {self.model_name}")
        else:
            self.model = None
            logger.warning("RequirementEngineService: GEMINI_API_KEY not found. Fallback mockup engine active.")

    def run_inference_with_retry(self, prompt: str, schema: Any, retries: int = 3) -> Any:
        if not self.model:
            return None

        for attempt in range(retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=schema
                    )
                )
                return response
            except Exception as e:
                logger.warn(f"Gemini API attempt {attempt+1} failed: {str(e)}")
                if attempt == retries - 1:
                    raise e
                time.sleep(2 ** attempt)

    def extract_requirement_intelligence(self, doc_text: str) -> RequirementIntelligenceOutput:
        prompt = PROMPT_REGISTRY[self.prompt_version]["extraction_prompt"].format(text=doc_text[:50000])
        
        t0 = time.time()
        response = self.run_inference_with_retry(prompt, RequirementIntelligenceOutput)
        latency_ms = (time.time() - t0) * 1000

        if not response:
            return self._mock_intelligence_output()

        try:
            data = json.loads(response.text)
            logger.info(f"Requirement intelligence extracted via Gemini. Latency: {latency_ms:.2f}ms")
            return RequirementIntelligenceOutput(**data)
        except Exception as e:
            logger.error(f"Failed to parse model intelligence output: {str(e)}")
            return self._mock_intelligence_output()

    def _mock_intelligence_output(self) -> RequirementIntelligenceOutput:
        # Mock responses representing a high-fidelity output for testing
        requirements = [
            RequirementExtractionOutput(
                temp_id="REQ-001",
                title="SPS Core Platform Deployment",
                text_content="The contractor shall deploy an Enterprise AI Proposal Management engine on-premise or inside secure hybrid cloud tenant spaces.",
                category="Technical",
                priority="High",
                req_type="Functional",
                mandatory=True,
                source_section="Section 3.1 Platform Architecture",
                source_page=4,
                temp_parent_id=None,
                assigned_departments=["Technical", "Operations"],
                confidence=0.98,
                evidence="The contractor shall deploy an Enterprise AI Proposal Management engine on-premise...",
                reasoning="Identified as a mandatory functional deployment requirement."
            ),
            RequirementExtractionOutput(
                temp_id="REQ-002",
                title="Data Isolation Security",
                text_content="All client proprietary uploaded PDF and Word documents must be encrypted at rest using AES-256 standards.",
                category="Security",
                priority="High",
                req_type="Non-Functional",
                mandatory=True,
                source_section="Section 5.2 Data Integrity",
                source_page=12,
                temp_parent_id="REQ-001",
                assigned_departments=["Technical", "Legal"],
                confidence=0.95,
                evidence="All client proprietary uploaded PDF and Word documents must be encrypted at rest using AES-256...",
                reasoning="Identified as a key security technical requirement linked to core deployment."
            ),
            RequirementExtractionOutput(
                temp_id="REQ-003",
                title="Multilingual Proposal Support",
                text_content="The platform should support drafting proposal sections in Spanish and French if required by the bidding organization.",
                category="Technical",
                priority="Low",
                req_type="Functional",
                mandatory=False,
                source_section="Section 3.4 Multi-Language Features",
                source_page=8,
                temp_parent_id=None,
                assigned_departments=["Technical"],
                confidence=0.88,
                evidence="The platform should support drafting proposal sections in Spanish and French if required...",
                reasoning="Identified as an optional multi-language feature requirement."
            )
        ]

        deliverables = [
            DeliverableExtractionOutput(
                temp_id="DEL-001",
                description="Deployment Blueprints and Network Topology Architecture",
                due_stage="Gate 2 Technical Review",
                mandatory=True,
                responsible_department="Technical",
                related_requirements=["REQ-001"],
                confidence=0.97,
                evidence="Provide network topology plans outlining tenant boundary spaces.",
                reasoning="Required documentation for system validation."
            ),
            DeliverableExtractionOutput(
                temp_id="DEL-002",
                description="System Security Configuration Guide",
                due_stage="Gate 3 Security Review",
                mandatory=True,
                responsible_department="Technical",
                related_requirements=["REQ-002"],
                confidence=0.94,
                evidence="Deliver a detailed guide explaining AES-256 storage keys management.",
                reasoning="Required documentation verifying isolation measures."
            )
        ]

        evaluation_criteria = [
            EvaluationCriteriaOutput(
                temp_id="EVA-001",
                criteria_text="Experience deploying containerized Generative AI apps inside secure government networks.",
                weight="25%",
                factor="Technical Competency",
                scoring_methodology="Graded 0-5 based on previous active project case studies.",
                ranking_criteria="Higher points for hybrid cloud multi-tenant setups.",
                selection_method="Best Value Trade-off",
                tie_break_rules="First vendor registered with local state business offices.",
                preferred_experience="Minimum 3 years active deployments.",
                preferred_certifications="AWS Certified Security Specialty or equivalent.",
                confidence=0.92,
                evidence="Grading will prioritize containerized Generative AI apps inside secure networks...",
                reasoning="Crucial grading criteria for vendor selection."
            )
        ]

        submission_instructions = [
            SubmissionInstructionOutput(
                temp_id="SUB-001",
                instruction_text="Upload technical proposal in PDF format through the SPS Procurement Portal.",
                format_type="PDF",
                submission_method="Portal",
                portal="https://procurement.sps-solutions.com",
                email=None,
                file_naming_rules="SPS_TECH_PROPOSAL_[VENDOR_NAME].pdf",
                file_formats="PDF",
                max_size="50MB",
                required_signatures="Authorized Representative Signature on Form A",
                required_forms="Form A: Bidder Profile, Form B: Cost Sheet",
                num_copies=1,
                submission_sequence="Technical upload followed by Financial upload.",
                late_policy="Late submissions will be automatically disqualified without review.",
                confidence=0.99,
                evidence="Upload technical proposal in PDF format... SPS_TECH_PROPOSAL_[VENDOR_NAME].pdf",
                reasoning="Mandatory format rules for submission compliance."
            )
        ]

        compliance_items = [
            ComplianceItemOutput(
                temp_id="COM-001",
                name="E-Verify Participation",
                status="Unknown",
                department_owner="Legal",
                evidence_required="MOU signature confirmation page.",
                priority="High",
                blocking=True,
                confidence=0.95,
                evidence="Bidders must submit proof of active registration with federal E-Verify systems.",
                reasoning="Legal constraint blocking bidding process if absent."
            )
        ]

        risks = [
            RiskOutput(
                temp_id="RSK-001",
                description="Strict on-premise installation constraints with tight timeline rules.",
                severity="High",
                likelihood="Medium",
                business_impact="Could lead to delay in project hand-off or penalties.",
                mitigation_suggestion="Formulate standard k8s helm chart templates before kickoff.",
                related_requirements=["REQ-001"],
                confidence=0.90,
                evidence="on-premise installation must complete within 30 days of award.",
                reasoning="Short timeframe represents deployment risk."
            )
        ]

        assumptions = [
            AssumptionOutput(
                temp_id="ASM-001",
                description="Assuming all server environments are provided pre-configured with GPU capabilities.",
                category="Technical",
                is_explicit=False,
                confidence=0.87,
                evidence="System must perform real-time extraction indexing.",
                reasoning="Real-time indexing implies hardware acceleration is pre-installed."
            )
        ]

        clarification_questions = [
            ClarificationQuestionOutput(
                temp_id="QST-001",
                question_text="Will SPS provide sandbox keys to the Procurement API for testing?",
                priority="Medium",
                reason="Needed to define API authentication scopes during initial setup.",
                suggested_recipient="RFP Contracting Officer",
                business_impact="Prevents integration blockages post-award.",
                related_requirements=["REQ-001"],
                confidence=0.91,
                evidence="Integration with Procurement API must be demonstrated.",
                reasoning="Unclear if sandbox endpoints are active."
            )
        ]

        knowledge_graph_edges = [
            KnowledgeGraphEdgeOutput(source_id="DEL-001", source_type="deliverable", target_id="REQ-001", target_type="requirement", relationship_type="requires"),
            KnowledgeGraphEdgeOutput(source_id="DEL-002", source_type="deliverable", target_id="REQ-002", target_type="requirement", relationship_type="requires"),
            KnowledgeGraphEdgeOutput(source_id="RSK-001", source_type="risk", target_id="REQ-001", target_type="requirement", relationship_type="mitigates"),
            KnowledgeGraphEdgeOutput(source_id="QST-001", source_type="clarification_question", target_id="REQ-001", target_type="requirement", relationship_type="addresses")
        ]

        return RequirementIntelligenceOutput(
            requirements=requirements,
            deliverables=deliverables,
            evaluation_criteria=evaluation_criteria,
            submission_instructions=submission_instructions,
            compliance_items=compliance_items,
            risks=risks,
            assumptions=assumptions,
            clarification_questions=clarification_questions,
            knowledge_graph_edges=knowledge_graph_edges
        )

requirement_engine_service = RequirementEngineService()
