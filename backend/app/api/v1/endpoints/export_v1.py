from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.services.exporter import ExporterService
from backend.app.models.proposal import ProposalPlan, ProposalSection

router = APIRouter()

@router.get("/{proposal_id}/docx")
def export_docx(proposal_id: str, db: Session = Depends(get_db)):
  try:
    file_stream = ExporterService.compile_to_docx(db, proposal_id)
    headers = {
        'Content-Disposition': f'attachment; filename="proposal_{proposal_id}.docx"'
    }
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )
  except ValueError as err:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

@router.get("/{proposal_id}/markdown")
def export_markdown(proposal_id: str, db: Session = Depends(get_db)):
  try:
    md_content = ExporterService.compile_to_markdown(db, proposal_id)
    return Response(
        content=md_content,
        media_type="text/markdown"
    )
  except ValueError as err:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

@router.get("/{proposal_id}/json")
def export_json(proposal_id: str, db: Session = Depends(get_db)):
  proposal = db.query(ProposalPlan).filter(ProposalPlan.id == proposal_id).first()
  if not proposal:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")

  sections = db.query(ProposalSection).filter(ProposalSection.proposal_plan_id == proposal_id).all()
  return {
      "id": proposal.id,
      "title": proposal.title,
      "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
      "sections": [
          {
              "id": sec.id,
              "title": sec.title,
              "content": sec.content,
              "status": sec.status
          }
          for sec in sections
      ]
  }
