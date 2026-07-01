import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.document import RFPDocument, Requirement, Deliverable, EvaluationCriteria, SubmissionInstruction
from backend.app.models.requirement_intelligence import (
    ComplianceObligation,
    RFPRisk,
    RFPAssumption,
    ClarificationQuestion,
    KnowledgeGraphEdge,
    RequirementAssignment,
)
from backend.app.services.requirement_engine import requirement_engine_service
from backend.app.schemas.requirement_intelligence import RequirementIntelligenceOutput

router = APIRouter()

@router.post("/{id}/requirements/extract", response_model=RequirementIntelligenceOutput)
def extract_requirements(id: str, db: Session = Depends(get_db)):
    doc = db.query(RFPDocument).filter(RFPDocument.id == id, RFPDocument.is_deleted == False).first()
    if not doc:
        raise HTTPException(status_code=404, detail="RFP Document not found")

    from backend.app.services.document_processor import DocumentProcessorFactory

    # Perform Gemini/Mock Extraction
    try:
        processor = DocumentProcessorFactory.get_processor(doc.file_path)
        doc_text = processor.extract_text(doc.file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract text from document: {str(e)}"
        )

    extracted_data = requirement_engine_service.extract_requirement_intelligence(doc_text)

    # 1. Clean up old intelligence entities
    req_subquery = db.query(Requirement.id).filter(Requirement.rfp_document_id == id)
    db.query(Deliverable).filter(Deliverable.requirement_id.in_(req_subquery)).delete(synchronize_session=False)
    db.query(EvaluationCriteria).filter(EvaluationCriteria.requirement_id.in_(req_subquery)).delete(synchronize_session=False)
    db.query(SubmissionInstruction).filter(SubmissionInstruction.requirement_id.in_(req_subquery)).delete(synchronize_session=False)
    db.query(RequirementAssignment).filter(RequirementAssignment.requirement_id.in_(req_subquery)).delete(synchronize_session=False)
    db.query(Requirement).filter(Requirement.rfp_document_id == id).delete(synchronize_session=False)
    db.query(ComplianceObligation).filter(ComplianceObligation.rfp_document_id == id).delete(synchronize_session=False)
    db.query(RFPRisk).filter(RFPRisk.rfp_document_id == id).delete(synchronize_session=False)
    db.query(RFPAssumption).filter(RFPAssumption.rfp_document_id == id).delete(synchronize_session=False)
    db.query(ClarificationQuestion).filter(ClarificationQuestion.rfp_document_id == id).delete(synchronize_session=False)
    db.query(KnowledgeGraphEdge).filter(KnowledgeGraphEdge.rfp_document_id == id).delete(synchronize_session=False)

    db.commit()

    # 2. Persist extracted entities
    temp_id_mapping = {}

    # Persist Requirements
    for req_data in extracted_data.requirements:
        db_req = Requirement(
            rfp_document_id=id,
            title=req_data.title,
            text_content=req_data.text_content,
            category=req_data.category,
            priority=req_data.priority,
            req_type=req_data.req_type,
            mandatory=req_data.mandatory,
            source_section=req_data.source_section,
            source_page=req_data.source_page,
            confidence=req_data.confidence
        )
        db.add(db_req)
        db.flush()  # generates db_req.id
        temp_id_mapping[req_data.temp_id] = str(db_req.id)

        # Department assignments
        for dept in req_data.assigned_departments:
            db_assign = RequirementAssignment(
                requirement_id=db_req.id,
                department_name=dept
            )
            db.add(db_assign)

    # Re-map parent_id for nested requirements
    for req_data in extracted_data.requirements:
        if req_data.temp_parent_id and req_data.temp_parent_id in temp_id_mapping:
            db_id = temp_id_mapping[req_data.temp_id]
            parent_db_id = temp_id_mapping[req_data.temp_parent_id]
            db_req = db.query(Requirement).filter(Requirement.id == db_id).first()
            if db_req:
                db_req.parent_id = parent_db_id

    # Persist Deliverables
    for del_data in extracted_data.deliverables:
        # Find primary requirement link if any
        primary_req_id = None
        if del_data.related_requirements and del_data.related_requirements[0] in temp_id_mapping:
            primary_req_id = temp_id_mapping[del_data.related_requirements[0]]

        # If no requirement link, create or map to fallback
        if not primary_req_id:
            # Create a placeholder or skip linking, let's keep requirement_id nullable in DB or map to a root
            # Let's map to first requirement or handle ForeignKey constraint
            first_req = db.query(Requirement).filter(Requirement.rfp_document_id == id).first()
            primary_req_id = str(first_req.id) if first_req else str(uuid.uuid4())

        db_del = Deliverable(
            requirement_id=primary_req_id,
            description=del_data.description,
            deadline=del_data.due_stage,
            due_stage=del_data.due_stage,
            mandatory=del_data.mandatory,
            responsible_department=del_data.responsible_department,
            confidence=del_data.confidence
        )
        db.add(db_del)
        db.flush()
        temp_id_mapping[del_data.temp_id] = str(db_del.id)

    # Persist Evaluation Criteria
    for eva_data in extracted_data.evaluation_criteria:
        first_req = db.query(Requirement).filter(Requirement.rfp_document_id == id).first()
        req_id = str(first_req.id) if first_req else str(uuid.uuid4())
        
        db_eva = EvaluationCriteria(
            requirement_id=req_id,
            criteria_text=eva_data.criteria_text,
            weight=eva_data.weight or "N/A",
            factor=eva_data.factor,
            scoring_methodology=eva_data.scoring_methodology,
            ranking_criteria=eva_data.ranking_criteria,
            selection_method=eva_data.selection_method,
            tie_break_rules=eva_data.tie_break_rules,
            preferred_experience=eva_data.preferred_experience,
            preferred_certifications=eva_data.preferred_certifications,
            confidence=eva_data.confidence
        )
        db.add(db_eva)
        db.flush()
        temp_id_mapping[eva_data.temp_id] = str(db_eva.id)

    # Persist Submission Instructions
    for sub_data in extracted_data.submission_instructions:
        first_req = db.query(Requirement).filter(Requirement.rfp_document_id == id).first()
        req_id = str(first_req.id) if first_req else str(uuid.uuid4())

        db_sub = SubmissionInstruction(
            requirement_id=req_id,
            instruction_text=sub_data.instruction_text,
            format_type=sub_data.format_type,
            submission_method=sub_data.submission_method,
            portal=sub_data.portal,
            email=sub_data.email,
            file_naming_rules=sub_data.file_naming_rules,
            file_formats=sub_data.file_formats,
            max_size=sub_data.max_size,
            required_signatures=sub_data.required_signatures,
            required_forms=sub_data.required_forms,
            num_copies=sub_data.num_copies,
            submission_sequence=sub_data.submission_sequence,
            late_policy=sub_data.late_policy,
            confidence=sub_data.confidence
        )
        db.add(db_sub)
        db.flush()
        temp_id_mapping[sub_data.temp_id] = str(db_sub.id)

    # Persist Compliance Obligations
    for com_data in extracted_data.compliance_items:
        db_com = ComplianceObligation(
            rfp_document_id=id,
            name=com_data.name,
            status=com_data.status,
            department_owner=com_data.department_owner,
            evidence_required=com_data.evidence_required,
            priority=com_data.priority,
            blocking=com_data.blocking,
            confidence=com_data.confidence
        )
        db.add(db_com)
        db.flush()
        temp_id_mapping[com_data.temp_id] = str(db_com.id)

    # Persist Risks
    for rsk_data in extracted_data.risks:
        req_db_id = None
        if rsk_data.related_requirements and rsk_data.related_requirements[0] in temp_id_mapping:
            req_db_id = temp_id_mapping[rsk_data.related_requirements[0]]

        db_rsk = RFPRisk(
            rfp_document_id=id,
            requirement_id=req_db_id,
            description=rsk_data.description,
            severity=rsk_data.severity,
            likelihood=rsk_data.likelihood,
            business_impact=rsk_data.business_impact,
            mitigation_suggestion=rsk_data.mitigation_suggestion,
            confidence=rsk_data.confidence
        )
        db.add(db_rsk)
        db.flush()
        temp_id_mapping[rsk_data.temp_id] = str(db_rsk.id)

    # Persist Assumptions
    for asm_data in extracted_data.assumptions:
        db_asm = RFPAssumption(
            rfp_document_id=id,
            description=asm_data.description,
            category=asm_data.category,
            is_explicit=asm_data.is_explicit,
            confidence=asm_data.confidence
        )
        db.add(db_asm)
        db.flush()
        temp_id_mapping[asm_data.temp_id] = str(db_asm.id)

    # Persist Clarifications
    for qst_data in extracted_data.clarification_questions:
        req_db_id = None
        if qst_data.related_requirements and qst_data.related_requirements[0] in temp_id_mapping:
            req_db_id = temp_id_mapping[qst_data.related_requirements[0]]

        db_qst = ClarificationQuestion(
            rfp_document_id=id,
            requirement_id=req_db_id,
            question_text=qst_data.question_text,
            priority=qst_data.priority,
            reason=qst_data.reason,
            suggested_recipient=qst_data.suggested_recipient,
            business_impact=qst_data.business_impact,
            confidence=qst_data.confidence
        )
        db.add(db_qst)
        db.flush()
        temp_id_mapping[qst_data.temp_id] = str(db_qst.id)

    # Persist Knowledge Graph Edges
    for edge in extracted_data.knowledge_graph_edges:
        src_db_id = temp_id_mapping.get(edge.source_id)
        tgt_db_id = temp_id_mapping.get(edge.target_id)
        if src_db_id and tgt_db_id:
            db_edge = KnowledgeGraphEdge(
                rfp_document_id=id,
                source_type=edge.source_type,
                source_id=src_db_id,
                target_type=edge.target_type,
                target_id=tgt_db_id,
                relationship_type=edge.relationship_type
            )
            db.add(db_edge)

    db.commit()
    return extracted_data


@router.get("/{id}/requirements")
def get_requirements(id: str, priority: Optional[str] = None, req_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Requirement).filter(Requirement.rfp_document_id == id, Requirement.is_deleted == False)
    if priority:
        query = query.filter(Requirement.priority == priority)
    if req_type:
        query = query.filter(Requirement.req_type == req_type)
        
    reqs = query.all()
    out = []
    for r in reqs:
        # Fetch assigned departments
        depts = db.query(RequirementAssignment).filter(RequirementAssignment.requirement_id == r.id).all()
        dept_names = [d.department_name for d in depts]
        out.append({
            "id": str(r.id),
            "title": r.title,
            "text_content": r.text_content,
            "category": r.category,
            "priority": r.priority,
            "req_type": r.req_type,
            "mandatory": r.mandatory,
            "source_section": r.source_section,
            "source_page": r.source_page,
            "parent_id": r.parent_id,
            "confidence": r.confidence,
            "assigned_departments": dept_names
        })
    return out


@router.get("/{id}/deliverables")
def get_deliverables(id: str, db: Session = Depends(get_db)):
    req_ids = db.query(Requirement.id).filter(Requirement.rfp_document_id == id)
    deliverables = db.query(Deliverable).filter(Deliverable.requirement_id.in_(req_ids), Deliverable.is_deleted == False).all()
    return deliverables


@router.get("/{id}/evaluation")
def get_evaluation(id: str, db: Session = Depends(get_db)):
    req_ids = db.query(Requirement.id).filter(Requirement.rfp_document_id == id)
    criteria = db.query(EvaluationCriteria).filter(EvaluationCriteria.requirement_id.in_(req_ids), EvaluationCriteria.is_deleted == False).all()
    return criteria


@router.get("/{id}/submission")
def get_submission(id: str, db: Session = Depends(get_db)):
    req_ids = db.query(Requirement.id).filter(Requirement.rfp_document_id == id)
    instructions = db.query(SubmissionInstruction).filter(SubmissionInstruction.requirement_id.in_(req_ids), SubmissionInstruction.is_deleted == False).all()
    return instructions


@router.get("/{id}/compliance")
def get_compliance(id: str, db: Session = Depends(get_db)):
    compliance = db.query(ComplianceObligation).filter(ComplianceObligation.rfp_document_id == id, ComplianceObligation.is_deleted == False).all()
    return compliance


@router.get("/{id}/clarifications")
def get_clarifications(id: str, db: Session = Depends(get_db)):
    clarifications = db.query(ClarificationQuestion).filter(ClarificationQuestion.rfp_document_id == id, ClarificationQuestion.is_deleted == False).all()
    return clarifications


@router.get("/{id}/knowledge-graph")
def get_knowledge_graph(id: str, db: Session = Depends(get_db)):
    edges = db.query(KnowledgeGraphEdge).filter(KnowledgeGraphEdge.rfp_document_id == id).all()
    
    # Compile unique node references to build nodes list
    node_set = set()
    for e in edges:
        node_set.add((e.source_id, e.source_type))
        node_set.add((e.target_id, e.target_type))
        
    nodes = []
    for node_id, node_type in node_set:
        # Retrieve label/title depending on entity type
        label = "Unknown Node"
        if node_type == "requirement":
            r = db.query(Requirement).filter(Requirement.id == node_id).first()
            if r: label = r.title
        elif node_type == "deliverable":
            d = db.query(Deliverable).filter(Deliverable.id == node_id).first()
            if d: label = d.description[:30] + "..." if len(d.description) > 30 else d.description
        elif node_type == "risk":
            rsk = db.query(RFPRisk).filter(RFPRisk.id == node_id).first()
            if rsk: label = rsk.description[:30] + "..." if len(rsk.description) > 30 else rsk.description
        elif node_type == "clarification_question":
            qst = db.query(ClarificationQuestion).filter(ClarificationQuestion.id == node_id).first()
            if qst: label = qst.question_text[:30] + "..." if len(qst.question_text) > 30 else qst.question_text
        elif node_type == "compliance_obligation":
            com = db.query(ComplianceObligation).filter(ComplianceObligation.id == node_id).first()
            if com: label = com.name
            
        nodes.append({
            "id": node_id,
            "type": node_type,
            "label": label
        })
        
    return {
        "nodes": nodes,
        "edges": [
            {
                "id": str(e.id),
                "source": e.source_id,
                "target": e.target_id,
                "relationship": e.relationship_type
            }
            for e in edges
        ]
    }
