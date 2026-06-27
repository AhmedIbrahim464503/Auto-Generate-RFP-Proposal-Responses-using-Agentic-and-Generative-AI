import time
from backend.app.core.celery_app import celery_app
from backend.app.db.session import SessionLocal

@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
  """
  Simulate background document parsing and metadata extraction
  """
  db = SessionLocal()
  try:
    print(f"Celery: starting document parsing for {document_id}")
    time.sleep(1) # simulate work
    print(f"Celery: finished document parsing for {document_id}")
    return {"status": "SUCCESS", "document_id": document_id}
  except Exception as exc:
    db.close()
    self.retry(exc=exc, countdown=5)
  finally:
    db.close()

@celery_app.task(bind=True, max_retries=3)
def index_knowledge_task(self, chunk_ids: list):
  """
  Simulate background vector embedding and indexing in FAISS/pgvector
  """
  try:
    print(f"Celery: starting indexing of chunks {chunk_ids}")
    time.sleep(1) # simulate embedding generation
    print(f"Celery: finished indexing of chunks")
    return {"status": "SUCCESS", "indexed_count": len(chunk_ids)}
  except Exception as exc:
    self.retry(exc=exc, countdown=5)

@celery_app.task(bind=True, max_retries=3)
def generate_proposal_section_task(self, proposal_id: str, section_id: str):
  """
  Simulate background agent generation and quality checks
  """
  try:
    print(f"Celery: generating draft for proposal {proposal_id} section {section_id}")
    time.sleep(2) # simulate writers LLM calls
    print(f"Celery: finished draft generation")
    return {"status": "SUCCESS", "proposal_id": proposal_id, "section_id": section_id}
  except Exception as exc:
    self.retry(exc=exc, countdown=5)
