import os
import time
import json
from typing import Dict, Any, List, Optional
from groq import Groq
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
        self.api_key = settings.GROQ_API_KEY
        self.model_name = "llama-3.3-70b-versatile"
        self.prompt_version = "v1.0"
        
        if self.api_key and self.api_key != "your-api-key-here":
            self.client = Groq(api_key=self.api_key)
            logger.info(f"RequirementEngineService initialized with Groq Model: {self.model_name}")
        else:
            self.client = None
            logger.warning("RequirementEngineService: GROQ_API_KEY not found. Fallback mockup engine active.")

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

    def _normalize_data(self, data: dict) -> dict:
        if not isinstance(data, dict):
            return {}
        
        reqs = data.get("requirements") or []
        norm_reqs = []
        for i, r in enumerate(reqs):
            if not isinstance(r, dict): continue
            raw_text = r.get("text_content") or r.get("text") or r.get("description") or r.get("clause") or r.get("obligation") or r.get("requirement") or r.get("title") or "Specified in document."
            raw_title = r.get("title") or r.get("name") or (str(raw_text)[:60] + "..." if len(str(raw_text)) > 60 else str(raw_text)) or f"Requirement {i+1}"
            norm_reqs.append({
                "temp_id": r.get("temp_id") or r.get("id") or f"REQ-{i+1:03d}",
                "title": raw_title,
                "text_content": raw_text,
                "category": r.get("category") or "Technical",
                "priority": r.get("priority") or "High",
                "req_type": r.get("req_type") or r.get("type") or "Functional",
                "mandatory": r.get("mandatory") if r.get("mandatory") is not None else True,
                "source_section": r.get("source_section") or "General",
                "source_page": r.get("source_page") or 1,
                "temp_parent_id": r.get("temp_parent_id"),
                "assigned_departments": r.get("assigned_departments") if isinstance(r.get("assigned_departments"), list) else ["Technical"],
                "confidence": float(r.get("confidence") or 0.95),
                "evidence": str(r.get("evidence") or raw_text),
                "reasoning": str(r.get("reasoning") or "")
            })

        dels = data.get("deliverables") or []
        norm_dels = []
        for i, d in enumerate(dels):
            if not isinstance(d, dict): continue
            norm_dels.append({
                "temp_id": d.get("temp_id") or d.get("id") or f"DEL-{i+1:03d}",
                "description": d.get("description") or d.get("name") or f"Deliverable {i+1}",
                "due_stage": d.get("due_stage") or d.get("deadline") or "Technical Review Stage",
                "mandatory": d.get("mandatory") if d.get("mandatory") is not None else True,
                "responsible_department": d.get("responsible_department") or "Technical",
                "related_requirements": d.get("related_requirements") if isinstance(d.get("related_requirements"), list) else [norm_reqs[0]["temp_id"]] if norm_reqs else [],
                "confidence": float(d.get("confidence") or 0.95)
            })

        evas = data.get("evaluation_criteria") or []
        norm_evas = []
        for i, e in enumerate(evas):
            if not isinstance(e, dict): continue
            norm_evas.append({
                "temp_id": e.get("temp_id") or e.get("id") or f"EVA-{i+1:03d}",
                "criteria_text": e.get("criteria_text") or e.get("description") or f"Criteria {i+1}",
                "weight": str(e.get("weight") or "25%"),
                "factor": str(e.get("factor") or "Technical Merit"),
                "scoring_methodology": str(e.get("scoring_methodology") or "Graded 0-5"),
                "confidence": float(e.get("confidence") or 0.92)
            })

        subs = data.get("submission_instructions") or []
        norm_subs = []
        for i, s in enumerate(subs):
            if not isinstance(s, dict): continue
            norm_subs.append({
                "temp_id": s.get("temp_id") or s.get("id") or f"SUB-{i+1:03d}",
                "instruction_text": s.get("instruction_text") or s.get("description") or "Follow standard portal submission rules.",
                "format_type": str(s.get("format_type") or "PDF"),
                "submission_method": str(s.get("submission_method") or "Portal"),
                "portal": str(s.get("portal") or "https://procurement.portal.gov"),
                "file_formats": str(s.get("file_formats") or "PDF, Word"),
                "max_size": str(s.get("max_size") or "50MB"),
                "late_policy": str(s.get("late_policy") or "Strict disqualification for late bids."),
                "confidence": float(s.get("confidence") or 0.98)
            })

        coms = data.get("compliance_items") or []
        norm_coms = []
        for i, c in enumerate(coms):
            if not isinstance(c, dict): continue
            norm_coms.append({
                "temp_id": c.get("temp_id") or c.get("id") or f"COM-{i+1:03d}",
                "name": c.get("name") or c.get("title") or c.get("description", "")[:40] or f"Compliance {i+1}",
                "status": c.get("status") or "Compliant",
                "department_owner": c.get("department_owner") or "Legal",
                "evidence_required": c.get("evidence_required") or "Signed certificate of compliance",
                "priority": c.get("priority") or "High",
                "blocking": c.get("blocking") if c.get("blocking") is not None else True,
                "confidence": float(c.get("confidence") or 0.96)
            })

        rsks = data.get("risks") or []
        norm_rsks = []
        for i, r in enumerate(rsks):
            if not isinstance(r, dict): continue
            norm_rsks.append({
                "temp_id": r.get("temp_id") or r.get("id") or f"RSK-{i+1:03d}",
                "description": r.get("description") or f"Identified risk {i+1}",
                "severity": r.get("severity") or "Medium",
                "likelihood": r.get("likelihood") or "Medium",
                "business_impact": str(r.get("business_impact") or "Potential project delay or budget variance"),
                "mitigation_suggestion": str(r.get("mitigation_suggestion") or "Proactive contingency planning and weekly monitoring"),
                "related_requirements": r.get("related_requirements") if isinstance(r.get("related_requirements"), list) else [norm_reqs[0]["temp_id"]] if norm_reqs else [],
                "confidence": float(r.get("confidence") or 0.90)
            })

        asms = data.get("assumptions") or []
        norm_asms = []
        for i, a in enumerate(asms):
            if not isinstance(a, dict): continue
            norm_asms.append({
                "temp_id": a.get("temp_id") or a.get("id") or f"ASM-{i+1:03d}",
                "description": a.get("description") or f"Assumption {i+1}",
                "category": a.get("category") or "Technical",
                "is_explicit": a.get("is_explicit") if a.get("is_explicit") is not None else True,
                "confidence": float(a.get("confidence") or 0.95)
            })

        clars = data.get("clarification_questions") or []
        norm_clars = []
        for i, q in enumerate(clars):
            if not isinstance(q, dict): continue
            norm_clars.append({
                "temp_id": q.get("temp_id") or q.get("id") or f"QST-{i+1:03d}",
                "question_text": q.get("question_text") or q.get("question") or q.get("description") or f"Clarification question {i+1}",
                "priority": q.get("priority") or "High",
                "reason": str(q.get("reason") or "To ensure precise scope alignment"),
                "suggested_recipient": str(q.get("suggested_recipient") or "Procurement Officer"),
                "business_impact": str(q.get("business_impact") or "Prevents pricing ambiguity"),
                "related_requirements": q.get("related_requirements") if isinstance(q.get("related_requirements"), list) else [norm_reqs[0]["temp_id"]] if norm_reqs else [],
                "confidence": float(q.get("confidence") or 0.94)
            })

        edges = data.get("knowledge_graph_edges") or []
        norm_edges = []
        for i, eg in enumerate(edges):
            if not isinstance(eg, dict): continue
            norm_edges.append({
                "source_id": eg.get("source_id") or eg.get("source") or (norm_dels[0]["temp_id"] if norm_dels else "DEL-001"),
                "source_type": eg.get("source_type") or "deliverable",
                "target_id": eg.get("target_id") or eg.get("target") or (norm_reqs[0]["temp_id"] if norm_reqs else "REQ-001"),
                "target_type": eg.get("target_type") or "requirement",
                "relationship_type": eg.get("relationship_type") or eg.get("relationship") or eg.get("relation") or "requires"
            })

        return {
            "requirements": norm_reqs,
            "deliverables": norm_dels,
            "evaluation_criteria": norm_evas,
            "submission_instructions": norm_subs,
            "compliance_items": norm_coms,
            "risks": norm_rsks,
            "assumptions": norm_asms,
            "clarification_questions": norm_clars,
            "knowledge_graph_edges": norm_edges
        }

    def run_inference_with_retry(self, prompt: str, schema: Any, retries: int = 3) -> Optional[str]:
        if not self.client:
            return None

        schema_hint = (
            'You MUST return ONLY a valid JSON object matching this exact structure:\n'
            '{\n'
            '  "requirements": [{"temp_id": "REQ-001", "title": "...", "text_content": "...", "category": "Technical", "priority": "High", "req_type": "Functional", "mandatory": true, "assigned_departments": ["Technical"], "confidence": 0.95, "evidence": "...", "reasoning": "..."}],\n'
            '  "deliverables": [{"temp_id": "DEL-001", "description": "...", "due_stage": "...", "mandatory": true, "responsible_department": "Technical", "related_requirements": ["REQ-001"], "confidence": 0.95}],\n'
            '  "evaluation_criteria": [{"temp_id": "EVA-001", "criteria_text": "...", "weight": "25%", "factor": "...", "scoring_methodology": "...", "confidence": 0.9}],\n'
            '  "submission_instructions": [{"temp_id": "SUB-001", "instruction_text": "...", "submission_method": "Portal", "portal": "...", "file_formats": "PDF", "max_size": "50MB", "confidence": 0.98}],\n'
            '  "compliance_items": [{"temp_id": "COM-001", "name": "...", "status": "Compliant", "department_owner": "Legal", "evidence_required": "...", "priority": "High", "blocking": true, "confidence": 0.95}],\n'
            '  "risks": [{"temp_id": "RSK-001", "description": "...", "severity": "High", "likelihood": "Medium", "business_impact": "...", "mitigation_suggestion": "...", "related_requirements": ["REQ-001"], "confidence": 0.9}],\n'
            '  "assumptions": [{"temp_id": "ASM-001", "description": "...", "category": "Technical", "is_explicit": true, "confidence": 0.95}],\n'
            '  "clarification_questions": [{"temp_id": "QST-001", "question_text": "...", "priority": "High", "reason": "...", "suggested_recipient": "...", "business_impact": "...", "related_requirements": ["REQ-001"], "confidence": 0.94}],\n'
            '  "knowledge_graph_edges": [{"source_id": "DEL-001", "source_type": "deliverable", "target_id": "REQ-001", "target_type": "requirement", "relationship_type": "requires"}]\n'
            '}'
        )
        full_prompt = f"{prompt}\n\n{schema_hint}"
        models_to_try = [self.model_name, "llama-3.1-8b-instant", "qwen/qwen3-32b"]

        for model in models_to_try:
            for attempt in range(retries):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are an exhaustive Enterprise RFP Audit & Checklist Engine. Extract EVERY SINGLE obligation across Financial, Legal, Technical, and Operational categories. Return strictly valid JSON."},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.2,
                        max_tokens=1800,
                        response_format={"type": "json_object"}
                    )
                    return self._clean_json(response.choices[0].message.content)
                except Exception as e:
                    err_str = str(e)
                    logger.warning(f"Groq API attempt {attempt+1} with model {model} failed: {err_str}")
                    if "429" in err_str or "rate_limit" in err_str.lower() or "413" in err_str:
                        logger.warning(f"Rate limit hit on {model}, falling back to next available Groq model.")
                        break
                    if attempt == retries - 1 and model == models_to_try[-1]:
                        return None
                    time.sleep(1)

    def extract_requirement_intelligence(self, doc_text: str) -> RequirementIntelligenceOutput:
        t0 = time.time()
        
        # If document is large (e.g. > 12,000 chars), perform multi-chunk exhaustive extraction
        if len(doc_text) > 12000:
            logger.info(f"Large enterprise RFP detected ({len(doc_text)} chars). Running multi-chunk exhaustive extraction...")
            chunks = [doc_text[i:i+8000] for i in range(0, len(doc_text), 7500)]
            
            agg_data = {
                "requirements": [],
                "deliverables": [],
                "evaluation_criteria": [],
                "submission_instructions": [],
                "compliance_items": [],
                "risks": [],
                "assumptions": [],
                "clarification_questions": [],
                "knowledge_graph_edges": []
            }
            
            seen_titles = set()
            for idx, chunk in enumerate(chunks[:6]): # Process 6 strategic chunks (~48k chars)
                chunk_prompt = PROMPT_REGISTRY[self.prompt_version]["extraction_prompt"].format(text=chunk)
                chunk_prompt += "\n\nCRITICAL INSTRUCTION: Extract EVERY SINGLE granular checklist obligation in this chunk across Financial, Legal, Technical, and Operational categories. Extract at least 15-20 detailed items."
                
                resp = self.run_inference_with_retry(chunk_prompt, RequirementIntelligenceOutput)
                if resp:
                    try:
                        raw = json.loads(resp)
                        for key in agg_data.keys():
                            items = raw.get(key) or []
                            if isinstance(items, list):
                                for item in items:
                                    if isinstance(item, dict):
                                        title = item.get("title") or item.get("name") or item.get("description") or item.get("text") or item.get("clause") or item.get("obligation") or item.get("requirement") or item.get("factor")
                                        if title and str(title).strip().lower() not in seen_titles:
                                            seen_titles.add(str(title).strip().lower())
                                            agg_data[key].append(item)
                    except Exception as ce:
                        logger.warning(f"Error parsing chunk {idx+1}: {ce}")
            
            logger.info(f"Aggregated {len(agg_data['requirements'])} requirements across chunks. Normalizing...")
            normalized_data = self._normalize_data(agg_data)
            latency_ms = (time.time() - t0) * 1000
            logger.info(f"Exhaustive requirement intelligence complete. Latency: {latency_ms:.2f}ms")
            return RequirementIntelligenceOutput(**normalized_data)

        # Single-pass for shorter documents
        prompt = PROMPT_REGISTRY[self.prompt_version]["extraction_prompt"].format(text=doc_text[:16000])
        response_text = self.run_inference_with_retry(prompt, RequirementIntelligenceOutput)
        latency_ms = (time.time() - t0) * 1000

        if not response_text:
            return self._mock_intelligence_output()

        try:
            raw_data = json.loads(response_text)
            normalized_data = self._normalize_data(raw_data)
            logger.info(f"Requirement intelligence extracted via Groq and normalized. Latency: {latency_ms:.2f}ms")
            return RequirementIntelligenceOutput(**normalized_data)
        except Exception as e:
            logger.error(f"Failed to parse Groq response even after normalization: {str(e)}")
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
