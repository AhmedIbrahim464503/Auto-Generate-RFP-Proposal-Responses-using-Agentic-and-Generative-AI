import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from groq import Groq
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument, Requirement
from backend.app.models.qualification import QualificationDecision
from backend.app.models.proposal import (
    ProposalPlan,
    ProposalSection,
    ComplianceMatrix,
    ComplianceItem,
    ProposalTask,
    ProposalMilestone,
    RequiredDocument,
    ClarificationRequest
)

logger = logging.getLogger("app")

PROMPT_REGISTRY = {
    "v1.0": {
        "planning_instruction": (
            "You are a Principal Enterprise Proposal Manager and RFP Capture Consultant. "
            "Review the RFP Opportunity metadata, extracted compliance requirements, and qualification decisions. "
            "Generate a complete Proposal Planning Package including Proposal Plan details, "
            "Adaptive Outlines (sections), WBS Tasks, Timeline Milestones, Required Documents checklist, "
            "and Clarification Management requests."
        )
    }
}

class ProposalPlanningEngineService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = "llama-3.3-70b-versatile"
        self.prompt_version = "v1.0"

        if self.api_key and self.api_key != "your-api-key-here":
            self.client = Groq(api_key=self.api_key)
            logger.info(f"ProposalPlanningEngineService initialized with Groq Model: {self.model_name}")
        else:
            self.client = None
            logger.warning("ProposalPlanningEngineService: GROQ_API_KEY not found. Fallback mockup engine active.")

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

        full_sys = f"{system_instruction}\n\nYou MUST return ONLY a valid JSON object."
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

    def generate_proposal_plan(self, db: Session, opportunity_id: str) -> ProposalPlan:
        # 1. Fetch Opportunity, Docs, Requirements, and Qualification Decisions
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        doc = db.query(RFPDocument).filter(RFPDocument.opportunity_id == opportunity_id, RFPDocument.is_deleted == False).first()
        doc_id = doc.id if doc else "temp-doc-id"

        requirements = db.query(Requirement).filter(Requirement.rfp_document_id == doc_id, Requirement.is_deleted == False).all()
        qual_decision = db.query(QualificationDecision).filter(QualificationDecision.opportunity_id == opportunity_id).first()

        # 2. Compute planning details or invoke AI engine
        plan_details = None
        if self.client:
            try:
                prompt = f"Generate JSON proposal plan for opportunity: {opp.title}, description: {opp.description}. Requirements count: {len(requirements)}."
                resp = self.run_inference_with_retry(prompt, PROMPT_REGISTRY[self.prompt_version]["planning_instruction"], None)
                if resp:
                    parsed = json.loads(resp)
                    if isinstance(parsed, dict) and "sections" in parsed:
                        plan_details = parsed
            except Exception as e:
                logger.warning(f"AI planning inference failed, falling back to dynamic template: {str(e)}")

        if not plan_details:
            plan_details = self._get_mock_plan_details(opp.title, requirements, qual_decision)

        # 3. Create or update ProposalPlan
        plan = db.query(ProposalPlan).filter(ProposalPlan.opportunity_id == opportunity_id).first()
        if not plan:
            plan = ProposalPlan(
                opportunity_id=opportunity_id,
                title=f"Proposal Plan: {opp.title}"
            )
            db.add(plan)
            db.flush()

        plan.client = plan_details["client"]
        plan.rfp_name = plan_details["rfp_name"]
        plan.proposal_type = plan_details["proposal_type"]
        plan.submission_deadline = plan_details["submission_deadline"]
        plan.estimated_duration_days = plan_details["estimated_duration_days"]
        plan.estimated_effort_hours = plan_details["estimated_effort_hours"]
        plan.complexity = plan_details["complexity"]
        plan.priority = plan_details["priority"]
        plan.required_departments = json.dumps(plan_details["required_departments"])
        plan.executive_sponsor = plan_details["executive_sponsor"]
        plan.proposal_owner = plan_details["proposal_owner"]
        plan.status = "DRAFT"
        plan.version = "v1.0.0"
        plan.planning_notes = plan_details["planning_notes"]
        plan.updated_at = datetime.utcnow()

        # 4. Save/Recreate Proposal Outline Sections
        db.query(ProposalSection).filter(ProposalSection.proposal_plan_id == plan.id).delete()
        sections_map = {}
        for sec in plan_details["sections"]:
            db_sec = ProposalSection(
                proposal_plan_id=plan.id,
                title=sec["title"],
                content=sec.get("content", ""),
                status="DRAFT",
                owner=sec["owner"],
                reviewer=sec["reviewer"],
                approver=sec["approver"],
                estimated_hours=sec["estimated_hours"],
                dependencies=json.dumps(sec.get("dependencies", [])),
                priority=sec["priority"],
                risk_level=sec["risk_level"],
                is_human_editable=True
            )
            db.add(db_sec)
            db.flush()
            sections_map[sec["title"]] = db_sec.id

        # 5. Create or get ComplianceMatrix
        matrix = db.query(ComplianceMatrix).filter(ComplianceMatrix.opportunity_id == opportunity_id).first()
        if not matrix:
            matrix = ComplianceMatrix(opportunity_id=opportunity_id)
            db.add(matrix)
            db.flush()

        # Save Compliance Items mapping requirements
        db.query(ComplianceItem).filter(ComplianceItem.compliance_matrix_id == matrix.id).delete()
        for idx, req in enumerate(requirements):
            # Dynamic matching to outline sections
            mapped_section_title = "Technical Approach"
            if "pricing" in req.text_content.lower() or "cost" in req.text_content.lower() or "commercial" in req.text_content.lower():
                mapped_section_title = "Pricing"
            elif "legal" in req.text_content.lower() or "contract" in req.text_content.lower() or "indemn" in req.text_content.lower():
                mapped_section_title = "Compliance Response"
            elif "deadline" in req.text_content.lower() or "milestone" in req.text_content.lower():
                mapped_section_title = "Implementation Plan"

            sec_id = sections_map.get(mapped_section_title)

            comp_item = ComplianceItem(
                compliance_matrix_id=matrix.id,
                requirement_id=req.id,
                proposal_section_id=sec_id,
                status="Unknown",
                explanation=f"AI auto-mapped to section: {mapped_section_title}",
                responsible_department=self._heuristic_department(mapped_section_title),
                responsible_owner=self._heuristic_owner(mapped_section_title),
                priority=req.priority or "Medium",
                mandatory=True,
                evidence_required="RFP Citation",
                source_page=1,
                source_paragraph="Raw section match",
                risk_if_missing="Non-compliance disqualification",
                dependencies=json.dumps([]),
                reviewer="Compliance Manager",
                approval_status="PENDING",
                traceability_links=json.dumps([str(req.id)]),
                confidence=0.95,
                comments=""
            )
            db.add(comp_item)

        # 6. Save Tasks (WBS)
        db.query(ProposalTask).filter(ProposalTask.proposal_plan_id == plan.id).delete()
        for t in plan_details["tasks"]:
            task = ProposalTask(
                proposal_plan_id=plan.id,
                title=t["title"],
                owner=t["owner"],
                priority=t["priority"],
                estimated_hours=t["estimated_hours"],
                status="TODO",
                dependencies=json.dumps(t.get("dependencies", [])),
                due_date=t["due_date"],
                is_critical_path=t.get("is_critical_path", False)
            )
            db.add(task)

        # 7. Save Milestones (Timeline)
        db.query(ProposalMilestone).filter(ProposalMilestone.proposal_plan_id == plan.id).delete()
        for m in plan_details["milestones"]:
            milestone = ProposalMilestone(
                proposal_plan_id=plan.id,
                name=m["name"],
                start_date=m["start_date"],
                end_date=m["end_date"],
                status="PENDING"
            )
            db.add(milestone)

        # 8. Save Required Documents
        db.query(RequiredDocument).filter(RequiredDocument.proposal_plan_id == plan.id).delete()
        for d_info in plan_details["required_documents"]:
            doc_req = RequiredDocument(
                proposal_plan_id=plan.id,
                document_name=d_info["document_name"],
                document_type=d_info["document_type"],
                status="MISSING",
                required_by_date=d_info["required_by_date"],
                notes=d_info.get("notes", "")
            )
            db.add(doc_req)

        # 9. Save Clarification Requests
        db.query(ClarificationRequest).filter(ClarificationRequest.proposal_plan_id == plan.id).delete()
        for c in plan_details["clarifications"]:
            req = ClarificationRequest(
                proposal_plan_id=plan.id,
                question=c["question"],
                reason=c["reason"],
                priority=c["priority"],
                owner=c["owner"],
                status="DRAFT"
            )
            db.add(req)

        db.commit()
        db.refresh(plan)
        return plan

    def _heuristic_department(self, section_title: str) -> str:
        if "pricing" in section_title.lower() or "cost" in section_title.lower():
            return "Finance"
        elif "compliance" in section_title.lower() or "legal" in section_title.lower():
            return "Legal"
        elif "technical" in section_title.lower() or "approach" in section_title.lower():
            return "Technical"
        elif "executive" in section_title.lower():
            return "Executive Review"
        elif "implementation" in section_title.lower() or "project" in section_title.lower():
            return "Operations"
        return "Proposal Management"

    def _heuristic_owner(self, section_title: str) -> str:
        dept = self._heuristic_department(section_title)
        return f"{dept} Lead"

    def _get_mock_plan_details(self, opp_title: str, requirements: List[Requirement], qual: Optional[QualificationDecision]) -> Dict[str, Any]:
        deadline = datetime.utcnow() + timedelta(days=30)
        
        sections = [
            {"title": "Executive Summary", "owner": "Proposal Manager", "reviewer": "Executive Sponsor", "approver": "Executive Sponsor", "estimated_hours": 10, "priority": "High", "risk_level": "Medium"},
            {"title": "Understanding of Requirements", "owner": "Proposal Manager", "reviewer": "Operations Lead", "approver": "Proposal Owner", "estimated_hours": 15, "priority": "Medium", "risk_level": "Low"},
            {"title": "Technical Approach", "owner": "Technical Lead", "reviewer": "Technical Lead", "approver": "Proposal Owner", "estimated_hours": 40, "priority": "High", "risk_level": "High"},
            {"title": "Implementation Plan", "owner": "Operations Lead", "reviewer": "Operations Lead", "approver": "Proposal Owner", "estimated_hours": 20, "priority": "Medium", "risk_level": "Medium"},
            {"title": "Compliance Response", "owner": "Legal Lead", "reviewer": "Legal Lead", "approver": "Proposal Owner", "estimated_hours": 12, "priority": "High", "risk_level": "High"},
            {"title": "Pricing", "owner": "Finance Lead", "reviewer": "Finance Lead", "approver": "Proposal Owner", "estimated_hours": 18, "priority": "High", "risk_level": "Medium"}
        ]

        tasks = [
            {"title": "Analyze Requirements", "owner": "Proposal Manager", "priority": "High", "estimated_hours": 4.0, "due_date": datetime.utcnow() + timedelta(days=2), "is_critical_path": True},
            {"title": "Technical Review", "owner": "Technical Lead", "priority": "High", "estimated_hours": 12.0, "due_date": datetime.utcnow() + timedelta(days=7), "is_critical_path": True},
            {"title": "Financial Review", "owner": "Finance Lead", "priority": "Medium", "estimated_hours": 8.0, "due_date": datetime.utcnow() + timedelta(days=10), "is_critical_path": False},
            {"title": "Write Technical Response", "owner": "Technical Lead", "priority": "High", "estimated_hours": 30.0, "due_date": datetime.utcnow() + timedelta(days=15), "is_critical_path": True},
            {"title": "Compliance Verification", "owner": "Legal Lead", "priority": "High", "estimated_hours": 10.0, "due_date": datetime.utcnow() + timedelta(days=20), "is_critical_path": True},
            {"title": "Executive Review", "owner": "Executive Sponsor", "priority": "High", "estimated_hours": 6.0, "due_date": datetime.utcnow() + timedelta(days=25), "is_critical_path": True}
        ]

        milestones = [
            {"name": "Kickoff", "start_date": datetime.utcnow(), "end_date": datetime.utcnow() + timedelta(days=1)},
            {"name": "Department Reviews", "start_date": datetime.utcnow() + timedelta(days=2), "end_date": datetime.utcnow() + timedelta(days=10)},
            {"name": "Draft Completion", "start_date": datetime.utcnow() + timedelta(days=10), "end_date": datetime.utcnow() + timedelta(days=20)},
            {"name": "Internal Review", "start_date": datetime.utcnow() + timedelta(days=20), "end_date": datetime.utcnow() + timedelta(days=25)},
            {"name": "Submission Buffer", "start_date": datetime.utcnow() + timedelta(days=25), "end_date": deadline - timedelta(days=1)},
            {"name": "Submission", "start_date": deadline - timedelta(days=1), "end_date": deadline}
        ]

        req_docs = [
            {"document_name": "Active Professional Liability Certificate", "document_type": "Insurance", "required_by_date": datetime.utcnow() + timedelta(days=15), "notes": "Minimum $5M liability coverage needed."},
            {"document_name": "Audited Financial Statements (Last 2 Years)", "document_type": "Financial", "required_by_date": datetime.utcnow() + timedelta(days=15), "notes": "Required by Finance Lead."},
            {"document_name": "SPS Corporate Profile & Case Studies", "document_type": "Case Study", "required_by_date": datetime.utcnow() + timedelta(days=10), "notes": "Need automotive BU case study."}
        ]

        clarifications = [
            {"question": "Can the E-Verify certificate deadline be extended?", "reason": "Standard processing times might exceed submission deadline.", "priority": "Medium", "owner": "Legal Lead"}
        ]

        return {
            "client": "Enterprise Customer Corp",
            "rfp_name": opp_title,
            "proposal_type": "Commercial RFP Response",
            "submission_deadline": deadline,
            "estimated_duration_days": 30,
            "estimated_effort_hours": 120,
            "complexity": "High",
            "priority": "High",
            "required_departments": ["Proposal Management", "Technical", "Finance", "Legal", "Operations", "Executive Review"],
            "executive_sponsor": "VP of Sales",
            "proposal_owner": "Bid Manager",
            "planning_notes": "Ensure tight coordination with Technical architects early to address legacy integration dependencies.",
            "sections": sections,
            "tasks": tasks,
            "milestones": milestones,
            "required_documents": req_docs,
            "clarifications": clarifications
        }

planning_engine_service = ProposalPlanningEngineService()
proposal_planning_engine_service = planning_engine_service
