import os
import io
from docx import Document
from sqlalchemy.orm import Session
from backend.app.models.proposal import ProposalPlan, ProposalSection

class ExporterService:
  @staticmethod
  def compile_to_docx(db: Session, proposal_id: str) -> io.BytesIO:
    proposal = db.query(ProposalPlan).filter(ProposalPlan.id == proposal_id).first()
    if not proposal:
      raise ValueError("Proposal not found")

    doc = Document()
    doc.add_heading(proposal.title or "Proposal Document", 0)

    sections = db.query(ProposalSection).filter(ProposalSection.proposal_plan_id == proposal_id).all()
    # Sort sections if outline structure has sequences
    for sec in sections:
      doc.add_heading(sec.title or "Untitled Section", level=1)
      doc.add_paragraph(sec.content or "Draft content pending generation.")

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

  @staticmethod
  def compile_to_markdown(db: Session, proposal_id: str) -> str:
    proposal = db.query(ProposalPlan).filter(ProposalPlan.id == proposal_id).first()
    if not proposal:
      raise ValueError("Proposal not found")

    md = []
    md.append(f"# {proposal.title or 'Proposal Document'}")
    md.append("")

    sections = db.query(ProposalSection).filter(ProposalSection.proposal_plan_id == proposal_id).all()
    for sec in sections:
      md.append(f"## {sec.title or 'Untitled Section'}")
      md.append("")
      md.append(sec.content or "Draft content pending generation.")
      md.append("")

    return "\n".join(md)
